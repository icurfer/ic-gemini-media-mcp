<!--
  Adapted from ic-praxis 0.7.0; see THIRD_PARTY_NOTICES.md.
  AGENTS.md — the same praxis constitution, for agents that read AGENTS.md
  (Codex, etc.). The block between the praxis:shared markers is a VERBATIM
  mirror of the one in CLAUDE.md — the pre-commit gate (Gate E) blocks the
  commit if the two drift. Edit the shared rules in either file, then copy the
  block into the other and stage both.
-->

<!-- praxis:shared:begin -->
# ic-gemini-media-mcp

## System map
| Component | Port | Role |
|---|---|---|
| `src/gemini_media_mcp/server.py` | stdio | MCP tools for starting, checking, and downloading Gemini Veo jobs |
| `tests/test_server.py` | none | Offline tests using a fake video client |
| `pyproject.toml` | none | Python package metadata and CLI entry point |

## Change size and work order
A new source file, a new MCP tool or argument, a dependency or infrastructure change, a rule change, or at least 100 changed code lines is a **big change**. Use the full flow:
1. Check `docs/requirements/backlog.md` for existing requests.
2. Write a dated plan in `docs/spec/`, with placement, credential storage, and the existing pattern it follows.
3. Record file and function scope in `docs/scope/`; put deferred work in `docs/deferred/`.
4. Implement and verify without making paid API requests.
5. Record the result in `docs/done/`, add a line to `docs/CHANGELOG.md`, and mark any matching backlog item complete.

For a smaller change, implement and verify it, add one CHANGELOG line, and update the backlog if it contains that request. Bump `pyproject.toml` only when preparing a package release. This repository has no deploy-trigger version file.

## Delegated responsibilities
- Run `uv run python -m unittest discover -s tests -v` and `uv run python -m compileall -q src` for code changes.
- Check staged files with `bash scripts/check-conventions.sh` before committing. The same gate runs in CI.
- Keep the shared block in `CLAUDE.md` and `AGENTS.md` byte-identical.

## Do NOT
- Do not commit `.env`, credentials, generated media, or personal agent notes. They are local data, and a leaked key can authorize paid jobs.
- Do not run a real `start_video` call as a routine test. Veo generation incurs a charge; use fake clients in tests.
- Do not include key values in tool results, exceptions, logs, or commit-gate output. The API key must stay private even when validation fails.
- Do not treat a code change as requiring an invented deploy version bump. No deployment pipeline watches one in this repository.

## Automated gate
`.githooks/pre-commit` and `.github/workflows/praxis-gate.yml` run `scripts/check-conventions.sh` on staged changes. Enable the local hook with `bash scripts/install-hooks.sh`. Add a checkable rule to the gate when a real incident or requirement calls for it.
<!-- praxis:shared:end -->

## Memory (agent-neutral, read on demand)
Durable cross-session facts live in `.claude/memory/` — one fact per file,
indexed in `.claude/memory/MEMORY.md`. The directory is plain markdown, not
Claude-specific: when a task touches a topic, read the index and open the
matching files. Save new durable facts there (and index them) instead of
re-learning them every session.

Everything there is committed and reviewed like code, so keep personal notes out
of it: use a `user-*.md` / `*.local.md` file (both git-ignored) or your own agent
memory outside the repo. This repo never links or moves anything under your
personal agent directory; if an older ic-praxis version did, undo it with
`bash scripts/unlink-claude-memory.sh`.

## What auto-loads here and what doesn't
The commit gate (`.githooks/pre-commit` → `scripts/check-conventions.sh`) is a
git hook — it fires no matter which agent (or human) makes the commit.
Codex discovers the native adapters in `.agents/skills/`; each adapter routes to
the matching canonical procedure under `.claude/commands/` or
`.claude/skills/`, so the workflow has one maintained source. Claude-native
hooks and sub-agents (`.claude/settings.json`, `.claude/agents/`) do not
auto-load in Codex; only use them as plain reference material unless an
equivalent Codex adapter is installed.
