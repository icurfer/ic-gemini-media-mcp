<!--
  Adapted from ic-praxis 0.7.0; see THIRD_PARTY_NOTICES.md.
  CLAUDE.md — the project constitution. The coding agent reads this every session.
  DUAL-AGENT: the block between the praxis:shared markers is mirrored VERBATIM
  in AGENTS.md (the same constitution for AGENTS.md-reading agents, e.g. Codex).
  Edit the shared rules in either file, copy the block into the other, stage
  both — the pre-commit gate (Gate E) blocks the commit if they drift.
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

## Routing a new rule (which layer?)
When a retro yields a new convention, place it in the RIGHT layer — the more
mechanical and the more often it must fire, the harder the layer:
- **checkable at commit** → git gate in `scripts/check-conventions.sh`
- **must fire during the agent's tool use** (block/modify/react) → a Claude Code
  hook in `.claude/settings.json` (PreToolUse/PostToolUse)
- **repeatable multi-step procedure** → a skill in `.claude/skills/` (the
  `SKILL.md` documents it; any runnable helper it calls lives in `scripts/`)
- **durable fact to recall when relevant** → `.claude/memory/`
- **always-on judgment rule** → a "Do NOT"/work-order line in this file
Don't put a narrow rule in an always-loaded layer — it taxes every unrelated session.

## Memory (team knowledge, read on demand)
`.claude/memory/` is the team's shared, git-versioned knowledge — one fact per
file, indexed in `.claude/memory/MEMORY.md`. It is **not** auto-loaded: when a
task touches a topic, read the index and open the matching files. Save new
durable facts there (and index them) instead of re-learning them each session;
save durable facts, not incidental conversation detail. Starter rules are marked
`(STARTER RULE …)` — keep or prune them.

**Team vs personal.** Everything in `.claude/memory/` is committed and reviewed
like code. Your own notes belong in a personal file — `user-*.md` or
`*.local.md`, both git-ignored — or in your own `~/.claude/` memory, which this
repo never touches. Do not link, move, or replace anything under `~/.claude/`
on account of this repo. (why: ic-praxis ≤ v0.5.3 symlinked a personal memory
directory into the repo; on a shared repo that leaked personal notes into the
team's working tree. Undo it with `bash scripts/unlink-claude-memory.sh`.)

This system is meant to grow, but growth must stay signal: periodically run
`/praxis-review` (or `bash scripts/praxis-review.sh`) to prune stale rules
and dead gates.
