# Vision And Plan

## Purpose
Define the long-term direction for Unified URL Toolkit and the execution plan that keeps the original consolidation intent intact.

## Vision
Unified URL Toolkit is the single, reliable URL and domain intelligence toolkit for:
- automation pipelines
- security triage workflows
- SEO/content operations
- data engineering tasks

The project must keep:
- one shared source of URL/domain logic
- low duplication across modules
- clear module boundaries
- stable APIs and CLI contracts

## Strategic Objectives
1. Reliability: deterministic outputs and explicit failure semantics.
2. Usability: one clear install/run path for local and CI use.
3. Maintainability: package-first imports and strict module ownership.
4. Verification: repeatable gates for tests, linting, formatting, and typing.
5. Adoption: predictable behavior for library embedding and CLI usage.

## Roadmap

### Phase 1: Foundation Stabilization
Goal: make the project consistently installable and runnable.

Deliverables:
- package metadata and installable entry points
- namespace-safe imports through `unified_url_toolkit.*`
- one dependency workflow for contributors and CI

Definition of done:
- `uv sync --all-groups` succeeds in a clean clone
- CLI entry points run (`uut-clean-domains`, `uut-extract-urls`, `uut-check-links`)
- editable install works

### Phase 2: Interface Hardening
Goal: lock public behavior.

Deliverables:
- documented output contracts for text/CSV/JSON
- stable defaults and exit-code semantics
- contract tests for public CLI behavior

Definition of done:
- user-visible behavior changes are tracked in `CHANGELOG.md`
- migration notes are updated for contract changes

### Phase 3: Quality And Verification
Goal: prevent regressions.

Deliverables:
- expanded unit/integration coverage
- enforced lint/format/type gates
- stronger failure-path testing

Definition of done:
- release branch is green on defined quality gates
- critical regressions are blocked before release

### Phase 4: Advanced Capability Expansion
Goal: grow specialized modules without destabilizing core behavior.

Deliverables:
- consistent data models across specialized analyzers
- advanced usage patterns documented with realistic examples
- optional extension points for organization-specific policies

### Phase 5: Release Discipline And Adoption
Goal: run as a dependable toolkit in repeated operations.

Deliverables:
- semantic versioning and release checklist
- upgrade/migration guidance per release
- compatibility/support policy

## Current Delivery State (2026-03-04)

### Completed
- `pyproject.toml` + `uv.lock` workflow established
- package scripts added (`uut-clean-domains`, `uut-extract-urls`, `uut-check-links`)
- CLI startup/import regression tests added (`tests/test_cli_smoke.py`)
- CLI contract tests added (`tests/test_cli_contracts.py`)
- documentation structure aligned around this roadmap file

### In Progress
- restoring full lint/format/type green state on current working branch
- tightening package-root consistency across docs/examples/modules

### Next
1. finalize interface contracts and error taxonomy documentation
2. close remaining quality-gate failures
3. expand targeted test coverage for core and specialized modules

## Governance Rules
- No new module may duplicate existing responsibilities.
- Public behavior changes require tests and docs updates in the same PR.
- Dependency additions must include maintenance rationale.
- `docs/VISION_AND_PLAN.md` remains the canonical strategy reference.

## Success Metrics
- verification pass rate (`pytest`, `ruff`, `mypy`)
- CLI startup and contract stability
- regression escape rate per release
- documentation freshness relative to implemented behavior

## Related Docs
- [Architecture](ARCHITECTURE.md)
- [Usage Guide](USAGE.md)
- [Project VERIFY](../VERIFY.md)
