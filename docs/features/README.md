# Feature specs

One file per feature: `NNNN-<slug>.md`, created from `.agent/templates/feature-spec.md`.
Statuses: `draft` → `approved` → `in-progress` → `done` (or `rejected`). Code for a feature is not
written before its spec is `approved`. `feat` PRs must touch this directory or `docs/adr/` (CI enforces).

| # | Feature | Status |
|---|---|---|
| 0001 | [Project skeleton](0001-project-skeleton.md) | done |
| 0002 | [Booking Confirmation: air-freight support](0002-booking-confirmation-air-freight.md) | done |
| 0003 | [Invoice: multi-column prices, part numbers, shipment details](0003-invoice-price-components.md) | done |
