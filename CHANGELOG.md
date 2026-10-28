# Changelog

All notable changes are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Project skeleton: core config/logging, domain schemas (invoice, packing list, booking confirmation),
  PDF ingestion, extraction pipeline with `ModelProvider` plugin interface and `mock` provider,
  FastAPI `/v1/extract` endpoint, Typer CLI, CI, agent rules (`AGENTS.md`, `.agent/`).
