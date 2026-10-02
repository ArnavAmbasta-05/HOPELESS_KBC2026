## Summary

<!-- Describe the change in 1-3 sentences. -->

## Requirement IDs

<!-- List BRD/SRS requirement IDs this PR addresses (e.g., FR-EVT-001, NFR-SEC-002). -->

- 

## Checklist

- [ ] Tests pass (`pytest tests/ -x --tb=short`)
- [ ] Lint clean (`ruff check .` and `ruff format --check .`)
- [ ] Type check passes (`mypy services/ packages/`)
- [ ] No secrets in source (`.env.example` has keys only, no values)
- [ ] Contracts updated if a seam changed (`packages/contracts/`)
- [ ] Requirement IDs traced in RTM
- [ ] CI pipeline green (lint, typecheck, test, security scan, build)
- [ ] VULNERABILITY CHECK evidence provided (if security-relevant)
- [ ] WORKFLOW CHECK evidence provided (if workflow-relevant)

## Test plan

<!-- Describe how this was tested. -->

## Screenshots / logs

<!-- If applicable, attach screenshots or relevant log output. -->
