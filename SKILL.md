---
name: readytrader-crypto
description: "Trade BTC via ReadyTrader-Crypto MCP — paper-first, risk-gated CEX."
version: 1.0.0
author: Agent Economy / Bill Wilson
license: MIT
tags: [bitcoin, crypto, trading, readytrader, cex, paper-trading, mcp]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Bitcoin, Crypto, Trading, CEX, ReadyTrader]
    category: finance
    related_skills: [stocks, polymarket]
---

# ReadyTrader-Crypto — BTC via Hermes MCP

Operate Bitcoin spot trading through the **ReadyTrader-Crypto** stdio MCP server.
Default posture: **paper mode, trading halted, live disabled**. Never enable live
execution or confirm live CEX orders unless the operator explicitly authorizes
Phase 4 dust UAT.

Full install: `docs/HERMES_INTEGRATION.md` (also in ReadyTrader-Crypto).
Stack: https://github.com/up2itnow0822/ReadyTrader-Crypto
MCP config snippet: `references/mcp-config.yaml`.
Tool safety: `references/tool-safety.md`.

## When to Use

- User wants paper BTC/USDT trading, risk checks, or ReadyTrader health/metrics
- User asks Hermes to run a crypto trading loop via ReadyTrader MCP
- Operator asks to validate kill switch / approve_each flows (still paper)

## When NOT to Use

- Live dust or production capital trades (Phase 4+) without written operator OK
- Withdrawals, key export, or changing signer to `env_private_key` for live
- Non-BTC exotic pairs outside allowlists unless operator expands policy

## Prerequisites

1. ReadyTrader-Crypto installed; Hermes `mcp_servers.readytrader-crypto` configured
2. Session restarted so `mcp_readytrader-crypto_*` (or equivalent) tools appear
3. Env: `PAPER_MODE=true`, `LIVE_TRADING_ENABLED=false`, `TRADING_HALTED=true`

## Typical Paper BTC Workflow

1. Call health/metrics tools — confirm paper + halted/live-off
2. `get_crypto_price` / OHLCV for BTC
3. `deposit_paper_funds` (e.g. USDT/USDC) if needed
4. `validate_trade_risk` before sizing
5. Place **paper** BTC/USDT orders only; record metrics
6. If user asks for live: refuse, cite Phase 4 gate, keep halted

## Kill Switch & Approval

- `TRADING_HALTED=true` must block live execution — verify if testing controls
- Prefer `EXECUTION_APPROVAL_MODE=approve_each`; do not auto-confirm live proposals
- Never set `LIVE_TRADING_ENABLED=true` or `PAPER_MODE=false` from this skill

## Pitfalls

- MCP tool names are host-prefixed; discover via Hermes tool list
- Live compose (`docker-compose.live.yml`) is separate from this paper MCP profile
- CEX keys must be trade+read only (no withdraw) if present at all
