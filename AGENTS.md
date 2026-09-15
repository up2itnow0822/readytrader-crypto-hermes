# DOX framework

- DOX is highly performant AGENTS.md hierarchy installed here
- Agent must follow DOX instructions across any edits

## Purpose

Public Hermes Agent skill package for ReadyTrader-Crypto BTC **paper** trading over stdio MCP.
Canonical home of the skill; the trading stack itself lives in ReadyTrader-Crypto.

## Ownership

- Owner: Agent Economy, LLC / Bill Wilson (@up2itnow0822)
- Companion stack: https://github.com/up2itnow0822/ReadyTrader-Crypto (source of truth for tools, env vars, guards)
- Hermes contract: https://github.com/up2itnow0822/hermes-agent (`tools/mcp_tool.py`, `tools/skills_hub.py`, `tools/skill_manager_tool.py`, `tests/skills/test_authoring_standards.py`)

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees
- Work products must stay understandable from the nearest AGENTS.md plus every parent above it

## Read Before Editing

1. Read this root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the root to each target path
4. Read every AGENTS.md along each route
5. Use the nearest AGENTS.md as the local contract
6. No child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass. Update the closest owning AGENTS.md when purpose, scope, contracts, workflows, or index contents change.

## Local Contracts

- `skills/finance/readytrader-crypto/` — the installable skill (`SKILL.md` + `references/`); Hermes layout `<category>/<name>/`
- `docs/HERMES_INTEGRATION.md` — operator guide, mirrored to ReadyTrader-Crypto `docs/HERMES_INTEGRATION.md`
- `scripts/validate.py` — the repo's verification gate; CI runs it (`.github/workflows/validate.yml`)
- `CHANGELOG.md` — versioned; bump `version:` in `SKILL.md` in the same change
- License is MIT; never commit secrets, exchange keys, or machine-local paths

## Work Guidance

- Every tool name, env var, file path, and Hermes mechanic stated in this repo must be verified against ReadyTrader-Crypto `main` and hermes-agent source before it is written; cite the file when in doubt
- Paper-first only: `PAPER_MODE=true`, `LIVE_TRADING_ENABLED=false`, `TRADING_HALTED=true`, `DEV_MODE=false`; never instruct agents to enable live trading or approve live proposals
- Entrypoint is `server.py`; Hermes tool names are `mcp__readytrader_crypto__<tool>`
- Runtime install target is `~/.hermes/skills/finance/readytrader-crypto/` (hub GitHub/URL install or manual copy); `optional-skills/` in a Hermes checkout is a contribution tree only
- `SKILL.md` must reference every file under `references/` by path — Hermes hub installs only fetch referenced files
- Keep `SKILL.md` within Hermes authoring rules: description ≤ 60 chars ending in a period, `name` == directory name, `platforms` set, no machine-local paths
- When `docs/HERMES_INTEGRATION.md` changes, open a PR to ReadyTrader-Crypto with the same content
- Do not grow Hermes core tools for ReadyTrader; capability stays at the MCP edge plus this skill

## Verification

- `python3 scripts/validate.py` passes (online) or `python3 scripts/validate.py --offline` (no network); CI: `.github/workflows/validate.yml` on push, PR, and weekly
- Live check: `python3 scripts/validate.py --offline --live --rt-root <ReadyTrader clone> --rt-python <its venv python>` (CI `live-smoke` job, weekly against `main`)

## User Preferences

- Fail closed / paper-first for all skill instructions
- Live dust trades out of scope until dedicated ReadyTrader Phase 4 UAT
- Repos must stay correct and functional; when the upstream stack breaks a documented path, say so in `SKILL.md` Pitfalls/Prerequisites with the upstream PR/issue number, and file it upstream rather than papering over it

## Child DOX Index

| Path | Owns |
|------|------|
| [skills/AGENTS.md](skills/AGENTS.md) | Skill bundles (`finance/readytrader-crypto/`): SKILL.md authoring rules and references/ contents |
| [docs/AGENTS.md](docs/AGENTS.md) | Operator docs mirrored to ReadyTrader-Crypto |
| [scripts/AGENTS.md](scripts/AGENTS.md) | Validator and CI contract |
| Parent retains: repo purpose, ownership, paper-first policy, release/versioning, cross-repo sync rules |
