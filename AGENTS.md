# DOX framework

- DOX is highly performant AGENTS.md hierarchy installed here
- Agent must follow DOX instructions across any edits

## Purpose

Public Hermes optional skill package for ReadyTrader-Crypto BTC paper trading via stdio MCP. Canonical land target for the skill (prefer this repo over forking Hermes core).

## Ownership

- Owner: Agent Economy, LLC / Bill Wilson (@up2itnow0822)
- Companion stack: https://github.com/up2itnow0822/ReadyTrader-Crypto

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

- `SKILL.md` — Hermes skill frontmatter + paper-first BTC workflow
- `references/` — MCP YAML snippet, tool map, tool safety (pre–Phase 4)
- `docs/HERMES_INTEGRATION.md` — operator install (keep aligned with ReadyTrader-Crypto copy)
- License is MIT; never commit secrets or live CEX credentials

## Work Guidance

- Paper-first only in skill guidance: `PAPER_MODE=true`, `LIVE_TRADING_ENABLED=false`, `TRADING_HALTED=true`
- Do not instruct agents to enable live trading or confirm live proposals
- Keep Hermes install path: `optional-skills/finance/readytrader-crypto`
- When ReadyTrader operator docs change, sync `docs/HERMES_INTEGRATION.md` and fix local links
- Prefer this public repo as the skill land target; do not grow Hermes core tools for ReadyTrader

## Verification

- README install path and mcp_servers example match `references/mcp-config.yaml`
- `SKILL.md` frontmatter valid; relative links under `references/` resolve
- `LICENSE` is MIT; repo visibility public
- No secrets in examples

## Hierarchy

- Root AGENTS.md is the DOX rail for this small skill package
- Child AGENTS.md files own durable subtrees listed below

## Closeout

1. Re-check changed paths against the DOX chain
2. Update nearest owning docs and indexes
3. Remove stale or contradictory text
4. Report docs intentionally left unchanged and why

## User Preferences

- Fail closed / paper-first for all skill instructions
- Live dust trades out of scope until dedicated ReadyTrader Phase 4 UAT

## Child DOX Index

| Path | Owns |
|------|------|
| [docs/AGENTS.md](docs/AGENTS.md) | Operator docs mirrored from ReadyTrader |
| [references/](references/) | Parent-owned MCP snippets and safety refs (no nested AGENTS.md) |
