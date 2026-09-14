# ReadyTrader MCP tool map (BTC paper UAT)

Prefer tools exposed by the `readytrader-crypto` MCP server. Exact Hermes names may be prefixed (`mcp_…`).

## Always safe (read / paper)

| Tool | Purpose |
|------|---------|
| `get_health` | Mode, halt, version |
| `get_metrics_snapshot` | Counters after activity |
| `get_crypto_price` | Spot price |
| `fetch_ohlcv` | Candles |
| `deposit_paper_funds` | Paper balance |
| `validate_trade_risk` | Risk Guardian check |
| Paper trade / portfolio helpers | Only when health says paper |

## Use with care (`approve_each`)

| Tool | Purpose |
|------|---------|
| `place_cex_order` | May return a **proposal** — do not confirm live |
| `list_pending_executions` | Inspect proposals |
| `confirm_execution` | **Forbidden** for live until Phase 4 dust UAT |

## Operator-only / deferred

- Unhalt (`TRADING_HALTED=false`)
- `LIVE_TRADING_ENABLED=true`
- Withdraw-capable CEX keys (must never be configured)

See ReadyTrader-Crypto [`docs/TOOLS.md`](https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/docs/TOOLS.md) for full signatures.
