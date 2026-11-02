"""Fetch one official page and retain it as evidence.

The order matters and is enforced here: read ``robots.txt`` first, refuse the
fetch if it says no, then fetch once, keep the readable text, and write an
artifact that records exactly what happened — request URL, the redirect chain,
final URL, HTTP status, content type, the hash of the raw response and of the
retained text, the user agent, the robots decision and the parser version.

Three consequences are deliberate:

- A redirect is not followed blindly. Each destination is checked against its
  own access rules *before* it is fetched, and every hop is recorded, so a
  citation pointing at an old host is caught instead of silently following the
  site elsewhere.
- The snapshot id is derived from the page address *and* the text, so a page
  that changes gets a new snapshot rather than overwriting the evidence a report
  was checked against.
- A file that already exists is never replaced: the same text fetched again
  would swap the provenance a report was checked against for a later fetch's.
"""

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import Message
from pathlib import Path
from typing import IO
from urllib.parse import urljoin, urlsplit

from pydantic import Field, HttpUrl

from app.collect.extract import extract_text
from app.collect.robots import RobotsRules
from app.domain.models import DomainModel
from app.publication.contracts import SourceSnapshot

PARSER_VERSION = "html-text/1"
USER_AGENT = "ScholarCheck/0.1 (evidence collection; +https://github.com/scholarcheck)"
ROBOTS_AGENT = "ScholarCheck"
TIMEOUT_SECONDS = 30
MAX_BYTES = 4_000_000
MAX_REDIRECTS = 5
HTML_TYPES = ("text/html", "application/xhtml+xml")
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
WEB_SCHEMES = ("http", "https")


class FetchRefused(Exception):
    """Raised when the source's access rules do not permit the fetch."""


class FetchFailed(Exception):
    """Raised when the page could not be fetched or read as page text."""


class SnapshotExists(Exception):
    """Raised when an artifact for this snapshot id is already retained.

    ``same_text`` tells the ordinary case (an unchanged page fetched again) from
    the odd one (a different page whose id collided); both refuse to write.
    """

    def __init__(self, message: str, *, path: Path, same_text: bool) -> None:
        super().__init__(message)
        self.path = path
        self.same_text = same_text


@dataclass(frozen=True)
class Fetched:
    """One response, kept as bytes so its hash is the bytes we actually read.

    ``location`` is set only when the answer was a redirect: collection resolves
    it, checks that address's access rules, and fetches it as the next hop.
    """

    request_url: str
    url: str
    status: int
    content_type: str
    charset: str
    payload: bytes
    retrieved_at: datetime
    location: str | None = None

    @property
    def raw_sha256(self) -> str:
        return hashlib.sha256(self.payload).hexdigest()

    def text(self) -> str:
        return self.payload.decode(self.charset, errors="replace")

    @property
    def is_html(self) -> bool:
        return any(kind in self.content_type for kind in HTML_TYPES)

    @property
    def is_redirect(self) -> bool:
        return self.location is not None


@dataclass(frozen=True)
class RobotsDecision:
    """What the access rules said, kept so the fetch can be audited."""

    robots_url: str
    allowed: bool
    detail: str

class SnapshotProvenance(DomainModel):
    """How a retained snapshot came to exist. Not shown, but never lost."""

    request_url: HttpUrl
    final_url: HttpUrl
    redirects: list[HttpUrl] = Field(
        default_factory=list,
        description=(
            "Addresses asked for and not retained, in order, each checked against "
            "its own access rules before it was fetched."
        ),
    )
    http_status: int = Field(ge=100, le=599)
    content_type: str = Field(min_length=1)
    raw_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    raw_bytes: int = Field(ge=0)
    user_agent: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    robots_url: HttpUrl
    robots_allowed: bool
    robots_detail: str = Field(min_length=1)


class SnapshotArtifact(DomainModel):
    """A retained snapshot plus the provenance needed to defend it."""

    snapshot: SourceSnapshot
    provenance: SnapshotProvenance


def snapshot_id(url: str, body: str) -> str:
    """Content-addressed id: same page text reuses it, changed text does not."""

    split = urlsplit(url)
    parts = [split.netloc.lower(), *[p for p in split.path.split("/") if p]]
    # Keep the meaningful tail of the path rather than chopping the id mid-word.
    while len("-".join(parts)) > 70 and len(parts) > 2:
        parts.pop(1)
    slug = re.sub(r"[^a-z0-9]+", "-", " ".join(parts)).strip("-")[:70].strip("-")
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{digest}"


def snapshot_from(fetched: Fetched) -> SourceSnapshot:
    """Build the retained snapshot, refusing pages with no usable text."""

    if fetched.is_redirect:
        raise FetchFailed(f"{fetched.request_url} redirects to {fetched.location}")
    if not fetched.is_html:
        raise FetchFailed(f"{fetched.content_type} is not an HTML page")
    if fetched.status >= 400:
        raise FetchFailed(f"the source answered {fetched.status}")

    body = extract_text(fetched.text())
    if len(body) < 200:
        raise FetchFailed(
            f"only {len(body)} characters of page text were readable; "
            "a snapshot that thin cannot support a claim"
        )

    return SourceSnapshot(
        id=snapshot_id(fetched.url, body),
        url=fetched.url,
        body=body,
        response_status=fetched.status,
        retrieved_at=fetched.retrieved_at,
        parser_version=PARSER_VERSION,
    )


class NoRedirects(urllib.request.HTTPRedirectHandler):
    """Stop urllib following redirects: collection checks each hop itself."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: Message,
        newurl: str,
    ) -> urllib.request.Request | None:
        """Return ``None`` so the redirect is reported instead of followed."""

        return None


_OPENER = urllib.request.build_opener(NoRedirects())


def fetch_page(url: str, *, user_agent: str = USER_AGENT) -> Fetched:
    """Fetch exactly one URL, without following a redirect, and keep its bytes."""

    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with _OPENER.open(request, timeout=TIMEOUT_SECONDS) as response:
            payload = response.read(MAX_BYTES + 1)
            if len(payload) > MAX_BYTES:
                raise FetchFailed(f"{url} is larger than {MAX_BYTES} bytes")
            return Fetched(
                request_url=url,
                url=response.geturl(),
                status=response.status,
                content_type=response.headers.get("Content-Type", ""),
                charset=response.headers.get_content_charset() or "utf-8",
                payload=payload,
                retrieved_at=datetime.now(tz=UTC).replace(microsecond=0),
            )
    except urllib.error.HTTPError as error:
        location = error.headers.get("Location") if error.headers else None
        if error.code in REDIRECT_STATUSES and location:
            return Fetched(
                request_url=url,
                url=url,
                status=error.code,
                content_type=error.headers.get("Content-Type", ""),
                charset="utf-8",
                payload=b"",
                retrieved_at=datetime.now(tz=UTC).replace(microsecond=0),
                location=urljoin(url, location),
            )
        raise FetchFailed(f"{url} answered {error.code}") from error
    except urllib.error.URLError as error:
        raise FetchFailed(f"{url} could not be reached: {error.reason}") from error




def read_robots(url: str, *, user_agent: str = USER_AGENT) -> RobotsDecision:
    """Read the site's access rules and decide whether ``url`` may be fetched."""

    split = urlsplit(url)
    robots_url = f"{split.scheme}://{split.netloc}/robots.txt"
    request = urllib.request.Request(robots_url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            rules = RobotsRules.parse(response.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as error:
        # An absent rules file states no restriction; a denied one does.
        if error.code in (401, 403):
            return RobotsDecision(robots_url, False, f"robots.txt answered {error.code}")
        return RobotsDecision(robots_url, True, f"robots.txt answered {error.code}")
    except urllib.error.URLError as error:
        return RobotsDecision(robots_url, True, f"robots.txt unreachable: {error.reason}")

    allowed = rules.allows(url, user_agent=ROBOTS_AGENT)
    detail = "no matching rule" if allowed else "a matching disallow rule"
    return RobotsDecision(robots_url, allowed, detail)


def collect(
    url: str,
    *,
    fetcher: Callable[[str, str], Fetched] | None = None,
    robots: Callable[[str], RobotsDecision] | None = None,
    user_agent: str = USER_AGENT,
) -> SnapshotArtifact:
    """Check the access rules at every hop, fetch, and retain what answered.

    A redirect is a second fetch of a second address, so it gets its own rules
    check before it happens. Nothing is fetched for an address the rules refuse,
    and the whole collection fails rather than falling back to the last permitted
    address: a page reached by a shortcut is not the page that was asked for.
    """

    read = robots or read_robots
    fetch = fetcher or (lambda target, agent: fetch_page(target, user_agent=agent))

    target = url
    redirects: list[str] = []
    while True:
        decision = read(target)
        if not decision.allowed:
            came_from = f" (redirected from {url})" if redirects else ""
            raise FetchRefused(f"{target}{came_from} may not be fetched: {decision.detail}")

        fetched = fetch(target, user_agent)
        if not fetched.is_redirect:
            break
        if len(redirects) >= MAX_REDIRECTS:
            raise FetchFailed(f"{url} redirects more than {MAX_REDIRECTS} times")
        hop = fetched.location or ""
        if urlsplit(hop).scheme not in WEB_SCHEMES:
            raise FetchFailed(f"{url} redirects to {hop!r}, which is not a web address")
        redirects.append(hop)
        target = hop

    if fetched.url != target:
        # A fetcher that follows redirects itself would hide the destination from
        # the rules check, so a mismatch is an error and not something to record.
        raise FetchFailed(
            f"the fetcher answered for {fetched.url} when asked for {target}; "
            "each redirect hop must be reported so its access rules are checked"
        )

    snapshot = snapshot_from(fetched)
    return SnapshotArtifact(
        snapshot=snapshot,
        provenance=SnapshotProvenance(
            request_url=url,
            final_url=fetched.url,
            redirects=redirects,
            http_status=fetched.status,
            content_type=fetched.content_type,
            raw_sha256=fetched.raw_sha256,
            raw_bytes=len(fetched.payload),
            user_agent=user_agent,
            parser_version=PARSER_VERSION,
            robots_url=decision.robots_url,
            robots_allowed=decision.allowed,
            robots_detail=decision.detail,
        ),
    )


def write_artifact(artifact: SnapshotArtifact, directory: Path) -> Path:
    """Keep one file per snapshot and never replace a retained one.

    The id is content-addressed, so an existing file holds the same page text:
    writing again would replace the time, status and hashes a report was checked
    against with a later fetch's. An identical artifact is a no-op; anything else
    raises :class:`SnapshotExists` and leaves the retained file untouched.
    """

    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{artifact.snapshot.id}.json"
    payload = artifact.model_dump(mode="json", by_alias=True)
    text = f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n"

    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError:
        if path.read_text(encoding="utf-8") == text:
            return path
        raise SnapshotExists(
            _already_retained(path, artifact), path=path, same_text=_same_text(path, artifact)
        ) from None
    return path


def _already_retained(path: Path, artifact: SnapshotArtifact) -> str:
    """Say what is already there, so the operator knows what the fetch would cost."""

    if _same_text(path, artifact):
        return (
            f"{path.name} already retains this page text; rewriting it would replace the "
            "provenance it was cited with, so nothing was written"
        )
    return (
        f"{path} already exists for a different page text; refusing to replace "
        "retained evidence"
    )


def _same_text(path: Path, artifact: SnapshotArtifact) -> bool:
    try:
        kept = load_artifact(path)
    except ValueError:
        return False
    return kept.snapshot.body == artifact.snapshot.body


def load_artifact(path: Path) -> SnapshotArtifact:
    """Read a retained artifact back, so a report can cite it later."""

    return SnapshotArtifact.model_validate_json(path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    """``python -m app.collect.snapshot URL...`` writes one artifact per page."""

    args = list(sys.argv[1:] if argv is None else argv)
    out = Path("content/snapshots")
    if "--out" in args:
        index = args.index("--out")
        out = Path(args[index + 1])
        del args[index : index + 2]

    failures = 0
    for url in args:
        try:
            artifact = collect(url)
        except (FetchRefused, FetchFailed) as error:
            failures += 1
            print(f"refused {url}: {error}", file=sys.stderr)
            continue
        try:
            path = write_artifact(artifact, out)
        except SnapshotExists as kept:
            if kept.same_text:
                print(f"{artifact.snapshot.id}  unchanged  {kept.path}")
                continue
            failures += 1
            print(f"refused {url}: {kept}", file=sys.stderr)
            continue
        snapshot = artifact.snapshot
        print(
            f"{snapshot.id}  {snapshot.response_status}  "
            f"{len(snapshot.body)} chars  {path}"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
