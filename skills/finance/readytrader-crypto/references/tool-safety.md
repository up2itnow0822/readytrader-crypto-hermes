# ReadyTrader-Crypto tool safety (pre–Phase 4)

Companion to `tool-map.md`. This file states the rules; the map states the mechanics.

## Allowed from this skill (paper profile)

- Market data and research: `get_crypto_price`, `fetch_ohlcv`, `get_sentiment`, `get_news`,
  `get_social_sentiment`, `get_financial_news`, `get_free_news`, `get_market_regime`,
  `run_backtest_simulation`, `post_market_insight`, `get_latest_insights`
- Paper wallet and risk: `deposit_paper_funds`, `validate_trade_risk`
- Paper orders: `place_cex_order` while `PAPER_MODE=true` (always pass `price`; BTC pairs only)
- Public exchange metadata: `get_cex_capabilities`

## Blocked until the operator authorizes Phase 4 dust UAT

- Any call to `place_cex_order`, `cancel_cex_order`, `cancel_all_cex_orders`, or
  `replace_cex_order` against a process where `PAPER_MODE=false`
- Approving a live proposal over the HTTP API (`POST /api/approve-trade`)
- Setting `LIVE_TRADING_ENABLED=true`, `PAPER_MODE=false`, or `TRADING_HALTED=false`
  anywhere (Hermes config, `.env`, compose files)
- `swap_tokens` or `transfer_eth` with a production signer
- `start_cex_private_ws` against a non-paper process (see below)

## Operator-only (never from an agent)

- Editing allowlists (`ALLOW_EXCHANGES`, `ALLOW_CEX_SYMBOLS`, `ALLOW_CEX_MARKET_TYPES`),
  `MAX_CEX_ORDER_AMOUNT`, JWT/admin secrets
- Configuring exchange API keys; keys must be trade+read only, never withdraw-capable
- Pointing the MCP entry at the live stack (`docker-compose.live.yml`, `.env.live`)

## What the controls actually do (verified against ReadyTrader-Crypto `main`, 2026-09-14)

- `TRADING_HALTED=true` and `LIVE_TRADING_ENABLED=false` are checked by
  `_require_live_allowed` (`app/tools/execution.py`) on the live **order and account** tools
  (`place_cex_order`, cancel/replace, balance/order reads, `swap_tokens`, `transfer_eth`).
  Paper orders bypass that guard by design.
- The private-update tools (`start_cex_private_ws`, `stop_cex_private_ws`,
  `list_cex_private_updates`) check `PAPER_MODE` first. From ReadyTrader-Crypto PR #7
  onward, `start_cex_private_ws` is additionally gated by `_require_live_allowed`
  (halt + consent + venue); `stop`/`list` stay available so a halt can still stop and
  observe streams. Before PR #7 all three opened/read authenticated streams even while
  halted (the issue #6 gap). Either way, one more reason `PAPER_MODE` stays `true` here.
- `ALLOW_EXCHANGES` / `ALLOW_CEX_SYMBOLS` / `ALLOW_CEX_MARKET_TYPES` are applied by the policy
  engine on the live order path only. Paper orders are not filtered; the agent enforces
  BTC-only itself.
- `EXECUTION_APPROVAL_MODE=approve_each` never produces a proposal in paper mode. Treat
  it as an extra latch for the live profile, not as a step in this workflow. (Before PR #5
  the live proposal path was inert as well because of an enum/string comparison.)
- Phase 4 is a documented operator process (`docs/LIVE_TESTING_PROTOCOL.md`,
  `docs/UAT_BTC_PRODUCTION_MINUS_DUST.md` in ReadyTrader-Crypto), not a runtime flag.
  Nothing in the code "unlocks" it; the operator changes env and restarts.
