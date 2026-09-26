# scripts/

## Purpose

Verification tooling for the skill package. `validate.py` is the single gate that keeps the
repo's claims aligned with Hermes' rules and ReadyTrader-Crypto's actual tools.

## Ownership

Owned by the root contract. CI (`.github/workflows/validate.yml`) runs `validate.py` on
push, pull request, and a weekly schedule so upstream drift is caught without a human.

## Local Contracts

- `validate.py --offline` must pass with no network (uses vendored `EXPECTED_TOOLS`)
- `validate.py` (online) fetches ReadyTrader-Crypto `docs/TOOLS.md`, `app/core/settings.py`, `env.example` from `main` and fails on drift; a fetch failure is a failure, not a warning
- `validate.py --live --rt-root <clone> --rt-python <interp>` launches `server.py` over MCP stdio and checks every tool behaviour `SKILL.md` relies on (numeric `get_crypto_price`; `validate_trade_risk` allowing 1% and refusing 20% of the portfolio in `data.result.allowed`; a price-less paper market order filled at the market price; keyless `get_news` answering no data; all 12 live-account tools refusing in paper mode), with the answers PR #20 introduced required once the server reports sizing on its paper fills; provider keys are blanked so a clone's `.env` cannot change the result; CI job `live-smoke` does this against upstream `main` on every push/PR and weekly
- Static scans judge only this repo's git-tracked files (rglob fallback skips nested repos/venvs) — CI checks out ReadyTrader-Crypto inside the workspace for `--live`, and that tree must never be scanned
- Hygiene fails on any tracked path under `SCRATCH_DIRS` (`.tmp/`, `tmp/`, `__pycache__/`, `.venv/`, `venv/`, `node_modules/`), on machine-specific paths, and on credential-shaped strings
- Every snake_case identifier in every `*.md` must be a registered tool, a `NON_TOOL_IDENTIFIERS` entry, or a `KNOWN_PHANTOMS` entry used only in a negated paragraph
- `--tools-md`, `--settings-py`, `--env-example` accept local copies for offline cross-checks
- Exit code 0 = pass, 1 = failures, 2 = missing dependency (PyYAML)

## Work Guidance

- When ReadyTrader-Crypto adds or removes an MCP tool, update `EXPECTED_TOOLS` and the tool tables in the same change
- When a new non-tool identifier appears in the docs, add it to `NON_TOOL_IDENTIFIERS` deliberately; never widen the regex instead
- Add a check here whenever a new class of defect is found in review; do not rely on prose rules alone
- Keep checks mirrored to the Hermes source they model (regexes copied from `tools/skills_hub.py` and `tests/skills/test_authoring_standards.py`) and note the origin in the docstring

## Verification

- `python3 scripts/validate.py --offline` and the online run both exit 0

## Child DOX Index

(none)
