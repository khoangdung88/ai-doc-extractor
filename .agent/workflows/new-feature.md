# Workflow — New feature

Use for any user-visible capability or behavior change. For the specific cases below use the dedicated
workflow instead: new document type, new model provider, new input format, bug fix, refactor.

1. **Spec first.** Copy `templates/feature-spec.md` to `docs/features/NNNN-<slug>.md`
   (next free number). Fill: problem, scope / non-scope, user flow, data contract changes, acceptance
   criteria, test plan. Status `draft`.
2. **Decide if an ADR is needed** — yes if it adds a dependency, changes a stable contract (`Document`,
   `ExtractionResult`, any schema), or changes architecture. Create from `templates/adr.md`.
3. **Get approval.** Open a PR containing only the spec (+ADR). Human sets status `approved`. If running
   autonomously, stop and ask the human to approve before step 4.
4. **Plan the implementation** inside the spec ("Implementation plan" section): files to add/change, in
   dependency order. Each step should be a commit.
5. **Implement bottom-up** (core → domain/ingestion → extraction → api/cli), writing tests alongside each
   step. Keep `make check` green after every commit.
6. **Docs.** Update `docs/architecture.md` if structure changed, README if usage changed, `CHANGELOG.md`
   under *Unreleased*.
7. **PR.** Title `feat(<scope>): ...`, body from template, link the spec. Set spec status `done` when merged.

Stop conditions (ask the human): the spec cannot be made unambiguous; implementation needs > ~400 lines in
one PR; a rule in `.agent/rules` must be broken to complete the work.
