# Feature specs

One file per feature: `NNNN-<slug>.md`, created from `.agent/templates/feature-spec.md`.
Statuses: `draft` → `approved` → `in-progress` → `done` (or `rejected`). Code for a feature is not
written before its spec is `approved`. `feat` PRs must touch this directory or `docs/adr/` (CI enforces).

| # | Feature | Status |
|---|---|---|
| 0001 | [Project skeleton](0001-project-skeleton.md) | done |
| 0002 | [Booking Confirmation: air-freight support](0002-booking-confirmation-air-freight.md) | done |
| 0003 | [Invoice: multi-column prices, part numbers, shipment details](0003-invoice-price-components.md) | done |
| 0004 | [Auto document-type detection for combined PDFs](0004-auto-document-type-detection.md) | in-progress |
| 0005 | [Web UI: model & API key picker, multi-file upload, results view](0005-web-ui.md) | in-progress |
| 0006 | [Web UI: review & edit extracted values](0006-review-and-edit-extraction.md) | in-progress |
