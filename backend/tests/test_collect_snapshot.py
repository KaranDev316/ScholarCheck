"""The collector: what it may fetch, what it keeps, and what it refuses.

Access rules come first, the retained text is the only thing a claim can quote,
and every artifact keeps enough provenance to defend the fetch later. These
tests use no network: the fetch and the rules read are injected.
"""

from datetime import UTC, datetime
from email.message import Message
from pathlib import Path
from urllib.request import Request

import pytest

from app.collect.extract import extract_text
from app.collect.robots import RobotsRules
from app.collect.snapshot import (
    FetchFailed,
    FetchRefused,
    Fetched,
    NoRedirects,
    RobotsDecision,
    SnapshotExists,
    collect,
    load_artifact,
    snapshot_from,
    snapshot_id,
    write_artifact,
)

RETRIEVED = datetime(2026, 11, 2, 9, 30, tzinfo=UTC)
URL = "https://www.example.edu/scholarships/doctoral-award"
SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "content" / "snapshots"

PAGE = """
<html><head><title>ignored</title><style>.x{color:red}</style></head>
<body>
<header><nav><a href="/">Home</a></nav></header>
<main>
  <h1>Doctoral award</h1>
  <p>The scholarship pays <b>$40,000</b> per year for 36 months.</p>
  <table><tr><th>Round</th><th>Deadline</th></tr>
  <tr><td>2027</td><td>17 October</td></tr></table>
  <ul><li>Full-time enrolment</li><li>No other award</li></ul>
  <p>Applicants must submit their research proposal and supporting documents through the university portal before the published deadline.</p>
</main>
<footer>Copyright</footer>
<script>var tracking = "never retained";</script>
</body></html>
"""


def fetched(
    html: str = PAGE,
    *,
    url: str = URL,
    request_url: str | None = None,
    status: int = 200,
    content_type: str = "text/html; charset=utf-8",
    retrieved_at: datetime = RETRIEVED,
) -> Fetched:
    return Fetched(
        request_url=request_url or url,
        url=url,
        status=status,
        content_type=content_type,
        charset="utf-8",
        payload=html.encode("utf-8"),
        retrieved_at=retrieved_at,
    )


def redirects_to(url: str, target: str, *, status: int = 302) -> Fetched:
    """One hop of a redirect chain: no page yet, only the address to check next."""

    return Fetched(
        request_url=url,
        url=url,
        status=status,
        content_type="text/html; charset=utf-8",
        charset="utf-8",
        payload=b"",
        retrieved_at=RETRIEVED,
        location=target,
    )


def allowed(url: str) -> RobotsDecision:
    return RobotsDecision(f"{url}/robots.txt", True, "no matching rule")


def denied(url: str) -> RobotsDecision:
    return RobotsDecision(f"{url}/robots.txt", False, "a matching disallow rule")


def test_extraction_keeps_the_text_a_claim_can_quote() -> None:
    text = extract_text(PAGE)

    assert "$40,000" in text and "17 October" in text
    assert "Full-time enrolment" in text


def test_extraction_drops_scripts_styles_and_page_chrome() -> None:
    text = extract_text(PAGE)

    for noise in ("never retained", "color:red", "Copyright", "Home", "ignored"):
        assert noise not in text


def test_inline_markup_does_not_split_a_sentence() -> None:
    """A bold amount must not become a separate line, or a quote cannot match."""

    assert "The scholarship pays $40,000 per year for 36 months." in extract_text(PAGE)


def test_block_markup_becomes_a_line_break() -> None:
    text = extract_text(PAGE)

    assert "Full-time enrolment\nNo other award" in text


def test_entities_are_unescaped_and_escaped_markup_is_removed() -> None:
    html = "<main><p>Caf&eacute; &amp;nbsp; award</p><p>stray</p>&lt;/p&gt;&lt;h3&gt;x&lt;/h3&gt;</main>"

    text = extract_text(html)

    assert "Café" in text
    assert "</p>" not in text and "<h3>" not in text


def test_a_page_without_a_main_region_still_yields_its_text() -> None:
    html = "<html><body><div>" + ("Award text. " * 60) + "</div></body></html>"

    assert "Award text." in extract_text(html)


def test_a_snapshot_records_the_page_it_came_from() -> None:
    snapshot = snapshot_from(fetched())

    assert str(snapshot.url) == URL
    assert snapshot.response_status == 200
    assert snapshot.retrieved_at == RETRIEVED
    assert snapshot.parser_version
    assert "Home" not in snapshot.body


@pytest.mark.parametrize(
    ("kwargs", "reason"),
    [
        ({"status": 500}, "answered 500"),
        ({"content_type": "application/pdf"}, "not an HTML page"),
        ({"html": "<html><body>too thin</body></html>"}, "cannot support a claim"),
    ],
)
def test_pages_that_cannot_support_a_claim_are_refused(kwargs, reason) -> None:
    with pytest.raises(FetchFailed, match=reason):
        snapshot_from(fetched(**kwargs))


def test_the_snapshot_id_follows_the_text() -> None:
    """Changed page text must produce a new snapshot, not overwrite the old one."""

    first = snapshot_id(URL, "award text")
    assert first == snapshot_id(URL, "award text")
    assert first != snapshot_id(URL, "award text, revised")
    assert first != snapshot_id("https://www.example.edu/other", "award text")


def test_access_rules_are_checked_before_the_page_is_fetched() -> None:
    calls: list[str] = []

    def fetch(url: str, user_agent: str) -> Fetched:
        calls.append(url)
        return fetched()

    with pytest.raises(FetchRefused):
        collect(URL, fetcher=fetch, robots=denied)

    assert calls == [], "a refused page must not be fetched at all"


def test_collection_keeps_the_redirect_visible() -> None:
    """A citation pointing at an old address must show what it was moved to."""

    moved = "https://www.example.ca/awards/doctoral"

    def fetch(url: str, agent: str) -> Fetched:
        return redirects_to(URL, moved, status=301) if url == URL else fetched(url=moved)

    artifact = collect(URL, fetcher=fetch, robots=allowed)

    assert str(artifact.provenance.request_url) == URL
    assert [str(hop) for hop in artifact.provenance.redirects] == [moved]
    assert str(artifact.provenance.final_url) == moved
    assert str(artifact.snapshot.url) == moved


def test_a_redirect_destination_is_checked_before_it_is_fetched() -> None:
    """The address that answers also gets asked, so its rules are checked too."""

    moved = "https://www.example.ca/awards/doctoral"
    fetched_urls: list[str] = []

    def fetch(url: str, agent: str) -> Fetched:
        fetched_urls.append(url)
        return redirects_to(URL, moved)

    def rules(url: str) -> RobotsDecision:
        return denied(url) if url == moved else allowed(url)

    with pytest.raises(FetchRefused, match="redirected from"):
        collect(URL, fetcher=fetch, robots=rules)

    assert fetched_urls == [URL], "the destination must not be fetched at all"


def test_every_address_on_the_way_is_checked_in_order() -> None:
    middle = "https://www.example.ca/moved"
    final = "https://www.example.edu/current/award"
    checked: list[str] = []

    def rules(url: str) -> RobotsDecision:
        checked.append(url)
        return allowed(url)

    def fetch(url: str, agent: str) -> Fetched:
        hops = {URL: middle, middle: final}
        return redirects_to(url, hops[url]) if url in hops else fetched(url=final)

    artifact = collect(URL, fetcher=fetch, robots=rules)

    assert checked == [URL, middle, final]
    assert [str(hop) for hop in artifact.provenance.redirects] == [middle, final]
    assert str(artifact.snapshot.url) == final


def test_a_redirect_loop_is_refused() -> None:
    with pytest.raises(FetchFailed, match="redirects more than"):
        collect(
            URL,
            fetcher=lambda url, agent: redirects_to(url, f"{url}/again"),
            robots=allowed,
        )


def test_a_redirect_outside_the_web_is_refused() -> None:
    with pytest.raises(FetchFailed, match="not a web address"):
        collect(
            URL,
            fetcher=lambda url, agent: redirects_to(URL, "ftp://files.example.edu/award"),
            robots=allowed,
        )


def test_a_fetcher_that_follows_redirects_itself_is_refused() -> None:
    """A hidden hop is an unchecked address, so it cannot be recorded as if it were."""

    moved = "https://www.example.ca/awards/doctoral"

    with pytest.raises(FetchFailed, match="each redirect hop must be reported"):
        collect(URL, fetcher=lambda url, agent: fetched(url=moved), robots=allowed)


def test_the_page_fetcher_leaves_redirects_to_the_collector() -> None:
    """urllib follows redirects by default; the fetch must not, or no hop is checked."""

    handler = NoRedirects()
    next_request = handler.redirect_request(
        Request(URL), None, 302, "Found", Message(), "https://www.example.ca/awards"
    )

    assert next_request is None


def test_artifacts_round_trip_through_disk(tmp_path: Path) -> None:
    artifact = collect(URL, fetcher=lambda url, agent: fetched(), robots=allowed)

    path = write_artifact(artifact, tmp_path)
    restored = load_artifact(path)

    assert restored == artifact
    assert restored.snapshot.body == artifact.snapshot.body


def test_writing_the_same_artifact_twice_is_a_no_op(tmp_path: Path) -> None:
    artifact = collect(URL, fetcher=lambda url, agent: fetched(), robots=allowed)

    path = write_artifact(artifact, tmp_path)

    assert write_artifact(artifact, tmp_path) == path
    assert load_artifact(path) == artifact


def test_a_repeat_fetch_cannot_replace_retained_provenance(tmp_path: Path) -> None:
    """The same text fetched later must leave the retained artifact's facts alone."""

    first = collect(URL, fetcher=lambda url, agent: fetched(), robots=allowed)
    path = write_artifact(first, tmp_path)
    retained = path.read_text(encoding="utf-8")

    later = datetime(2026, 11, 9, 8, 0, tzinfo=UTC)
    refetched = collect(
        URL, fetcher=lambda url, agent: fetched(retrieved_at=later), robots=allowed
    )
    assert refetched.snapshot.id == first.snapshot.id, "same text, so the same id"
    assert refetched.snapshot.retrieved_at != first.snapshot.retrieved_at

    with pytest.raises(SnapshotExists) as refused:
        write_artifact(refetched, tmp_path)

    assert refused.value.same_text is True
    assert refused.value.path == path
    assert "already retains this page text" in str(refused.value)
    assert path.read_text(encoding="utf-8") == retained
    assert load_artifact(path).snapshot.retrieved_at == RETRIEVED


def test_an_id_collision_never_replaces_a_different_page(tmp_path: Path) -> None:
    artifact = collect(URL, fetcher=lambda url, agent: fetched(), robots=allowed)
    path = write_artifact(artifact, tmp_path)
    other_page = artifact.model_copy(
        update={"snapshot": artifact.snapshot.model_copy(update={"body": "a different page"})}
    )

    with pytest.raises(SnapshotExists) as refused:
        write_artifact(other_page, tmp_path)

    assert refused.value.same_text is False
    assert load_artifact(path) == artifact


def test_retained_evidence_still_round_trips_through_the_writer(tmp_path: Path) -> None:
    """Every artifact kept in the repository must still load and still write once."""

    snapshots = sorted(SNAPSHOT_DIR.glob("*.json"))
    assert snapshots, "no retained snapshots to check"

    for path in snapshots:
        artifact = load_artifact(path)
        assert write_artifact(artifact, tmp_path) == tmp_path / path.name
        assert load_artifact(tmp_path / path.name) == artifact


def test_registered_collection_refuses_unapproved_redirect_before_fetching():
    fetched_urls = []
    def fetch(url, agent):
        fetched_urls.append(url)
        return redirects_to(url, 'https://unapproved.example/award')
    with pytest.raises(FetchRefused, match='not registered'):
        collect(URL, fetcher=fetch, robots=allowed, allowed_hosts=('example.edu',))
    assert fetched_urls == [URL]
