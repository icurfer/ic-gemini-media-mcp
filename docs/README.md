<!-- Adapted from ic-praxis 0.7.0; see ../THIRD_PARTY_NOTICES.md. -->
# Project change record

Use the four-stage flow for a new MCP tool or argument, a new source file,
a dependency or infrastructure change, a rule change, or at least 100 changed
code lines. Smaller fixes need a CHANGELOG line and a backlog update when a
matching request exists.

| Location | Purpose |
|---|---|
| `requirements/backlog.md` | Requests and their completion state |
| `spec/` | Dated plan, including code placement and credential handling |
| `scope/` | Files and functions included in the change |
| `deferred/` | Work explicitly left for later |
| `done/` | Verification and completed result |
| `CHANGELOG.md` | Brief record of completed changes |

The project is a local Python MCP package. It has no deployment pipeline or
deploy-trigger file. Change the package version in `pyproject.toml` when
preparing a release. If a deployment pipeline is added, configure the real
trigger in `scripts/check-conventions.sh` and document it here.

Turn recurring, mechanically checkable mistakes into checks in
`scripts/check-conventions.sh`.
