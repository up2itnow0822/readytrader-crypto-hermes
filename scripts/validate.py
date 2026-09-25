#!/usr/bin/env python3
"""Validate the readytrader-crypto-hermes skill package.

Checks (each maps to a rule Hermes or ReadyTrader-Crypto actually enforces):

  frontmatter   SKILL.md frontmatter: required fields, name == directory, name regex,
                description <= 60 chars ending in '.', no marketing words
                (hermes-agent tests/skills/test_authoring_standards.py,
                tools/skill_manager_tool.py::_validate_frontmatter).
  references    Every file under references/ is referenced from SKILL.md using the same
                regex the Hermes hub uses to decide which support files to download
                (tools/skills_hub.py::_referenced_support_paths); every referenced path exists.
  config        The mcp_servers YAML in docs/HERMES_INTEGRATION.md equals
                references/mcp-config.yaml (whole entry); paper-first flags are set;
                entrypoint is server.py; no credentials in the example.
  tools         Every snake_case identifier in backticks or code fences across every .md
                file is either a registered ReadyTrader tool, a known non-tool identifier,
                or a known phantom mentioned only in a negated sentence. The vendored
                EXPECTED_TOOLS list must match ReadyTrader-Crypto docs/TOOLS.md (fetched
                live unless --offline / --tools-md).
  env           Every env var in mcp-config.yaml is read by ReadyTrader-Crypto
                app/core/settings.py or listed in env.example (fetched live unless --offline).
  links         Relative markdown links resolve; absolute ReadyTrader-Crypto links resolve (online).
  hygiene       No machine-local paths, no credential-shaped strings, no legacy tool prefix,
                no tracked scratch (.tmp/, tmp/, __pycache__/, venvs).
  dox           Every AGENTS.md link points at an existing file.
  live          (--live) Launch ReadyTrader-Crypto server.py over MCP stdio with the
                mcp-config.yaml env, assert the 29-tool roster, and check every tool
                behaviour SKILL.md relies on: get_crypto_price carries a numeric data.price;
                deposit -> validate_trade_risk -> a paper market order sent WITHOUT a price
                fills at the market price; get_news without keys answers no data; the
                live-account tools refuse in the paper profile.

Online mode (the default) treats any upstream fetch failure as a failure so drift checks
cannot silently pass. Exit 0 when everything passes, 1 otherwise. Requires PyYAML.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "finance" / "readytrader-crypto"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"
MCP_CONFIG = REFERENCES / "mcp-config.yaml"
OPERATOR_DOC = ROOT / "docs" / "HERMES_INTEGRATION.md"

RT_RAW = "https://raw.githubusercontent.com/up2itnow0822/ReadyTrader-Crypto/main/"
RT_TOOLS_MD = RT_RAW + "docs/TOOLS.md"
RT_SETTINGS = RT_RAW + "app/core/settings.py"
RT_ENV_EXAMPLE = RT_RAW + "env.example"

# The 29 tools registered by ReadyTrader-Crypto server.py (verified 2026-09-14 by launching
# the server over MCP stdio and listing tools). Drift against upstream fails the run.
EXPECTED_TOOLS = {
    "cancel_all_cex_orders", "cancel_cex_order", "deposit_paper_funds", "fetch_ohlcv",
    "get_cex_balance", "get_cex_capabilities", "get_cex_my_trades", "get_cex_order",
    "get_crypto_price", "get_financial_news", "get_free_news", "get_latest_insights",
    "get_market_regime", "get_news", "get_sentiment", "get_social_sentiment",
    "list_cex_open_orders", "list_cex_orders", "list_cex_private_updates", "place_cex_order",
    "post_market_insight", "replace_cex_order", "run_backtest_simulation",
    "start_cex_private_ws", "stop_cex_private_ws", "swap_tokens", "transfer_eth",
    "validate_trade_risk", "wait_for_cex_order",
}
# Names earlier versions of this package (and upstream docs) invented. They may only appear
# in paragraphs that say they do not exist.
KNOWN_PHANTOMS = {
    "get_health", "get_metrics_snapshot", "get_metrics_prometheus", "list_pending_executions",
    "confirm_execution", "get_marketdata_status", "start_marketdata_ws", "stop_marketdata_ws",
}
# snake_case identifiers that legitimately appear in the docs and are not tools. Anything
# snake_case that is not a tool, not a phantom, and not listed here fails the run, so a new
# invented tool name cannot slip in without a conscious edit of this list.
NON_TOOL_IDENTIFIERS = {
    # ReadyTrader settings / concepts
    "paper_mode_not_supported", "approve_each", "agent_zero", "execute_trade", "agent_id",
    "user_id", "amount_usd", "portfolio_value", "market_type", "order_type", "strategy_code",
    "idempotency_key", "request_id", "confirm_token", "policy_engine", "paper_engine",
    "risk_config", "trading_halted", "live_enabled", "is_live_execution_allowed",
    "paper_price_required", "paper_engine_missing", "_require_live_allowed",
    "validate_cex_order", "marketdata_bus", "get_balances", "get_fear_greed_index",
    "api_server", "env_private_key", "cb_mpc_2pc", "ccxt_rest",
    # ReadyTrader answer codes the skill tells the agent how to handle
    "risk_blocked", "limit_not_marketable", "insufficient_funds", "not_configured", "source_unavailable", "cex_error",
    "allowed_while_halted",
    # Hermes config keys / modules
    "mcp_servers", "connect_timeout", "skills_hub", "mcp_tool", "skill_manager_tool",
    "test_authoring_standards", "skill_manage", "related_skills", "readytrader_crypto",
    # this repo / validator
    "validate_py", "tools_md", "settings_py", "env_example", "rt_root", "rt_python",
    "no_cache", "expected_tools", "node_modules",
}
REQUIRED_FM = ("name", "description", "version", "author", "license", "platforms")
VALID_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
MARKETING = re.compile(
    r"\b(powerful|comprehensive|seamless|revolutionary|cutting-edge|state-of-the-art)\b", re.I
)
MACHINE_LOCAL = re.compile(r"/home/(?!runner\b)[a-z0-9_-]+/|/Users/[A-Za-z0-9_-]+/|[A-Z]:\\+Users\\+(?!<)")
# Same expression as hermes-agent tools/skills_hub.py::_LOCAL_LINK_RE.
LOCAL_LINK_RE = re.compile(
    r"(?:\]\(|`|(?:^|[\s\"']))((?:references|templates|scripts|assets|examples)/[^\s)`\"'<>]+)",
    re.MULTILINE,
)
KNOWN_TOKEN_SHAPES = re.compile(
    r"\b(sk-[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]{10,})\b"
)
ASSIGNED_SECRET = re.compile(r"(?:API_KEY|API_SECRET|SECRET|TOKEN|PASSWORD)\s*[:=]\s*[\"']?([A-Za-z0-9+/=_-]{20,})")
PLACEHOLDER_WORDS = re.compile(r"your|replace|change|example|placeholder|here|dummy|xxx|set-this|todo|redacted|\.\.\.", re.I)
LEGACY_PREFIX = "mcp_readytrader-crypto_"
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
SNAKE_RE = re.compile(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b")
NEGATION_RE = re.compile(r"\b(no|not|never|do not|don't|nonexistent|phantom|invented)\b", re.I)

failures: list[str] = []
warnings: list[str] = []
ONLINE = True


def fail(msg: str) -> None:
    failures.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def fetch(url: str, timeout: int = 20) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (fixed https URLs)
            return resp.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        fail(f"online mode: could not fetch {url}: {exc} (use --offline to skip upstream checks)")
        return None


def head_ok(url: str, timeout: int = 20) -> bool | None:
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout):  # noqa: S310
            return True
    except urllib.error.HTTPError as exc:
        return exc.code < 400
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        fail(f"{path.name}: must start with ---")
        return {}, content
    m = re.search(r"\n---\s*\n", content[3:])
    if not m:
        fail(f"{path.name}: unclosed frontmatter")
        return {}, content
    fm = yaml.safe_load(content[3 : m.start() + 3])
    if not isinstance(fm, dict):
        fail(f"{path.name}: frontmatter must be a YAML mapping")
        return {}, content
    return fm, content


def check_frontmatter() -> None:
    fm, content = parse_frontmatter(SKILL_MD)
    if not fm:
        return
    missing = [f for f in REQUIRED_FM if f not in fm]
    if missing:
        fail(f"SKILL.md: missing frontmatter fields {missing}")
    hermes = (fm.get("metadata") or {}).get("hermes") or {}
    if not (hermes.get("tags") or fm.get("tags")):
        fail("SKILL.md: no tags (metadata.hermes.tags or top-level tags)")
    name = str(fm.get("name") or "")
    if name != SKILL_DIR.name:
        fail(f"SKILL.md: name {name!r} != directory {SKILL_DIR.name!r}")
    if not VALID_NAME_RE.match(name) or len(name) > 64:
        fail(f"SKILL.md: name {name!r} violates ^[a-z0-9][a-z0-9._-]*$ / 64 chars")
    desc = str(fm.get("description") or "")
    if len(desc) > 60:
        fail(f"SKILL.md: description is {len(desc)} chars (Hermes hardline 60)")
    if not desc.rstrip().endswith("."):
        fail("SKILL.md: description must end with a period")
    m = MARKETING.search(desc)
    if m:
        fail(f"SKILL.md: marketing word in description: {m.group(0)!r}")
    if "platforms" in fm and not isinstance(fm["platforms"], list):
        fail("SKILL.md: platforms must be a list")
    if len(content) > 100_000:
        fail("SKILL.md: exceeds 100k chars")
    if hermes.get("category") != "finance":
        warn("SKILL.md: metadata.hermes.category is not 'finance'")


def referenced_paths(text: str) -> set[str]:
    return {m.group(1).rstrip(".,;:") for m in LOCAL_LINK_RE.finditer(text.replace("\\", "/"))}


def check_references() -> None:
    text = SKILL_MD.read_text(encoding="utf-8")
    refs = {p for p in referenced_paths(text) if p.startswith("references/")}
    on_disk = {f"references/{p.relative_to(REFERENCES).as_posix()}" for p in REFERENCES.rglob("*") if p.is_file()}
    for missing in sorted(on_disk - refs):
        fail(f"SKILL.md never references {missing}; Hermes hub installs would drop it")
    for dangling in sorted(refs - on_disk):
        fail(f"SKILL.md references {dangling} but it does not exist")
    if "../" in text:
        fail("SKILL.md contains a parent-directory reference")
    if re.search(r"`docs/[^`]+`", text):
        fail("SKILL.md points at docs/, which is not part of the installed skill bundle")


def yaml_block(md: Path) -> dict | None:
    text = md.read_text(encoding="utf-8")
    m = re.search(r"```yaml\n(.*?)```", text, re.S)
    if not m:
        fail(f"{md.relative_to(ROOT)}: no ```yaml block found")
        return None
    return yaml.safe_load(m.group(1))


def check_config() -> dict | None:
    cfg = yaml.safe_load(MCP_CONFIG.read_text(encoding="utf-8")) or {}
    servers = cfg.get("mcp_servers") or {}
    entry = servers.get("readytrader-crypto")
    if not entry:
        fail("mcp-config.yaml: missing mcp_servers.readytrader-crypto")
        return None
    if set(servers) != {"readytrader-crypto"} or set(cfg) != {"mcp_servers"}:
        fail("mcp-config.yaml: must contain exactly mcp_servers.readytrader-crypto and nothing else")
    doc_cfg = yaml_block(OPERATOR_DOC)
    if doc_cfg is not None:
        doc_servers = doc_cfg.get("mcp_servers") or {}
        if set(doc_servers) != {"readytrader-crypto"}:
            fail("docs/HERMES_INTEGRATION.md: yaml block must define exactly mcp_servers.readytrader-crypto")
        if doc_servers.get("readytrader-crypto") != entry:
            fail("docs/HERMES_INTEGRATION.md mcp_servers.readytrader-crypto != references/mcp-config.yaml (whole entry)")
    env = entry.get("env") or {}
    for k, v in {"PAPER_MODE": "true", "LIVE_TRADING_ENABLED": "false", "TRADING_HALTED": "true"}.items():
        if str(env.get(k)).lower() != v:
            fail(f"mcp-config.yaml: {k} must be \"{v}\" (paper-first, fail-closed)")
    if entry.get("args") != ["server.py"]:
        fail("mcp-config.yaml: args must be [server.py]; `python app/main.py` failed before ReadyTrader-Crypto PR #5")
    if "readytrader-crypto" not in str(entry.get("cwd", "")).lower():
        warn("mcp-config.yaml: cwd does not look like a ReadyTrader-Crypto clone path")
    for name in env:
        if any(s in name.upper() for s in ("API_KEY", "API_SECRET", "PASSWORD", "TOKEN")):
            fail(f"mcp-config.yaml: credential-like env var {name} present in the paper example")
    return entry


def tracked_files() -> list[Path]:
    """This repository's own files, and nothing else.

    Static checks must never judge a nested checkout (CI clones ReadyTrader-Crypto
    into the workspace for --live, venv included) — git-tracked files are the
    authoritative universe. Fallback for non-git contexts: rglob, skipping any
    directory that is itself a repo or a virtualenv.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            capture_output=True, text=True, check=True, timeout=30,
        ).stdout
        return sorted(p for p in (ROOT / name for name in out.split("\0") if name) if p.is_file())
    except Exception:
        def foreign(p: Path) -> bool:
            for parent in p.parents:
                if parent == ROOT:
                    return False
                if (parent / ".git").exists() or (parent / "pyvenv.cfg").exists():
                    return True
            return False
        return sorted(p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and not foreign(p))


def markdown_files() -> dict[Path, str]:
    files = [p for p in tracked_files() if p.suffix == ".md"]
    return {p: p.read_text(encoding="utf-8") for p in files}


def snake_identifiers(text: str) -> set[str]:
    """snake_case identifiers inside inline code spans and fenced blocks."""
    spans = INLINE_CODE_RE.findall(text) + FENCE_RE.findall(text)
    names: set[str] = set()
    for span in spans:
        span = span.replace("mcp__readytrader_crypto__", " ")
        names.update(SNAKE_RE.findall(span))
    return names


def check_tools(tools_md: str | None) -> None:
    upstream: set[str] | None = None
    if tools_md is not None:
        upstream = set(re.findall(r"^### `([a-z_]+)`", tools_md, re.M))
        if upstream != EXPECTED_TOOLS:
            fail(
                "EXPECTED_TOOLS drifted from ReadyTrader-Crypto docs/TOOLS.md: "
                f"missing upstream={sorted(EXPECTED_TOOLS - upstream)} new upstream={sorted(upstream - EXPECTED_TOOLS)}"
            )
    for path, text in markdown_files().items():
        rel = path.relative_to(ROOT)
        if LEGACY_PREFIX in text:
            fail(f"{rel}: legacy tool prefix {LEGACY_PREFIX!r}; Hermes uses mcp__readytrader_crypto__")
        for name in sorted(snake_identifiers(text)):
            if name in EXPECTED_TOOLS or name in NON_TOOL_IDENTIFIERS:
                continue
            if name in KNOWN_PHANTOMS:
                for para in re.split(r"\n\s*\n", text):
                    if re.search(rf"`[^`\n]*\b{name}\b[^`\n]*`", para) and not NEGATION_RE.search(para):
                        fail(f"{rel}: phantom tool `{name}` mentioned without negation: {para.strip()[:90]!r}")
                continue
            fail(f"{rel}: `{name}` is not a registered ReadyTrader tool; if it is not a tool name, add it to NON_TOOL_IDENTIFIERS")


def check_env(entry: dict | None, settings_py: str | None, env_example: str | None) -> None:
    if entry is None or (settings_py is None and env_example is None):
        return
    known: set[str] = set()
    if settings_py:
        known |= set(re.findall(r'os\.getenv\(\s*"([A-Z0-9_]+)"', settings_py))
        known |= set(re.findall(r'os\.environ\.get\(\s*"([A-Z0-9_]+)"', settings_py))
    if env_example:
        known |= set(re.findall(r"^#?\s*([A-Z][A-Z0-9_]+)=", env_example, re.M))
    for name in (entry.get("env") or {}):
        if name not in known:
            fail(f"mcp-config.yaml: env var {name} is not read by ReadyTrader-Crypto settings.py/env.example")


def check_links() -> None:
    for path, text in markdown_files().items():
        rel = path.relative_to(ROOT)
        for target in MD_LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                if ONLINE and target.startswith("https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/"):
                    raw = target.replace("https://github.com/up2itnow0822/ReadyTrader-Crypto/blob/main/", RT_RAW)
                    ok = head_ok(raw)
                    if ok is False:
                        fail(f"{rel}: upstream link 404: {target}")
                    elif ok is None:
                        fail(f"{rel}: online mode: could not verify {target}")
                continue
            local = (path.parent / target.split("#", 1)[0]).resolve()
            if not local.exists():
                fail(f"{rel}: broken relative link {target}")


def credential_hits(text: str) -> list[str]:
    hits = [m.group(0) for m in KNOWN_TOKEN_SHAPES.finditer(text)]
    for m in ASSIGNED_SECRET.finditer(text):
        value = m.group(1)
        has_letters = re.search(r"[A-Za-z]", value) is not None
        has_digits = re.search(r"[0-9]", value) is not None
        if has_letters and has_digits and not PLACEHOLDER_WORDS.search(value):
            hits.append(m.group(0))
    return hits


SCRATCH_DIRS = {".tmp", "tmp", "__pycache__", ".venv", "venv", "node_modules"}


def check_hygiene() -> None:
    this = Path(__file__).resolve()
    for path in tracked_files():
        rel_parts = path.relative_to(ROOT).parts
        if rel_parts and rel_parts[0] in SCRATCH_DIRS:
            fail(f"{path.relative_to(ROOT)}: scratch/tooling output is tracked; keep {rel_parts[0]}/ out of the repo (see .gitignore)")
            continue
        if path.suffix not in {".md", ".yaml", ".yml", ".py", ".txt"} or path == this:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT)
        m = MACHINE_LOCAL.search(text)
        if m:
            fail(f"{rel}: machine-local path {m.group(0)!r}")
        for hit in credential_hits(text):
            fail(f"{rel}: credential-shaped string {hit[:40]!r}")


def check_dox() -> None:
    for agents in (p for p in tracked_files() if p.name == "AGENTS.md"):
        for target in MD_LINK_RE.findall(agents.read_text(encoding="utf-8")):
            if target.startswith(("http", "#")):
                continue
            if not (agents.parent / target).exists():
                fail(f"{agents.relative_to(ROOT)}: link {target} does not exist")


LIVE_CLIENT = r'''
import asyncio, json, os, sys
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
cfg = json.loads(sys.argv[1]); rt_root = sys.argv[2]; expected = set(json.loads(sys.argv[3]))
env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
env.update({k: str(v) for k, v in (cfg.get("env") or {}).items()})
for k in ("PAPER_DB_PATH", "AUDIT_DB_PATH", "IDEMPOTENCY_DB_PATH", "EXECUTION_DB_PATH", "INSIGHT_DB_PATH", "STRATEGY_DB_PATH"):
    env[k] = os.path.join(sys.argv[4], k.lower() + ".db")
def txt(r): return "".join(getattr(c, "text", "") for c in r.content)
async def main():
    out = {}
    async with Client(StdioTransport(command=sys.executable, args=list(cfg["args"]), cwd=rt_root, env=env)) as c:
        names = {t.name for t in await c.list_tools()}
        out["missing"] = sorted(expected - names); out["extra"] = sorted(names - expected)
        r = json.loads(txt(await c.call_tool("get_crypto_price", {"symbol": "BTC/USDT"})))
        price = (r.get("data") or {}).get("price")
        out["price"] = price if isinstance(price, (int, float)) and not isinstance(price, bool) else None
        out["price_answer"] = json.dumps(r)[:300]
        r = json.loads(txt(await c.call_tool("deposit_paper_funds", {"asset": "USDT", "amount": 10000.0})))
        out["deposit_ok"] = bool(r.get("ok"))
        r = json.loads(txt(await c.call_tool("validate_trade_risk", {"side": "buy", "symbol": "BTC/USDT", "amount_usd": 100.0, "portfolio_value": 10000.0})))
        out["risk_ok"] = bool(r.get("ok"))
        try:
            # The Procedure's order: a market order with no price; the server must fill it at its market price.
            r = json.loads(txt(await c.call_tool("place_cex_order", {"symbol": "BTC/USDT", "side": "buy", "amount": 0.001, "order_type": "market"})))
            data = r.get("data") or {}
            out["order_mode"] = data.get("mode"); out["order_ok"] = bool(r.get("ok"))
            out["fill_price"] = (data.get("fill") or {}).get("price"); out["order_answer"] = json.dumps(r)[:300]
        except Exception as exc:
            out["order_ok"] = False; out["order_error"] = str(exc)[:300]
        r = json.loads(txt(await c.call_tool("get_news", {})))
        out["news"] = {"ok": bool(r.get("ok")), "code": (r.get("error") or {}).get("code"), "text": json.dumps(r.get("data"))[:300]}
        r = json.loads(txt(await c.call_tool("list_cex_open_orders", {})))
        out["account"] = {"ok": bool(r.get("ok")), "code": (r.get("error") or {}).get("code")}
    print(json.dumps(out))
asyncio.run(main())
'''


def check_live(rt_root: Path, rt_python: Path, entry: dict | None, tmp: Path) -> None:
    if entry is None:
        return
    if not (rt_root / "server.py").exists():
        fail(f"--live: {rt_root} has no server.py")
        return
    tmp.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [str(rt_python), "-c", LIVE_CLIENT, json.dumps(entry), str(rt_root), json.dumps(sorted(EXPECTED_TOOLS)), str(tmp)],
        capture_output=True, text=True, timeout=240,
    )
    if proc.returncode != 0:
        fail(f"--live: MCP client failed: {proc.stderr.strip()[-400:]}")
        return
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    if out["missing"] or out["extra"]:
        fail(f"--live: tool roster drift: missing={out['missing']} extra={out['extra']}")
    if not out["deposit_ok"]:
        fail("--live: deposit_paper_funds failed")
    if not out["risk_ok"]:
        fail("--live: validate_trade_risk failed")
    price = out.get("price")
    if not price or price <= 0:
        fail(f"--live: get_crypto_price has no positive numeric data.price (SKILL.md Procedure step 2): {out.get('price_answer')}")
    if not out.get("order_ok") or out.get("order_mode") != "paper":
        fail(f"--live: paper place_cex_order (market, no price) failed: {out.get('order_error') or out.get('order_answer')}")
    elif price and price > 0:
        fill = out.get("fill_price")
        if not isinstance(fill, (int, float)) or abs(fill - price) / price > 0.05:
            fail(f"--live: paper market order did not fill at the market price (market {price}, fill {fill})")
    news = out.get("news") or {}
    keyless_no_data = (not news.get("ok") and news.get("code") == "not_configured") or (
        news.get("ok") and "not configured" in (news.get("text") or "").lower()  # before ReadyTrader-Crypto PR #20
    )
    if not keyless_no_data:
        fail(f"--live: get_news without keys should answer no data (not_configured): {news}")
    if (out.get("account") or {}).get("ok"):
        fail(f"--live: list_cex_open_orders answered ok in the paper profile; the docs say live-account tools refuse: {out.get('account')}")


def main() -> int:
    global ONLINE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip every network fetch")
    ap.add_argument("--tools-md", type=Path, help="local ReadyTrader-Crypto docs/TOOLS.md to use instead of fetching")
    ap.add_argument("--settings-py", type=Path, help="local ReadyTrader-Crypto app/core/settings.py")
    ap.add_argument("--env-example", type=Path, help="local ReadyTrader-Crypto env.example")
    ap.add_argument("--live", action="store_true", help="launch ReadyTrader-Crypto over MCP stdio and run the paper path")
    ap.add_argument("--rt-root", type=Path, help="ReadyTrader-Crypto clone (required with --live)")
    ap.add_argument("--rt-python", type=Path, help="interpreter with ReadyTrader deps + fastmcp (required with --live)")
    ap.add_argument("--tmp", type=Path, default=Path("/tmp/readytrader-crypto-hermes-live"), help="scratch dir for --live SQLite state")
    args = ap.parse_args()
    ONLINE = not args.offline

    tools_md = args.tools_md.read_text(encoding="utf-8") if args.tools_md else (None if args.offline else fetch(RT_TOOLS_MD))
    settings_py = args.settings_py.read_text(encoding="utf-8") if args.settings_py else (None if args.offline else fetch(RT_SETTINGS))
    env_example = args.env_example.read_text(encoding="utf-8") if args.env_example else (None if args.offline else fetch(RT_ENV_EXAMPLE))

    check_frontmatter()
    check_references()
    entry = check_config()
    check_tools(tools_md)
    check_env(entry, settings_py, env_example)
    check_links()
    check_hygiene()
    check_dox()
    if args.live:
        if not (args.rt_root and args.rt_python):
            fail("--live requires --rt-root and --rt-python")
        else:
            check_live(args.rt_root.absolute(), args.rt_python.absolute(), entry, args.tmp)

    for w in warnings:
        print(f"WARN  {w}")
    for f in failures:
        print(f"FAIL  {f}")
    if failures:
        print(f"\n{len(failures)} failure(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK    all checks passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
