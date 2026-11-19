# ScholarCheck: context windows, token usage and evidence-preserving optimisation

Prepared 19 November 2026. Measurements are live extraction calls; implementation
references describe the code at commits `dd3a56d` and `fdd832a`.

## 1. Start with the context window

A token is a unit of model text encoding: it can represent a word fragment,
punctuation or part of structured data. Tokens are not characters, bytes or
necessarily whole words. JSON keys, quoted evidence, instructions and schema
representations all contribute to the material the model processes.

The context window is the bounded working context available to a model request.
Input and generated output must fit the model's applicable limits; output also
has its own cap. GPT-4.1 is documented with a 1,047,576-token context window and
32,768 maximum output tokens. Our adapter sets `max_output_tokens=24000`, which
is a ceiling, not a request to generate or a charge for 24,000 tokens. The actual
output counts in these experiments were much smaller. These model limits and
standard token rates were checked against the [GPT-4.1 model documentation](https://developers.openai.com/api/docs/models/gpt-4.1).

ScholarCheck was not running out of context. Its measured extraction inputs
were approximately 9,400–10,500 tokens, about 1% of that model's window. The
engineering problem was unnecessary repetition and unreliable evidence copying,
not insufficient context capacity. A larger window does not make duplicate
content free, establish factual correctness or remove the need for validation.

The application uses independent extraction and checking requests. Each request
supplies its own instructions and source context. The checker does not inherit
the extractor's working memory. `store=False` is set and no
`previous_response_id` is supplied. That preserves separation, but it means
source material sent to both calls is input to both calls. Reusing text across
calls does not automatically make it free. Provider caching can affect input
billing; all three measured calls reported **zero cached input tokens**.

## 2. Product context: why two model passes exist

ScholarCheck publishes scholarship facts grounded in retained official-source
pages. Material facts include award amounts, duration, programme requirements,
application routes, deadlines and eligibility restrictions. Unsupported values
must remain unknown or cause a hold; the application must not invent a currency,
university, date or funding coverage to fill a required field.

The processing path is:

```text
Retained official source
    → model extraction proposal
    → schema and exact-evidence validation
    → separate model evidence checking
    → deterministic publication gates
    → optional atomic publication
```

Extraction proposes facts. Checking independently judges whether source context
supports them. Python decides whether their evidence and contracts permit
publication. Neither a valid JSON object nor a model's support verdict grants
publication by itself.

These experiments used a retained CGRS D scholarship page, not a fresh fetch.
They demonstrate model execution on fixed evidence, not scholarship freshness.
No experiment published a record.

## 3. Before: the model acted as a quotation copier

Before the optimisation, extraction returned an opportunity, evidence passages
and fact readings containing copied source excerpts. A passage could reappear in
several readings. The checker design then supplied full snapshots together with
the candidate and asked the checker to repeat fact identifiers, snapshot IDs,
evidence IDs and excerpts in each adjudication.

This created two avoidable costs:

1. Repeated text enlarged request/response representations.
2. Reproducing exact quotations consumed model output and introduced transcription
   errors, although deterministic code could preserve those bytes directly.

The baseline extraction returned an excerpt joining different source passages
with `...`. The gate rejected it because it was not a contiguous retained span.
The shared evidence passage also stitched multiple portions of the page together.
The prompt already said not to do this: stronger wording alone was not a
sufficient engineering control.

The Indigenous supplement also had empty conditions despite source restrictions.
That is a semantic issue, distinct from quotation fidelity. Preserving exact
text does not by itself guarantee complete or correctly interpreted facts.

## 4. After: use models for decisions and code for exact copying

### 4.1 Extraction selects source-block IDs

`_quote_protocol` divides retained source bodies into non-empty blocks at newline
boundaries, including literal escaped newline separators used by the retained
text. Each block is assigned an ID within that request. The model receives the
blocks with their text; it selects IDs for `passage` and `excerpt` fields. The
wire schema restricts those fields to available IDs.

After the response, `_resolve_quotes` replaces selected IDs with the exact
stored blocks. The ordinary proposal and evidence validators still run.

Conceptual example:

```json
{
  "source_blocks": [
    {"quote_id": "17", "text": "An exact continuous passage from the retained page."}
  ]
}
```

The model's quotation field becomes `"excerpt": "17"`. Python expands it back
to the retained passage. The model can choose an unsuitable passage, but it no
longer needs to reproduce its text. Selection correctness remains a checking
and publication-gate responsibility.

Source-block IDs are request-local references, not permanent evidence identities.
Durable audit outputs still contain restored quotations and snapshot bindings.
The optimisation changes the model exchange, not the published data contract.

### 4.2 The checker uses reading IDs

`_checker_protocol` assigns IDs to stated readings. Repeated excerpts are stored
once in an excerpt table; candidate readings refer to them. Duplicated passages
are removed from candidate evidence entries. Full retained snapshots remain in
the checker input so that applicability and contradictory context can be assessed.

The checker returns a reading ID, its verdict, a reason and applicability data.
Python restores the original fact/snapshot/evidence/excerpt bindings. Unknown,
duplicate or missing reading IDs are rejected. Restoring identity does not
manufacture a support verdict or overwrite the checker's applicability decision.

This should reduce repeated input quotations and output identity/quotation text.
**Checker savings have not yet been measured live.** The first two experiments
stopped before checking; the final experiment deliberately tested extraction only.

### 4.3 Remove duplicated request scaffolding

The adapter now excludes `schema` and `instructions` from the JSON task payload
because they are already supplied through the structured-output format and
request instructions. JSON payload serialisation uses compact separators.

These changes remove unnecessary representation overhead. They do not remove
schemas from model processing, eliminate the need for full sources or establish
an exact token saving for each individual edit. Source blocks and ID enums also
add some overhead of their own.

### 4.4 Correct the domain contract rather than invent a university

After quotation copying was fixed, the next live extraction returned an empty
programme institution. The old model required a non-empty institution name,
although the scholarship may be tenable at multiple eligible institutions.

`Programme.institution` now accepts `null`; named strings must still be non-empty.
Extractor guidance explicitly distinguishes the programme institution from the
award provider and institution eligibility rules. Existing JSONB storage needs
no SQL column migration. Other evidence requirements remain intact.

This was a correctness fix, not an attempt to make every output smaller. The
successful result is more valuable than a shorter proposal that cannot validate.

## 5. Experiment design and evidence

All three calls ran on 19 November 2026 with model
`gpt-4.1-2025-04-14` and the same source body. Their independently recomputed
SHA-256 values match:

```text
dcfbf661b0e980cc7a7425bfe9d5177e385f9b4073c90f1ed3fc4c533e26e90b
```

Counts come from provider-returned `usage` in `extraction-call.json`, not from
character counts or a local tokenizer estimate. All calls reported completed
API responses, zero cached input tokens and zero reasoning tokens. A completed
API response can still fail application validation.

| Run | Configuration | Input | Output | Total | Local result |
|---|---|---:|---:|---:|---|
| A | Copied quotations; required institution | 10,527 | 5,852 | 16,379 | Exact quotation rejected |
| B | Source-block IDs; required institution | 9,404 | 3,475 | 12,879 | Empty institution rejected |
| C | Source-block IDs; nullable institution | 9,486 | 4,004 | 13,490 | Schema and candidate evidence validation passed |

The output content was not identical:

| Run | Proposed facts | Fact readings | Evidence entries |
|---|---:|---:|---:|
| A | 30 | 22 | 1 |
| B | 19 | 15 | 6 |
| C | 25 | 16 | 8 |

In B, all 15 reading excerpts and all six evidence passages matched the source.
In C, the restored proposal passed candidate evidence validation with an unnamed
institution represented as `null`. Passing this stage is not proof of semantic
completeness, independent checking or publication readiness.

## 6. Before/after calculations

For each metric:

```text
Reduction (%) = (baseline tokens − new tokens) / baseline tokens × 100
```

| Comparison | Input reduction | Output reduction | Total reduction |
|---|---:|---:|---:|
| A → B | 10.67% | 40.62% | 21.37% |
| A → C | 9.89% | 31.58% | 17.64% |

The strongest supported headline is:

> On the same retained scholarship source and GPT-4.1 snapshot, the first locally
> valid extraction used 13,490 tokens versus 16,379 in the original failed run:
> an observed 17.64% reduction, while eliminating model-generated quotation copying.

Do not present 21.37% as the successful extraction result: that was the
intermediate run that still failed the institution constraint.

### Why output savings were larger than input savings

The full official source still has to be read. That large input component remains.
By contrast, output no longer needs long repeated quotations: short IDs replace
them. Duplicate schema/instruction removal also reduces input, partly offset by
block wrappers and ID enumeration. These mechanisms explain the expected
direction; no ablation experiment measured each contribution independently.

### Why C used more tokens than B

C used 82 additional input tokens and 529 additional output tokens, a total
increase of 611 tokens or 4.74%. Its domain schema and instructions changed, and
it produced 25 facts rather than 19, plus eight evidence entries rather than six.
It is therefore plausible that the larger content explains much of the output
increase. We cannot assign exact shares to stochastic variation, schema changes
or more extensive extraction from one sample per configuration.

The nullable-field change improved representational correctness. A lower token
count was not its acceptance criterion.

## 7. Cost interpretation

Using documented GPT-4.1 standard rates of $2 per million uncached input tokens
and $8 per million output tokens, the illustrative calculation is:

```text
Estimated USD = input_tokens × 2 / 1,000,000
              + output_tokens × 8 / 1,000,000
```

| Run | Input estimate | Output estimate | Total estimate |
|---|---:|---:|---:|
| A | $0.021054 | $0.046816 | $0.067870 |
| B | $0.018808 | $0.027800 | $0.046608 |
| C | $0.018972 | $0.032032 | $0.051004 |

A → C saves approximately **$0.016866 per extraction, or 24.85%** under these
rates. The cost reduction exceeds the 17.64% token reduction because output is
more expensive and output tokens fell more sharply. These are calculated
estimates, not verified invoices; account-specific pricing, credits, service
settings and future rate changes may differ. Rates come from the
[official GPT-4.1 model page](https://developers.openai.com/api/docs/models/gpt-4.1).

If 1,000 calls repeated exactly these counts, extraction would cost roughly
$67.87 versus $51.00. This is an illustration, not a forecast. It excludes
checking, retries, collection, storage and hosting. Failed outputs still consume
billable model work; optimising cost per accepted record requires measuring
failure and retry rates, not just cost per call.

## 8. Usage accounting and observability

`ModelPass.last_metadata` retains response ID, model, response status and usage.
The pipeline saves per-pass call metadata and a `usage.json` summary in a
`finally` block, including when a completed model response fails local validation.
Usage contains input/output/total tokens and provider detail such as cached input.
Missing usage is unknown, not evidence of a free call. Summary totals sum reported
values; an absent pass is not a completed zero-token pass.

The standalone extraction-only C runner also wrote usage, but used a smaller
`usage.json` structure containing the extraction pass. Consumers should use the
per-call files as the common evidence format rather than assume all historical
summary files have identical structure.

Known gaps: network failures may leave no provider usage, raw wire responses are
not separately persisted by the adapter, elapsed time is not a benchmark metric
in these artifacts, and no application-wide monetary budget cap is implemented.
The restored extraction output can be larger on disk than the model's output:
Python has expanded IDs locally. Disk JSON size is not the billed output count.

## 9. What the results prove—and what they do not

Proven in these runs:

- Fixed-source, fixed-model extraction usage was recorded by the provider.
- A reference-based quotation protocol removed the observed quote-copying failure.
- The final run passed schema and candidate evidence validation at lower total
  token usage than the original failed run.
- No publication happened; the checker was not reached or requested.

Not yet proven:

- Generalised savings across scholarships, languages and page layouts.
- Independent checker savings or a passing end-to-end publication decision.
- Equal semantic coverage across A/B/C: their fact counts differ.
- A higher overall accuracy rate, shorter latency or a particular production cost.
- Causal savings attributable separately to block IDs, compact JSON or scaffolding removal.

The three calls are an engineering case study, not a controlled statistical
benchmark. The honest interview claim is the observed result and the mechanism,
with these limitations stated explicitly.

## 10. Next benchmark

Freeze a representative source set, model snapshot, prompt/protocol version and
expected material-fact rubric. Run repeated trials under both protocols and
retain every failure as well as every success. Measure input, cached input,
output, estimated cost, latency, exact-quotation success, required-fact coverage,
unsupported claims and accepted candidates. Compare cost per valid candidate and
per fully checked record. Do not trade missing eligibility restrictions for a
smaller output.

Measure the checker independently on the same validated candidates, using both
full-quotation and reading-ID exchanges. Keep full-source context constant.
This will separate representation savings from changes in extracted content.
A later experiment can examine source-block granularity, schema overhead and
prompt caching. No such further paid experiments were performed for this report.

## 11. Interview explanation

A concise answer:

> I built an evidence-backed scholarship extraction pipeline. Initially the LLM
> copied quotations into multiple fields, which cost output tokens and produced
> stitched excerpts that our exact-match gate rejected. I changed the exchange:
> the extractor selects source-block IDs and Python restores exact text. The
> checker similarly uses reading IDs while keeping full source context. On the
> same GPT-4.1 snapshot and retained page, the first locally valid extraction
> dropped from 16,379 to 13,490 tokens—17.64% less. I also fixed an incorrect
> required-institution assumption rather than forcing the model to invent a
> university. These are single-run observations; checker savings and semantic
> coverage still need controlled evaluation.

Useful follow-up answers:

| Interview question | Defensible answer |
|---|---|
| Why not just shorten the prompt? | The main correctness issue was exact copying. References remove that task from the model while keeping source context. |
| Why not trust structured JSON? | Schema correctness does not prove factual support; source and applicability gates remain necessary. |
| Why not send only snippets to the checker? | Surrounding context can contain applicant restrictions, exceptions or contradictory claims. |
| Did caching cause the reduction? | No measured call had cached input tokens. |
| Did you save 21%? | The intermediate failed run used 21.37% fewer tokens. The successful extraction's measured reduction was 17.64%. |
| Is this full pipeline accuracy? | No. C passed extraction validation only; independent checking and publication are separate gates. |
| Why does the latest version use more than the intermediate version? | It extracted more facts and used a changed schema; correctness matters more than minimising raw output. |
| Can a wrong quote ID still pass? | Exact text is guaranteed by lookup, not semantic support. A wrong selection still needs rejection by evidence checking and code gates. |

## 12. Local evidence and implementation references

Local audit directories are private, ignored runtime artifacts; do not publish
raw source snapshots or credentials as part of an interview portfolio. They may
not exist in a fresh clone. This report preserves the measured aggregates.

| Run | Audit directory under `backend/var/audits/` |
|---|---|
| A | `live-gpt41-20261119T130702434279Z` |
| B | `live-quote-ids-20261119T131621932712Z` |
| C | `live-nullable-institution-20261119T133301723439Z` |

Relevant files: `extraction-call.json` (provider counts/model),
`extraction-output.json` (restored proposal), `snapshots.json` (fixed source),
`failure.txt` where applicable, and `candidate.json` for C.

Implementation: [model adapter](../backend/app/publication/model_pass.py),
[pipeline and usage accounting](../backend/app/publication/pipeline.py),
[programme model](../backend/app/domain/models.py),
[adapter regression tests](../backend/tests/test_model_pass.py), and
[domain regression tests](../backend/tests/test_domain_models.py).
