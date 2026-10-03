#!/usr/bin/env bash
# Adapted from ic-praxis 0.7.0; see THIRD_PARTY_NOTICES.md.
# Point this repo's git hooks at .githooks/ (run once per clone).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
chmod +x "$ROOT/.githooks/pre-commit" "$ROOT/scripts/check-conventions.sh" 2>/dev/null || true
git -C "$ROOT" config core.hooksPath .githooks
echo "✓ core.hooksPath = .githooks — the praxis gate is now active."
echo "  Test it: stage a fake secret in a temporary file and run scripts/check-conventions.sh."
