# Changelog

All notable changes to this skill package. Versions track `version:` in
`skills/finance/readytrader-crypto/SKILL.md`.

## 1.1.1 — 2026-09-15

Doc sync for ReadyTrader-Crypto PR #7 (closes upstream issue #6), revision-qualified so the
skill stays correct against older checkouts:

- Paper `place_cex_order` with omitted/≤ 0 price now resolves via the market-data bus or
  fails `paper_price_required` (older revisions: silent `100000.0` placeholder fill).
- `get_cex_balance` is paper-safe from PR #7 (paper wallet view, no keys); moved out of the
  requires-credentials class in `tool-map.md`.
- `start_cex_private_ws` is halt/consent-gated from PR #7; `stop`/`list` deliberately stay
  available while halted (`tool-safety.md`).
- Pitfalls now point at PR #7 as the fix for the audit's issue-#6 defects.

## 1.1.0 — 2026-09-14

Audit against ReadyTrader-Crypto `main` and hermes-agent source; every claim re-verified by
launching the MCP server over stdio and by reading the Hermes loader/hub code.

### Fixed

- Removed four MCP tools that never existed (`get_health`, `get_metrics_snapshot`,
  `list_pending_executions`, `confirm_execution`); documented the HTTP-only equivalents.
- Tool-name convention corrected to `mcp__readytrader_crypto__<tool>` (Hermes sanitizes
  hyphens and uses a double-underscore delimiter).
- Entrypoint corrected to `server.py`; `python app/main.py` fails with
  `ModuleNotFoundError: No module named 'server'` on current main.
- Install instructions rewritten: Hermes loads `~/.hermes/skills/`, not a checkout's
  `optional-skills/`; added hub GitHub-source, hub URL, and manual-copy paths.
- `description` shortened to satisfy the Hermes 60-character hardline.
- `references/tool-map.md` is now referenced from `SKILL.md` so hub installs fetch it.
- `SKILL.md` no longer points at `docs/`, which is not part of the installed bundle.
- `approve_each` semantics documented truthfully (no proposals in paper mode; live path
  inert on current main); kill-switch scope documented (live path only).
- `DEV_MODE` defaults to `false` in the example (only `api_server.py` needs it).
- Recommended a dedicated venv and absolute interpreter path (`make setup` creates no venv).
- `docs/HERMES_INTEGRATION.md`: removed the `READYTRADER_ROOT` reference (`cwd` is the knob),
  smoke checklist made executable from the paper profile.
- Procedure takes the numeric price from `fetch_ohlcv` (`get_crypto_price` returns a sentence).
- Tool map corrected after adversarial review: `get_sentiment` is keyless, `swap_tokens` is
  paper-capable but out of scope, `transfer_eth` returns `paper_mode_not_supported`,
  private-WS tools bypass the halt flag, `ALLOW_*` allowlists apply to the live path only.
- Documented that ReadyTrader-Crypto `main` before PR #5 crashes on paper `place_cex_order`
  (`agent_id` TypeError) and that the agent must stop after the risk check on such revisions.

### Added

- Skill moved to `skills/finance/readytrader-crypto/` (Hermes `<category>/<name>` layout).
- `scripts/validate.py` and `.github/workflows/validate.yml`: static checks on every push, and a
  weekly `live-smoke` job that launches ReadyTrader-Crypto `main` over MCP stdio and runs the
  paper path. Online mode fails closed on fetch errors; phantom detection covers every
  snake_case identifier in every markdown file.
- Upstream: ReadyTrader-Crypto PR #5 (code + docs fixes) and issue #6 (live-safety gaps).
- Paper-mode pitfalls: placeholder `100000.0` fill when `price` is omitted; `get_cex_balance`
  needs real keys even in paper mode.
- `CHANGELOG.md`, `.gitignore`, `skills/AGENTS.md`, `scripts/AGENTS.md`.

## 1.0.0 — initial public release

- Initial Hermes skill for ReadyTrader BTC paper MCP.
