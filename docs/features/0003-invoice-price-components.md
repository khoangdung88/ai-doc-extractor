# 0003 — Invoice: multi-column prices, part numbers, shipment details (schema v2)

- **Status:** done
- **Owner:** @khoangdung88   **Agent:** Devin
- **Created:** 2026-10-28   **Related ADRs:** 0003   **Issue/PR:** —

## Problem
Processing-trade (gia công) invoices print **two or more price columns per line** — e.g. "Unit price
(processing fee) / Amount (payment)" and "Unit price (material) / Total (payment & no payment)" — plus a
part number and shipment details ("Shipped per: AIR FREIGHT", "Ship on board", cartons, weights).
With the v1 schema (one `unit_price`, one `amount`) the model mixed the columns: on a real sample it
returned `unit_price = 1478.016` (a column total) and invented `freight = 0`. Nothing flagged it.

## Goal / Non-goals
- Goal: represent every printed price column without losing the simple `unit_price`/`amount` view;
  capture part number, contract number, shipped-per, shipment date, packages and weights; detect
  `quantity x unit_price != amount`; forbid invented zero charges in the prompt.
- Non-goals: tax/VAT breakdowns, multi-currency lines, proforma-specific fields, OCR.

## User flow
Unchanged endpoint / CLI. `data.line_items[*]` now also carries
```json
{"part_number": "8X-000A001",
 "unit_price": {"amount": "5.5000", "currency": "USD"}, "amount": {"amount": "5280.00", "currency": "USD"},
 "price_components": [
   {"label": "Unit price (processing fee)", "unit_price": {"amount": "1.5000", "currency": "USD"}, "amount": {"amount": "1440.00", "currency": "USD"}},
   {"label": "Unit price (material)", "unit_price": {"amount": "5.5000", "currency": "USD"}, "amount": {"amount": "5280.00", "currency": "USD"}}]}
```
and a wrong unit price yields `warnings: ["line 1: quantity x unit_price = ... differs from amount ..."]`.

## Design
- Modules touched: `domain/common.py` (`PriceComponent`, `LineItem.part_number`,
  `LineItem.price_components`), `domain/invoice.py` (v2 fields + warning), prompt
  `extraction/prompts/invoice/v2.md` (v1 kept), fixtures/golden, glossary.
- Data contract changes: `Invoice.schema_version` → `"2"`; new optional fields `contract_number`,
  `shipped_per`, `shipment_date`, `amount_components`, `total_packages`, `net_weight`,
  `gross_weight`. `LineItem` is shared with `PackingList` — new fields are optional and default-empty,
  so packing-list output is unaffected.
- Warning tolerance: `max(0.01, 0.5 %)` of the expected amount, to absorb printed rounding.
- New dependencies: none. Config / env vars: none.
- Failure modes: unchanged.

## Acceptance criteria
- [x] Synthetic processing invoice extracts via `mock:fixture` with zero warnings (golden test).
- [x] The real-world mistake (`unit_price` = line total) produces a warning (unit test).
- [x] Prompt v2 forbids `0` for unprinted charges and defines the column mapping.
- [x] `make check` green.

## Test plan
Unit: `tests/unit/domain/test_invoice.py`. Golden: `tests/fixtures/golden/invoice/*.json`.
Fixtures: synthetic PDFs from `scripts/make_sample_pdfs.py` — no real company data.

## Implementation plan
1. `PriceComponent` + `LineItem` fields; `Invoice` v2 + warning; tests.
2. Prompt v2, registry bump.
3. Synthetic processing-invoice fixture + golden; glossary; CHANGELOG.

## Open questions
- Should `amount_components` be promoted to a typed "amount payable" field once more samples confirm
  the pattern? Revisit after the eval set exists.
