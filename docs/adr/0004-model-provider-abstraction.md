# ADR-0004: Model providers via REST (httpx), addressed as `provider:model`
- **Status:** accepted  **Date:** 2026-10-28  **Deciders:** @khoangdung88
## Context
Many vendors, fast-changing SDKs, and we need the core to install light and test offline.
## Decision
`ModelProvider` returns raw JSON text + usage + latency; schema validation is centralised in the pipeline.
Initial providers call vendor REST APIs with `httpx` (no SDK dependency). Models are addressed as
`"<provider>:<model>"` and parsed in one place. Prompts are versioned files, temperature 0 by default.
A `mock` provider enables offline unit tests.
## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| LangChain/LiteLLM | many providers out of the box | heavy, opaque, abstraction churn |
| Vendor SDKs | typed, maintained | each adds deps; typing friction under mypy strict |
## Consequences
Each provider is ~100 lines we own; SDK-based providers remain possible behind optional extras.
