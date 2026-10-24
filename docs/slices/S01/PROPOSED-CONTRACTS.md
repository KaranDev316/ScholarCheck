# Proposed student assessment API contracts (deferred)

> D-10 rebase: this is the proposed **personal assessment** contract for a
> later release. Source checking and publication use the separate policy in
> docs/PUBLICATION-POLICY.md. This draft does not block the S01 public MVP.

Status: **PROPOSED — not approved.** This review copy will be settled with
later student assessment work. Its routes and response shape are not part of
the autonomous publication decision contract.

Sources of truth (kept in step deliberately):

| Layer | File |
|---|---|
| Python request/response | `backend/app/models/assessment.py` |
| Python error envelope | `backend/app/api/errors.py` |
| TypeScript mirror | Deferred; create when personal assessment is implemented |

Wire format is camelCase (`alias_generator=to_camel`); Python attributes stay
snake_case. Enums are `lower_snake_case` strings on the wire and are never
translated by the client.

## Routes in this proposal

| Method | Path | Success | Notes |
|---|---|---|---|
| GET | `/api/health` | `200 HealthResponse` | Implemented (T01). |
| POST | `/api/v1/opportunities/{opportunity_id}/assessment` | `200 AssessmentResponse` | Not routed yet (T07). |

The opportunity read routes (`GET /api/v1/opportunities[/{id}]`) and the shape
of a listing are designed in T04/T05 against the seed format and will need their
own contract note; they are **not** part of this gate.

`HealthResponse` is `{"status": "ok", "service": "scholarcheck-api",
"environment": "<name>"}`.

## Assessment

### Request

```json
{
  "profile": {
    "nationality": "MW",
    "residenceCountry": "IN",
    "degreeType": "BCA",
    "degreeDurationYears": 3,
    "degreeStatus": "ongoing",
    "intendedLevel": "research_master",
    "grade": { "value": "8", "scale": "10-point CGPA" }
  },
  "roundId": "round-2027"
}
```

- `profile` is evaluated statelessly and never stored (D-04, invariant 8).
- `intendedLevel` is one of `bachelor`, `taught_master`, `research_master`,
  `doctoral` (CONTEXT D-08); `degreeStatus` is `ongoing` or `completed`.
- `roundId` is optional and omitted when the opportunity has a single round; a
  multi-round scheme requires it.
- `grade` is optional and is echoed, never converted: `value` is a string.
- `profile` is `extra="forbid"`: unknown keys are rejected, not ignored.

### Response `200`

```json
{
  "assessment": {
    "opportunityId": "opp-cambridge-gates",
    "roundId": "round-2027",
    "outcome": "potential_fit_confirmation_needed",
    "outcomeReason": "The published requirements do not say whether a three-year BCA is recognised.",
    "rules": [
      {
        "ruleId": "rule-degree-recognition",
        "result": "unresolved",
        "reason": "Degree recognition is not stated for this qualification.",
        "evidenceRefs": ["ev-req-page"]
      }
    ]
  }
}
```

- `outcome` is exactly one of `meets_checked_requirements`,
  `potential_fit_confirmation_needed`, `does_not_meet_stated_requirement`,
  `insufficient_information`; `result` is one of `met`, `not_met`, `unresolved`,
  `insufficient_information`. No score, percentage or probability appears in
  any response.
- `evidenceRefs` are ids the client resolves through the opportunity payload; a
  rule with no evidence is legal and renders as unverified (AC-11).
- `roundId` is `null` when the request omitted it and the opportunity has one
  round.

## Error envelope

Every non-2xx JSON response is `{"code": ..., "message": ..., "details": ...}`.
`message` is written for the applicant; stack traces are never returned.
`details` is `[{"field": "...", "message": "..."}]` and is `null` when there is
nothing field-specific to report (decision C below).

| `code` | Status | Raised when | Implemented |
|---|---|---|---|
| `validation_error` | 422 | Body fails schema validation (framework handler). | yes |
| `invalid_profile` | 422 | Profile parses but is not evaluable (e.g. unknown country code at evaluation time). | no (T07) |
| `opportunity_not_found` | 404 | Id or round does not exist in the loaded fixtures. | no (T05) |
| `not_found` | 404 | Unknown route (framework handler). | yes |
| `assessment_failed` | 502 | Evaluator raised; no partial outcome is returned. | no (T07) |
| `internal_error` | 500 | Unhandled failure. | yes |

Client-side only, never emitted by the server: `network_error` (request never
reached the API) and `invalid_response` (body was not the expected shape).

## Decisions needed before T07

**A. Wire casing.** camelCase JSON with snake_case Python — accepted as built.
Reject now if any consumer expects snake_case; changing later touches every
model and every test.

**B. Result nesting.** Return `{"assessment": {...}}` rather than the bare
result, so later phases (funding summary, availability) can be added without a
breaking change. The client already reads `payload.assessment`.

**C. `details` on empty.** Always present as `null` when empty (current
behaviour, simplest for the TS `ErrorBody` type) versus omitted. A tri-state
field is the alternative if TypeScript consumers prefer absence.

## When personal assessment work approves this contract

1. Copy the route row, request/response examples and error table into
   that feature's verification contract, with the date.
2. Replace the "PROPOSED" headers in `backend/app/models/assessment.py`
   and `backend/app/api/errors.py`, and create the TypeScript mirror then.
3. Keep `backend/tests/test_assessment_contract.py` as the executable form of
   the agreed shape.
