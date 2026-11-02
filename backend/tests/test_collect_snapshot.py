"""The collector: what it may fetch, what it keeps, and what it refuses.

Access rules come first, the retained text is the only thing a claim can quote,
and every artifact keeps enough provenance to defend the fetch later. These
tests use no network: the fetch and the rules read are injected.
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.collect.extract import extract_text
from app.collect.robots import RobotsRules
from app.collect.snapshot import (
    FetchFailed,
    FetchRefused,
    Fetched,
    RobotsDecision,
    collect,
    load_artifact,
    snapshot_from,
    snapshot_id,
    write_artifact,
)

RETRIEVED = datetime(2026, 11, 2, 9, 30, tzinfo=UTC)
URL = "https://www.example.edu/scholarships/doctoral-award"

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
) -> Fetched:
    return Fetched(
        request_url=request_url or url,
        url=url,
        status=status,
        content_type=content_type,
        charset="utf-8",
        payload=html.encode("utf-8"),
        retrieved_at=RETRIEVED,
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
    """A citation pointing at an old address must not silently follow the site."""

    moved = "https://www.example.ca/awards/doctoral"

    artifact = collect(
        URL,
        fetcher=lambda url, agent: fetched(url=moved, request_url=url),
        robots=allowed,
    )

    assert str(artifact.provenance.request_url) == URL
    assert str(artifact.provenance.final_url) == moved
    assert str(artifact.snapshot.url) == moved


def test_artifacts_round_trip_through_disk(tmp_path: Path) -> None:
    artifact = collect(URL, fetcher=lambda url, agent: fetched(), robots=allowed)

    path = write_artifact(artifact, tmp_path)
    restored = load_artifact(path)

    assert restored == artifact
    assert restored.snapshot.body == artifact.snapshot.body
