# Retained source snapshots

One JSON file per fetched page, named after the snapshot id
(`<host and path slug>-<first 8 hex of the text hash>`). Each file holds the
snapshot the publication gate checks against and the provenance that explains
how it was obtained:

| Field | Meaning |
|---|---|
| `snapshot.body` | The readable page text a passage must occur in. |
| `snapshot.content_hash` | SHA-256 of `body`, computed by the model; the id ends with its first 8 characters. |
| `snapshot.responseStatus` | The HTTP status the page answered. |
| `snapshot.retrievedAt` | When the fetch happened; fixtures must record the same time. |
| `snapshot.parserVersion` | Which extractor produced `body` (`html-text/1`). |
| `provenance.rawSha256`, `rawBytes` | Hash and length of the received response; the raw bytes are not retained. |
| `provenance.requestUrl`, `finalUrl` | The address asked for and the address that answered. Followed redirects are recorded. |
| `provenance.robotsAllowed`, `robotsUrl` | The access-rule decision taken before the fetch. |
| `provenance.userAgent` | The identifying user agent used for the fetch. |

Collect or re-collect a page:

```bash
cd backend && PYTHONPATH=. .venv/bin/python -m app.collect.snapshot \
  --out ../content/snapshots 'https://www.sydney.edu.au/…/rtp-international.html'
```

The collector reads `robots.txt` first and refuses a page it may not fetch. It
fetches once, keeps the readable text (scripts, styles and page chrome removed),
and refuses a non-HTML response or a page with too little text to support a
claim.

## What a snapshot is not

- It is not a claim that the page is correct or current, only that this text was
  served at that time.
- It is not permission to publish anything: only the gate can do that, and only
  with a validation report checked against these snapshots.
- It is not the whole of a page. Text‑only extraction loses anything rendered by
  JavaScript: RMIT's round calendar is exactly such a table, which is why the
  RMIT record is held (see `content/publication/first-pass-review.json`).

Re-collecting a page whose text changed produces a new id and a new file; the
old snapshot stays, because a report may still refer to it. Do not edit a
retained body by hand: a changed body is a new snapshot, and hand edits would
break the promise that the text is what the page said.
