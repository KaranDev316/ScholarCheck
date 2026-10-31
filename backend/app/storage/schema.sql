CREATE TABLE IF NOT EXISTS opportunities (
    id text PRIMARY KEY,
    payload jsonb NOT NULL,
    content_hash text NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS publication_state (
    opportunity_id text PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
    assurance text NOT NULL DEFAULT 'insufficient_evidence',
    source_checked_at timestamptz,
    validation_policy_version text,
    freshness text NOT NULL DEFAULT 'not_checked'
        CHECK (freshness IN ('not_checked', 'current', 'needs_recheck', 'stale')),
    revision integer,
    CONSTRAINT publication_state_assurance_check
        CHECK (assurance IN ('insufficient_evidence', 'source_checked')),
    CONSTRAINT publication_state_metadata_check
        CHECK (
            (assurance = 'insufficient_evidence' AND source_checked_at IS NULL
                AND validation_policy_version IS NULL AND revision IS NULL)
            OR (assurance = 'source_checked' AND source_checked_at IS NOT NULL
                AND validation_policy_version IS NOT NULL AND revision IS NOT NULL)
        )
);

CREATE TABLE IF NOT EXISTS programmes (
    opportunity_id text NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    id text NOT NULL,
    position integer NOT NULL,
    payload jsonb NOT NULL,
    PRIMARY KEY (opportunity_id, id),
    UNIQUE (opportunity_id, position)
);

CREATE TABLE IF NOT EXISTS rounds (
    opportunity_id text NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    id text NOT NULL,
    position integer NOT NULL,
    payload jsonb NOT NULL,
    PRIMARY KEY (opportunity_id, id),
    UNIQUE (opportunity_id, position)
);

CREATE TABLE IF NOT EXISTS eligibility_rules (
    opportunity_id text NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    id text NOT NULL,
    position integer NOT NULL,
    payload jsonb NOT NULL,
    PRIMARY KEY (opportunity_id, id),
    UNIQUE (opportunity_id, position)
);

CREATE TABLE IF NOT EXISTS funding_components (
    opportunity_id text NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    id text NOT NULL,
    position integer NOT NULL,
    payload jsonb NOT NULL,
    PRIMARY KEY (opportunity_id, id),
    UNIQUE (opportunity_id, position)
);

CREATE TABLE IF NOT EXISTS evidence (
    opportunity_id text NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    id text NOT NULL,
    position integer NOT NULL,
    payload jsonb NOT NULL,
    PRIMARY KEY (opportunity_id, id),
    UNIQUE (opportunity_id, position)
);

CREATE TABLE IF NOT EXISTS source_snapshots (
    id text PRIMARY KEY,
    url text NOT NULL,
    body text NOT NULL,
    content_hash text NOT NULL,
    response_status integer NOT NULL,
    retrieved_at timestamptz NOT NULL,
    parser_version text NOT NULL,
    stored_at timestamptz NOT NULL DEFAULT now()
);

-- A retained snapshot is the evidence a decision points at; rewriting it would
-- silently change what a published record was checked against.
CREATE OR REPLACE FUNCTION reject_source_snapshot_change() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'source snapshots are immutable';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS source_snapshots_immutable ON source_snapshots;
CREATE TRIGGER source_snapshots_immutable
    BEFORE UPDATE OR DELETE ON source_snapshots
    FOR EACH ROW EXECUTE FUNCTION reject_source_snapshot_change();

CREATE TABLE IF NOT EXISTS opportunity_revisions (
    opportunity_id text NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    revision integer NOT NULL CHECK (revision >= 1),
    content_hash text NOT NULL,
    payload jsonb NOT NULL,
    policy_version text NOT NULL,
    checked_at timestamptz NOT NULL,
    report jsonb NOT NULL,
    published_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (opportunity_id, revision)
);

CREATE TABLE IF NOT EXISTS revision_snapshots (
    opportunity_id text NOT NULL,
    revision integer NOT NULL,
    snapshot_id text NOT NULL REFERENCES source_snapshots(id),
    PRIMARY KEY (opportunity_id, revision, snapshot_id),
    FOREIGN KEY (opportunity_id, revision)
        REFERENCES opportunity_revisions(opportunity_id, revision)
        ON DELETE CASCADE
);

-- Migration: human verification is no longer an assurance level (D-11), and a
-- claimed source check must name the published revision behind it. Rows that
-- predate the gate cannot satisfy either rule, so they fall back to
-- insufficient_evidence and ask for a recheck instead of keeping a label.
ALTER TABLE publication_state
    DROP CONSTRAINT IF EXISTS publication_state_assurance_check,
    DROP CONSTRAINT IF EXISTS publication_state_metadata_check,
    DROP CONSTRAINT IF EXISTS publication_state_check,
    ADD COLUMN IF NOT EXISTS revision integer;

UPDATE publication_state
SET assurance = 'insufficient_evidence',
    source_checked_at = NULL,
    validation_policy_version = NULL,
    revision = NULL,
    freshness = 'needs_recheck'
WHERE assurance = 'human_verified'
    OR (assurance = 'source_checked' AND revision IS NULL);

ALTER TABLE publication_state
    ADD CONSTRAINT publication_state_assurance_check
        CHECK (assurance IN ('insufficient_evidence', 'source_checked')),
    ADD CONSTRAINT publication_state_metadata_check
        CHECK (
            (assurance = 'insufficient_evidence' AND source_checked_at IS NULL
                AND validation_policy_version IS NULL AND revision IS NULL)
            OR (assurance = 'source_checked' AND source_checked_at IS NOT NULL
                AND validation_policy_version IS NOT NULL AND revision IS NOT NULL)
        ),
    DROP CONSTRAINT IF EXISTS publication_state_revision_fkey,
    ADD CONSTRAINT publication_state_revision_fkey
        FOREIGN KEY (opportunity_id, revision)
        REFERENCES opportunity_revisions(opportunity_id, revision);
