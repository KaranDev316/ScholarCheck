# Release and monitoring

The API and built React website run as one FastAPI service. PostgreSQL retains
published revisions, problem reports and monitoring history. Files under
`var/` hold private extraction/checking audit artifacts and changed snapshots.
Do not serve that directory or `content/` as static assets.

## Required deployment inputs

Set the real `PUBLIC_ORIGIN` and `CONTACT_EMAIL`, a PostgreSQL password and a
random `REPORT_HASH_KEY` in an uncommitted `.env` using `.env.example`. The key
HMACs client addresses for the report rate limit; raw addresses are not stored.
Use a URL-safe database password or percent-encode it in the connection URL.
ScholarCheck remains the product name. No contact address has been invented.

Docker Compose deployment (Docker is not installed in the implementation
workspace, so this container build has not been executed here):

```sh
docker compose build
docker compose up -d database
docker compose run --rm web python -m app.manage init
docker compose run --rm web python -m app.manage publish-launch
docker compose up -d web
```

The web port binds to localhost. Configure the chosen hosting platform or a
TLS reverse proxy for the real origin. The process does not trust forwarded
client-address headers; behind a proxy the report limit is therefore shared
by that proxy's address. Configure a trusted proxy boundary before enabling
forwarded client addresses. The current limit is five reports per address hash
per hour, with an 8 KiB request-body cap and bounded input fields.

The launch command validates the recorded CGRS D proposal and separate
adjudications, rebuilds the report with its actual recorded check time, runs
policy `s01.publication.3`, and publishes atomically. It is idempotent for an
identical record/report/snapshot set. It does not refresh a source or invent a
new check date. RMIT's finding stays in the register and blocks publication.
The launch inputs are retained in `content/publication/cgrs-d/complete-run/`.

For a native deployment, run `npm ci && npm run build` in `frontend`, install
`backend` from `pyproject.toml`, set `DATABASE_URL`, `APP_ENV=production`,
`FRONTEND_DIST` to the absolute `frontend/dist` path, `CONTACT_EMAIL`,
`REPORT_HASH_KEY` and `CORS_ALLOWED_ORIGINS` to the actual origin. Run
`python -m app.manage init`, then `python -m app.manage publish-launch` from
`backend`, and serve `app.main:app` with Uvicorn.

## Release proof

After deployment, run from the repository root:

```sh
python3 scripts/smoke.py https://YOUR_REAL_ORIGIN --report --require-contact
```

This checks the deployed HTML, health, public catalogue/detail, empty search,
RMIT's private status, contact configuration and a persisted test report.
Also exercise the home → search/filter → detail → official links and report
journey in a browser at that origin. The local production build was tested;
no public deployment URL or deployed smoke result exists yet.

A problem report is accepted into `problem_reports`, not emailed. Operators
can inspect that table through their database tooling. There is no public
endpoint exposing reports or caller hashes.

## Model configuration

The two passes are stateless, separate calls. Set `OPENAI_API_KEY`,
`EXTRACT_MODEL` and `CHECK_MODEL` in the runtime environment to use the built-in
Responses API adapter; choose model IDs available to your project. Do not put
credentials in chat, source control, commands or audit files. API calls use
JSON mode with mandatory local Pydantic validation; JSON syntax is not evidence
of factual support. Incomplete responses, refusals and invalid proposals never
publish. The adapter follows the [official structured-output documentation](https://developers.openai.com/api/docs/guides/structured-outputs).

Alternatively, set `EXTRACT_COMMAND` and `CHECK_COMMAND` to executables that
read the pipeline's JSON input on stdin and write the requested JSON result on
stdout. They run without a shell, with a timeout. The extractor receives full
snapshots, a schema and the previous published record when monitoring; the
checker receives the candidate and full snapshots in a separate invocation.
The checker does not inherit an extractor conversation or support verdict.

A new validation run can be executed with:

```sh
cd backend
python -m app.publication.pipeline --snapshot ../content/snapshots/RETAINED_FILE.json --audit var/audits/UNIQUE_RUN_ID
```

Add `--publish` only when that run should write a passing revision. The CLI
also accepts `--proposal` and `--adjudications` for replaying independently
recorded pass outputs. Audit directories are created exclusively and never
overwritten. Raw outputs, validated inputs, snapshot fingerprints, material
facts, the report and gate decision remain internal.

The committed launch proposal and adjudications were produced during the Codex
source review, using the retained full CGRS D page. They are not represented
as an executed Responses API request. The built-in API adapter has transport
and refusal tests; a live provider call remains untested without configured
credentials/models.

## One-record monitoring

After publishing the launch record:

```sh
docker compose --profile monitoring up -d monitor
```

This polls scheduling state hourly and checks CGRS D daily. With a native
installation, schedule `python -m app.monitoring.worker cgsd-doctoral` hourly,
or use `--loop`. `--force` runs a check immediately, including retrying held
content. Only registered published source URLs are monitored, and the provider
allowlist and access rules are checked at every redirect before fetching.

Unchanged page text does no extraction/checking or publication work. Changed
text passes through extraction, checking and the same gate. A supported change
creates a revision; unsupported or uncertain output preserves the previous
revision and marks `needs_recheck`. Without model configuration a changed page
is retained and held. Failed fetches preserve the check date and mark `stale`,
with retries after 2, 4, 8, 16 and at most 24 hours. PostgreSQL locks prevent
concurrent workers from duplicating work. `monitor_runs` and `monitor_state`
record outcomes and due times; audit files are on the persistent `audits` volume.

The worker's unchanged, unsupported-change, supported-change, duplicate,
failed-fetch and retry paths have PostgreSQL tests. Production scheduling and
live model-provider behavior still need validation in the chosen deployment.
