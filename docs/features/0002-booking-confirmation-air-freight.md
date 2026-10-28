# 0002 — Booking Confirmation: air-freight support (schema v2)

- **Status:** done
- **Owner:** @khoangdung88   **Agent:** Devin
- **Created:** 2026-10-28   **Related ADRs:** 0003, 0004   **Issue/PR:** —

## Problem
The v1 `booking_confirmation` schema and prompt assume sea freight (vessel/voyage, containers, SI/VGM/CY
cut-offs). Real-world air-export confirmations issued by forwarders carry MAWB/HAWB numbers, a flight
line (`VN611  Oct 03,2026  HAN-BKK  08:50 - 20:00`), a single cargo cut-off, a handling terminal and a
pieces/weight/volume line. With v1 the model puts the shipper's invoice reference into `booking_number`,
copies the forwarder into `carrier`, duplicates the one cut-off into `si_cutoff` and `cy_cutoff`, and
drops the flight and terminal entirely.

## Goal / Non-goals
- Goal: one `booking_confirmation` type that covers sea **and** air bookings with explicit fields, plus
  prompt rules that resolve the ambiguities above. Business-rule warnings for mode/field mismatches.
- Non-goals: separate `air_booking` document type; road/rail specifics beyond the `transport_mode`
  enum value; parsing of airline from the flight prefix (not printed → not extracted).

## User flow
Unchanged: `POST /v1/extract type=booking_confirmation` / `docext extract --type booking_confirmation`.
Response `data` now includes e.g.
```json
{"transport_mode": "air", "booking_number": "987654321012", "booking_reference": "INV-2026-0001",
 "mawb_number": "123-45678901", "hawb_number": "987654321012", "flight_number": "XY123",
 "port_of_loading": "SGN", "port_of_discharge": "BKK", "etd": "2026-03-05",
 "cargo_cutoff": "2026-03-04T22:00:00", "pieces": 4, "gross_weight": {"value": "25.5", "unit": "KG"}}
```

## Design
- Modules touched: `domain/booking_confirmation.py` (schema v2), `extraction/prompts/booking_confirmation/v2.md`
  (v1 kept for reproducibility), fixtures/golden, glossary.
- Data contract changes: `BookingConfirmation` gains `transport_mode` (`sea|air|road|rail`),
  `booking_reference`, `mawb_number`, `hawb_number`, `flight_number`, `ex_factory_date`,
  `cargo_cutoff`, `terminal`, `pieces`, `chargeable_weight`; `schema_version` → `"2"`. All new fields are
  optional, so v1 outputs still validate. `port_of_loading/port_of_discharge` double as airports.
- Warnings: `booking_number missing` only when no booking/HAWB/MAWB identifier exists; MAWB format
  `NNN-NNNNNNNN`; containers on an air booking; AWB/flight on a sea booking.
- New dependencies: none. Config / env vars: none.
- Failure modes: unchanged (validation errors → `ExtractionValidationError`).

## Acceptance criteria
- [x] Synthetic air booking fixture extracts via `mock:fixture` with zero warnings (golden test).
- [x] Existing sea fixture still passes with a golden file of its own.
- [x] Prompt v2 states the booking-number vs reference, carrier vs forwarder and cut-off rules.
- [x] `make check` green.

## Test plan
Unit: `tests/unit/domain/test_booking_confirmation.py` (mode warnings, MAWB format, identifier
fallback). Golden: `tests/fixtures/golden/booking_confirmation/*.json`. Fixtures: synthetic PDFs from
`scripts/make_sample_pdfs.py` — no real company data.

## Implementation plan
1. Schema v2 + warnings + unit tests.
2. Prompt v2, registry bump to `prompt_version="v2"`.
3. Synthetic air fixture + golden files; glossary; CHANGELOG.

## Open questions
- Should `carrier` be inferred from the flight prefix via an airline-code table? Deferred; would be a
  post-processing step, not a prompt rule.
