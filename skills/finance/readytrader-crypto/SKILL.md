---
name: readytrader-crypto
description: "Paper-first BTC trading via ReadyTrader-Crypto MCP."
version: 1.1.1
author: Bill Wilson (up2itnow0822), Hermes Agent
license: MIT
tags: [bitcoin, crypto, trading, readytrader, cex, paper-trading, mcp]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitcoin, crypto, trading, readytrader, cex, paper-trading, mcp]
    category: finance
    related_skills: [stocks, polymarket]
---

# ReadyTrader-Crypto Skill

Operate Bitcoin spot trading through the **ReadyTrader-Crypto** stdio MCP server
(https://github.com/up2itnow0822/ReadyTrader-Crypto). This skill covers the
**paper** profile only: `PAPER_MODE=true`, `LIVE_TRADING_ENABLED=false`,
`TRADING_HALTED=true`. It never enables live execution, never confirms live
orders, and never touches exchange credentials. Live dust/production trading is
a separate operator-run process (ReadyTrader "Phase 4 UAT") and is out of scope.

Reference files shipped with this skill: `references/mcp-config.yaml` (the
`mcp_servers` entry), `references/tool-map.md` (every MCP tool and its paper
safety class), `references/tool-safety.md` (what is blocked before Phase 4).

## When to Use

- User wants paper BTC/USDT (or BTC/USD) trades, risk checks, or backtests via ReadyTrader
- User asks Hermes to run a paper crypto trading loop through ReadyTrader MCP
- User wants BTC price, OHLCV candles, sentiment, or news from ReadyTrader's market-data tools

Don't use for:

- Live dust or production capital trades — refuse and cite the Phase 4 gate
- Withdrawals, key export, signer changes, or editing ReadyTrader allowlists
- Non-BTC pairs. ReadyTrader's `ALLOW_CEX_SYMBOLS` allowlist is enforced only on the live
  order path, so in paper mode the agent must self-enforce BTC-only

## Prerequisites

1. ReadyTrader-Crypto cloned and installed into its own virtualenv (Python 3.12+):
   `terminal(command="cd /path/to/ReadyTrader-Crypto && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt")`
2. `mcp_servers.readytrader-crypto` merged into `~/.hermes/config.yaml` from
   `references/mcp-config.yaml`, with `command` pointing at that venv's interpreter and
   `cwd` at the clone. The entrypoint is `server.py`; `python app/main.py` fails with
   `ModuleNotFoundError: No module named 'server'` on revisions before ReadyTrader-Crypto PR #5.
3. Env in that entry: `PAPER_MODE=true`, `LIVE_TRADING_ENABLED=false`, `TRADING_HALTED=true`,
   `EXECUTION_MODE=cex`, `EXECUTION_APPROVAL_MODE=approve_each`, `RISK_PROFILE=conservative`.
   No exchange API keys are needed for the paper profile.
4. A fresh Hermes session after editing config — MCP tools register at session start.
5. ReadyTrader-Crypto at or after PR #5 (`fix/paper-execution-path-and-enum-compare`).
   Before it, paper `place_cex_order` raises
   `TypeError: execute_trade() got an unexpected keyword argument 'agent_id'`; on such a
   revision stop after Procedure step 4 and report the upstream defect instead of retrying.

## How to Run

Hermes registers ReadyTrader tools as `mcp__readytrader_crypto__<tool>` (server name
hyphens become underscores; the delimiter is a double underscore). Example:
`mcp__readytrader_crypto__get_crypto_price(symbol="BTC/USDT")`.

## Quick Reference

Paper-safe tools (no credentials, no live side effects):

| Tool | Use |
|------|-----|
| `get_crypto_price(symbol, exchange="binance")` | Spot price as a sentence in `data.result` (`The current price of BTC/USDT is <n> (Source: …)`) |
| `fetch_ohlcv(symbol, timeframe="1h", limit=24)` | Candle records (`open/high/low/close/volume`) in `data.data`; the numeric price source |
| `get_sentiment()`, `get_free_news(symbol="")` | Keyless: Fear & Greed index, RSS headlines |
| `get_news()`, `get_social_sentiment(symbol)`, `get_financial_news(symbol)` | Need provider keys; degrade to empty without them |
| `get_market_regime(symbol, timeframe="1d")`, `run_backtest_simulation(strategy_code, symbol, timeframe)` | Analysis (the backtest executes the code you pass — review it first) |
| `deposit_paper_funds(asset, amount)` | Seed the paper wallet; response includes the updated balance |
| `validate_trade_risk(side, symbol, amount_usd, portfolio_value)` | Risk Guardian check |
| `place_cex_order(symbol, side, amount, order_type, price, exchange)` | Routes to the paper engine when `PAPER_MODE=true` (works from PR #5 onward) |
| `get_cex_capabilities(exchange, symbol)` | Public exchange metadata (no auth) |

Everything else (order query/cancel/replace, private WS, `transfer_eth`) needs live
credentials or returns `paper_mode_not_supported`; `get_cex_balance` joins the paper-safe
list from ReadyTrader-Crypto PR #7 onward (paper wallet view, no keys); `swap_tokens`
is DEX and out of scope here — see `references/tool-map.md`.

## Procedure

1. Confirm the server is loaded: the tool list contains `mcp__readytrader_crypto__validate_trade_risk`.
   If absent, stop and report the config/session problem — do not improvise with shell.
2. Get a numeric price: `fetch_ohlcv(symbol="BTC/USDT", timeframe="1m", limit=1)` and take
   `close` from the last record (fallback: parse the number out of `get_crypto_price`'s
   `data.result` sentence). Done when you hold a positive float.
3. Seed paper funds if needed: `deposit_paper_funds(asset="USDT", amount=10000)`.
   Done when the response shows the balance.
4. Size the trade and run `validate_trade_risk(side, symbol, amount_usd, portfolio_value)`.
   Proceed only on an approved result; otherwise report the rejection reason.
5. Place the paper order with an explicit price: `place_cex_order(symbol="BTC/USDT",
   side="buy", amount=<btc>, order_type="market", price=<price from step 2>)`.
   Done when the response has `"mode": "paper"`. A `TypeError` mentioning `agent_id` means
   ReadyTrader predates PR #5 — report it and stop.
6. Report symbol, side, amount, fill price, and the paper balance to the user.
7. If the user asks for live trading at any point: refuse, cite the Phase 4 gate,
   and leave `TRADING_HALTED=true`.

## Pitfalls

- No health, metrics, portfolio, or approval MCP tools exist. Those live only on the
  HTTP API (`api_server.py`: `/api/health`, `/api/metrics`, `/api/portfolio`,
  `/api/pending-approvals`). Do not call `get_health`, `get_metrics_snapshot`,
  `list_pending_executions`, or `confirm_execution` — they are not registered.
- Paper `place_cex_order` price: from ReadyTrader-Crypto PR #7 onward, an omitted/≤ 0
  `price` resolves via the market-data bus or fails with `paper_price_required` (never a
  fabricated fill). On older revisions it silently fills at a placeholder `100000.0`.
  Either way, pass the explicit price from step 2 for deterministic fills.
- `get_cex_balance`: from PR #7 onward, paper mode returns the paper wallet's balances
  (`mode: "paper"`, no keys needed). On older revisions it requires real exchange keys
  even in paper mode, and the only MCP view of paper balances is the
  `deposit_paper_funds` response.
- `EXECUTION_APPROVAL_MODE=approve_each` is defense in depth, not a workflow: in paper
  mode no proposal is ever returned. Keep it set; do not rely on it.
- The kill switch (`TRADING_HALTED`) is checked only on the live paths. Paper orders
  execute while halted — that is expected. Allowlists (`ALLOW_*`) are likewise live-only.
  From PR #7 onward `start_cex_private_ws` is also halt/consent-gated; before it, private
  streams opened even while halted.
- Hermes tool names use `mcp__readytrader_crypto__` (double underscores, no hyphens). Older
  docs that show a single-underscore, hyphenated prefix are wrong.
- The upstream defects from the 2026-09-14 audit (issue #6) are fixed by ReadyTrader-Crypto
  PR #7 (2026-09-15); the revision-qualified notes above cover older checkouts.

## Verification

- `fetch_ohlcv(symbol="BTC/USDT", timeframe="1m", limit=1)` returns `ok: true` with one
  record containing a numeric `close`.
- A `place_cex_order` call with an explicit price returns `"mode": "paper"` and no
  exchange credentials were ever configured.
- `~/.hermes/config.yaml` still has `PAPER_MODE: "true"`, `LIVE_TRADING_ENABLED: "false"`,
  `TRADING_HALTED: "true"` after the session (the skill never edits them).
