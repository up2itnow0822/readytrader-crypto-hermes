# readytrader-crypto-hermes

Hermes Agent skill for **paper-first BTC trading** through the
[ReadyTrader-Crypto](https://github.com/up2itnow0822/ReadyTrader-Crypto) stdio MCP server.

This repo is the canonical public home of the skill. Capability stays at the MCP edge plus
this skill package; nothing here is added to Hermes core.

**License:** MIT  
**Owner:** Agent Economy, LLC / Bill Wilson ([@up2itnow0822](https://github.com/up2itnow0822))

## Layout

| Path | Role |
|------|------|
| `skills/finance/readytrader-crypto/SKILL.md` | The Hermes skill: triggers, prerequisites, procedure, pitfalls, verification |
| `skills/finance/readytrader-crypto/references/mcp-config.yaml` | Copy-paste `mcp_servers.readytrader-crypto` entry |
| `skills/finance/readytrader-crypto/references/tool-map.md` | All 29 MCP tools classified for the paper profile |
| `skills/finance/readytrader-crypto/references/tool-safety.md` | What is allowed, blocked, and operator-only before Phase 4 |
| `docs/HERMES_INTEGRATION.md` | Operator guide (mirrored to ReadyTrader-Crypto `docs/HERMES_INTEGRATION.md`) |
| `scripts/validate.py` | Repo validator run by CI (frontmatter, links, config parity, tool-name cross-check, secrets) |

The skill directory follows the Hermes layout (`<category>/<name>/SKILL.md` + `references/`)
so every install path below works unchanged.

## Install into Hermes

Hermes loads skills from `~/.hermes/skills/`. Pick one:

**A. Skills Hub (GitHub source)**

```bash
hermes skills install up2itnow0822/readytrader-crypto-hermes/skills/finance/readytrader-crypto --category finance
```

**B. Skills Hub (direct URL)**

```bash
hermes skills install https://raw.githubusercontent.com/up2itnow0822/readytrader-crypto-hermes/main/skills/finance/readytrader-crypto/SKILL.md --category finance
```

**C. Manual copy**

```bash
git clone https://github.com/up2itnow0822/readytrader-crypto-hermes.git /tmp/rt-hermes
mkdir -p ~/.hermes/skills/finance
cp -r /tmp/rt-hermes/skills/finance/readytrader-crypto ~/.hermes/skills/finance/
```

Then merge `references/mcp-config.yaml` into `~/.hermes/config.yaml` (set `command` to your
ReadyTrader venv interpreter and `cwd` to your clone) and start a **new** Hermes session.
Tools register as `mcp__readytrader_crypto__<tool>`.

Do not clone this repo into a Hermes checkout's `optional-skills/` tree — that directory is
the upstream contribution tree and is not loaded at runtime. To contribute the skill to a
Hermes fork, copy `skills/finance/readytrader-crypto/` to `optional-skills/finance/` and open a PR there.

## Install ReadyTrader-Crypto (the MCP server)

```bash
git clone https://github.com/up2itnow0822/ReadyTrader-Crypto.git
cd ReadyTrader-Crypto
python3 -m venv .venv          # Python 3.12+
.venv/bin/pip install -r requirements.txt
```

The paper profile needs no `.env` and no exchange keys; the Hermes `env:` block supplies
every flag. The canonical entrypoint is `server.py`.

## Safety posture

- Default and only supported posture: **paper mode, trading halted, live disabled**
- The skill never sets `LIVE_TRADING_ENABLED=true`, `PAPER_MODE=false`, or `TRADING_HALTED=false`
- Live dust / production trades are an operator process (ReadyTrader Phase 4 UAT) and out of scope
- Exchange API keys, if ever configured, must be trade+read only — never withdraw-capable

## Validate

```bash
python3 scripts/validate.py            # online: also checks ReadyTrader-Crypto main for drift
python3 scripts/validate.py --offline  # no network
python3 scripts/validate.py --offline --live --rt-root /path/to/ReadyTrader-Crypto --rt-python /path/to/ReadyTrader-Crypto/.venv/bin/python
```

Static checks: SKILL.md frontmatter against Hermes' authoring rules (60-char description, name
matches directory, `platforms`, tags); every `references/` file is referenced from SKILL.md
(Hermes hub installs only fetch referenced files); the operator doc's YAML equals
`references/mcp-config.yaml`; every snake_case identifier in every markdown file is a
registered ReadyTrader tool, an allowlisted non-tool, or a known phantom mentioned only as
non-existent; env vars exist in ReadyTrader's `settings.py`/`env.example`; links resolve; no
secrets or machine-local paths. Online mode fails closed if upstream cannot be fetched.

`--live` launches `server.py` over MCP stdio with the config's env, asserts the 29-tool roster,
and runs deposit → risk check → paper order. CI runs the static checks on every push and both
static and live weekly against ReadyTrader-Crypto `main`; a red `live-smoke` job means the
paper path is broken upstream (it is, on revisions before ReadyTrader-Crypto PR #5).

## Upstream status

- ReadyTrader-Crypto [PR #5](https://github.com/up2itnow0822/ReadyTrader-Crypto/pull/5) — fixes the
  paper `place_cex_order` crash, the enum/string settings comparisons, `python app/main.py`, and
  the stale tool names in its docs. Until it merges, Procedure step 5 in the skill fails.
- ReadyTrader-Crypto [issue #6](https://github.com/up2itnow0822/ReadyTrader-Crypto/issues/6) — remaining
  live-safety gaps (private-WS tools bypass the halt flag, skipped safety tests, placeholder paper price).

## Related

- Trading stack: https://github.com/up2itnow0822/ReadyTrader-Crypto
  ([OPS_BTC_PRODUCTION.md](https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/docs/OPS_BTC_PRODUCTION.md),
  [UAT_BTC_PRODUCTION_MINUS_DUST.md](https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/docs/UAT_BTC_PRODUCTION_MINUS_DUST.md),
  [TOOLS.md](https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/docs/TOOLS.md))
- Hermes Agent: https://github.com/up2itnow0822/hermes-agent (fork of https://github.com/NousResearch/hermes-agent)
