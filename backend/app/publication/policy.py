"""Named publication policy values.

``POLICY_VERSION`` identifies the exact gate implementation that produced a
report. Bump it whenever the checks change: a report written under another
version is re-checked rather than published.

The approved hosts are the official providers the four regression fixtures and
the first launch set cite. Government portals, universities and established
scholarship NGOs only (``ARCHITECTURE.md`` boundary 1). The list moves to
configuration when the collector exists; the gate already takes it as an
argument so tests can exercise a different set.
"""

from collections.abc import Sequence
from urllib.parse import urlsplit

from pydantic import HttpUrl

POLICY_VERSION = "s01.publication.1"

APPROVED_SOURCE_HOSTS: tuple[str, ...] = (
    "nserc-crsng.gc.ca",
    "registraire.umontreal.ca",
    "esp.umontreal.ca",
    "rmit.edu.au",
    "sydney.edu.au",
)


def source_host(url: HttpUrl | str) -> str:
    """The lower-case host of a source URL, without a trailing dot."""

    return (urlsplit(str(url)).hostname or "").lower().rstrip(".")


def is_approved_source(
    url: HttpUrl | str, approved_hosts: Sequence[str]
) -> bool:
    """True when the URL's host is, or is under, an approved provider domain."""

    host = source_host(url)
    return any(
        host == allowed or host.endswith(f".{allowed}") for allowed in approved_hosts
    )
