# Changelog

All notable changes are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed
- Reconciliation guards: invoice lines are only repaired when a price column matches the line or
  invoice total (no last-column guess); sea booking numbers are never reinterpreted as MAWBs; a
  booking number that duplicates the MAWB falls back to the HAWB.
- Deterministic repairs in domain models (ADR 0007): `Invoice` takes `unit_price`/`amount` from the
  consistent `price_components` column when the model pasted a column total into `unit_price`;
  `LineItem.hs_code` keeps digits only and drops implausible values; `BookingConfirmation` moves a
  `NNN-NNNNNNNN` value from `hawb_number`/`booking_number` to `mawb_number` and falls back to the
  HAWB as `booking_number`.
- `ollama` provider: dedicated `DOCEXT_OLLAMA_TIMEOUT_S` (default 300 s) so cold model loads no
  longer hit the shared 60 s timeout; `options.num_ctx` is now sized from the prompt (override with
  `DOCEXT_OLLAMA_NUM_CTX`, cap with `DOCEXT_OLLAMA_MAX_NUM_CTX`) instead of Ollama's silent 4096 default;
  prompts that cannot fit the cap fail with `input_too_large` instead of being truncated.

### Added
- `invoice` prompt v3: column selection when freight/insurance are printed separately from goods
  totals. ADR 0007 (schema versioning + deterministic post-processing). Fixture README rows for the
  processing-invoice and air-booking samples.
- `invoice` schema v2 / prompt v2: `LineItem.part_number` and `LineItem.price_components` for
  multi-column (processing-trade) prices, `contract_number`, `shipped_per`, `shipment_date`,
  `amount_components`, `total_packages`, `net_weight`, `gross_weight`; warning when
  `quantity x unit_price` differs from `amount`; prompt forbids invented zero charges; synthetic
  processing-invoice fixture and golden file (spec 0003).
- `booking_confirmation` schema v2 / prompt v2 with air-freight support: `transport_mode`,
  `booking_reference`, `mawb_number`, `hawb_number`, `flight_number`, `cargo_cutoff`, `terminal`,
  `pieces`, `chargeable_weight`, `ex_factory_date`; mode-consistency warnings; synthetic air fixture
  and golden files (spec 0002).
- Project skeleton: core config/logging, domain schemas (invoice, packing list, booking confirmation),
  PDF ingestion, extraction pipeline with `ModelProvider` plugin interface and `mock` provider,
  FastAPI `/v1/extract` endpoint, Typer CLI, CI, agent rules (`AGENTS.md`, `.agent/`).
