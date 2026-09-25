# ReadyTrader-Crypto MCP tool map (paper profile)

All 29 tools registered by `server.py` on ReadyTrader-Crypto `main`, classified for the
paper profile (`PAPER_MODE=true`, `LIVE_TRADING_ENABLED=false`, `TRADING_HALTED=true`).
Hermes exposes each one as `mcp__readytrader_crypto__<tool>`.

Source of truth for signatures: ReadyTrader-Crypto
[`docs/TOOLS.md`](https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/docs/TOOLS.md).
`scripts/validate.py` in this repo cross-checks this list against that file.

## Paper-safe (no credentials, no live side effects)

| Tool | Purpose | Notes |
|------|---------|-------|
| `get_crypto_price` | Spot price for a pair | Numeric `data.price`, plus the same price as a sentence in `data.result` |
| `fetch_ohlcv` | Candles | `data.data` is a list of `{timestamp, open, high, low, close, volume}` |
| `get_sentiment` | Crypto Fear & Greed index | Keyless (alternative.me) |
| `get_free_news` | Keyless RSS headlines | Works without keys |
| `get_news`, `get_social_sentiment`, `get_financial_news` | Provider-backed news/sentiment | Need provider keys; without them `not_configured` (`ok: false`), a source that fails `source_unavailable`; before ReadyTrader-Crypto PR #20, `ok: true` with an "Unavailable" sentence. No data either way |
| `get_market_regime` | Regime classification | Analysis only |
| `run_backtest_simulation` | Backtest supplied strategy code | Runs code you pass in — review it first |
| `post_market_insight` / `get_latest_insights` | Shared insight store | Local state only |
| `deposit_paper_funds` | Seed the paper wallet | Response carries the updated balance |
| `validate_trade_risk` | Risk Guardian check | Pure validation |
| `place_cex_order` | Paper order via the paper engine when `PAPER_MODE=true` | Fills at the server's market price: omit `price` on market orders (before PR #20 a passed price was used as the fill price); a limit fills only when marketable (`limit_not_marketable`); the Risk Guardian can answer `risk_blocked` (PR #20); broken before PR #5 (`agent_id` TypeError) |
| `get_cex_capabilities` | Public exchange metadata | `auth=False`; blocked only if `EXECUTION_MODE=dex` |
| `get_cex_balance` | Paper wallet balances (`mode: "paper"`, no keys) | Paper-safe from ReadyTrader-Crypto PR #7 onward; before PR #7 it opened `CexExecutor(auth=True)` and failed without keys |

## Live-account tools: `paper_mode_not_supported` in the paper profile

Paper orders fill at once and never rest on an exchange, so these answer
`paper_mode_not_supported` when `PAPER_MODE=true`:

| Tool | Live use |
|------|----------|
| `get_cex_order`, `list_cex_open_orders`, `list_cex_orders`, `get_cex_my_trades`, `wait_for_cex_order` | Account reads |
| `cancel_cex_order`, `cancel_all_cex_orders`, `replace_cex_order` | Account writes |
| `start_cex_private_ws`, `stop_cex_private_ws`, `list_cex_private_updates` | Private order stream |
| `transfer_eth` | Native-coin transfer |

Before ReadyTrader-Crypto PR #20 the order reads and writes in the first two rows tried an
authenticated exchange session instead and failed with `cex_error` in the paper profile.

## Out of scope for this BTC/CEX skill

`swap_tokens` — DEX path. In paper mode it routes to the paper engine without credentials
(same `agent_id` defect before PR #5); live mode needs an on-chain signer. Not used here.

## Not MCP tools (HTTP API only — `api_server.py`)

| Capability | Endpoint |
|------------|----------|
| Health / mode flags | `GET /api/health` (`mode`, `trading_halted`, `live_enabled`, `version`) |
| Metrics snapshot | `GET /api/metrics` |
| Paper portfolio | `GET /api/portfolio` |
| Pending approvals / confirm | `GET /api/pending-approvals`, `POST /api/approve-trade` |

`get_health`, `get_metrics_snapshot`, `list_pending_executions`, and `confirm_execution`
do not exist as MCP tools. Older copies of this skill listed them; do not call them.

## Operator-only (never from this skill)

- Clearing `TRADING_HALTED`, enabling `LIVE_TRADING_ENABLED`, disabling `PAPER_MODE`
- Configuring exchange API keys (must be trade+read only, never withdraw-capable)
- Editing allowlists (`ALLOW_EXCHANGES`, `ALLOW_CEX_SYMBOLS`, `ALLOW_CEX_MARKET_TYPES`), `MAX_CEX_ORDER_AMOUNT`, JWT/admin secrets. Note these allowlists are enforced only on the live order path.
