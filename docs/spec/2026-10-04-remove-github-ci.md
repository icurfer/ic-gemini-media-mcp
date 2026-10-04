# Remove GitHub CI — 2026-10-04

- Request: this project does not need GitHub CI; remove it and push the change.
- Placement: delete the only workflow, `.github/workflows/praxis-gate.yml`.
- Pattern: keep the existing local pre-commit convention gate and its `--all` mode.
- Credentials: no credentials or secrets are added, read, or stored.
- Verification: confirm no workflows remain, shared rules match, and the staged convention gate passes. No paid API calls.
