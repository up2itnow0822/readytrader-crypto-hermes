# docs/

## Purpose

Operator-facing Hermes integration guide packaged with the repo so standalone clones are
self-contained (no relative links into ReadyTrader-Crypto).

## Ownership

`HERMES_INTEGRATION.md` is mirrored to ReadyTrader-Crypto `docs/HERMES_INTEGRATION.md`.
This repo is where the guide is edited first; ReadyTrader-Crypto receives the same content by PR.

## Local Contracts

- `HERMES_INTEGRATION.md` — venv install, `mcp_servers` entry, verified MCP tool list, smoke checklist, production-halted notes
- The fenced `yaml` block must equal the `mcp_servers.readytrader-crypto` entry in `skills/finance/readytrader-crypto/references/mcp-config.yaml` (validator compares the whole entry)
- Link out to ReadyTrader-Crypto for OPS/UAT/live compose; do not duplicate full runbooks here

## Work Guidance

- Paper-first examples only; never embed real secrets or machine-local paths
- State only verified facts about ReadyTrader tools and Hermes mechanics; the smoke checklist must be executable from the paper profile
- After editing, open a PR to ReadyTrader-Crypto carrying the same `HERMES_INTEGRATION.md`

## Verification

- `python3 scripts/validate.py` (config parity, link resolution, tool names)

## Child DOX Index

(none)
