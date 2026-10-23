# Evidence — S01

Status: **not recorded yet.**

Per `VERIFICATION.md` section 8, each acceptance criterion needs an artifact.
Record them here as the slice progresses:

- AC-01..AC-03: profile form component tests + screenshots, storage inspection.
- AC-04: listing component test, link check, screenshot.
- AC-05: API 404 example (`{code: "opportunity_not_found"}`), UI screenshot.
- AC-06..AC-09: evaluator matrix test output, UI screenshots.
- AC-10: data-to-UI test output, screenshot.
- AC-11: evidence-panel test, screenshot.
- AC-12, AC-13: storage-fixture tests, storage inspection.
- AC-14: forced-failure test, screenshot.

Step 1 artifacts (scaffold only). Proposed API shapes awaiting the T02/T07 gate
are in `PROPOSED-CONTRACTS.md`; they are not part of `VERIFICATION.md` §5 yet.

| Check | Command | Result |
|---|---|---|
| Backend tests | `cd backend && .venv/bin/python -m pytest` | 27 passed |
| Frontend tests | `cd frontend && npm run test` | 7 passed |
| Type check | `cd frontend && npx tsc -b --force` | exit 0 |
| Lint | `cd frontend && npm run lint` | exit 0 |
| Production build | `cd frontend && npm run build` | built |

No acceptance criterion is proven by Step 1: it adds no listing, profile form,
evidence panel or save behaviour. Fixture data is still unverified against
official sources and remains a release blocker for S01.
