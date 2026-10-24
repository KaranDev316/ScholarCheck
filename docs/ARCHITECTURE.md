# ScholarCheck architecture

Owner architecture direction, 24 October 2026. This expands the supplied
source → collector → AI → database → website diagram with the evidence and
publication boundary required by `PUBLICATION-POLICY.md`.

```mermaid
flowchart TD
    G[Government portals] --> C[Automated collector]
    U[University sites] --> C
    N[Approved scholarship NGOs] --> C
    C --> S[Retained official-source snapshots]
    S --> X[AI candidate extraction]
    S --> V[Separate AI evidence check]
    X --> V
    V --> P{Deterministic publication gates}
    S --> P
    P -->|Pass| D[(Published revisions in PostgreSQL)]
    P -->|Hold or reject| H[(Private candidates and decision reports)]
    D --> A[Published-only read API]
    A --> W[Public ScholarCheck website]
```

## Boundaries

1. **Official sources:** Only allowlisted government portals, universities
   and established scholarship NGOs enter the collector. Use an official API
   or RSS feed when available; otherwise monitor permitted public pages.
   Access rules and source identity are recorded before fetching.
2. **Collector and snapshots:** Store the exact fetched content, URL, time,
   hash, response status and parser version. An unavailable page does not
   erase prior evidence or close a scholarship. Stage 1 collects selected
   launch sources; Stage 2 schedules rechecks of one published record; Stage 3
   adds discovery of new opportunities.
3. **AI extraction and evidence check:** One pass proposes structured facts
   with snapshot spans. A separate pass checks whether the spans support those
   facts for the correct scholarship, applicant group, degree level, round and
   rate year. Both outputs are proposals, not publication authority.
4. **Publication gate:** Code checks source permission, exact excerpt
   presence, values and qualifiers, schema, conflicts, duplicates, dates,
   routes and funding classification. It publishes only when all material
   claims are supported. An unclear or contradictory claim produces a private
   hold with reasons.
5. **Storage and website:** PostgreSQL stores candidates, decisions and
   immutable published revisions; the snapshot store retains the underlying
   content. The public API reads only published revisions. The React website
   shows plain source evidence, actual check dates and official links, without
   exposing internal gate or model details.

The current repository has the PostgreSQL seed loader and a development-only
detail endpoint. The collector, snapshot store, AI passes, publication gate,
published-only catalogue API and public listing UI are planned, not built.
