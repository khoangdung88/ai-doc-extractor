# Changelog

All notable changes are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
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
