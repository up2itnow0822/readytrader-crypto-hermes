Merge PR #1: Audit repairs v1.1.0: real tool roster, Hermes naming/install mechanics, validator + CI, upstream fixes filed

## What changed
- Skill rebuilt as a hub-installable bundle at `skills/finance/readytrader-crypto/` (SKILL.md + 3 references), replacing the root-level layout Hermes never loads; description within the 60-char hardline; all references reachable by the hub installer.
- Ground truth corrected: the real 29-tool roster (4 phantom HTTP-only tools removed), `mcp__readytrader_crypto__<tool>` naming, `server.py` entrypoint, numeric price from `fetch_ohlcv` (not the `get_crypto_price` sentence), paper-profile env.
- `scripts/validate.py`: offline/online/--live checks (frontmatter, references, config parity, tool/phantom drift vs upstream, links, hygiene, DOX), mutation-tested; static scans scoped to git-tracked files so CI's nested upstream checkout can't false-fail it.
- `.github/workflows/validate.yml`: static on push/PR, static + live paper-path smoke (MCP stdio vs upstream main) on push/PR and weekly cron.
- DOX chain (AGENTS.md × 4), CHANGELOG 1.1.0, .gitignore.

## Why
The 2026-09-14 audit found the original package non-functional: phantom tools, wrong tool naming, wrong install path, wrong entrypoint, and an upstream paper-order crash. Upstream fixes merged as ReadyTrader-Crypto PR #5; this PR makes the skill match verified reality and keeps it pinned there via CI.

## Automerge summary
- Rounds: 2
- CI fixes: live-smoke — validate.py static scans swept CI's nested ReadyTrader-Crypto checkout (317 false failures); scoped to tracked files, verified by nested-clone repro + discrimination test.
- Checks on head bfef834: static ×2, live-smoke ×2, Cursor approval agent — all SUCCESS. Local: offline, online, and --live (vs merged upstream main) all exit 0; Hermes authoring suite 6/6 on the bundle.
- Review: cursor[bot] APPROVED (reviewDecision APPROVED); approval is bound to b1a3095, one commit behind head — the delta is only the validator-scoping fix, itself CI-green and mutation-tested. Merged with that lag documented rather than poking the bot with an empty commit.
- Acknowledged informational notices: chatgpt-codex-connector (usage limit); Cursor review summary (automation marker).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
