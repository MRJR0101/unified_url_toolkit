# Definition Of Done Checklist

Release-readiness checklist aligned with [docs/VISION_AND_PLAN.md](docs/VISION_AND_PLAN.md).

## 1) Foundation And Packaging
- [ ] package and import namespace behavior is documented and stable
- [ ] install workflow works in a clean clone (`uv sync --all-groups`)
- [ ] CLI entry points start correctly in a clean environment

## 2) Interface Hardening
- [ ] API contracts for core behavior are documented and tested
- [ ] CLI output and exit-code contracts are documented and tested
- [ ] default retry/timeout/concurrency behavior is documented

## 3) Verification Gates
- [ ] `pytest` passes
- [ ] `ruff check` passes
- [ ] `ruff format --check` passes
- [ ] `mypy --explicit-package-bases core io processing analysis config utils` passes
- [ ] verification procedure in [VERIFY.md](VERIFY.md) matches actual workflow

## 4) Documentation Completeness
- [ ] root docs point to `docs/VISION_AND_PLAN.md` as canonical strategy
- [ ] architecture and usage docs match implemented behavior
- [ ] module READMEs use package-namespace import examples
- [ ] migration and changelog docs reflect user-visible changes

## 5) Reliability
- [ ] failure paths are explicit and covered with tests
- [ ] no known contract regressions in release candidate branch
- [ ] output contracts remain stable for downstream consumers

## 6) Final Gate
- [ ] a new contributor can set up, run checks, and execute CLI workflows using docs only
