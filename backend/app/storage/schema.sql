CREATE TABLE IF NOT EXISTS opportunities (
    id text PRIMARY KEY,
    payload jsonb NOT NULL,
    content_hash text NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS publication_state (
    opportunity_id text PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
    assurance text NOT NULL DEFAULT 'insufficient_evidence'
        CHECK (assurance IN ('insufficient_evidence', 'source_checked', 'human_verified')),
    source_checked_at timestamptz,
    validation_policy_version text,
    freshness text NOT NULL DEFAULT 'not_checked'
        CHECK (freshness IN ('not_checked', 'current', 'needs_recheck', 'stale')),
    CHECK (
        (assurance = 'insufficient_evidence' AND source_checked_at IS NULL
            AND validation_policy_version IS NULL)
        OR (assurance IN ('source_checked', 'human_verified')
            AND source_checked_at IS NOT NULL
            AND validation_policy_version IS NOT NULL)
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
