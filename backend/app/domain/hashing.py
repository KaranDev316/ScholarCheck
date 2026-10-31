"""Canonical hash of an opportunity's published facts.

One definition serves the fixture loader, the publication gate and the stored
revision, so a validation report can name the exact revision it validated and
the loader can tell an unchanged file from a changed one.
"""

import hashlib
import json

from app.domain.models import Opportunity


def content_hash(opportunity: Opportunity) -> str:
    """SHA-256 over the record's canonical JSON form (key order independent)."""

    payload = opportunity.model_dump(mode="json", by_alias=False)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
