# skills/

## Purpose

Hermes skill bundles in Hermes layout (`<category>/<name>/`). Today: `finance/readytrader-crypto/`. Everything a hub install copies to
`~/.hermes/skills/finance/readytrader-crypto/` lives here and nowhere else.

## Ownership

Owned by the root contract. `SKILL.md` is the agent-facing contract; `references/` holds
material too bulky or too mechanical for the skill body.

## Local Contracts

- `SKILL.md` — frontmatter per Hermes authoring standards; body order: intro, When to Use, Prerequisites, How to Run, Quick Reference, Procedure, Pitfalls, Verification
- `references/mcp-config.yaml` — the `mcp_servers.readytrader-crypto` entry; must parse and match the YAML block in `docs/HERMES_INTEGRATION.md`
- `references/tool-map.md` — all 29 ReadyTrader MCP tools classified for the paper profile, plus the HTTP-only capabilities that are not MCP tools
- `references/tool-safety.md` — allowed / blocked / operator-only rules and what the runtime controls actually enforce

## Work Guidance

- Only name tools that ReadyTrader-Crypto `server.py` registers; phantom names may appear only in sentences that say they do not exist
- Every file under `references/` must be referenced from `SKILL.md` by path (`references/<file>`)
- No `docs/` or parent-directory references from `SKILL.md`; the bundle must be self-contained
- Paper `place_cex_order` guidance must require an explicit `price`
- Keep the body under ~150 lines; move detail into `references/`

## Verification

- `python3 scripts/validate.py` (frontmatter, references, config parity, tool and env cross-check, hygiene)

## Child DOX Index

(none — bundle directories stay free of AGENTS.md so hub and manual installs copy only skill files)
