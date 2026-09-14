# ReadyTrader MCP tool safety (pre–Phase 4)

## Prefer (paper / read)

- Health and metrics tools
- Market data: price, OHLCV, sentiment (read-only)
- Paper deposit / paper trade / portfolio tools
- `validate_trade_risk`

## Block without Phase 4 authorization

- Live `place_cex_order` / cancel / replace when not in paper mode
- Confirming live execution proposals (`confirm_execution`) with real funds
- Enabling `LIVE_TRADING_ENABLED`, disabling `PAPER_MODE`, or clearing `TRADING_HALTED`
- On-chain live swaps / transfers with production signer

## Operator-only

- Editing allowlists, max sizes, JWT/admin secrets
- Pointing MCP at `docker-compose.live.yml` stack
