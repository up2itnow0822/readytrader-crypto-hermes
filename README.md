# readytrader-crypto-hermes

Hermes optional skill for **paper-first BTC trading** via [ReadyTrader-Crypto](https://github.com/up2itnow0822/ReadyTrader-Crypto) stdio MCP.

This repo is the **canonical public skill package**. Install it into Hermes as `optional-skills/finance/readytrader-crypto/`. Do not grow Hermes core tools for ReadyTrader — capability stays at the MCP edge plus this skill.

**License:** MIT  
**Owner:** Agent Economy, LLC / Bill Wilson ([@up2itnow0822](https://github.com/up2itnow0822))

## What it is

| Path | Role |
|------|------|
| `SKILL.md` | Hermes skill: when to use, paper BTC workflow, kill-switch rules |
| `references/mcp-config.yaml` | Example `mcp_servers.readytrader-crypto` YAML |
| `references/tool-map.md` | Safe vs deferred MCP tools |
| `references/tool-safety.md` | Pre–Phase 4 tool safety |
| `docs/HERMES_INTEGRATION.md` | Operator install + smoke checklist (copied from ReadyTrader) |

Full trading stack, API, Docker live compose, and UAT evidence live in **ReadyTrader-Crypto**:

- Ops (halted BTC): [OPS_BTC_PRODUCTION.md](https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/docs/OPS_BTC_PRODUCTION.md)
- UAT evidence: [UAT_BTC_PRODUCTION_MINUS_DUST.md](https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/docs/UAT_BTC_PRODUCTION_MINUS_DUST.md)
- Hermes guide (upstream copy): [HERMES_INTEGRATION.md](https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/docs/HERMES_INTEGRATION.md)

## Install into Hermes

From a Hermes Agent checkout:

```bash
mkdir -p optional-skills/finance
git clone https://github.com/up2itnow0822/readytrader-crypto-hermes.git \
  optional-skills/finance/readytrader-crypto
```

Or copy `SKILL.md` + `references/` into that path. Restart the Hermes session so tools reload.

Also install and configure [ReadyTrader-Crypto](https://github.com/up2itnow0822/ReadyTrader-Crypto) (`make setup`, paper `.env` from `env.example`).

## `mcp_servers` YAML example

Merge into `~/.hermes/config.yaml` (set `cwd` to your ReadyTrader clone):

```yaml
mcp_servers:
  readytrader-crypto:
    command: python
    args:
      - app/main.py
    cwd: /path/to/ReadyTrader-Crypto
    timeout: 120
    connect_timeout: 60
    env:
      PAPER_MODE: "true"
      LIVE_TRADING_ENABLED: "false"
      TRADING_HALTED: "true"
      DEV_MODE: "true"
      EXECUTION_MODE: "cex"
      RISK_PROFILE: "conservative"
      EXECUTION_APPROVAL_MODE: "approve_each"
      ALLOW_EXCHANGES: "binance,kraken,coinbase"
      ALLOW_CEX_SYMBOLS: "btc/usdt,btc/usd"
      ALLOW_CEX_MARKET_TYPES: "spot"
```

See `references/mcp-config.yaml` and `docs/HERMES_INTEGRATION.md` for the full operator guide.

## Safety (paper-first)

- Default posture: **paper mode, trading halted, live disabled**
- Never set `LIVE_TRADING_ENABLED=true` or `PAPER_MODE=false` from this skill
- Never confirm live execution proposals until the operator authorizes Phase 4 dust UAT
- Prefer `EXECUTION_APPROVAL_MODE=approve_each`
- CEX keys (if any) must be **trade + read only** — no withdraw

Live capital and dust trades are **out of scope** for this skill package.

## Layout for Hermes

Expected install tree:

```
optional-skills/finance/readytrader-crypto/
  SKILL.md
  references/
    mcp-config.yaml
    tool-map.md
    tool-safety.md
```

`docs/` here is for operators cloning this repo standalone; Hermes only requires `SKILL.md` + `references/`.

## Related

- Trading stack: https://github.com/up2itnow0822/ReadyTrader-Crypto
- Hermes Agent: https://github.com/up2itnow0822/hermes-agent
