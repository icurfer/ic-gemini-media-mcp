---
name: verify-app
description: Verify the local Gemini media MCP package without making paid API calls.
---

<!-- Adapted from ic-praxis 0.7.0; see ../../../THIRD_PARTY_NOTICES.md. -->
# Verify this MCP package

Run from the repository root:

```bash
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q src
bash scripts/check-conventions.sh --all
```

The tests use a fake video client. Never use a real `start_video` request as a
routine check because it incurs a charge. For a packaging change, also run
`uv build` and inspect the wheel contents. When a new MCP flow needs repeated
verification, add an offline test in `tests/` and document the flow under
`scenarios/`.
