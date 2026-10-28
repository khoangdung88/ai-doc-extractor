# ADR-0007: Document schema versioning and deterministic post-processing

- **Status:** accepted
- **Date:** 2026-10-28
- **Deciders:** @khoangdung88, Devin

## Context
Document schemas (`Invoice`, `PackingList`, `BookingConfirmation`) are the data contract that API/CLI
consumers depend on, yet they must evolve as real documents expose gaps (air-freight bookings,
processing-trade invoices with several price columns — specs 0002 and 0003). At the same time, the
models we run — especially local 30B-class models — ignore subtle prompt rules: they paste a column
total into `unit_price`, put a MAWB into `hawb_number`, or copy a quantity into `hs_code`. Prompt
wording alone did not fix these; each extra rule costs tokens and is applied inconsistently.

## Decision
1. **Schema versioning.** Every document schema carries `schema_version`. Adding optional fields bumps
   the version (v1 outputs still validate); removing/renaming fields or changing semantics is a breaking
   change that additionally needs a new ADR and a migration note in the CHANGELOG. Prompts are
   versioned files (`prompts/<type>/vN.md`); a merged prompt version is never edited in place — new
   rules go in `vN+1.md` and `DocumentType.prompt_version` is bumped.
2. **Deterministic post-processing lives in the domain models.** Mistakes that are detectable from the
   extracted data itself are repaired by Pydantic validators (`field_validator`, `model_validator`
   `mode="after"`) on the schema, not by more prompt text and not by provider-specific code. Repairs
   must be (a) derivable from printed values only, never invented; (b) covered by a unit test built
   from the real-world mistake (anonymised numbers); (c) documented in the field description or a
   docstring. Anything that cannot be repaired deterministically is surfaced via `warnings()`.

## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| Prompt rules only | No code | Model-dependent, unreliable on small/local models, token cost |
| Separate "post-processor" layer in `extraction/` | Keeps schemas pure | Splits one document's rules across two places; pipeline needs per-type hooks |
| Fix in each provider | Can use provider quirks | Duplicated per provider; violates provider abstraction |
| Validators on the schema (chosen) | One place per document type, runs on every path (API, CLI, golden tests), model-agnostic | Schemas gain logic; must keep repairs small and well-tested |

## Consequences
- Positive: outputs are correct regardless of model quality where the data allows; golden tests
  exercise the repairs; consumers can rely on `schema_version` to detect contract changes.
- Negative / risks: a wrong repair silently alters output — mitigated by requiring tests from real
  cases and by keeping repairs conservative (only when the current value is provably inconsistent).
- Follow-ups: eval set over anonymised real documents (docs/evals) to measure repair impact per model.
