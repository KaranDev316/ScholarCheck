"""Fetch one official page and retain it as evidence.

The order matters and is enforced here: read ``robots.txt`` first, refuse the
fetch if it says no, then fetch once, keep the readable text, and write an
artifact that records exactly what happened — request URL, final URL after
redirects, HTTP status, content type, the hash of the raw response and of the
retained text, the user agent, the robots decision and the parser version.

Two consequences are deliberate:

- A redirect that leaves the approved provider is visible in the artifact, so a
  citation pointing at an old host is caught instead of silently following the
  site elsewhere.
- The snapshot id is derived from the page address *and* the text, so a page
  that changes gets a new snapshot rather than overwriting the evidence a report
  was checked against.
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
from pathlib import Path
from urllib.parse import urlsplit

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
HTML_TYPES = ("text/html", "application/xhtml+xml")


class FetchRefused(Exception):
    """Raised when the source's access rules do not permit the fetch."""


class FetchFailed(Exception):
    """Raised when the page could not be fetched or read as page text."""


@dataclass(frozen=True)
class Fetched:
    """One response, kept as bytes so its hash is the bytes we actually read."""

    request_url: str
    url: str
    status: int
    content_type: str
    charset: str
    payload: bytes
    retrieved_at: datetime

    @property
    def raw_sha256(self) -> str:
        return hashlib.sha256(self.payload).hexdigest()

    def text(self) -> str:
        return self.payload.decode(self.charset, errors="replace")

    @property
    def is_html(self) -> bool:
        return any(kind in self.content_type for kind in HTML_TYPES)


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


def fetch_page(url: str, *, user_agent: str = USER_AGENT) -> Fetched:
    """Fetch one URL once, following redirects, and keep its bytes."""

    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
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
    """Check the access rules, fetch once, and return the retained snapshot."""

    read = robots or read_robots
    fetch = fetcher or (lambda target, agent: fetch_page(target, user_agent=agent))

    decision = read(url)
    if not decision.allowed:
        raise FetchRefused(f"{url} may not be fetched: {decision.detail}")

    fetched = fetch(url, user_agent)
    snapshot = snapshot_from(fetched)
    return SnapshotArtifact(
        snapshot=snapshot,
        provenance=SnapshotProvenance(
            request_url=fetched.request_url,
            final_url=fetched.url,
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
    """Keep the artifact beside the rest of the content, one file per snapshot."""

    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{artifact.snapshot.id}.json"
    payload = artifact.model_dump(mode="json", by_alias=True)
    body = json.dumps(payload, indent=2, ensure_ascii=False)
    path.write_text(f"{body}\n", encoding="utf-8")
    return path


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
        path = write_artifact(artifact, out)
        snapshot = artifact.snapshot
        print(
            f"{snapshot.id}  {snapshot.response_status}  "
            f"{len(snapshot.body)} chars  {path}"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
