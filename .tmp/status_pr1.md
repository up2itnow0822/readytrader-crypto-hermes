Round 2 (final): all checks green on head bfef834 (static ×2, live-smoke ×2, Cursor approval agent). Round 1 fixed live-smoke: validate.py static scans swept CI's nested ReadyTrader-Crypto checkout (317 false failures) — now scoped to git-tracked files, verified via nested-clone repro, --live against a nested rt-root, and a tracked-bad-file discrimination test.

Local verification: validate.py offline / online / --live (vs merged upstream main incl. PR #5) all exit 0; Hermes authoring-standards suite 6/6 on the bundle; `mcp__readytrader_crypto__*` naming and all three reference paths confirmed against hermes-agent source.

Merging with cursor[bot]'s APPROVED review (reviewDecision APPROVED) bound one commit behind head — the delta is only the CI-green, mutation-tested validator-scoping fix; deviation documented rather than poking the bot with an empty commit.
