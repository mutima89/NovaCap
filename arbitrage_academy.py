#!/usr/bin/env python3
"""
================================================================================
  PRINCIPAL STRATEGIST — 90-Day FinTech Arbitrage Training Simulator
  Role: FinTech Arbitrage Specialist (Trainee)
  Firm: NovaCap Financial Technologies Ltd.
  Standards: CMA & SOCPA Financial Compliance

  This master simulation engine runs a 90-day rigorous training curriculum
  for algorithmic arbitrage trading. It combines a file-based workspace
  manager, local mock exchange server, SQLite ledger engine, AST code
  auditor, and ruthless evaluation protocol in a single executable script.

  Usage:
      python arbitrage_academy.py

  Requirements: Python 3.8+ (standard library only — no pip deps)
================================================================================
"""

import cmd
import json
import math
import os
import re
import sys
import textwrap
import time
import threading
import sqlite3
import ast
import subprocess
import random
import io
import signal
import traceback
import shutil
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse, parse_qs
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

__version__ = "2.0.0"
__author__ = "Principal Strategist — NovaCap Financial Technologies Ltd."


# ==============================================================================
# SECTION 1 — ANSI COLOR UTILITIES & PRINCIPAL STRATEGIST PERSONA
# ==============================================================================

class Color:
    """Terminal ANSI escape codes — clinical, high-contrast palette."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_DARK_GRAY = "\033[100m"

    # Clinical persona palette
    FAIL = f"{BOLD}{BRIGHT_RED}{BG_RED}"
    PASS = f"{BOLD}{BRIGHT_GREEN}"
    WARN = f"{BOLD}{BRIGHT_YELLOW}"
    INFO = f"{BRIGHT_CYAN}"
    CLINICAL = f"{BOLD}{BRIGHT_WHITE}"
    MUTED = f"{GRAY}"
    SYSTEM = f"{BRIGHT_MAGENTA}"
    HEADER = f"{BOLD}{BRIGHT_CYAN}"

    @staticmethod
    def supports_color() -> bool:
        if not sys.stdout.isatty():
            return False
        return True

    @classmethod
    def strip(cls, text: str) -> str:
        return re.sub(r"\033\[[0-9;]*m", "", text)


_USE_COLOR = Color.supports_color()


def c(code: str, text: str) -> str:
    """Apply ANSI color if supported."""
    return f"{code}{text}{Color.RESET}" if _USE_COLOR else text


def clinical(text: str) -> str:
    """Clinical white / bold."""
    return c(Color.CLINICAL, text)


def fail(text: str) -> str:
    """Failure red with background."""
    return c(Color.FAIL, text)


def pass_text(text: str) -> str:
    """Pass green."""
    return c(Color.PASS, text)


def warn(text: str) -> str:
    """Warning yellow."""
    return c(Color.WARN, text)


def info(text: str) -> str:
    """Info cyan."""
    return c(Color.INFO, text)


def muted(text: str) -> str:
    """Dim gray."""
    return c(Color.MUTED, text)


def header(text: str) -> str:
    """Header bright cyan bold."""
    return c(Color.HEADER, text)


class BoxChars:
    """Box-drawing chars with ASCII fallback."""
    _uni = True
    try:
        "\u2502".encode(sys.stdout.encoding or "utf-8")
    except (UnicodeEncodeError, AttributeError):
        _uni = False

    if _uni:
        H = "\u2500"
        V = "\u2502"
        TL = "\u250c"
        TR = "\u2510"
        ML = "\u251c"
        MR = "\u2524"
        BL = "\u2514"
        BR = "\u2518"
        H2 = "\u2550"
        V2 = "\u2551"
        TL2 = "\u2554"
        TR2 = "\u2557"
        BL2 = "\u255a"
        BR2 = "\u255d"
        BULLET = "\u25b8"
        CHECK = "\u2713"
        CROSS = "\u2717"
        DASH = "\u2500"
        ARROW = "\u2192"
    else:
        H = "-"; V = "|"; TL = "+"; TR = "+"; ML = "+"; MR = "+"
        BL = "+"; BR = "+"; H2 = "="; V2 = "|"
        TL2 = "+"; TR2 = "+"; BL2 = "+"; BR2 = "+"
        BULLET = ">"; CHECK = "v"; CROSS = "x"; DASH = "-"; ARROW = "->"


# ==============================================================================
# PRINCIPAL STRATEGIST — The Harsh Persona
# ==============================================================================

class PrincipalStrategist:
    """
    The Principal Strategist communicates with clinical detachment.
    Zero praise. Zero encouragement. Only objective analysis of logical
    flaws, algorithmic latency, and variance from accounting standards.
    """

    TITLE = "Principal Strategist — NovaCap Financial Technologies"
    CALLSIGN = "Strategist"

    @staticmethod
    def _banner() -> str:
        Bc = BoxChars
        lines = [
            "",
            c(Color.BRIGHT_CYAN, f"{Bc.TL2}{Bc.H2 * 74}{Bc.TR2}"),
            c(Color.BRIGHT_CYAN, f"{Bc.V2}") + " " * 74 + c(Color.BRIGHT_CYAN, f"{Bc.V2}"),
            c(Color.BRIGHT_CYAN, f"{Bc.V2}") + f"  {c(Color.BRIGHT_WHITE, 'PRINCIPAL STRATEGIST')}" + " " * 49 + c(Color.BRIGHT_CYAN, f"{Bc.V2}"),
            c(Color.BRIGHT_CYAN, f"{Bc.V2}") + f"  {c(Color.GRAY, 'NovaCap Financial Technologies Ltd. — 90-Day Arbitrage Protocol')}" + " " * 13 + c(Color.BRIGHT_CYAN, f"{Bc.V2}"),
            c(Color.BRIGHT_CYAN, f"{Bc.V2}") + " " * 74 + c(Color.BRIGHT_CYAN, f"{Bc.V2}"),
            c(Color.BRIGHT_CYAN, f"{Bc.BL2}{Bc.H2 * 74}{Bc.BR2}"),
            "",
        ]
        return "\n".join(lines)

    @staticmethod
    def morning_briefing(day: int, phase: int) -> str:
        phase_names = {
            1: "DATA INGESTION & FOUNDATIONAL RISK MATH",
            2: "ALGORITHMIC ARBITRAGE LOGIC & API EXECUTION",
            3: "MARKET SLIPPAGE, LATENCY & SOCPA COMPLIANCE",
        }
        pname = phase_names.get(phase, "UNKNOWN PHASE")
        lines = [
            "",
            header("=" * 76),
            header(f"  DAY {day} — PHASE {phase}: {pname}"),
            header("=" * 76),
            muted(f"  Simulation Date: {datetime.date.today().isoformat()}"),
            muted(f"  Standards: CMA | SOCPA | IFRS"),
            "",
        ]
        return "\n".join(lines)

    @staticmethod
    def evaluate_results_text(score: int, max_score: int, violations: List[str],
                               ast_issues: List[str], ledger_ok: bool) -> str:
        pct = (score / max_score * 100) if max_score > 0 else 0
        passed = score >= max_score  # Must be 100% to pass

        Bc = BoxChars
        lines = [
            "",
            header(f"{Bc.H2 * 76}"),
            header(f"  END-OF-DAY EVALUATION — VARIANCE REPORT"),
            header(f"{Bc.H2 * 76}"),
            "",
            f"  Score: {c(Color.BRIGHT_WHITE if passed else Color.FAIL, f'{score}/{max_score}')} "
            f"({c(Color.BRIGHT_GREEN if passed else Color.BRIGHT_RED, f'{pct:.1f}%')})",
            f"  Status: {c(Color.BRIGHT_GREEN if passed else Color.BRIGHT_RED, 'PASS' if passed else 'FAIL')}",
            "",
        ]

        if violations:
            lines.append(f"  {c(Color.FAIL, 'CRITICAL VIOLATIONS:')}")
            for v in violations:
                lines.append(f"    {c(Color.BRIGHT_RED, Bc.CROSS)} {v}")
            lines.append("")

        if ast_issues:
            lines.append(f"  {c(Color.WARN, 'CODE QUALITY ISSUES (AST Audit):')}")
            for a in ast_issues:
                lines.append(f"    {c(Color.YELLOW, Bc.BULLET)} {a}")
            lines.append("")

        if not ledger_ok:
            lines.append(f"  {c(Color.FAIL, 'LEDGER INTEGRITY: FAILED')}")
            lines.append(f"    {c(Color.BRIGHT_RED, 'Double-entry bookkeeping violation detected.')}")
            lines.append(f"    {c(Color.BRIGHT_RED, 'Ledger does not balance. Potential fraud risk.')}")
            lines.append("")

        if not passed:
            lines.append(f"  {c(Color.FAIL, 'VERDICT:')} Score below 100. Advancement denied.")
            lines.append(f"  {c(Color.FAIL, 'You will repeat Day {day} until all criteria are met.')}")
            consequences = PrincipalStrategist._get_failure_consequences(violations)
            if consequences:
                lines.append("")
                lines.append(f"  {c(Color.WARN, 'REAL-WORLD CONSEQUENCES:')}")
                for cns in consequences:
                    lines.append(f"    {c(Color.YELLOW, Bc.BULLET)} {cns}")
        else:
            lines.append(f"  {c(Color.BRIGHT_GREEN, 'VERDICT:')} All criteria satisfied. Advancing to next day.")
            lines.append(f"  {c(Color.BRIGHT_GREEN, 'Maintain this standard.')}")
            lines.append(f"  {c(Color.MUTED, 'Note: This is the expected baseline. No exceptional credit given.')}")

        lines.append("")
        lines.append(header(f"{Bc.H2 * 76}"))
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _get_failure_consequences(violations: List[str]) -> List[str]:
        mapping = {
            "network": "Unhandled network exceptions in production would cause incomplete trade "
                       "settlements, counterparty disputes, and potential exchange-imposed trading bans.",
            "complexity": "O(n^2) algorithms on order book data cause microsecond-scale latency. At "
                          "NovaCap's volume, this translates to $40K+ in missed arbitrage opportunities per millisecond.",
            "ledger": "Ledger reconciliation failures indicate breakdown in internal controls. Under "
                      "SOCPA Article 23, this constitutes a reportable material weakness.",
            "eval": "Use of eval()/exec() in trading code is an immediate security violation. "
                    "This exposes the firm to code injection attacks on trading infrastructure.",
            "try-except": "Missing exception handling on network calls (PEP 8 E722 violation). "
                          "A single unhandled ConnectionError during market volatility "
                          "causes the entire trading engine to halt with no fallback.",
            "division": "Unchecked division by zero. In low-liquidity scenarios, volume-weighted "
                        "average price calculations will produce NaN values, corrupting the entire P&L.",
        }
        results = []
        for v in violations:
            for key, msg in mapping.items():
                if key in v.lower():
                    results.append(msg)
                    break
            else:
                results.append(f"Protocol violation: {v}")
        return results

    @staticmethod
    def observation(text: str) -> str:
        """Clinical observation — no sugarcoating."""
        return f"  {c(Color.CLINICAL, 'OBSERVATION:')} {muted(text)}"

    @staticmethod
    def directive(text: str) -> str:
        """Direct command — not a suggestion."""
        return f"  {c(Color.BRIGHT_YELLOW, 'DIRECTIVE:')} {clinical(text)}"


# ==============================================================================
# SECTION 2 — MOCK EXCHANGE SERVER
# ==============================================================================

class RegimeConfig:
    """Configuration for a market regime."""

    def __init__(
        self,
        name: str,
        volatility: float,
        mean_reversion_strength: float,
        trend_bias: float,
        spread_multiplier: float,
        jump_intensity: float,
        jump_scale: float,
        depth: int,
        description: str = "",
    ):
        self.name = name
        self.volatility = volatility
        self.mean_reversion_strength = mean_reversion_strength
        self.trend_bias = trend_bias
        self.spread_multiplier = spread_multiplier
        self.jump_intensity = jump_intensity
        self.jump_scale = jump_scale
        self.depth = depth
        self.description = description


REGIMES: Dict[int, RegimeConfig] = {
    0: RegimeConfig(
        name="LOW_VOL_TRENDING",
        volatility=0.003,
        mean_reversion_strength=0.002,
        trend_bias=0.0004,
        spread_multiplier=0.8,
        jump_intensity=0.002,
        jump_scale=0.005,
        depth=12,
        description="Low volatility with mild positive drift. Tight spreads, deep book.",
    ),
    1: RegimeConfig(
        name="HIGH_VOL_MEAN_REVERTING",
        volatility=0.025,
        mean_reversion_strength=0.08,
        trend_bias=-0.0001,
        spread_multiplier=1.8,
        jump_intensity=0.015,
        jump_scale=0.04,
        depth=6,
        description="High volatility mean-reverting. Wide spreads, shallow book, frequent jumps.",
    ),
}


class MockPriceGenerator:
    """
    Two-state regime-switching price generator with jump diffusion.

    Regime 0 — Low-vol trending (tight spreads, deep book, mild drift)
    Regime 1 — High-vol mean-reverting (wide spreads, shallow book, jumps)
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.base_prices = {
            "BTC/USD": 67800.0,
            "ETH/USD": 3125.0,
            "BTC/USDT": 67850.0,
            "ETH/USDT": 3128.0,
            "SOL/USD": 142.0,
            "AVAX/USDT": 35.0,
            "LINK/USD": 14.5,
        }
        self.base_spreads = {
            "BTC/USD": 0.0015,
            "ETH/USD": 0.0025,
            "BTC/USDT": 0.0015,
            "ETH/USDT": 0.0025,
            "SOL/USD": 0.004,
            "AVAX/USDT": 0.005,
            "LINK/USD": 0.006,
        }
        self.prices: Dict[str, float] = dict(self.base_prices)
        self.tick = 0
        self.current_regime: int = 0
        self.regime_duration = 0
        self.max_regime_duration = self.rng.randint(30, 80)
        self.price_history: Dict[str, List[float]] = {s: [] for s in self.prices}
        self.order_book: Dict[str, Dict[str, Any]] = {}
        self.limit_orders: List[Dict[str, Any]] = []
        self.order_id_counter = 0

    def _maybe_switch_regime(self) -> None:
        """Transition between regimes via 2-state Markov chain."""
        self.regime_duration += 1
        if self.regime_duration < self.max_regime_duration:
            return
        p_stay = 0.85 if self.current_regime == 0 else 0.70
        if self.rng.random() > p_stay:
            self.current_regime = 1 - self.current_regime
            self.regime_duration = 0
            self.max_regime_duration = self.rng.randint(20, 100)

    def _apply_jump(self, sym: str, cfg: RegimeConfig) -> float:
        """Poisson jump process — returns multiplicative shock."""
        if self.rng.random() < cfg.jump_intensity:
            direction = 1 if self.rng.random() > 0.5 else -1
            return 1.0 + direction * self.rng.expovariate(1.0 / cfg.jump_scale)
        return 1.0

    def update(self) -> None:
        """Advance one tick with regime-appropriate dynamics."""
        self.tick += 1
        self._maybe_switch_regime()
        cfg = REGIMES[self.current_regime]

        for sym in self.prices:
            base = self.base_prices.get(sym, 100.0)
            ret = self.rng.gauss(cfg.trend_bias, cfg.volatility)

            # Mean reversion toward base
            reversion = cfg.mean_reversion_strength * (base - self.prices[sym]) / base

            # Jump component
            jump = self._apply_jump(sym, cfg)

            self.prices[sym] *= (1 + ret + reversion) * jump
            self.prices[sym] = max(self.prices[sym], base * 0.1)  # floor

            # Store history
            self.price_history[sym].append(self.prices[sym])
            if len(self.price_history[sym]) > 100:
                self.price_history[sym].pop(0)

    def _build_order_book(self, symbol: str) -> Dict[str, Any]:
        """Generate L2 order book from current price and regime."""
        mid = self.prices.get(symbol, 100.0)
        cfg = REGIMES[self.current_regime]
        base_spread_pct = self.base_spreads.get(symbol, 0.002)
        spread_pct = base_spread_pct * cfg.spread_multiplier
        half_spread = mid * spread_pct / 2

        bid = mid - half_spread + self.rng.gauss(0, half_spread * 0.1)
        ask = mid + half_spread + self.rng.gauss(0, half_spread * 0.1)

        depth = cfg.depth
        bids, asks = [], []
        for i in range(depth):
            decay = 1 - i / (depth * 1.5)
            qty = self.rng.uniform(0.3, 40) * max(0.1, decay)
            px_bid = bid * (1 - i * spread_pct * 0.3 * cfg.spread_multiplier)
            px_ask = ask * (1 + i * spread_pct * 0.3 * cfg.spread_multiplier)
            bids.append({"price": round(px_bid, 2), "quantity": round(qty, 4)})
            asks.append({"price": round(px_ask, 2), "quantity": round(qty, 4)})

        ob = {
            "symbol": symbol,
            "exchange": "PRIMARY",
            "timestamp": datetime.datetime.now().isoformat(),
            "tick": self.tick,
            "regime": self.current_regime,
            "regime_name": cfg.name,
            "mid": round(mid, 2),
            "spread": round(ask - bid, 2),
            "spread_bps": round((ask - bid) / mid * 10000, 1),
            "bids": bids,
            "asks": asks,
        }
        self.order_book[symbol] = ob
        return ob

    def get_orderbook(self, symbol: str, exchange: str = "PRIMARY") -> Dict[str, Any]:
        return self._build_order_book(symbol)

    def estimate_slippage_bps(self, symbol: str, quantity: float, side: str) -> float:
        """Estimate slippage in bps based on order book depth."""
        ob = self.order_book.get(symbol)
        if not ob:
            return 0.0
        levels = ob["asks"] if side == "buy" else ob["bids"]
        mid = ob["mid"]
        remaining = abs(quantity)
        total_cost = 0.0
        for level in levels:
            if remaining <= 0:
                break
            fill = min(remaining, level["quantity"])
            total_cost += fill * level["price"]
            remaining -= fill
        if remaining > 0:
            total_cost += remaining * mid * 1.05  # slippage beyond book
        avg_price = total_cost / abs(quantity) if quantity != 0 else mid
        expected_price = mid * (1 + 0.5 * self.base_spreads.get(symbol, 0.002))
        slippage_bps = (avg_price - expected_price) / expected_price * 10000 if expected_price > 0 else 0
        return abs(round(slippage_bps, 2))

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker with 24h stats."""
        mid = self.prices.get(symbol, 100.0)
        hist = self.price_history.get(symbol, [])
        change_24h = ((mid / hist[0]) - 1) * 100 if len(hist) > 1 else self.rng.uniform(-3, 3)
        vol_24h = self.rng.uniform(1000, 50000) * (2 if self.current_regime == 1 else 1)
        return {
            "symbol": symbol,
            "price": round(mid, 2),
            "change_24h_pct": round(change_24h, 2),
            "volume_24h": round(vol_24h, 2),
            "regime": self.current_regime,
            "regime_name": REGIMES[self.current_regime].name,
            "timestamp": datetime.datetime.now().isoformat(),
        }


class OrderBookManager:
    """
    Maintains limit order queues and matches against market orders.
    Supports GTC, IOC, and FOK order types with partial fills.
    """

    def __init__(self):
        self.buy_orders: List[Dict[str, Any]] = []  # price-desc priority
        self.sell_orders: List[Dict[str, Any]] = []  # price-asc priority
        self.order_id_counter = 0

    def _gen_order_id(self) -> str:
        self.order_id_counter += 1
        return f"ORD-{int(time.time() * 1000)}-{self.order_id_counter}"

    def add_limit_order(self, order: Dict[str, Any]) -> str:
        """Insert a limit order into the book. Returns order_id."""
        oid = self._gen_order_id()
        order["order_id"] = oid
        order["filled_qty"] = 0.0
        order["status"] = "open"
        order["created_at"] = datetime.datetime.now().isoformat()
        if order["side"] == "buy":
            self.buy_orders.append(order)
            self.buy_orders.sort(key=lambda x: (-x["price"], x.get("created_at", "")))
        else:
            self.sell_orders.append(order)
            self.sell_orders.sort(key=lambda x: (x["price"], x.get("created_at", "")))
        return oid

    def match_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """
        Match a market order against the limit book.
        Returns execution report with potential partial fills.
        """
        fills = []
        remaining = quantity
        book = self.sell_orders if side == "buy" else self.buy_orders

        # Iterate a copy since we modify in place
        matched_ids = []
        for order in book:
            if remaining <= 0:
                break
            if order["symbol"] != symbol:
                continue
            available = order["quantity"] - order["filled_qty"]
            if available <= 0:
                matched_ids.append(order["order_id"])
                continue
            fill_qty = min(remaining, available)
            fill_price = order["price"]
            fills.append({"price": fill_price, "quantity": fill_qty})
            order["filled_qty"] += fill_qty
            remaining -= fill_qty
            if order["filled_qty"] >= order["quantity"]:
                order["status"] = "filled"
                matched_ids.append(order["order_id"])

        # Remove fully filled orders
        for oid in matched_ids:
            self.buy_orders = [o for o in self.buy_orders if o["order_id"] != oid]
            self.sell_orders = [o for o in self.sell_orders if o["order_id"] != oid]

        filled_qty = quantity - remaining
        return {"fills": fills, "filled_qty": filled_qty, "remaining": remaining}


class MockExchangeHandler(BaseHTTPRequestHandler):
    """
    RESTful handler for the mock exchange with limit order book.
    Endpoints:
      GET   /v1/orderbook?symbol=BTC/USD
      GET   /v1/ticker?symbol=BTC/USD
      GET   /v1/account
      GET   /v1/orders?status=open
      POST  /v1/execute
      POST  /v1/orderbook
      POST  /v1/cancel
      GET   /v1/health
    """

    rate_limit_requests: Dict[str, List[float]] = {}
    rate_limit_win = 1.0
    rate_limit_max = 15

    def log_message(self, fmt, *args):
        pass

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, msg: str, status: int = 400):
        self._send_json({"error": msg}, status)

    def _check_rate_limit(self) -> bool:
        client = self.client_address[0]
        now = time.time()
        window_start = now - self.rate_limit_win
        if client not in self.rate_limit_requests:
            self.rate_limit_requests[client] = []
        self.rate_limit_requests[client] = [
            t for t in self.rate_limit_requests[client] if t > window_start
        ]
        if len(self.rate_limit_requests[client]) >= self.rate_limit_max:
            return False
        self.rate_limit_requests[client].append(now)
        return True

    def _get_pg(self):
        return getattr(self.server, "price_gen", None)

    def _get_obm(self):
        if not hasattr(self.server, "order_book_mgr"):
            self.server.order_book_mgr = OrderBookManager()
        return self.server.order_book_mgr

    def do_GET(self):
        if not self._check_rate_limit():
            self._send_json({"error": "rate_limit_exceeded", "retry_after_ms": 1000}, 429)
            return
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)
        pg = self._get_pg()

        if path == "/v1/orderbook":
            symbol = params.get("symbol", ["BTC/USD"])[0]
            exchange = params.get("exchange", ["PRIMARY"])[0]
            if not pg:
                self._send_error("Exchange not initialized", 500)
                return
            self._send_json(pg.get_orderbook(symbol, exchange))

        elif path == "/v1/ticker":
            symbol = params.get("symbol", ["BTC/USD"])[0]
            if not pg:
                self._send_error("Exchange not initialized", 500)
                return
            self._send_json(pg.get_ticker(symbol))

        elif path == "/v1/orders":
            status_filter = params.get("status", ["all"])[0]
            obm = self._get_obm()
            all_orders = obm.buy_orders + obm.sell_orders
            if status_filter != "all":
                all_orders = [o for o in all_orders if o["status"] == status_filter]
            self._send_json({"orders": all_orders, "count": len(all_orders)})

        elif path == "/v1/regime":
            if pg:
                self._send_json({
                    "regime": pg.current_regime,
                    "regime_name": REGIMES[pg.current_regime].name,
                    "regime_duration": pg.regime_duration,
                    "description": REGIMES[pg.current_regime].description,
                })
            else:
                self._send_error("Exchange not initialized", 500)

        elif path == "/v1/account":
            self._send_json({
                "account_id": "TRAINEE-001",
                "balances": {"USD": 100000.0, "BTC": 0.0, "ETH": 0.0, "USDT": 50000.0, "SOL": 0.0, "AVAX": 0.0, "LINK": 0.0},
                "day_pnl": 0.0,
                "total_pnl": 0.0,
            })

        elif path == "/v1/health":
            self._send_json({
                "status": "operational",
                "uptime_ticks": pg.tick if pg else 0,
                "regime": pg.current_regime if pg else -1,
                "limit_orders": self._get_obm().order_id_counter if hasattr(self.server, "order_book_mgr") else 0,
            })

        else:
            self._send_error(f"Unknown endpoint: {path}", 404)

    def do_POST(self):
        if not self._check_rate_limit():
            self._send_json({"error": "rate_limit_exceeded", "retry_after_ms": 1000}, 429)
            return
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        content_length = int(self.headers.get("Content-Length", 0))
        body = b""
        if content_length > 0:
            body = self.rfile.read(content_length)
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error("Invalid JSON body", 400)
            return
        pg = self._get_pg()

        if path == "/v1/execute":
            if not pg:
                self._send_error("Exchange not initialized", 500)
                return

            symbol = data.get("symbol", "BTC/USD")
            side = data.get("side", "buy")
            quantity = float(data.get("quantity", 0))
            order_type = data.get("type", "market").lower()
            limit_price = float(data.get("price", 0)) if data.get("price") else None

            if quantity <= 0:
                self._send_error("Invalid quantity", 400)
                return

            mid = pg.prices.get(symbol, 100.0)
            obm = self._get_obm()
            fee_rate = 0.001

            if order_type in ("limit", "gtc"):
                if not limit_price or limit_price <= 0:
                    self._send_error("Limit price required for limit orders", 400)
                    return
                oid = obm.add_limit_order({
                    "symbol": symbol, "side": side,
                    "quantity": quantity, "price": limit_price,
                    "type": "limit",
                })
                self._send_json({
                    "order_id": oid, "symbol": symbol, "side": side,
                    "type": "limit", "quantity": quantity,
                    "price": limit_price, "status": "open",
                    "message": "Limit order placed in book",
                    "timestamp": datetime.datetime.now().isoformat(),
                })

            elif order_type == "ioc":
                # Immediate-or-Cancel: match what we can, cancel rest
                result = obm.match_market_order(symbol, side, quantity)
                filled_qty = result["filled_qty"]
                if filled_qty <= 0:
                    self._send_json({
                        "order_id": obm._gen_order_id(),
                        "symbol": symbol, "side": side,
                        "quantity": quantity, "filled_qty": 0,
                        "avg_price": 0, "total": 0, "fee": 0,
                        "status": "cancelled",
                        "reason": "No liquidity",
                        "timestamp": datetime.datetime.now().isoformat(),
                    })
                    return
                total_cost = sum(f["price"] * f["quantity"] for f in result["fills"])
                avg_price = total_cost / filled_qty
                fee = total_cost * fee_rate
                self._send_json({
                    "order_id": obm._gen_order_id(),
                    "symbol": symbol, "side": side,
                    "type": "ioc",
                    "quantity": quantity,
                    "filled_qty": filled_qty,
                    "remaining": result["remaining"],
                    "avg_price": round(avg_price, 2),
                    "total": round(total_cost, 2),
                    "fee": round(fee, 2),
                    "fills": result["fills"],
                    "status": "partially_filled" if result["remaining"] > 0 else "filled",
                    "timestamp": datetime.datetime.now().isoformat(),
                })

            elif order_type == "fok":
                # Fill-or-Kill: must fill entirely or cancel
                result = obm.match_market_order(symbol, side, quantity)
                if result["remaining"] > 0:
                    self._send_json({
                        "order_id": obm._gen_order_id(),
                        "symbol": symbol, "side": side,
                        "quantity": quantity, "filled_qty": 0,
                        "status": "cancelled",
                        "reason": "Could not fill entire quantity (FOK)",
                        "timestamp": datetime.datetime.now().isoformat(),
                    })
                    return
                total_cost = sum(f["price"] * f["quantity"] for f in result["fills"])
                avg_price = total_cost / quantity
                fee = total_cost * fee_rate
                self._send_json({
                    "order_id": obm._gen_order_id(),
                    "symbol": symbol, "side": side,
                    "type": "fok",
                    "quantity": quantity,
                    "filled_qty": quantity,
                    "avg_price": round(avg_price, 2),
                    "total": round(total_cost, 2),
                    "fee": round(fee, 2),
                    "fills": result["fills"],
                    "status": "filled",
                    "timestamp": datetime.datetime.now().isoformat(),
                })

            else:
                # Market order — match against limit book
                ob = pg.get_orderbook(symbol)
                # First try matching against existing limit orders
                result = obm.match_market_order(symbol, side, quantity)
                filled_qty = result["filled_qty"]
                remaining = result["remaining"]

                # Any unfilled quantity fills at market (with slippage from book depth)
                if remaining > 0:
                    mid = ob["mid"]
                    slippage_bps = pg.estimate_slippage_bps(symbol, remaining, side)
                    fill_price = mid * (1 + slippage_bps / 10000 * (1 if side == "buy" else -1))
                    result["fills"].append({"price": fill_price, "quantity": remaining})
                    filled_qty += remaining
                    remaining = 0

                if filled_qty <= 0:
                    self._send_error("No liquidity available", 400)
                    return

                total_cost = sum(f["price"] * f["quantity"] for f in result["fills"])
                avg_price = total_cost / filled_qty
                fee = total_cost * fee_rate

                self._send_json({
                    "order_id": obm._gen_order_id(),
                    "symbol": symbol, "side": side,
                    "type": "market",
                    "quantity": quantity,
                    "filled_qty": filled_qty,
                    "avg_price": round(avg_price, 2),
                    "total": round(total_cost, 2),
                    "fee": round(fee, 2),
                    "slippage_bps": round(slippage_bps, 2) if remaining == 0 else 0,
                    "fills": result["fills"],
                    "status": "filled",
                    "timestamp": datetime.datetime.now().isoformat(),
                })

        elif path == "/v1/orderbook":
            if pg:
                pg.update()
                # Also advance all open limit orders: check for new matches
                self._get_obm()
                self._send_json({"status": "tick_advanced", "tick": pg.tick, "regime": pg.current_regime})
            else:
                self._send_error("Exchange not initialized", 500)

        elif path == "/v1/cancel":
            order_id = data.get("order_id", "")
            obm = self._get_obm()
            for book in (obm.buy_orders, obm.sell_orders):
                for o in book:
                    if o["order_id"] == order_id and o["status"] == "open":
                        o["status"] = "cancelled"
                        self._send_json({"order_id": order_id, "status": "cancelled"})
                        return
            self._send_error(f"Order {order_id} not found or not cancellable", 404)

        else:
            self._send_error(f"Unknown endpoint: {path}", 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


class MockExchangeServer:
    """
    Background threaded HTTP server simulating a financial exchange.
    """

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.price_gen = MockPriceGenerator()
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False

    def start(self) -> bool:
        """Start the exchange server in a background daemon thread."""
        if self.running:
            return True

        try:
            self.server = HTTPServer((self.host, self.port), MockExchangeHandler)
            self.server.price_gen = self.price_gen
            self.thread = threading.Thread(target=self.server.serve_forever,
                                           daemon=True)
            self.thread.start()
            self.running = True
            # Advance a few ticks so there's data
            for _ in range(5):
                self.price_gen.update()
            return True
        except OSError as e:
            print(f"  {c(Color.ERROR, f'[FAIL] Could not start exchange on {self.host}:{self.port}: {e}')}")
            return False

    def stop(self):
        """Gracefully stop the exchange server."""
        if self.server and self.running:
            self.server.shutdown()
            self.running = False

    def is_running(self) -> bool:
        return self.running

    def status(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "running": self.running,
            "tick": self.price_gen.tick,
            "symbols": list(self.price_gen.prices.keys()),
        }


# ==============================================================================
# SECTION 3 — SQLITE LEDGER ENGINE (Double-Entry Bookkeeping)
# ==============================================================================

LEDGER_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('asset','liability','equity','revenue','expense')),
    balance REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS trades (
    id TEXT PRIMARY KEY,
    day INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL CHECK(side IN ('buy','sell')),
    price REAL NOT NULL,
    quantity REAL NOT NULL,
    total REAL NOT NULL,
    fee REAL DEFAULT 0,
    timestamp TEXT DEFAULT (datetime('now')),
    status TEXT DEFAULT 'executed'
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT,
    account_code TEXT NOT NULL,
    debit REAL DEFAULT 0,
    credit REAL DEFAULT 0,
    description TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (trade_id) REFERENCES trades(id),
    FOREIGN KEY (account_code) REFERENCES accounts(code)
);

CREATE TABLE IF NOT EXISTS daily_pnl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    realized_pnl REAL DEFAULT 0,
    unrealized_pnl REAL DEFAULT 0,
    total_fees REAL DEFAULT 0,
    net_pnl REAL DEFAULT 0,
    timestamp TEXT DEFAULT (datetime('now'))
);
"""

SEED_ACCOUNTS = [
    ("1000", "Cash - USD", "asset", 100000.0),
    ("1100", "Cash - BTC", "asset", 0.0),
    ("1200", "Cash - ETH", "asset", 0.0),
    ("1300", "Cash - USDT", "asset", 50000.0),
    ("2000", "Trade Settlements Payable", "liability", 0.0),
    ("3000", "Retained Earnings", "equity", 150000.0),
    ("4000", "Trading Revenue", "revenue", 0.0),
    ("4100", "Fee Expense", "expense", 0.0),
    ("4200", "P&L Summary", "equity", 0.0),
]


class LedgerEngine:
    """
    SQLite-based double-entry bookkeeping system.
    All trades, settlements, and P&L are recorded here.
    """

    def __init__(self, db_path: str = "training_ledger.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        """Open connection and ensure schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()
        self._seed_accounts()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def _init_schema(self):
        for statement in LEDGER_SCHEMA_SQL.split(";"):
            s = statement.strip()
            if s:
                self.conn.execute(s)
        self.conn.commit()

    def _seed_accounts(self):
        """Insert default chart of accounts if empty."""
        cur = self.conn.execute("SELECT COUNT(*) as cnt FROM accounts")
        if cur.fetchone()["cnt"] == 0:
            for code, name, typ, balance in SEED_ACCOUNTS:
                self.conn.execute(
                    "INSERT INTO accounts (code, name, type, balance) VALUES (?, ?, ?, ?)",
                    (code, name, typ, balance),
                )
            self.conn.commit()

    def record_trade(self, trade_id: str, day: int, symbol: str, side: str,
                     price: float, quantity: float, total: float, fee: float = 0.0) -> bool:
        """Record a trade with double-entry bookkeeping."""
        try:
            # Insert trade
            self.conn.execute(
                "INSERT INTO trades (id, day, symbol, side, price, quantity, total, fee) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (trade_id, day, symbol, side, price, quantity, total, fee),
            )

            if side == "buy":
                # Debit: Asset (Crypto)
                # Credit: Cash (USD)
                if "BTC" in symbol:
                    asset_code = "1100"  # Cash - BTC
                elif "ETH" in symbol:
                    asset_code = "1200"  # Cash - ETH
                else:
                    asset_code = "1300"  # Cash - USDT

                # Debit the asset account (increase)
                self.conn.execute(
                    "INSERT INTO ledger_entries (trade_id, account_code, debit, credit, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (trade_id, asset_code, total, 0, f"Buy {quantity} {symbol} @ {price}"),
                )
                # Credit the cash account (decrease)
                self.conn.execute(
                    "INSERT INTO ledger_entries (trade_id, account_code, debit, credit, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (trade_id, "1000", 0, total, f"Cash outflow for {symbol} purchase"),
                )
            else:
                # Sell: Credit Asset, Debit Cash
                if "BTC" in symbol:
                    asset_code = "1100"
                elif "ETH" in symbol:
                    asset_code = "1200"
                else:
                    asset_code = "1300"

                # Credit the asset (decrease)
                self.conn.execute(
                    "INSERT INTO ledger_entries (trade_id, account_code, debit, credit, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (trade_id, asset_code, 0, total, f"Sell {quantity} {symbol} @ {price}"),
                )
                # Debit cash (increase)
                self.conn.execute(
                    "INSERT INTO ledger_entries (trade_id, account_code, debit, credit, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (trade_id, "1000", total, 0, f"Cash inflow from {symbol} sale"),
                )

            # Record fee if any
            if fee > 0:
                self.conn.execute(
                    "INSERT INTO ledger_entries (trade_id, account_code, debit, credit, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (trade_id, "4100", fee, 0, f"Trading fee for {trade_id}"),
                )
                self.conn.execute(
                    "INSERT INTO ledger_entries (trade_id, account_code, debit, credit, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (trade_id, "1000", 0, fee, f"Fee payment from cash for {trade_id}"),
                )

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            return False

    def get_trades(self, day: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get trades, optionally filtered by day."""
        if day:
            cur = self.conn.execute(
                "SELECT * FROM trades WHERE day = ? ORDER BY timestamp", (day,)
            )
        else:
            cur = self.conn.execute("SELECT * FROM trades ORDER BY timestamp")
        return [dict(row) for row in cur.fetchall()]

    def get_ledger_entries(self, trade_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get ledger entries."""
        if trade_id:
            cur = self.conn.execute(
                "SELECT * FROM ledger_entries WHERE trade_id = ? ORDER BY timestamp",
                (trade_id,),
            )
        else:
            cur = self.conn.execute(
                "SELECT * FROM ledger_entries ORDER BY timestamp"
            )
        return [dict(row) for row in cur.fetchall()]

    def verify_double_entry(self) -> Tuple[bool, float]:
        """
        Verify that total debits = total credits across all entries.
        Returns (is_balanced, difference).
        """
        cur = self.conn.execute(
            "SELECT COALESCE(SUM(debit), 0) as total_debit, "
            "COALESCE(SUM(credit), 0) as total_credit FROM ledger_entries"
        )
        row = cur.fetchone()
        diff = abs(row["total_debit"] - row["total_credit"])
        return diff < 0.001, diff

    def calculate_pnl(self, day: int) -> List[Dict[str, Any]]:
        """Calculate P&L by symbol for a given day."""
        cur = self.conn.execute(
            "SELECT symbol, side, SUM(total) as total, SUM(fee) as fees, "
            "COUNT(*) as trade_count FROM trades WHERE day = ? "
            "GROUP BY symbol, side ORDER BY symbol", (day,)
        )
        results = {}
        for row in cur.fetchall():
            sym = row["symbol"]
            if sym not in results:
                results[sym] = {"symbol": sym, "buy_volume": 0, "sell_volume": 0,
                                "buy_total": 0.0, "sell_total": 0.0, "fees": 0.0,
                                "trade_count": 0}
            r = results[sym]
            r["trade_count"] += row["trade_count"]
            r["fees"] += row["fees"]
            if row["side"] == "buy":
                r["buy_volume"] += 1
                r["buy_total"] += row["total"]
            else:
                r["sell_volume"] += 1
                r["sell_total"] += row["total"]

        pnl_rows = []
        for sym, r in results.items():
            realized = r["sell_total"] - r["buy_total"]
            net = realized - r["fees"]
            pnl_rows.append({
                "symbol": sym,
                "realized_pnl": round(realized, 2),
                "total_fees": round(r["fees"], 2),
                "net_pnl": round(net, 2),
                "trade_count": r["trade_count"],
            })
            # Store in daily_pnl
            self.conn.execute(
                "INSERT INTO daily_pnl (day, symbol, realized_pnl, total_fees, net_pnl) "
                "VALUES (?, ?, ?, ?, ?)",
                (day, sym, round(realized, 2), round(r["fees"], 2), round(net, 2)),
            )
        self.conn.commit()
        return pnl_rows

    def get_account_balances(self) -> List[Dict[str, Any]]:
        """Get current account balances."""
        cur = self.conn.execute(
            "SELECT code, name, type, balance FROM accounts ORDER BY code"
        )
        return [dict(row) for row in cur.fetchall()]

    def reset_for_day(self, day: int):
        """Reset operational accounts for a new training day."""
        # Clear trades and ledger entries for the day if re-running
        self.conn.execute("DELETE FROM trades WHERE day = ?", (day,))
        self.conn.execute("""
            DELETE FROM ledger_entries WHERE trade_id IN
            (SELECT id FROM trades WHERE day = ?)
        """, (day,))
        self.conn.execute("DELETE FROM daily_pnl WHERE day = ?", (day,))
        self.conn.commit()

    def clear_all(self):
        """Wipe all data for fresh start."""
        self.conn.execute("DELETE FROM trades")
        self.conn.execute("DELETE FROM ledger_entries")
        self.conn.execute("DELETE FROM daily_pnl")
        self.conn.commit()


# ==============================================================================
# SECTION 4 — AST STATIC CODE AUDITOR
# ==============================================================================

class CodeAuditor:
    """
    AST-based static code analyzer for structural quality enforcement.
    Checks: try-except coverage, time complexity, security, annotations.
    """

    ISSUE_CRITICAL = "critical"
    ISSUE_WARNING = "warning"
    ISSUE_INFO = "info"

    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.complexity_score: int = 0

    def audit(self, code: str, filename: str = "<trainee_code>") -> List[Dict[str, Any]]:
        """
        Audit a piece of Python code for structural issues.
        Returns list of issues found.
        """
        self.issues = []
        self.complexity_score = 0

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.issues.append({
                "severity": self.ISSUE_CRITICAL,
                "line": e.lineno or 0,
                "message": f"Syntax error: {e.msg}",
                "code": "SYNTAX_ERR",
            })
            return self.issues

        # Run all checks
        self._check_network_handling(tree, code)
        self._check_complexity(tree)
        self._check_security(tree)
        self._check_annotations(tree)
        self._check_division_by_zero(tree)
        self._check_infinite_loops(tree)
        self._check_global_state(tree)

        return self.issues

    def _check_network_handling(self, tree: ast.AST, code: str):
        """Check that urllib/requests calls are wrapped in try-except."""
        network_calls = set()
        for node in ast.walk(tree):
            # Check for urllib calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                    if func_name in ("urlopen", "request", "get", "post"):
                        # Check if this is inside a try block
                        line = node.lineno
                        network_calls.add(line)

        # Check which are in try blocks
        try_lines = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    for child in ast.walk(handler):
                        if hasattr(child, 'lineno'):
                            try_lines.add(child.lineno)

        uncovered = network_calls - try_lines
        for line in sorted(uncovered):
            # Get source line for context
            source_lines = code.split('\n')
            context = source_lines[line - 1].strip() if 0 < line <= len(source_lines) else ""
            self.issues.append({
                "severity": self.ISSUE_CRITICAL,
                "line": line,
                "message": f"Network call without try-except at line {line}: '{context[:60]}'",
                "code": "NO_NETWORK_EXCEPT",
            })

    def _check_complexity(self, tree: ast.AST):
        """
        Detect O(n^2) nested loops over trading data structures.
        Flag nested for loops iterating over lists.
        """
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.AsyncFor)):
                # Check what we're iterating over
                iter_name = self._get_iter_name(node.iter)
                # Look for nested loops
                for child in ast.walk(node):
                    if child is node:
                        continue
                    if isinstance(child, (ast.For, ast.AsyncFor)):
                        child_iter = self._get_iter_name(child.iter)
                        # Check for obvious list/dict iteration
                        if iter_name and child_iter:
                            self.complexity_score += 1
                            self.issues.append({
                                "severity": self.ISSUE_WARNING,
                                "line": child.lineno,
                                "message": f"Nested loop (potential O(n^2)) at line {child.lineno}. "
                                           f"Consider vectorized operations for order book data.",
                                "code": "NESTED_LOOP",
                            })

    def _check_security(self, tree: ast.AST):
        """Check for eval, exec, and other dangerous patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ("eval", "exec", "compile"):
                        self.issues.append({
                            "severity": self.ISSUE_CRITICAL,
                            "line": node.lineno,
                            "message": f"Security violation: '{node.func.id}()' is prohibited in trading code.",
                            "code": "SECURITY_EVAL",
                        })
            # Check for dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("pickle", "subprocess", "ctypes"):
                        self.issues.append({
                            "severity": self.ISSUE_CRITICAL,
                            "line": node.lineno,
                            "message": f"Prohibited import: '{alias.name}' is not allowed in trading code.",
                            "code": "SECURITY_IMPORT",
                        })
            if isinstance(node, ast.ImportFrom):
                if node.module in ("pickle", "subprocess", "ctypes", "os"):
                    self.issues.append({
                        "severity": self.ISSUE_WARNING,
                        "line": node.lineno,
                        "message": f"Restricted import from '{node.module}' in trading code.",
                        "code": "SECURITY_IMPORT",
                    })

    def _check_annotations(self, tree: ast.AST):
        """Check that function definitions have type annotations."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                missing = []
                # Check return annotation
                if not node.returns:
                    missing.append("return type")
                # Check argument annotations
                for arg in node.args.args:
                    if not arg.annotation and arg.arg != "self":
                        missing.append(f"arg '{arg.arg}'")
                if missing:
                    self.issues.append({
                        "severity": self.ISSUE_INFO,
                        "line": node.lineno,
                        "message": f"Function '{node.name}' missing annotations: {', '.join(missing)}. "
                                   f"PEP 484 annotations improve code clarity.",
                        "code": "MISSING_ANNOTATION",
                    })

    def _check_division_by_zero(self, tree: ast.AST):
        """Check for division operations that might cause ZeroDivisionError."""
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                # Check if right operand might not be checked
                divisor = node.right
                if isinstance(divisor, ast.Name):
                    # Simple heuristic: flag if not preceded by a check
                    source_lines = []
                    try:
                        with open(__file__, 'r') as f:
                            pass
                    except:
                        pass
                    self.issues.append({
                        "severity": self.ISSUE_WARNING,
                        "line": node.lineno,
                        "message": f"Division at line {node.lineno}: variable '{divisor.id}' used as divisor "
                                   f"without apparent zero-check. Could cause ZeroDivisionError.",
                        "code": "DIVISION_BY_ZERO",
                    })

    def _check_infinite_loops(self, tree: ast.AST):
        """Check for while True loops without breaks (potential infinite loops)."""
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                # Check if condition is constant True
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    has_break = any(
                        isinstance(child, ast.Break)
                        for child in ast.walk(node)
                    )
                    if not has_break:
                        self.issues.append({
                            "severity": self.ISSUE_WARNING,
                            "line": node.lineno,
                            "message": f"'while True' loop at line {node.lineno} without break. "
                                       f"Infinite loop risk in production trading systems.",
                            "code": "INFINITE_LOOP",
                        })

    def _check_global_state(self, tree: ast.AST):
        """Flag use of global variables in trading functions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                self.issues.append({
                    "severity": self.ISSUE_WARNING,
                    "line": node.lineno,
                    "message": f"Use of 'global' at line {node.lineno}. Global state is "
                               f"discouraged in trading algorithms (race condition risk).",
                    "code": "GLOBAL_STATE",
                })

    def _get_iter_name(self, node: ast.AST) -> Optional[str]:
        """Extract the iterable name from a for loop iterator."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                return node.func.attr
        elif isinstance(node, ast.List):
            return "__list_literal__"
        return None

    def has_critical_issues(self) -> bool:
        return any(i["severity"] == self.ISSUE_CRITICAL for i in self.issues)

    def summary(self) -> Dict[str, int]:
        return {
            "critical": sum(1 for i in self.issues if i["severity"] == self.ISSUE_CRITICAL),
            "warning": sum(1 for i in self.issues if i["severity"] == self.ISSUE_WARNING),
            "info": sum(1 for i in self.issues if i["severity"] == self.ISSUE_INFO),
            "complexity_score": self.complexity_score,
        }


# ==============================================================================
# SECTION 5 — 90-DAY STATE MACHINE
# ==============================================================================

class StateManager:
    """
    Manages the 90-day progression state machine.
    State persisted to save_state.json.
    """

    PHASE_1_DAYS = (1, 30)   # Data Ingestion & Risk Math
    PHASE_2_DAYS = (31, 60)  # Algorithmic Arbitrage & API Execution
    PHASE_3_DAYS = (61, 90)  # Market Slippage, Latency & SOCPA Compliance

    STATE_FILE = "save_state.json"

    def __init__(self):
        self.current_day: int = 1
        self.phase: int = 1
        self.completed_days: List[int] = []
        self.scores: Dict[str, Any] = {}
        self.ledger_db: str = "training_ledger.db"
        self.workspace_dir: str = ""
        self.total_score: float = 0.0
        self.max_score: float = 0.0
        self.compliance_audit_passed: bool = False
        self.load()

    @property
    def phase_name(self) -> str:
        if 1 <= self.current_day <= 30:
            return "Phase 1: Data Ingestion & Foundational Risk Math"
        elif 31 <= self.current_day <= 60:
            return "Phase 2: Algorithmic Arbitrage Logic & API Execution"
        else:
            return "Phase 3: Market Slippage, Latency & SOCPA Compliance"

    def get_phase(self) -> int:
        if self.current_day <= 30:
            return 1
        elif self.current_day <= 60:
            return 2
        else:
            return 3

    def can_advance(self) -> bool:
        """Check if the current day was passed (score = 100)."""
        day_key = str(self.current_day)
        if day_key in self.scores:
            s = self.scores[day_key]
            return s.get("score", 0) >= s.get("max_score", 1) * 0.999  # Allow floating point
        return False

    def advance_day(self) -> bool:
        """Advance to next day. Returns False if already at max."""
        if self.current_day >= 90:
            return False
        self.current_day += 1
        self.phase = self.get_phase()
        self.save()
        return True

    def record_score(self, score: int, max_score: int, violations: List[str],
                     ast_issues: List[str], ledger_balanced: bool):
        """Record the day's evaluation result."""
        self.scores[str(self.current_day)] = {
            "score": score,
            "max_score": max_score,
            "pct": (score / max_score * 100) if max_score > 0 else 0,
            "violations": violations,
            "ast_issues": ast_issues,
            "ledger_balanced": ledger_balanced,
            "passed": score >= max_score,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        if score >= max_score and self.current_day not in self.completed_days:
            self.completed_days.append(self.current_day)
            self.total_score += score
            self.max_score += max_score

        self.compliance_audit_passed = ledger_balanced
        self.save()

    def load(self):
        """Load state from save_state.json if it exists."""
        if os.path.exists(self.STATE_FILE):
            try:
                with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.current_day = data.get("current_day", 1)
                self.phase = data.get("phase", 1)
                self.completed_days = data.get("completed_days", [])
                self.scores = data.get("scores", {})
                self.total_score = data.get("total_score", 0.0)
                self.max_score = data.get("max_score", 0.0)
                self.ledger_db = data.get("ledger_db", "training_ledger.db")
                self.workspace_dir = data.get("workspace_dir", "")
                self.compliance_audit_passed = data.get("compliance_audit_passed", False)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        """Persist state to save_state.json."""
        data = {
            "current_day": self.current_day,
            "phase": self.phase,
            "completed_days": self.completed_days,
            "scores": self.scores,
            "total_score": self.total_score,
            "max_score": self.max_score,
            "ledger_db": self.ledger_db,
            "workspace_dir": self.workspace_dir,
            "compliance_audit_passed": self.compliance_audit_passed,
            "updated": datetime.datetime.now().isoformat(),
            "program": "NovaCap 90-Day Arbitrage Protocol",
            "version": __version__,
        }
        with open(self.STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def reset(self):
        """Reset all progress."""
        self.current_day = 1
        self.phase = 1
        self.completed_days = []
        self.scores = {}
        self.total_score = 0.0
        self.max_score = 0.0
        self.compliance_audit_passed = False
        if os.path.exists(self.STATE_FILE):
            os.remove(self.STATE_FILE)

    def status_report(self) -> str:
        """Generate a status summary."""
        lines = [
            header("=" * 76),
            header(f"  TRAINING STATUS — Day {self.current_day} of 90"),
            header("=" * 76),
            f"  Phase:      {self.phase_name}",
            f"  Days Comp.: {len(self.completed_days)}/90",
            f"  Cum. Score: {self.total_score:.0f}/{self.max_score:.0f} pts",
        ]
        if self.completed_days:
            avg = self.total_score / len(self.completed_days) if self.completed_days else 0
            lines.append(f"  Avg Score:  {avg:.1f}/100")
        lines.append("")
        return "\n".join(lines)


# ==============================================================================
# SECTION 6 — RISK MANAGER
# ==============================================================================

class RiskManager:
    """
    Multi-layer risk management system.
    Monitors portfolio-level VaR/CVaR, correlation, position limits,
    leverage constraints, and circuit breaker conditions.
    """

    LEVERAGE_MAX = 2.0
    POSITION_LIMIT_PCT = 0.15
    CIRCUIT_BREAKER_DRAWDOWN_PCT = 0.05
    CIRCUIT_BREAKER_WINDOW = 10
    VAR_CONFIDENCE = 0.95
    INITIAL_CAPITAL = 100000.0

    def __init__(self, ledger: LedgerEngine):
        self.ledger = ledger
        self.halted = False
        self.halt_reason: Optional[str] = None
        self.equity_curve: List[float] = [self.INITIAL_CAPITAL]
        self.returns: List[float] = []

    def check_circuit_breaker(self, day: int) -> bool:
        """
        Check if P&L has dropped more than threshold in the last N bars.
        Returns True if circuit breaker is tripped (trading halted).
        """
        if self.halted:
            return True
        pnl_rows = self.ledger.calculate_pnl(day)
        day_pnl = sum(r["net_pnl"] for r in pnl_rows)
        current_equity = self.equity_curve[-1] + day_pnl if self.equity_curve else self.INITIAL_CAPITAL
        self.equity_curve.append(current_equity)
        if len(self.equity_curve) > 1:
            ret = (self.equity_curve[-1] - self.equity_curve[-2]) / self.equity_curve[-2]
            self.returns.append(ret)

        # Check drawdown over window
        window = self.equity_curve[-(self.CIRCUIT_BREAKER_WINDOW + 1):]
        if len(window) >= self.CIRCUIT_BREAKER_WINDOW:
            peak = max(window[:-1])
            peak_to_current = (peak - current_equity) / peak if peak > 0 else 0
            if peak_to_current >= self.CIRCUIT_BREAKER_DRAWDOWN_PCT:
                self.halted = True
                self.halt_reason = (
                    f"Circuit breaker tripped: {peak_to_current*100:.2f}% drawdown "
                    f"exceeds {self.CIRCUIT_BREAKER_DRAWDOWN_PCT*100:.0f}% threshold"
                )
                return True
        return False

    def check_position_limit(self, symbol_balance: float, capital: float) -> bool:
        """Check if a position exceeds the per-symbol limit."""
        return symbol_balance <= capital * self.POSITION_LIMIT_PCT

    def check_leverage(self, gross_exposure: float, capital: float) -> bool:
        """Check if total leverage exceeds max allowed."""
        if capital <= 0:
            return False
        return (gross_exposure / capital) <= self.LEVERAGE_MAX

    def compute_var(self, confidence: float = 0.95) -> float:
        """Historical VaR at given confidence level."""
        if len(self.returns) < 20:
            return 0.0
        sorted_rets = sorted(self.returns)
        idx = max(0, int((1 - confidence) * len(sorted_rets)) - 1)
        return abs(sorted_rets[idx])

    def compute_cvar(self, confidence: float = 0.95) -> float:
        """Conditional VaR (expected shortfall)."""
        if len(self.returns) < 20:
            return 0.0
        var = self.compute_var(confidence)
        tail = [r for r in self.returns if r <= -var]
        if not tail:
            return var
        return abs(sum(tail) / len(tail))

    def compute_correlation(self, trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Compute symbol-level return correlations.
        Returns dict of symbol→correlation-to-portfolio.
        """
        if len(trades) < 5:
            return {}
        by_sym: Dict[str, List[float]] = {}
        for t in trades:
            sym = t.get("symbol", "UNKNOWN")
            pnl = t.get("total", 0) * (1 if t.get("side") == "sell" else -1)
            by_sym.setdefault(sym, []).append(pnl)
        result = {}
        portfolio_rets = [sum(by_sym[s][i] for s in by_sym if i < len(by_sym[s])) for i in range(max(len(v) for v in by_sym.values()))]
        if len(portfolio_rets) < 3:
            return {}
        for sym, rets in by_sym.items():
            if len(rets) < 3:
                continue
            n = min(len(rets), len(portfolio_rets))
            sym_arr = rets[:n]
            port_arr = portfolio_rets[:n]
            mean_s = sum(sym_arr) / n
            mean_p = sum(port_arr) / n
            num = sum((s - mean_s) * (p - mean_p) for s, p in zip(sym_arr, port_arr))
            den = (sum((s - mean_s)**2 for s in sym_arr) * sum((p - mean_p)**2 for p in port_arr)) ** 0.5
            result[sym] = round(num / den, 4) if den != 0 else 0.0
        return result

    def risk_report(self, day: int) -> str:
        """Generate a human-readable risk summary."""
        lines = [f"  {c(Color.BRIGHT_WHITE, 'RISK REPORT — Day ' + str(day))}"]
        lines.append(f"  {muted('=' * 50)}")
        if self.halted:
            lines.append(f"  {c(Color.FAIL, 'CIRCUIT BREAKER: ACTIVE')}")
            lines.append(f"  {c(Color.BRIGHT_RED, 'Reason: ' + (self.halt_reason or 'N/A'))}")
        else:
            lines.append(f"  {c(Color.BRIGHT_GREEN, 'Circuit Breaker: Inactive')}")
        eq = self.equity_curve[-1] if self.equity_curve else self.INITIAL_CAPITAL
        dd = 0.0
        if len(self.equity_curve) > 1:
            peak = max(self.equity_curve)
            dd = (peak - eq) / peak * 100 if peak > 0 else 0
        lines.append(f"  Equity: ${eq:,.2f}  |  Max DD: {dd:.2f}%")
        var95 = self.compute_var(0.95)
        cvar95 = self.compute_cvar(0.95)
        lines.append(f"  VaR(95%): {var95*100:.2f}%  |  CVaR(95%): {cvar95*100:.2f}%")
        gross = sum(max(0, a.get("balance", 0)) for a in self.ledger.get_account_balances())
        lev = gross / eq if eq > 0 else 0
        lines.append(f"  Gross Exposure: ${gross:,.2f}  |  Leverage: {lev:.2f}x (max {self.LEVERAGE_MAX}x)")
        trades = self.ledger.get_trades(day)
        corr = self.compute_correlation(trades)
        if corr:
            corr_str = "  |  ".join(f"{s}: {v:+.3f}" for s, v in sorted(corr.items()))
            lines.append(f"  Correlation: {corr_str}")
        lines.append(f"  Positions: {len(trades)} trades today")
        lines.append("")
        return "\n".join(lines)


# ==============================================================================
# SECTION 7 — BACKTEST ENGINE
# ==============================================================================

class BacktestRun:
    """Holds results from a single backtest iteration."""

    def __init__(self, seed: int, final_equity: float, sharpe: float,
                 max_dd: float, total_trades: int, win_rate: float,
                 returns: List[float], equity_curve: List[float]):
        self.seed = seed
        self.final_equity = final_equity
        self.sharpe = sharpe
        self.max_dd = max_dd
        self.total_trades = total_trades
        self.win_rate = win_rate
        self.returns = returns
        self.equity_curve = equity_curve


class BacktestEngine:
    """
    Monte Carlo backtesting engine.
    Replays a stored price sequence against a strategy using seeded runs.
    """

    def __init__(self, ledger: LedgerEngine):
        self.ledger = ledger
        self.runs: List[BacktestRun] = []
        self._price_series: Dict[str, List[float]] = {}

    def capture_price_series(self, pg: MockPriceGenerator) -> None:
        """Capture current price history from the live generator."""
        self._price_series = {}
        for sym, prices in pg.price_history.items():
            self._price_series[sym] = list(prices)

    def run_backtest(self, seed: int, solution_path: str, days: int = 30) -> BacktestRun:
        """
        Run a single backtest with a fixed seed.
        Replays stored price sequence against the strategy.
        """
        # We use the existing EvaluationEngine to score
        pg = MockPriceGenerator(seed)
        # Fast-forward to build history
        for _ in range(100):
            pg.update()

        # Run the solution against the seeded generator using subprocess
        start_equity = 100000.0
        equity = [start_equity]
        returns: List[float] = []

        for day_idx in range(days):
            if not os.path.exists(solution_path):
                break
            try:
                env = os.environ.copy()
                env["NOVACAP_SEED"] = str(seed + day_idx)
                env["NOVACAP_DAY"] = str(day_idx + 1)
                result = subprocess.run(
                    [sys.executable, solution_path],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    env=env,
                    cwd=os.path.dirname(solution_path) if os.path.dirname(solution_path) else None,
                )
                # Parse stdout for P&L signal
                pnl = 0.0
                for line in (result.stdout or "").split("\n"):
                    if "PNL" in line.upper() or "NET_PNL" in line:
                        try:
                            pnl = float(line.split("=")[-1].strip())
                        except (ValueError, IndexError):
                            pass
                equity.append(equity[-1] + pnl)
                if equity[-2] > 0:
                    returns.append((equity[-1] - equity[-2]) / equity[-2])
                else:
                    returns.append(0.0)
            except (subprocess.TimeoutExpired, OSError):
                returns.append(0.0)
                equity.append(equity[-1])

        final_eq = equity[-1]
        risk_free = 0.02 / 252
        mean_ret = sum(returns) / len(returns) if returns else 0
        std_ret = (sum((r - mean_ret)**2 for r in returns) / len(returns))**0.5 if returns else 1
        sharpe = ((mean_ret - risk_free) / std_ret * (252**0.5)) if std_ret > 0 else 0.0

        peak = max(equity)
        max_dd = max(((peak - eq) / peak) for eq in equity) if peak > 0 else 0.0

        wins = sum(1 for r in returns if r > 0)
        win_rate = wins / len(returns) if returns else 0.0

        run = BacktestRun(
            seed=seed,
            final_equity=final_eq,
            sharpe=sharpe,
            max_dd=max_dd,
            total_trades=len(returns),
            win_rate=win_rate,
            returns=returns,
            equity_curve=equity,
        )
        self.runs.append(run)
        return run

    def run_monte_carlo(self, solution_path: str, iterations: int = 50,
                        days: int = 30) -> Dict[str, Any]:
        """Run N backtest iterations with random seeds."""
        self.runs = []
        for i in range(iterations):
            seed = 42 + i * 7
            self.run_backtest(seed, solution_path, days)

        final_eqs = [r.final_equity for r in self.runs]
        sharpes = [r.sharpe for r in self.runs]
        dds = [r.max_dd for r in self.runs]
        wrs = [r.win_rate for r in self.runs]

        def _mean(arr): return sum(arr) / len(arr) if arr else 0
        def _std(arr):
            m = _mean(arr)
            return (sum((x - m)**2 for x in arr) / len(arr))**0.5 if arr else 0
        def _percentile(arr, pct):
            s = sorted(arr)
            idx = max(0, min(len(s) - 1, int(len(s) * pct)))
            return s[idx]

        return {
            "iterations": iterations,
            "days_per_iteration": days,
            "mean_final_equity": round(_mean(final_eqs), 2),
            "median_final_equity": round(_percentile(final_eqs, 0.5), 2),
            "std_final_equity": round(_std(final_eqs), 2),
            "min_final_equity": round(min(final_eqs), 2),
            "max_final_equity": round(max(final_eqs), 2),
            "mean_sharpe": round(_mean(sharpes), 3),
            "median_sharpe": round(_percentile(sharpes, 0.5), 3),
            "std_sharpe": round(_std(sharpes), 3),
            "mean_max_dd": round(_mean(dds), 4),
            "median_max_dd": round(_percentile(dds, 0.5), 4),
            "mean_win_rate": round(_mean(wrs), 4),
            "p10_final_equity": round(_percentile(final_eqs, 0.1), 2),
            "p90_final_equity": round(_percentile(final_eqs, 0.9), 2),
            "sharpe_gt_1_pct": round(sum(1 for s in sharpes if s > 1.0) / iterations * 100, 1) if iterations > 0 else 0,
        }


# ==============================================================================
# SECTION 8 — WORKSPACE GENERATOR
# ==============================================================================

class WorkspaceGenerator:
    """
    Generates the daily workspace: DAILY_BRIEF.md, boilerplate .py files,
    and hidden test suites for evaluation.
    """

    def __init__(self, base_dir: str = "workspace"):
        self.base_dir = base_dir

    def ensure_dir(self, path: str):
        os.makedirs(path, exist_ok=True)

    def generate_daily_workspace(self, day: int, phase: int,
                                 curriculum: Dict[str, Any]) -> str:
        """
        Generate the day's workspace files.
        Returns the workspace directory path.
        """
        day_dir = os.path.join(self.base_dir, f"day_{day:03d}")
        self.ensure_dir(day_dir)

        # Generate DAILY_BRIEF.md
        self._write_briefing(day_dir, day, phase, curriculum)

        # Generate boilerplate Python file
        self._write_boilerplate(day_dir, day, curriculum)

        # Generate hidden test file
        test_dir = os.path.join(day_dir, "__tests__")
        self.ensure_dir(test_dir)
        self._write_tests(test_dir, day, curriculum)

        return day_dir

    def _write_briefing(self, day_dir: str, day: int, phase: int,
                        curriculum: Dict[str, Any]):
        """Write the DAILY_BRIEF.md file."""
        content = curriculum.get("briefing_md", "")
        phase_names = {
            1: "Phase 1: Data Ingestion & Foundational Risk Math",
            2: "Phase 2: Algorithmic Arbitrage Logic & API Execution",
            3: "Phase 3: Market Slippage, Latency & SOCPA Compliance",
        }
        pname = phase_names.get(phase, "Unknown Phase")

        md = f"""# DAILY BRIEF — Day {day} | {pname}

**Principal Strategist — NovaCap Financial Technologies Ltd.**
**Standards: CMA | SOCPA | IFRS**

---

## SITUATION

{curriculum.get('situation', 'No briefing provided.')}

## OBJECTIVES

"""
        for i, obj in enumerate(curriculum.get("objectives", []), 1):
            md += f"{i}. {obj}\n"

        md += f"""
## SPECIFICATION

{curriculum.get('specification', 'No specification provided.')}

## TECHNICAL REQUIREMENTS

"""
        for req in curriculum.get("requirements", []):
            md += f"- {req}\n"

        md += f"""
## DATA SOURCES

- Mock Exchange: http://localhost:8080/v1/orderbook?symbol=BTC/USD
- Mock Exchange: http://localhost:8080/v1/ticker?symbol=BTC/USD
- Trade Execution: POST http://localhost:8080/v1/execute
- Ledger DB: training_ledger.db (SQLite, double-entry schema)

## CMA / SOCPA STANDARDS REFERENCED

"""
        for std in curriculum.get("standards", []):
            md += f"- {std}\n"

        md += f"""
## DEADLINE

EOD (17:00) — Type `EOD` in the Principal Strategist CLI to trigger evaluation.

---
*This briefing is auto-generated by the NovaCap 90-Day Arbitrage Protocol v{__version__}.*
"""
        path = os.path.join(day_dir, "DAILY_BRIEF.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

    def _write_boilerplate(self, day_dir: str, day: int,
                           curriculum: Dict[str, Any]):
        """Write the boilerplate Python file the user edits."""
        boilerplate = curriculum.get("boilerplate_py", "# No boilerplate provided.\n")
        path = os.path.join(day_dir, f"solution_day_{day:03d}.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(boilerplate)
        # Also write a __init__.py
        init_path = os.path.join(day_dir, "__init__.py")
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(f"# Day {day} Solution Package\n")

    def _write_tests(self, test_dir: str, day: int,
                     curriculum: Dict[str, Any]):
        """Write hidden test files for evaluation."""
        tests = curriculum.get("tests_py", "")
        path = os.path.join(test_dir, f"test_day_{day:03d}.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(tests)
        # Write runner
        runner = f"""#!/usr/bin/env python3
\"\"\"Hidden test runner for Day {day}. Do not modify.\"\"\"
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from __tests__.test_day_{day:03d} import run_tests

if __name__ == "__main__":
    result = run_tests()
    print(json.dumps(result))
"""
        runner_path = os.path.join(test_dir, f"runner_day_{day:03d}.py")
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(runner)

    def get_user_solution_path(self, day: int) -> str:
        """Get the path to the user's solution file for a given day."""
        return os.path.join(self.base_dir, f"day_{day:03d}", f"solution_day_{day:03d}.py")

    def user_solution_exists(self, day: int) -> bool:
        """Check if the user has a solution file."""
        return os.path.exists(self.get_user_solution_path(day))


# ==============================================================================
# SECTION 7 — EVALUATION ENGINE
# ==============================================================================

class EvaluationEngine:
    """
    Runs the EOD evaluation: AST audit, code execution against hidden tests,
    ledger verification, scoring.
    """

    def __init__(self, state: StateManager, ledger: LedgerEngine):
        self.state = state
        self.ledger = ledger
        self.auditor = CodeAuditor()

    def evaluate(self, day: int, workspace_dir: str,
                 curriculum: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full evaluation pipeline for a day.
        1. Read user's solution code
        2. AST audit
        3. Run hidden tests
        4. Verify ledger integrity
        5. Score
        """
        violations: List[str] = []
        ast_issues: List[str] = []
        test_results: Dict[str, Any] = {}
        score = 0
        max_score = 100

        solution_path = os.path.join(workspace_dir, f"solution_day_{day:03d}.py")

        # Step 1: Read user code
        user_code = ""
        if os.path.exists(solution_path):
            with open(solution_path, "r", encoding="utf-8") as f:
                user_code = f.read()
        else:
            violations.append("No solution file submitted")

        # Step 2: AST audit
        if user_code.strip():
            issues = self.auditor.audit(user_code, solution_path)
            for issue in issues:
                sev = issue["severity"]
                msg = issue["message"]
                formatted = f"[{sev.upper()}] Line {issue.get('line', '?')}: {msg}"
                ast_issues.append(formatted)
                if sev == CodeAuditor.ISSUE_CRITICAL:
                    violations.append(f"AST Critical: {msg}")

        # Step 3: Run hidden tests
        test_runner = os.path.join(
            workspace_dir, "__tests__", f"runner_day_{day:03d}.py"
        )
        if os.path.exists(test_runner):
            try:
                result = subprocess.run(
                    [sys.executable, test_runner],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.path.dirname(workspace_dir),
                )
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        test_results = json.loads(result.stdout)
                    except json.JSONDecodeError:
                        test_results = {"raw": result.stdout[:500]}
                else:
                    test_results = {
                        "error": result.stderr[:500] if result.stderr else "Unknown test failure"
                    }
                    violations.append(f"Test execution failed: {result.stderr[:200]}")
            except subprocess.TimeoutExpired:
                violations.append("Test execution timed out (>30s)")
            except OSError as e:
                violations.append(f"Test runner error: {e}")
        else:
            violations.append(f"Test suite not found: {test_runner}")

        # Step 4: Ledger integrity
        ledger_ok = True
        try:
            balanced, diff = self.ledger.verify_double_entry()
            if not balanced:
                ledger_ok = False
                violations.append(f"Ledger imbalance: debits/credits differ by ${diff:.2f}")
        except Exception as e:
            ledger_ok = False
            violations.append(f"Ledger verification error: {e}")

        # Step 5: Calculate score
        score = self._calculate_score(violations, ast_issues, test_results,
                                      ledger_ok, max_score)

        return {
            "day": day,
            "score": score,
            "max_score": max_score,
            "passed": score >= max_score,
            "violations": violations,
            "ast_issues": ast_issues,
            "test_results": test_results,
            "ledger_balanced": ledger_ok,
        }

    def _calculate_score(self, violations: List[str], ast_issues: List[str],
                         test_results: Dict[str, Any], ledger_ok: bool,
                         max_score: int) -> int:
        """
        Scoring logic:
        - Start at 100
        - Critical violations (unhandled network, security, O(n^2)): -40 each, min 0
        - Any critical violation = immediate 0 if >= 2
        - Ledger imbalance: -50
        - Test failures: proportional deduction
        - AST warnings: -10 each
        """
        if not ledger_ok:
            return 0  # Ledger must be perfect

        critical_violations = [v for v in violations if "Critical" in v
                               or "Network" in v or "security" in v.lower()
                               or "Ledger" in v]

        if len(critical_violations) >= 2:
            return 0  # Two+ critical violations = automatic failure

        score = max_score

        # Deduct for violations
        for v in violations:
            if "No solution" in v:
                return 0
            if any(kw in v.lower() for kw in ["critical", "security", "eval",
                                                "exec", "network"]):
                score -= 40
            elif any(kw in v.lower() for kw in ["ledger", "test execution",
                                                  "timed out"]):
                score -= 30
            else:
                score -= 15

        # Deduct for AST issues (warnings)
        for issue in ast_issues:
            if "[WARNING]" in issue:
                score -= 10
            elif "[CRITICAL]" in issue:
                score -= 25

        # Test results
        if test_results:
            passed = test_results.get("passed", 0)
            total = test_results.get("total", 1)
            if total > 0:
                pct = passed / total
                if pct < 1.0:
                    deduction = int((1 - pct) * 60)
                    score -= deduction

        # Clamp
        return max(0, min(max_score, score))

    def get_violations_for_consequences(self, violations: List[str]) -> List[str]:
        """Map violations to real-world consequences for the report."""
        return [v for v in violations if "AST" in v or "Ledger" in v or "Critical" in v]


# ==============================================================================
# SECTION 8 — DAYS 1-3 CURRICULUM DATA
# ==============================================================================

CURRICULUM_DAY_1 = {
    "title": "Data Ingestion & SMA Calculation",
    "situation": (
        "You are a newly onboarded FinTech Arbitrage Specialist at NovaCap Financial. "
        "Your first assignment is to establish a reliable data pipeline. You must fetch "
        "live BTC/USD order book data from the mock exchange and calculate Simple Moving "
        "Averages (SMA-5 and SMA-20). All ingested data must be logged to the firm's "
        "double-entry SQLite ledger for audit trail compliance."
    ),
    "objectives": [
        "Connect to http://localhost:8080/v1/orderbook and fetch BTC/USD data",
        "Calculate SMA(5) and SMA(20) from consecutive bid prices",
        "Log each data point and calculation to the SQLite ledger",
        "Handle network errors gracefully (no crashes)",
        "Ensure all calculations are typed and documented",
    ],
    "specification": (
        "Write a Python script that:\n"
        "1. Fetches the BTC/USD order book from the Mock Exchange every second for 30 iterations\n"
        "2. Maintains a sliding window of the last 20 mid-prices\n"
        "3. Calculates SMA(5) and SMA(20) when sufficient data exists\n"
        "4. Logs each price and SMA to the SQLite `trades` and `ledger_entries` tables\n"
        "5. Handles rate limiting (HTTP 429) with exponential backoff\n"
        "6. Outputs a summary table of prices and SMAs to stdout"
    ),
    "requirements": [
        "Use urllib (standard library) for HTTP requests",
        "All network calls must be wrapped in try-except blocks",
        "No external packages (standard library only)",
        "Functions must have type annotations (PEP 484)",
        "Log trade data to SQLite: INSERT INTO trades (id, day, symbol, side, price, quantity, total)",
        "Maintain proper double-entry: asset increase + cash decrease for buys",
    ],
    "standards": [
        "CMA Part 1 - Section C: Financial Statement Analysis (data sourcing)",
        "SOCPA Standard 4: Documentation and audit trail requirements",
        "IFRS 9: Financial Instruments recognition and measurement",
    ],
    "briefing_md": """## MARKET CONTEXT

BTC/USD is trading in a volatile range between $64,000 and $72,000. The mock exchange
streams live order book data with realistic bid-ask spreads and depth profiles. Your
data pipeline must handle:

- **Rate limiting**: Max 10 requests/second per client IP
- **Price ticks**: Updated every 100ms with random walk microstructure
- **Spread**: Typically $100-150 between best bid and ask

## DATA PIPELINE ARCHITECTURE

```
[Exchange :8080] --> [urllib GET] --> [price extraction] --> [SMA calc] --> [SQLite]
```

## ACCEPTANCE CRITERIA

1. SMA(5) and SMA(20) calculated correctly to within 0.1% tolerance
2. No unhandled exceptions (try-except on ALL network calls)
3. All 30 data points logged to SQLite ledger_entries table
4. STDOUT shows a clean summary table
""",
    "boilerplate_py": """#!/usr/bin/env python3
\"\"\"
Day 1: Data Ingestion & SMA Calculation
Complete the functions below. Do not change function signatures.
\"\"\"
import json
import sqlite3
import time
import urllib.request
import urllib.error
from typing import List, Optional, Tuple


# ── CONFIGURATION ──────────────────────────────────────────────────────────

EXCHANGE_URL = "http://localhost:8080/v1/orderbook?symbol=BTC/USD"
LEDGER_DB = "training_ledger.db"
DAY = 1


# ── TASK 1: Fetch Order Book ─────────────────────────────────────────────

def fetch_orderbook(url: str = EXCHANGE_URL) -> Optional[dict]:
    \"\"\"
    Fetch the order book from the mock exchange.
    Must handle: urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError.
    Returns the parsed JSON response, or None on failure.
    \"\"\"
    # TODO: Implement with proper error handling
    pass


# ── TASK 2: Calculate SMA ────────────────────────────────────────────────

def calculate_sma(prices: List[float], window: int) -> List[Optional[float]]:
    \"\"\"
    Calculate Simple Moving Average for the given window size.
    Returns a list where first (window-1) values are None.
    \"\"\"
    # TODO: Implement SMA calculation
    pass


# ── TASK 3: Log to Ledger ────────────────────────────────────────────────

def log_price_to_ledger(conn: sqlite3.Connection, day: int, price: float,
                        sma5: Optional[float], sma20: Optional[float]) -> bool:
    \"\"\"
    Log a price observation and SMA values to the ledger.
    Returns True on success.
    \"\"\"
    # TODO: Implement ledger logging
    pass


# ── TASK 4: Main Pipeline ────────────────────────────────────────────────

def run_pipeline(iterations: int = 30, interval: float = 1.0) -> None:
    \"\"\"
    Main data pipeline: fetch, calculate, log.
    Runs for `iterations` cycles with `interval` seconds between each.

    Must output a summary table to stdout showing:
      Iteration | Price | SMA(5) | SMA(20)
    \"\"\"
    # TODO: Implement the full pipeline
    pass


# ── MAIN ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_pipeline()
""",
    "tests_py": """#!/usr/bin/env python3
\"\"\"Hidden tests for Day 1. Do not modify.\"\"\"
import sys
import os
import json
import sqlite3
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the trainee's solution
try:
    from solution_day_001 import fetch_orderbook, calculate_sma, log_price_to_ledger, run_pipeline
except ImportError as e:
    def run_tests():
        return {"passed": 0, "total": 1, "errors": [f"ImportError: {e}"]}
    # Can't proceed — provide a stub


def run_tests():
    \"\"\"Execute all hidden tests for Day 1.\"\"\"
    results = {"passed": 0, "total": 5, "errors": [], "details": []}

    # Test 1: fetch_orderbook returns valid data
    try:
        data = fetch_orderbook()
        assert data is not None, "fetch_orderbook returned None"
        assert "bids" in data, "Response missing 'bids'"
        assert "asks" in data, "Response missing 'asks'"
        assert len(data["bids"]) > 0, "Empty bids array"
        results["passed"] += 1
        results["details"].append("Test 1 PASSED: fetch_orderbook works")
    except Exception as e:
        results["errors"].append(f"Test 1 FAILED: fetch_orderbook - {e}")
        results["details"].append(f"Test 1 FAILED: {e}")

    # Test 2: SMA calculation correct
    try:
        test_prices = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        sma3 = calculate_sma(test_prices, 3)
        assert sma3[0] is None, "First SMA value should be None"
        assert sma3[1] is None, "Second SMA value should be None"
        assert abs(sma3[2] - 2.0) < 0.001, f"SMA(3) at index 2 should be 2.0, got {sma3[2]}"
        assert abs(sma3[5] - 5.0) < 0.001, f"SMA(3) at index 5 should be 5.0, got {sma3[5]}"
        results["passed"] += 1
        results["details"].append("Test 2 PASSED: SMA calculation correct")
    except Exception as e:
        results["errors"].append(f"Test 2 FAILED: SMA calculation - {e}")
        results["details"].append(f"Test 2 FAILED: {e}")

    # Test 3: Ledger logging works
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), "training_ledger.db"))
        conn.row_factory = sqlite3.Row
        # Clear test entries
        result = log_price_to_ledger(conn, 1, 50000.0, 49000.0, 48000.0)
        assert result is True, "log_price_to_ledger returned False"
        conn.close()
        results["passed"] += 1
        results["details"].append("Test 3 PASSED: Ledger logging works")
    except Exception as e:
        results["errors"].append(f"Test 3 FAILED: Ledger logging - {e}")
        results["details"].append(f"Test 3 FAILED: {e}")

    # Test 4: Pipeline runs without exception
    try:
        run_pipeline(iterations=3, interval=0.1)
        results["passed"] += 1
        results["details"].append("Test 4 PASSED: Pipeline runs")
    except Exception as e:
        results["errors"].append(f"Test 4 FAILED: Pipeline crash - {e}")
        results["details"].append(f"Test 4 FAILED: {e}")

    # Test 5: SMA values in database
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), "training_ledger.db"))
        cur = conn.execute("SELECT COUNT(*) as cnt FROM trades WHERE day=1")
        count = cur.fetchone()["cnt"]
        assert count > 0, "No trades logged for day 1"
        conn.close()
        results["passed"] += 1
        results["details"].append("Test 5 PASSED: Day 1 data in ledger")
    except Exception as e:
        results["errors"].append(f"Test 5 FAILED: Ledger data - {e}")
        results["details"].append(f"Test 5 FAILED: {e}")

    return results
""",
}

CURRICULUM_DAY_2 = {
    "title": "Cross-Exchange Arbitrage Detection",
    "situation": (
        "You have successfully built the data pipeline. Now, NovaCap's arbitrage desk "
        "needs you to monitor spread discrepancies between two simulated exchanges "
        "(PRIMARY and SECONDARY). When the spread exceeds 0.5%, you must execute an "
        "arbitrage trade through the mock exchange API. All trades must be logged "
        "via double-entry bookkeeping."
    ),
    "objectives": [
        "Poll order books from two simulated exchanges via /v1/orderbook?exchange=PRIMARY and /v1/orderbook?exchange=SECONDARY",
        "Calculate cross-exchange spread percentage",
        "Execute arbitrage trade via POST /v1/execute when spread > 0.5%",
        "Log all trades to SQLite ledger with proper double-entry",
        "Calculate and report P&L for each trade",
    ],
    "specification": (
        "Write a Python script that:\n"
        "1. Polls both exchanges for ETH/USDT order books every 2 seconds\n"
        "2. Calculates the spread: (best_ask_exchange1 - best_bid_exchange2) / mid\n"
        "3. When spread > 0.5%, executes a buy on the cheaper exchange and sell on the pricier\n"
        "4. Records each leg of the trade independently in SQLite\n"
        "5. Reports total P&L for the session to stdout"
    ),
    "requirements": [
        "Handle exchange-specific rate limits independently",
        "Use POST to /v1/execute for trade execution (JSON body)",
        "Implement exponential backoff on rate limit (HTTP 429)",
        "Account for 0.1% trading fee on each leg",
        "Functions must have complete type annotations",
    ],
    "standards": [
        "CMA Part 2 - Section A: Quantitative Methods (spread analysis)",
        "CMA Part 2 - Section D: Investment Decision Analysis (arbitrage)",
        "SOCPA Standard 7: Transaction recording and verification",
        "IFRS 13: Fair Value Measurement (mark-to-market)",
    ],
    "briefing_md": """## MARKET CONTEXT

Two simulated exchanges (PRIMARY and SECONDARY) stream ETH/USDT order books with
slightly different prices. The spread between them fluctuates due to simulated
latency and order flow imbalances. Your job is to capture these discrepancies.

## EXCHANGE CONFIGURATION

- **PRIMARY**:  http://localhost:8080/v1/orderbook?symbol=ETH/USDT&exchange=PRIMARY
- **SECONDARY**: http://localhost:8080/v1/orderbook?symbol=ETH/USDT&exchange=SECONDARY
- **Execution**: POST http://localhost:8080/v1/execute

## RISK PARAMETERS

- Max position size per trade: 10 ETH
- Stop-loss: -2% of capital
- Max open positions: 1 (no hedging)
""",
    "boilerplate_py": """#!/usr/bin/env python3
\"\"\"
Day 2: Cross-Exchange Arbitrage Detection
\"\"\"
import json
import sqlite3
import time
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Tuple


EXCHANGE_BASE = "http://localhost:8080/v1/orderbook"
EXECUTE_URL = "http://localhost:8080/v1/execute"
LEDGER_DB = "training_ledger.db"
DAY = 2

FEE_RATE = 0.001  # 0.1%
SPREAD_THRESHOLD = 0.005  # 0.5%
MAX_POSITION = 10.0


# ── TASK 1: Fetch Order Book ─────────────────────────────────────────────

def fetch_exchange(symbol: str = "ETH/USDT",
                   exchange: str = "PRIMARY") -> Optional[Dict]:
    \"\"\"Fetch order book from a specific exchange.\"\"\"
    # TODO: Implement with error handling
    pass


# ── TASK 2: Calculate Spread ─────────────────────────────────────────────

def calculate_spread(ex1: Dict, ex2: Dict) -> Optional[float]:
    \"\"\"
    Calculate the cross-exchange spread percentage.
    spread = (best_ask_ex1 - best_bid_ex2) / mid_price
    \"\"\"
    # TODO: Implement
    pass


# ── TASK 3: Execute Trade ────────────────────────────────────────────────

def execute_trade(symbol: str, side: str, quantity: float,
                  order_type: str = "market") -> Optional[Dict]:
    \"\"\"
    Execute a trade on the mock exchange via POST /v1/execute.
    Returns the order response or None on failure.
    \"\"\"
    # TODO: Implement with proper error handling
    pass


# ── TASK 4: Log Trade to Ledger ──────────────────────────────────────────

def log_arbitrage_trade(conn: sqlite3.Connection, trade_id: str, day: int,
                        symbol: str, side: str, price: float,
                        quantity: float, total: float, fee: float) -> bool:
    \"\"\"Log a trade to the SQLite ledger with double-entry.\"\"\"
    # TODO: Implement
    pass


# ── TASK 5: Main Arbitrage Loop ──────────────────────────────────────────

def run_arbitrage(iterations: int = 60, interval: float = 2.0) -> None:
    \"\"\"Run the arbitrage detection loop.\"\"\"
    # TODO: Implement
    pass


if __name__ == "__main__":
    run_arbitrage()
""",
    "tests_py": """#!/usr/bin/env python3
\"\"\"Hidden tests for Day 2.\"\"\"
import sys
import os
import json
import sqlite3
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from solution_day_002 import (
        fetch_exchange, calculate_spread, execute_trade,
        log_arbitrage_trade, run_arbitrage
    )
except ImportError as e:
    pass  # Will be caught in tests


def run_tests():
    results = {"passed": 0, "total": 5, "errors": [], "details": []}

    # Test 1: fetch_exchange works for both exchanges
    try:
        d1 = fetch_exchange("ETH/USDT", "PRIMARY")
        assert d1 is not None
        assert "bids" in d1
        d2 = fetch_exchange("ETH/USDT", "SECONDARY")
        assert d2 is not None
        results["passed"] += 1
        results["details"].append("Test 1 PASSED: Both exchanges accessible")
    except Exception as e:
        results["errors"].append(f"Test 1 FAILED: {e}")
        results["details"].append(f"Test 1 FAILED: {e}")

    # Test 2: calculate_spread returns valid spread
    try:
        ex1 = {"bids": [{"price": 3100.0}], "asks": [{"price": 3105.0}]}
        ex2 = {"bids": [{"price": 3095.0}], "asks": [{"price": 3100.0}]}
        spread = calculate_spread(ex1, ex2)
        assert spread is not None, "Spread returned None"
        assert isinstance(spread, float), f"Spread should be float, got {type(spread)}"
        results["passed"] += 1
        results["details"].append(f"Test 2 PASSED: Spread calculation works ({spread:.4f})")
    except Exception as e:
        results["errors"].append(f"Test 2 FAILED: {e}")
        results["details"].append(f"Test 2 FAILED: {e}")

    # Test 3: execute_trade works
    try:
        result = execute_trade("ETH/USDT", "buy", 1.0)
        assert result is not None
        assert result.get("status") == "filled"
        assert "order_id" in result
        results["passed"] += 1
        results["details"].append(f"Test 3 PASSED: Trade executed (order {result.get('order_id')})")
    except Exception as e:
        results["errors"].append(f"Test 3 FAILED: {e}")
        results["details"].append(f"Test 3 FAILED: {e}")

    # Test 4: Ledger logging
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), "training_ledger.db"))
        ok = log_arbitrage_trade(conn, "TEST-ORD-001", 2, "ETH/USDT", "buy", 3100.0, 1.0, 3100.0, 3.10)
        assert ok, "log_arbitrage_trade returned False"
        conn.close()
        results["passed"] += 1
        results["details"].append("Test 4 PASSED: Trade logged to ledger")
    except Exception as e:
        results["errors"].append(f"Test 4 FAILED: {e}")
        results["details"].append(f"Test 4 FAILED: {e}")

    # Test 5: Full arbitrage loop runs cleanly
    try:
        run_arbitrage(iterations=3, interval=0.1)
        results["passed"] += 1
        results["details"].append("Test 5 PASSED: Full loop executed")
    except Exception as e:
        results["errors"].append(f"Test 5 FAILED: {e}")
        results["details"].append(f"Test 5 FAILED: {e}")

    return results
""",
}

CURRICULUM_DAY_3 = {
    "title": "Ledger Reconciliation & P&L Reporting (SOCPA)",
    "situation": (
        "You have executed several arbitrage trades over the past two days. The "
        "compliance officer (under SOCPA Article 23) now requires a full ledger "
        "reconciliation. You must verify that all debits equal credits (double-entry "
        "integrity), calculate the P&L by symbol, and produce a compliance-grade "
        "report. Any discrepancies must be identified and explained."
    ),
    "objectives": [
        "Query the SQLite ledger to extract all trades and ledger entries",
        "Verify double-entry bookkeeping: total debits = total credits",
        "Calculate P&L by symbol (realized = sell_total - buy_total - fees)",
        "Identify any reconciliation gaps or anomalies",
        "Produce a structured compliance report (stdout)",
    ],
    "specification": (
        "Write a Python script that:\n"
        "1. Connects to training_ledger.db and queries the trades and ledger_entries tables\n"
        "2. Verifies double-entry integrity using SQL aggregate queries\n"
        "3. Calculates P&L by symbol: SUM(sell_total) - SUM(buy_total) - SUM(fees)\n"
        "4. Generates a formatted compliance report with SOCPA references\n"
        "5. Outputs the report to stdout and saves it to ledger_report.txt"
    ),
    "requirements": [
        "Use SQL aggregate functions (SUM, COUNT, GROUP BY)",
        "Report must include date, reviewer, SOCPA article references",
        "Flag any trades where fees > 1% of total (exception reporting)",
        "Include a 'Ledger Balance Verification' section showing debits = credits",
    ],
    "standards": [
        "SOCPA Article 23: Internal control and reconciliation requirements",
        "SOCPA Standard 8: Financial reporting and disclosure",
        "CMA Part 1 - Section E: Internal Controls",
        "IFRS 1: First-time adoption of financial instruments",
    ],
    "briefing_md": """## REGULATORY CONTEXT

SOCPA (Saudi Organization for Certified Public Accountants) requires that all
financial transactions be recorded with:
1. Complete audit trail (who, what, when)
2. Double-entry verification (debits = credits)
3. Periodic reconciliation (at least daily for trading desks)
4. Exception reporting for anomalous transactions

## LEDGER SCHEMA

```
accounts(id, code, name, type, balance)
trades(id, day, symbol, side, price, quantity, total, fee)
ledger_entries(id, trade_id, account_code, debit, credit, description)
daily_pnl(id, day, symbol, realized_pnl, total_fees, net_pnl)
```

## REPORT REQUIREMENTS

The compliance report MUST include:
1. Header with date, reviewer name, SOCPA reference
2. Trade count and volume summary
3. P&L by symbol
4. Ledger balance verification (debits vs credits)
5. Exception items (fees > 1%, missing entries)
6. Sign-off section
""",
    "boilerplate_py": """#!/usr/bin/env python3
\"\"\"
Day 3: Ledger Reconciliation & P&L Reporting (SOCPA Compliance)
\"\"\"
import sqlite3
import datetime
from typing import List, Dict, Tuple, Optional


LEDGER_DB = "training_ledger.db"
REPORT_FILE = "ledger_report.txt"
DAY = 3


# ── TASK 1: Query Trades ────────────────────────────────────────────────

def get_trades_by_day(conn: sqlite3.Connection, day: int) -> List[Dict]:
    \"\"\"Get all trades for a specific day.\"\"\"
    # TODO: Implement
    pass


# ── TASK 2: Verify Double-Entry ──────────────────────────────────────────

def verify_double_entry(conn: sqlite3.Connection) -> Tuple[bool, float, float, float]:
    \"\"\"
    Verify that total debits = total credits in ledger_entries.
    Returns (is_balanced, total_debits, total_credits, difference).
    \"\"\"
    # TODO: Implement using SQL aggregate functions
    pass


# ── TASK 3: Calculate P&L ────────────────────────────────────────────────

def calculate_pnl_by_symbol(conn: sqlite3.Connection,
                             day: int) -> List[Dict]:
    \"\"\"
    Calculate realized P&L grouped by symbol.
    P&L = SUM(sell_total) - SUM(buy_total) - SUM(fees)
    \"\"\"
    # TODO: Implement
    pass


# ── TASK 4: Find Exceptions ──────────────────────────────────────────────

def find_exceptions(conn: sqlite3.Connection, day: int) -> List[Dict]:
    \"\"\"Find anomalous trades (fees > 1% of total).\"\"\"
    # TODO: Implement
    pass


# ── TASK 5: Generate Compliance Report ───────────────────────────────────

def generate_report(day: int, reviewer: str = "FinTech Arbitrage Specialist") -> str:
    \"\"\"
    Generate a complete SOCPA compliance report.
    Saves to REPORT_FILE and returns the report text.
    \"\"\"
    # TODO: Implement
    pass


if __name__ == "__main__":
    report = generate_report(DAY)
    print(report)
""",
    "tests_py": """#!/usr/bin/env python3
\"\"\"Hidden tests for Day 3.\"\"\"
import sys
import os
import json
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from solution_day_003 import (
        get_trades_by_day, verify_double_entry,
        calculate_pnl_by_symbol, find_exceptions, generate_report
    )
except ImportError as e:
    pass


def run_tests():
    results = {"passed": 0, "total": 5, "errors": [], "details": []}

    # Test 1: get_trades_by_day returns list
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), "training_ledger.db"))
        conn.row_factory = sqlite3.Row
        trades = get_trades_by_day(conn, 3)
        assert isinstance(trades, list), f"Expected list, got {type(trades)}"
        conn.close()
        results["passed"] += 1
        results["details"].append("Test 1 PASSED: get_trades_by_day works")
    except Exception as e:
        results["errors"].append(f"Test 1 FAILED: {e}")
        results["details"].append(f"Test 1 FAILED: {e}")

    # Test 2: verify_double_entry returns correct tuple
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), "training_ledger.db"))
        balanced, debits, credits, diff = verify_double_entry(conn)
        assert isinstance(balanced, bool)
        assert isinstance(debits, (int, float))
        assert isinstance(credits, (int, float))
        conn.close()
        results["passed"] += 1
        results["details"].append(f"Test 2 PASSED: Double-entry check (balanced={balanced}, diff={diff:.2f})")
    except Exception as e:
        results["errors"].append(f"Test 2 FAILED: {e}")
        results["details"].append(f"Test 2 FAILED: {e}")

    # Test 3: calculate_pnl_by_symbol
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), "training_ledger.db"))
        pnl = calculate_pnl_by_symbol(conn, 3)
        assert isinstance(pnl, list)
        if pnl:
            assert "symbol" in pnl[0]
            assert "net_pnl" in pnl[0]
        conn.close()
        results["passed"] += 1
        results["details"].append("Test 3 PASSED: P&L calculation works")
    except Exception as e:
        results["errors"].append(f"Test 3 FAILED: {e}")
        results["details"].append(f"Test 3 FAILED: {e}")

    # Test 4: find_exceptions
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), "training_ledger.db"))
        exc = find_exceptions(conn, 3)
        assert isinstance(exc, list)
        conn.close()
        results["passed"] += 1
        results["details"].append("Test 4 PASSED: Exception finder works")
    except Exception as e:
        results["errors"].append(f"Test 4 FAILED: {e}")
        results["details"].append(f"Test 4 FAILED: {e}")

    # Test 5: generate_report produces valid output
    try:
        report = generate_report(3)
        assert report is not None
        assert len(report) > 50, "Report too short"
        # Check for required sections
        required = ["SOCPA", "P&L", "Balance", "debit", "credit"]
        found = [r.lower() in report.lower() for r in required]
        assert all(found), f"Missing sections: {[r for r, f in zip(required, found) if not f]}"
        # Check report file was saved
        assert os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), REPORT_FILE if 'REPORT_FILE' in dir() else "ledger_report.txt")), "Report file not saved"
        results["passed"] += 1
        results["details"].append("Test 5 PASSED: Complete compliance report generated")
    except Exception as e:
        results["errors"].append(f"Test 5 FAILED: {e}")
        results["details"].append(f"Test 5 FAILED: {e}")

    return results
""",
}

# Map days to curriculum
CURRICULUM = {
    1: CURRICULUM_DAY_1,
    2: CURRICULUM_DAY_2,
    3: CURRICULUM_DAY_3,
}

# Generic curriculum generator for days 4+
def generate_generic_curriculum(day: int, phase: int) -> Dict[str, Any]:
    """Generate a generic curriculum entry for days beyond 3."""
    phase_1_tasks = [
        "Sharpe Ratio calculation from historical returns",
        "Maximum drawdown analysis on simulated portfolio",
        "Volume-weighted average price (VWAP) implementation",
        "Beta and correlation matrix computation",
        "Portfolio variance minimization (Markowitz)",
        "Historical VaR calculation at 95% and 99%",
        "Expected shortfall (CVaR) computation",
        "Jensen's alpha and information ratio",
    ]
    phase_2_tasks = [
        "Triangular arbitrage across BTC/ETH/USDT",
        "Statistical arbitrage (pairs trading) implementation",
        "Order book imbalance signal detection",
        "Market making spread optimization",
        "TWAP/VWAP execution algorithm",
        "Latency measurement and optimization",
        "Cross-exchange fee arbitrage",
        "Rebalancing trigger optimization",
    ]
    phase_3_tasks = [
        "Slippage impact modeling on large orders",
        "Network latency simulation and hedging",
        "SOCPA Article 23 full compliance audit",
        "Transaction cost analysis (TCA) report",
        "Multi-exchange position reconciliation",
        "Real-time P&L attribution with SQL",
        "Circuit breaker implementation",
        "Audit trail reconstruction from ledger",
    ]

    task_pool = {1: phase_1_tasks, 2: phase_2_tasks, 3: phase_3_tasks}
    tasks = task_pool.get(phase, phase_1_tasks)
    task = tasks[(day - 1) % len(tasks)]

    return {
        "title": task,
        "situation": f"Day {day} of Phase {phase}. Focus: {task}. "
                     f"Continue building on previous days' work. All previous "
                     f"evaluation criteria remain in effect.",
        "objectives": [
            f"Implement {task}",
            "Ensure all network calls have try-except handling",
            "Log all operations to SQLite ledger",
            "Maintain double-entry bookkeeping integrity",
            "Output results to stdout in structured format",
        ],
        "specification": f"Implement {task} using the mock exchange and ledger infrastructure. "
                         f"Follow the patterns established in Days 1-3.",
        "requirements": [
            "Type annotations on all functions",
            "Try-except on all external calls",
            "SQLite ledger logging for all operations",
            "No eval/exec or prohibited imports",
            "Maximum response time under 30 seconds",
        ],
        "standards": [
            "CMA Part 1 - Section C: Financial Statement Analysis",
            "CMA Part 2 - Section A: Quantitative Methods",
            "SOCPA Standard 4: Documentation and audit trail",
            "IFRS 9: Financial Instruments",
        ],
        "briefing_md": f"# DAILY BRIEF — Day {day}\n\n## TASK\n\n{task}\n\n"
                       f"Continue following NovaCap's coding standards and SOCPA compliance requirements.",
        "boilerplate_py": f"""#!/usr/bin/env python3
\"\"\"
Day {day}: {task}
\"\"\"
import json
import sqlite3
import time
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Tuple

LEDGER_DB = "training_ledger.db"
DAY = {day}


def main():
    \"\"\"
    Implement {task}.
    All network calls must have try-except handling.
    All operations must be logged to the SQLite ledger.
    \"\"\"
    # TODO: Implement
    pass


if __name__ == "__main__":
    main()
""",
        "tests_py": f"""#!/usr/bin/env python3
\"\"\"Hidden tests for Day {day}.\"\"\"
import sys
import os
import json
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from solution_day_{day:03d} import main
except ImportError:
    pass


def run_tests():
    results = {{"passed": 0, "total": 2, "errors": [], "details": []}}

    # Test 1: main runs without exception
    try:
        main()
        results["passed"] += 1
        results["details"].append("Test 1 PASSED: main() executed")
    except Exception as e:
        results["errors"].append(f"Test 1 FAILED: {{e}}")
        results["details"].append(f"Test 1 FAILED: {{e}}")

    # Test 2: Ledger data exists
    try:
        conn = sqlite3.connect(LEDGER_DB)
        cur = conn.execute("SELECT COUNT(*) as cnt FROM trades WHERE day=?", ({day},))
        cnt = cur.fetchone()[0]
        conn.close()
        if cnt > 0:
            results["passed"] += 1
            results["details"].append(f"Test 2 PASSED: {{cnt}} trades in ledger")
        else:
            results["errors"].append("No trades found in ledger")
    except Exception as e:
        results["errors"].append(f"Test 2 FAILED: {{e}}")

    return results
""",
    }


# ==============================================================================
# SECTION 9 — MAIN CLI APPLICATION
# ==============================================================================

class ArbitrageAcademyCLI(cmd.Cmd):
    """
    Principal Strategist CLI — the main interaction point for the trainee.
    Clinical, harsh, zero-praise tone. Manages the full daily workflow.
    """

    intro = ""
    prompt = c(Color.BRIGHT_CYAN, "strategist> ")

    def __init__(self):
        super().__init__()
        self.state = StateManager()
        self.ledger = LedgerEngine(self.state.ledger_db)
        self.exchange = MockExchangeServer()
        self.workspace = WorkspaceGenerator()
        self.evaluator = EvaluationEngine(self.state, self.ledger)
        self.risk_mgr = RiskManager(self.ledger)
        self.backtest = BacktestEngine(self.ledger)
        self.current_day_curriculum: Optional[Dict[str, Any]] = None
        self.day_workspace_dir: Optional[str] = None
        self.running = True
        self._initialized = False

    # ── UI Helpers ─────────────────────────────────────────────────────────

    def _init_display(self):
        """Display the initial banner and status."""
        print(PrincipalStrategist._banner())
        print()
        print(f"  {c(Color.BRIGHT_WHITE, 'WELCOME, TRAINEE.')}")
        print()
        print(f"  {muted('You are enrolled in the NovaCap 90-Day FinTech Arbitrage Protocol.')}")
        print(f"  {muted('Standards enforced: CMA (Certified Management Accountant)')}")
        print(f"  {muted('                     SOCPA (Saudi CPA)')}")
        print(f"  {muted('                     IFRS (International Financial Reporting)')}")
        print()
        print(f"  {PrincipalStrategist.observation('This is not a course. This is a simulation of')}")
        print(f"  {PrincipalStrategist.observation('the most demanding trading desk in the region.')}")
        print(f"  {PrincipalStrategist.observation('You will write code. You will make mistakes.')}")
        print(f"  {PrincipalStrategist.observation('You will fix them. Or you will not advance.')}")
        print()
        directive_msg = 'Type "start" to begin Day 1.'
        help_msg = 'Type "help" for available commands.'
        print(f"  {c(Color.BRIGHT_YELLOW, 'DIRECTIVE:')} {c(Color.BRIGHT_WHITE, directive_msg)}")
        print(f"  {muted(help_msg)}")
        print()

    def _display_day_start(self):
        """Display day start information."""
        day = self.state.current_day
        phase = self.state.get_phase()

        print()
        print(PrincipalStrategist.morning_briefing(day, phase))
        print()

        # Get curriculum
        if day in CURRICULUM:
            self.current_day_curriculum = CURRICULUM[day]
        else:
            self.current_day_curriculum = generate_generic_curriculum(day, phase)

        # Generate workspace
        self.day_workspace_dir = self.workspace.generate_daily_workspace(
            day, phase, self.current_day_curriculum
        )

        title = self.current_day_curriculum.get("title", "")
        print(f"  {c(Color.BRIGHT_WHITE, 'TODAYS TASK:')} {c(Color.BRIGHT_CYAN, title)}")
        print()
        print(f"  {PrincipalStrategist.observation(self.current_day_curriculum['situation'][:200])}")
        print()
        for obj in self.current_day_curriculum["objectives"]:
            print(f"    {c(Color.MUTED, BoxChars.BULLET)} {obj}")
        print()
        print(f"  {c(Color.BRIGHT_YELLOW, 'WORKSPACE:')} {c(Color.BRIGHT_WHITE, self.day_workspace_dir)}")
        print(f"  {c(Color.BRIGHT_YELLOW, 'BRIEFING:')}  {c(Color.BRIGHT_WHITE, os.path.join(self.day_workspace_dir, 'DAILY_BRIEF.md'))}")
        print(f"  {c(Color.BRIGHT_YELLOW, 'SOLUTION:')}  {c(Color.BRIGHT_WHITE, os.path.join(self.day_workspace_dir, f'solution_day_{day:03d}.py'))}")
        print()

        # Reset ledger for this day
        self.ledger.connect()
        self.ledger.reset_for_day(day)

        print(f"  {c(Color.BRIGHT_GREEN, '[' + BoxChars.CHECK + ']')} Exchange available at {c(Color.BRIGHT_WHITE, 'http://localhost:8080')}")
        print(f"  {c(Color.BRIGHT_GREEN, '[' + BoxChars.CHECK + ']')} Ledger ready at {c(Color.BRIGHT_WHITE, self.state.ledger_db)}")
        print(f"  {c(Color.BRIGHT_GREEN, '[' + BoxChars.CHECK + ']')} Workspace generated at {c(Color.BRIGHT_WHITE, self.day_workspace_dir)}")
        print()
        print(f"  {muted('Edit the solution file, run your code, and type EOD when finished.')}")
        print()

    def _run_eod(self):
        """Execute the End-of-Day evaluation."""
        day = self.state.current_day

        if not self.day_workspace_dir:
            eod_msg = 'No workspace for today. Type "start" first.'
            print(f"  {c(Color.ERROR, eod_msg)}")
            return

        print()
        print(f"  {c(Color.BRIGHT_RED, BoxChars.H2 * 76)}")
        print(f"  {c(Color.FAIL, 'END OF DAY PROTOCOL INITIATED')}")
        print(f"  {c(Color.BRIGHT_RED, BoxChars.H2 * 76)}")
        print()

        # Stop exchange
        if self.exchange.is_running():
            print(f"  {info('Halting mock exchange server...')}")
            self.exchange.stop()
        print(f"  {info('Running AST audit...')}")
        print(f"  {info('Executing test suites...')}")
        print(f"  {info('Verifying ledger integrity...')}")
        print()

        # Evaluate
        result = self.evaluator.evaluate(
            day, self.day_workspace_dir, self.current_day_curriculum or {}
        )

        # Record score
        self.state.record_score(
            score=result["score"],
            max_score=result["max_score"],
            violations=result["violations"],
            ast_issues=result["ast_issues"],
            ledger_balanced=result["ledger_balanced"],
        )

        # Display report
        print(PrincipalStrategist.evaluate_results_text(
            score=result["score"],
            max_score=result["max_score"],
            violations=result["violations"],
            ast_issues=result["ast_issues"],
            ledger_ok=result["ledger_balanced"],
        ))

        # If passed, offer to advance
        if result["passed"]:
            if self.state.current_day < 90:
                advance_msg = 'Type "advance" to proceed to Day ' + str(self.state.current_day + 1) + '.'
                print(f"  {c(Color.BRIGHT_GREEN, advance_msg)}")
            else:
                print(f"  {c(Color.BRIGHT_GREEN, 'ALL 90 DAYS COMPLETE.')}")
                print(f"  {c(Color.BRIGHT_GREEN, 'You have completed the NovaCap Arbitrage Protocol.')}")
                print(f"  {muted('Your performance record has been saved.')}")
        else:
            print(f"  {c(Color.BRIGHT_RED, 'You must resolve all violations and score 100 before advancing.')}")
            retry_msg = 'Type "start" to retry Day ' + str(day) + '.'
            print(f"  {c(Color.BRIGHT_RED, retry_msg)}")

        # Close ledger
        self.ledger.close()

    # ── Command Handlers ───────────────────────────────────────────────────

    def do_start(self, arg: str):
        """Start the current day's training. Usage: start"""
        day = self.state.current_day

        if day > 90:
            all_done_msg = 'All 90 days completed. Type "status" to see your record.'
            print(f"  {c(Color.BRIGHT_GREEN, all_done_msg)}")
            return

        # If already passed this day and want to restart
        if self.state.can_advance() and day < 90:
            already_msg = 'Day ' + str(day) + ' already passed. Type "advance" to proceed.'
            print(f"  {warn(already_msg)}")
            return

        # Start exchange server
        print(f"  {info('Starting mock exchange server...')}")
        if not self.exchange.start():
            print(f"  {c(Color.ERROR, 'Failed to start exchange. Is port 8080 in use?')}")
            return

        # Connect ledger
        self.ledger.connect()

        # Display day start
        self._display_day_start()

        # Record in state
        self.state.workspace_dir = self.day_workspace_dir or ""
        self.state.save()

    def do_eod(self, arg: str):
        """Trigger End-of-Day evaluation. Usage: eod"""
        if self.state.current_day > 90:
            print(f"  {c(Color.WARN, 'Training complete. No further evaluations.')}")
            return
        self._run_eod()

    def do_advance(self, arg: str):
        """Advance to the next day. Only allowed if current day is passed. Usage: advance"""
        if not self.state.can_advance():
            print(f"  {c(Color.ERROR, 'Cannot advance. Current day not passed (score must be 100).')}")
            return
        if self.state.current_day >= 90:
            print(f"  {c(Color.BRIGHT_GREEN, 'Training complete. You have finished all 90 days.')}")
            return

        self.state.advance_day()
        print(f"  {c(Color.BRIGHT_GREEN, '[' + BoxChars.CHECK + ']')} Advanced to Day {self.state.current_day}")
        start_msg = 'Type "start" to begin.'
        print(f"  {c(Color.BRIGHT_YELLOW, start_msg)}")

    def do_run(self, arg: str):
        """Run the day's solution file. Usage: run [args]"""
        day = self.state.current_day
        sol_path = self.workspace.get_user_solution_path(day)

        if not os.path.exists(sol_path):
            print(f"  {c(Color.ERROR, 'No solution file for Day ' + str(day) + '.' )}")
            print(f"  {c(Color.WARN, 'File expected at: ' + sol_path)}")
            return

        print(f"  {info('Executing ' + sol_path + '...')}")
        print(f"  {muted('-' * 60)}")
        print()

        try:
            result = subprocess.run(
                [sys.executable, sol_path] + arg.split(),
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(sol_path),
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"  {c(Color.YELLOW, 'STDERR:')}")
                print(result.stderr)
            if result.returncode != 0:
                print(f"  {c(Color.ERROR, 'Exit code: ' + str(result.returncode))}")
            else:
                print(f"  {c(Color.BRIGHT_GREEN, '[' + BoxChars.CHECK + ']')} Execution completed (exit 0)")
        except subprocess.TimeoutExpired:
            print(f"  {c(Color.ERROR, 'Execution timed out (>30s). Check for infinite loops.')}")
        except OSError as e:
            print(f"  {c(Color.ERROR, 'Execution error: ' + str(e))}")
        print()

    def do_status(self, arg: str):
        """Display current training status. Usage: status"""
        print(self.state.status_report())

        # Show recent scores
        if self.state.scores:
            print(f"  {muted('Recent days:')}")
            recent = sorted(self.state.scores.keys(), key=int)[-5:]
            for d in recent:
                s = self.state.scores[d]
                status = c(Color.BRIGHT_GREEN, 'PASS') if s.get("passed") else c(Color.BRIGHT_RED, 'FAIL')
                pct = s.get("pct", 0)
                print(f"    Day {d}: {s.get('score', 0)}/{s.get('max_score', 100)} ({pct:.0f}%) {status}")
        print()

    def do_exchange(self, arg: str):
        """Display mock exchange status. Usage: exchange"""
        if self.exchange.is_running():
            status = self.exchange.status()
            print(f"  {c(Color.BRIGHT_GREEN, '[' + BoxChars.CHECK + ']')} Exchange running")
            print(f"    Host: {status['host']}:{status['port']}")
            print(f"    Ticks: {status['tick']}")
            print(f"    Symbols: {', '.join(status['symbols'])}")
        else:
            print(f"  {c(Color.YELLOW, 'Exchange not running.')}")
        print()

    def do_audit(self, arg: str):
        """Run AST audit on the current solution file. Usage: audit"""
        day = self.state.current_day
        sol_path = self.workspace.get_user_solution_path(day)

        if not os.path.exists(sol_path):
            print(f"  {c(Color.ERROR, 'No solution file for Day ' + str(day))}")
            return

        with open(sol_path, "r", encoding="utf-8") as f:
            code = f.read()

        auditor = CodeAuditor()
        issues = auditor.audit(code, sol_path)
        summary = auditor.summary()

        print(f"  {c(Color.BRIGHT_WHITE, 'AST AUDIT RESULTS — Day ' + str(day))}")
        print(f"  {muted('File: ' + sol_path)}")
        print(f"  {muted('Critical: ' + str(summary['critical']) + ', Warnings: ' + str(summary['warning']) + ', Info: ' + str(summary['info']))}")
        print()

        if not issues:
            print(f"  {c(Color.BRIGHT_GREEN, '[' + BoxChars.CHECK + '] No issues found.')}")
        else:
            for issue in issues:
                sev = issue["severity"]
                line = issue.get("line", "?")
                msg = issue["message"]
                if sev == CodeAuditor.ISSUE_CRITICAL:
                    print(f"  {c(Color.FAIL, 'CRITICAL')} L{line}: {msg}")
                elif sev == CodeAuditor.ISSUE_WARNING:
                    print(f"  {c(Color.YELLOW, 'WARNING')} L{line}: {msg}")
                else:
                    print(f"  {c(Color.INFO, 'INFO')} L{line}: {msg}")
        print()

    def do_ledger(self, arg: str):
        """Display ledger summary. Usage: ledger"""
        try:
            self.ledger.connect()
            accounts = self.ledger.get_account_balances()
            trades = self.ledger.get_trades()
            balanced, diff = self.ledger.verify_double_entry()

            print(f"  {c(Color.BRIGHT_WHITE, 'LEDGER SUMMARY')}")
            print(f"  {muted('Database: ' + self.state.ledger_db)}")
            print()
            print(f"  {c(Color.BRIGHT_CYAN, 'Account Balances:')}")
            for acc in accounts:
                bal_str = f"${acc['balance']:>10.2f}"
                print(f"    {acc['code']:6s} {acc['name']:25s} {acc['type']:10s} "
                      f"{c(Color.BRIGHT_WHITE, bal_str)}")
            print()
            print(f"  Trades logged: {len(trades)}")
            print(f"  Double-entry balanced: {c(Color.BRIGHT_GREEN if balanced else Color.FAIL, str(balanced))}")
            if not balanced:
                print(f"  Difference: ${diff:.2f}")
            print()
            self.ledger.close()
        except Exception as e:
            print(f"  {c(Color.ERROR, 'Ledger error: ' + str(e))}")

    def do_risk(self, arg: str):
        """Display risk report. Usage: risk"""
        try:
            self.ledger.connect()
            cb = self.risk_mgr.check_circuit_breaker(self.state.current_day)
            print(self.risk_mgr.risk_report(self.state.current_day))
            if cb:
                print(f"  {c(Color.FAIL, 'WARNING: Circuit breaker is active. Trading halted.')}")
                risk_reset_msg = 'Run "risk_reset" to clear if you have resolved the issue.'
                print(f"  {c(Color.WARN, risk_reset_msg)}")
            self.ledger.close()
        except Exception as e:
            print(f"  {c(Color.ERROR, 'Risk report error: ' + str(e))}")

    def do_risk_reset(self, arg: str):
        """Reset circuit breaker. Usage: risk_reset"""
        self.risk_mgr.halted = False
        self.risk_mgr.halt_reason = None
        self.risk_mgr.equity_curve = [RiskManager.INITIAL_CAPITAL]
        self.risk_mgr.returns = []
        print(f"  {c(Color.BRIGHT_GREEN, '[v] Circuit breaker reset. Risk metrics cleared.')}")

    def do_backtest(self, arg: str):
        """Run Monte Carlo backtest on the current solution. Usage: backtest [iterations=30] [days=30]"""
        day = self.state.current_day
        sol_path = self.workspace.get_user_solution_path(day)
        if not os.path.exists(sol_path):
            print(f"  {c(Color.ERROR, 'No solution file for Day ' + str(day))}")
            return

        args = arg.split()
        iterations = int(args[0]) if len(args) > 0 else 30
        days = int(args[1]) if len(args) > 1 else 30

        print(f"  {info(f'Running Monte Carlo backtest: {iterations} iterations x {days} days...')}")
        print(f"  {muted('This may take a while. Each iteration runs in a subprocess.')}")
        print()

        # Capture current price regime
        if self.exchange.is_running():
            self.backtest.capture_price_series(self.exchange.price_gen)

        results = self.backtest.run_monte_carlo(sol_path, iterations, days)

        print(f"  {c(Color.BRIGHT_WHITE, 'MONTE CARLO BACKTEST RESULTS')}")
        print(f"  {muted('=' * 50)}")
        print(f"  Iterations: {results['iterations']}  |  Days per run: {results['days_per_iteration']}")
        print(f"  {c(Color.BRIGHT_CYAN, 'Equity Distribution:')}")
        print(f"    Mean:    ${results['mean_final_equity']:>10,.2f}")
        print(f"    Median:  ${results['median_final_equity']:>10,.2f}")
        print(f"    Std:     ${results['std_final_equity']:>10,.2f}")
        print(f"    P10:     ${results['p10_final_equity']:>10,.2f}")
        print(f"    P90:     ${results['p90_final_equity']:>10,.2f}")
        print(f"    Min:     ${results['min_final_equity']:>10,.2f}")
        print(f"    Max:     ${results['max_final_equity']:>10,.2f}")
        print(f"  {c(Color.BRIGHT_CYAN, 'Risk Metrics (distribution across runs):')}")
        print(f"    Mean Sharpe:    {results['mean_sharpe']:.3f}")
        print(f"    Median Sharpe:  {results['median_sharpe']:.3f}")
        print(f"    Mean Max DD:    {results['mean_max_dd']*100:.2f}%")
        print(f"    Mean Win Rate:  {results['mean_win_rate']*100:.1f}%")
        print(f"    Sharpe > 1.0:   {results['sharpe_gt_1_pct']:.1f}% of runs")
        print()

    def do_reset(self, arg: str):
        """Reset all progress (WARNING: loses all data). Usage: reset"""
        print(f"  {c(Color.FAIL, 'WARNING: This will erase all training progress.')}")
        print(f"  {c(Color.BRIGHT_RED, 'Type: YES, RESET ALL PROGRESS')} to confirm.")
        print(f"  {muted('Type anything else to cancel.')}")
        # We can't easily get interactive input in cmd, so just ask
        # We'll handle this via the pre/post loop
        self._pending_reset = True
        cancel_msg = 'Cancelled. Use "reset_confirm" to execute reset.'
        print(f"  {warn(cancel_msg)}")

    def do_reset_confirm(self, arg: str):
        """Confirm and execute reset. Usage: reset_confirm"""
        self.state.reset()
        self.ledger.connect()
        self.ledger.clear_all()
        self.ledger.close()

        # Remove workspace
        if os.path.exists(self.workspace.base_dir):
            shutil.rmtree(self.workspace.base_dir, ignore_errors=True)

        # Remove old ledger
        if os.path.exists(self.state.ledger_db):
            os.remove(self.state.ledger_db)

        print(f"  {c(Color.BRIGHT_RED, 'ALL PROGRESS RESET.')}")
        reset_msg = 'Type "start" to begin again from Day 1.'
        print(f"  {c(Color.BRIGHT_WHITE, reset_msg)}")

    def do_help(self, arg: str):
        """Show available commands."""
        commands = [
            ("start", "Begin the current day's training"),
            ("eod", "End-of-Day evaluation (17:00 close)"),
            ("advance", "Advance to next day (must score 100)"),
            ("run", "Run today's solution file"),
            ("audit", "AST audit today's solution"),
            ("ledger", "Show SQLite ledger status"),
            ("risk", "Display risk report (VaR/CVaR/circuit breaker)"),
            ("risk_reset", "Reset circuit breaker and risk metrics"),
            ("backtest", "Monte Carlo backtest [iters=30] [days=30]"),
            ("exchange", "Show mock exchange status"),
            ("status", "Show training progress"),
            ("reset", "Reset all training progress"),
            ("quit/exit", "Exit the simulator"),
        ]
        print(f"\n  {c(Color.BRIGHT_WHITE, 'AVAILABLE COMMANDS')}")
        print(f"  {muted('-' * 50)}")
        for cmd_name, desc in commands:
            print(f"    {c(Color.BRIGHT_CYAN, cmd_name + ' ' * (14 - len(cmd_name)))} {desc}")
        print()

    def do_quit(self, arg: str):
        """Exit the simulator."""
        print(f"  {muted('Shutting down...')}")
        if self.exchange.is_running():
            self.exchange.stop()
        if self.ledger.conn:
            self.ledger.close()
        self.state.save()
        print(f"  {c(Color.BRIGHT_GREEN, 'State saved. Goodbye.')}")
        self.running = False
        return True

    def do_exit(self, arg: str):
        """Exit the simulator."""
        return self.do_quit(arg)

    def do_EOF(self, arg: str):
        """Exit on Ctrl+D/Ctrl+Z."""
        print()
        return self.do_quit(arg)

    def emptyline(self):
        """Do nothing on empty line."""
        pass

    def precmd(self, line: str) -> str:
        """Pre-process command - lowercase for consistency."""
        line = line.strip()
        if line.upper() == "EOD":
            return "eod"
        if line.upper() == "EOF":
            return "EOF"
        return line

    def postcmd(self, stop: bool, line: str) -> bool:
        """After command, check if we should stop."""
        if stop:
            return True
        return not self.running


# ==============================================================================
# SECTION 10 — WEB UI SERVER (Port 8081)
# ==============================================================================

# Global application context shared between CLI and WebUI
app_context = {
    "cli": None,        # Set by CLI on init
    "web_running": False,
}


class WebUIHandler(BaseHTTPRequestHandler):
    """Serves the HTML dashboard UI and REST API on port 8081."""

    def log_message(self, fmt, *args):
        pass  # Suppress logs

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, msg: str, status: int = 400):
        self._send_json({"error": msg}, status)

    def _get_cli(self):
        cli = app_context.get("cli")
        if not cli:
            self._send_error("CLI not initialized", 500)
            return None
        return cli

    def _read_body(self) -> Dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        # ── API endpoints ─────────────────────────────────────────
        if path == "/" or path == "":
            self._send_html(HTML_DASHBOARD)
        elif path == "/api/status":
            self._handle_api_status()
        elif path == "/api/briefing":
            self._handle_api_briefing()
        elif path == "/api/solution":
            day = int(params.get("day", [0])[0]) if params.get("day") else 0
            self._handle_api_solution(day)
        elif path == "/api/ledger":
            self._handle_api_ledger()
        elif path == "/api/audit":
            self._handle_api_audit()
        elif path == "/api/exchange":
            self._handle_api_exchange()
        elif path == "/api/results":
            self._handle_api_results()
        elif path == "/api/ticker":
            self._handle_api_ticker()
        elif path == "/api/orderbook":
            symbol = params.get("symbol", ["BTC/USD"])[0]
            self._handle_api_orderbook(symbol)
        else:
            self._send_error("Not found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        handlers = {
            "/api/start": self._handle_api_start,
            "/api/eod": self._handle_api_eod,
            "/api/advance": self._handle_api_advance,
            "/api/run": self._handle_api_run,
            "/api/save": self._handle_api_save,
        }
        if path in handlers:
            handlers[path]()
        else:
            self._send_error("Not found", 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── API Handlers ──────────────────────────────────────────────

    def _get_day_solution_text(self, day: int) -> str:
        """Read the solution file for a given day."""
        if not app_context.get("cli"):
            return ""
        ws = app_context["cli"].workspace
        path = ws.get_user_solution_path(day)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _get_briefing_text(self, day: int) -> str:
        """Read the DAILY_BRIEF.md for a given day."""
        ws_path = os.path.join("workspace", f"day_{day:03d}", "DAILY_BRIEF.md")
        if os.path.exists(ws_path):
            with open(ws_path, "r", encoding="utf-8") as f:
                return f.read()
        return "# No briefing generated."

    def _handle_api_status(self):
        cli = self._get_cli()
        if not cli:
            return
        s = cli.state
        scores_list = []
        for d_key in sorted(s.scores.keys(), key=int):
            sc = s.scores[d_key]
            scores_list.append({
                "day": int(d_key),
                "score": sc.get("score", 0),
                "max_score": sc.get("max_score", 100),
                "pct": sc.get("pct", 0),
                "passed": sc.get("passed", False),
            })
        data = {
            "current_day": s.current_day,
            "phase": s.phase,
            "phase_name": s.phase_name,
            "completed_days": len(s.completed_days),
            "total_days": 90,
            "total_score": s.total_score,
            "max_score": max(s.max_score, 1),
            "scores": scores_list,
            "exchange_running": cli.exchange.is_running(),
            "web_port": 8081,
            "exchange_port": 8080,
            "has_workspace": cli.day_workspace_dir is not None,
        }
        self._send_json(data)

    def _handle_api_briefing(self):
        cli = self._get_cli()
        if not cli:
            return
        day = cli.state.current_day
        text = self._get_briefing_text(day)
        self._send_json({"day": day, "briefing": text})

    def _handle_api_solution(self, day: int):
        cli = self._get_cli()
        if not cli:
            return
        if day <= 0:
            day = cli.state.current_day
        text = self._get_day_solution_text(day)
        ws_path = os.path.join("workspace", f"day_{day:03d}",
                               f"solution_day_{day:03d}.py")
        exists = os.path.exists(ws_path)
        self._send_json({
            "day": day,
            "code": text,
            "exists": exists,
            "path": ws_path if exists else "",
        })

    def _handle_api_ledger(self):
        cli = self._get_cli()
        if not cli:
            return
        try:
            led = cli.ledger
            led.connect()
            accounts = led.get_account_balances()
            trades = led.get_trades()
            balanced, diff = led.verify_double_entry()
            pnl = led.calculate_pnl(cli.state.current_day) if trades else []
            led.close()
            self._send_json({
                "accounts": accounts,
                "trade_count": len(trades),
                "balanced": balanced,
                "difference": round(diff, 2),
                "pnl": pnl,
            })
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_api_audit(self):
        cli = self._get_cli()
        if not cli:
            return
        day = cli.state.current_day
        sol_path = cli.workspace.get_user_solution_path(day)
        if not os.path.exists(sol_path):
            self._send_json({"issues": [], "summary": {}, "error": "No solution file"})
            return
        with open(sol_path, "r", encoding="utf-8") as f:
            code = f.read()
        auditor = CodeAuditor()
        issues = auditor.audit(code, sol_path)
        summary = auditor.summary()
        self._send_json({
            "issues": issues,
            "summary": summary,
            "has_critical": auditor.has_critical_issues(),
        })

    def _handle_api_exchange(self):
        cli = self._get_cli()
        if not cli:
            return
        if cli.exchange.is_running():
            st = cli.exchange.status()
            self._send_json({"running": True, **st})
        else:
            self._send_json({"running": False})

    def _handle_api_results(self):
        cli = self._get_cli()
        if not cli:
            return
        s = cli.state
        results = []
        for d_key in sorted(s.scores.keys(), key=int):
            sc = s.scores[d_key]
            results.append({
                "day": int(d_key),
                "score": sc.get("score", 0),
                "max_score": sc.get("max_score", 100),
                "pct": sc.get("pct", 0),
                "passed": sc.get("passed", False),
                "violations": sc.get("violations", []),
                "ast_issues": sc.get("ast_issues", []),
                "ledger_balanced": sc.get("ledger_balanced", True),
            })
        self._send_json({"results": results})

    def _handle_api_ticker(self):
        """Quick live ticker for the dashboard."""
        cli = self._get_cli()
        if not cli or not cli.exchange.is_running():
            self._send_json({"running": False})
            return
        pg = cli.exchange.price_gen
        prices = {}
        for sym in pg.prices:
            prices[sym] = round(pg.prices[sym], 2)
        self._send_json({"running": True, "tick": pg.tick, "prices": prices})

    def _handle_api_orderbook(self, symbol: str):
        cli = self._get_cli()
        if not cli:
            return
        if not cli.exchange.is_running():
            self._send_json({"error": "Exchange not running"}, 503)
            return
        try:
            pg = cli.exchange.price_gen
            ob = pg.get_orderbook(symbol)
            ob["regime"] = pg.current_regime
            ob["regime_name"] = "LOW_VOL_TRENDING" if pg.current_regime == 0 else "HIGH_VOL_REGIME"
            ob["tick"] = pg.tick
            for sym in pg.prices:
                ob["price_" + sym.replace("/", "_")] = round(pg.prices[sym], 2)
            self._send_json(ob)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_api_start(self):
        cli = self._get_cli()
        if not cli:
            return
        try:
            cli.onecmd("start")
            self._send_json({"success": True, "message": f"Day {cli.state.current_day} started"})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_api_eod(self):
        cli = self._get_cli()
        if not cli:
            return
        try:
            cli.onecmd("eod")
            self._send_json({"success": True, "message": "EOD evaluation complete"})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_api_advance(self):
        cli = self._get_cli()
        if not cli:
            return
        try:
            if cli.state.can_advance():
                cli.state.advance_day()
                self._send_json({"success": True, "day": cli.state.current_day})
            else:
                self._send_json({"error": "Cannot advance - day not passed"}, 400)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_api_run(self):
        cli = self._get_cli()
        if not cli:
            return
        body = self._read_body()
        args = body.get("args", "")
        day = cli.state.current_day
        sol_path = cli.workspace.get_user_solution_path(day)
        if not os.path.exists(sol_path):
            self._send_json({"error": "No solution file"}, 404)
            return
        try:
            result = subprocess.run(
                [sys.executable, sol_path] + args.split(),
                capture_output=True, text=True, timeout=30,
                cwd=os.path.dirname(sol_path),
            )
            self._send_json({
                "stdout": result.stdout[:5000],
                "stderr": result.stderr[:2000],
                "exit_code": result.returncode,
                "success": result.returncode == 0,
            })
        except subprocess.TimeoutExpired:
            self._send_json({"error": "Execution timed out (>30s)"}, 408)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_api_save(self):
        cli = self._get_cli()
        if not cli:
            return
        body = self._read_body()
        code = body.get("code", "")
        day = cli.state.current_day
        sol_path = cli.workspace.get_user_solution_path(day)
        if not sol_path:
            self._send_json({"error": "No workspace"}, 404)
            return
        os.makedirs(os.path.dirname(sol_path), exist_ok=True)
        with open(sol_path, "w") as f:
            f.write(code)
        self._send_json({"success": True, "path": sol_path})


class WebUIServer:
    """Threaded HTTP server for the HTML dashboard on port 8081."""

    def __init__(self, port: int = 8081):
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False

    def start(self) -> bool:
        if self.running:
            return True
        try:
            self.server = HTTPServer(("0.0.0.0", self.port), WebUIHandler)
            self.thread = threading.Thread(target=self.server.serve_forever,
                                           daemon=True)
            self.thread.start()
            self.running = True
            return True
        except OSError as e:
            print(f"  {c(Color.ERROR, f'[FAIL] Web UI on :{self.port}: {e}')}")
            return False

    def stop(self):
        if self.server and self.running:
            self.server.shutdown()
            self.running = False


HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NovaCap Principal Strategist — Terminal Dashboard</title>
<style>
  :root {
    --bg-primary: #0A0E17;
    --bg-surface: #1A2235;
    --bg-elevated: #222B40;
    --bg-input: #121A2A;
    --border: rgba(255,255,255,0.08);
    --border-subtle: rgba(255,255,255,0.04);
    --text-primary: #C8D0DC;
    --text-secondary: #8892A6;
    --text-muted: #5A6478;
    --accent: #4A90D9;
    --positive: #34B77A;
    --negative: #D45A5A;
    --warning: #C9A84C;
    --positive-bg: rgba(52,183,122,0.08);
    --negative-bg: rgba(212,90,90,0.08);
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 24px;
    --font-data: 'JetBrains Mono','Cascadia Code','Fira Code','Consolas',monospace;
    --font-ui: 'Inter','Segoe UI',-apple-system,BlinkMacSystemFont,sans-serif;
  }
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%;overflow:hidden}
  body{font-family:var(--font-ui);background:var(--bg-primary);color:var(--text-primary);font-size:12px;line-height:1.5;display:flex;flex-direction:column}
  a{color:var(--accent);text-decoration:none}
  ::-webkit-scrollbar{width:var(--space-1);height:var(--space-1)}
  ::-webkit-scrollbar-track{background:transparent}
  ::-webkit-scrollbar-thumb{background:var(--text-muted)}

  /* ── Header ── */
  .header{background:var(--bg-surface);border-bottom:1px solid var(--border);padding:0 var(--space-5);
          display:flex;align-items:center;justify-content:space-between;
          flex-shrink:0;height:44px}
  .header-left{display:flex;align-items:center;gap:var(--space-5)}
  .logo{font-size:12px;font-weight:700;color:var(--text-primary);letter-spacing:0.3px}
  .header-right{display:flex;align-items:center;gap:var(--space-4)}
  .header-clock{font-size:11px;color:var(--text-muted);font-variant-numeric:tabular-nums;font-family:var(--font-data)}
  .day-badge{display:inline-block;padding:2px 8px;font-size:10px;font-weight:500;color:var(--text-secondary);border:1px solid var(--border)}
  .day-badge.active{color:var(--positive);border-color:rgba(52,183,122,0.2)}
  .day-badge.idle{color:var(--text-secondary);border-color:var(--border)}
  .phase-text{font-size:10px;color:var(--text-muted);font-weight:500}

  /* ── Layout ── */
  .main{display:flex;flex:1;overflow:hidden}

  /* ── Sidebar ── */
  .sidebar{width:180px;min-width:180px;background:var(--bg-primary);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden}
  .sidebar-title{padding:var(--space-4) var(--space-4) var(--space-2);font-size:9px;color:var(--text-muted);font-weight:600}
  .sidebar-nav{flex:1;overflow-y:auto;padding:var(--space-1) var(--space-2)}
  .nav-item{padding:7px 10px;margin:1px 0;cursor:pointer;font-size:11px;color:var(--text-muted);transition:background 0.1s;display:flex;align-items:center;gap:8px;font-weight:500;border-left:2px solid transparent}
  .nav-item:hover{background:rgba(255,255,255,0.03);color:var(--text-secondary)}
  .nav-item.active{background:rgba(74,144,217,0.06);color:var(--accent);border-left-color:var(--accent)}
  .nav-item .icon{font-size:10px;width:16px;text-align:center;opacity:0.5}
  .nav-item.active .icon{opacity:1}
  .nav-item .badge{font-size:8px;padding:1px 5px;background:var(--bg-elevated);color:var(--text-muted);margin-left:auto;font-weight:600}
  .nav-item .badge.pass{background:var(--positive-bg);color:var(--positive)}
  .nav-item .badge.fail{background:var(--negative-bg);color:var(--negative)}

  /* ── Content ── */
  .content{flex:1;overflow-y:auto;padding:var(--space-4) var(--space-5)}

  /* ── Card Containers ── */
  .card{background:var(--bg-surface);border:1px solid var(--border);padding:var(--space-4)}
  .card-title{font-size:10px;font-weight:600;color:var(--text-primary);margin-bottom:var(--space-3);display:flex;align-items:center;gap:var(--space-2);padding-bottom:var(--space-2);border-bottom:1px solid var(--border)}
  .card-title .accent{display:inline-block;width:2px;height:12px;background:var(--accent);margin-right:6px;vertical-align:middle}

  /* ── Section Titles (legacy) ── */
  .dash-section-title{font-size:10px;font-weight:600;color:var(--text-primary);margin-bottom:var(--space-3);display:flex;align-items:center;gap:var(--space-2);padding-bottom:var(--space-2);border-bottom:1px solid var(--border)}
  .dash-section-title .accent{display:inline-block;width:2px;height:12px;background:var(--accent);margin-right:6px;vertical-align:middle}

  /* ── Dashboard Grid ── */
  .dash-grid{display:grid;grid-template-columns:1.2fr 1fr;gap:14px;align-items:start;margin-bottom:var(--space-4)}
  @media(max-width:1000px){.dash-grid{grid-template-columns:1fr}}

  /* ── Market Overview ── */
  .mkt-grid{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-3)}
  .mkt-card{background:var(--bg-surface);border:1px solid var(--border);padding:var(--space-4) var(--space-4);position:relative}
  .mkt-sym{font-size:9px;color:var(--text-muted);font-weight:600}
  .mkt-price{font-size:24px;font-weight:700;color:var(--text-primary);margin:var(--space-2) 0 var(--space-3);font-family:var(--font-data);font-variant-numeric:tabular-nums;letter-spacing:-0.5px;line-height:1.1}
  .mkt-chg{font-size:11px;font-weight:600;margin-left:var(--space-2);font-family:var(--font-data)}
  .mkt-chg.up{color:var(--positive)}
  .mkt-chg.down{color:var(--negative)}
  .mkt-details{display:flex;flex-direction:column;gap:var(--space-1)}
  .mkt-row{display:flex;justify-content:space-between;align-items:center;padding:4px 6px;font-size:10px;background:var(--bg-primary);border-left:2px solid var(--border-subtle);transition:border-color 0.1s}
  .mkt-row:hover{border-left-color:rgba(255,255,255,0.1)}
  .mkt-lbl{color:var(--text-muted);font-weight:500}
  .mkt-val{color:var(--text-primary);font-weight:500;font-family:var(--font-data);font-size:10px;margin-left:auto;margin-left:8px}
  .mkt-val.reg-trend{color:var(--positive)}
  .mkt-val.reg-vol{color:var(--warning)}

  /* ── Portfolio ── */
  .pf-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px 12px;margin-bottom:var(--space-3)}
  .pf-item{display:flex;justify-content:space-between;padding:6px 10px;font-size:10px;background:rgba(6,10,20,0.4);border:1px solid rgba(50,70,110,0.15)}
  .pf-lbl{color:var(--text-muted);font-weight:500}
  .pf-val{color:var(--text-primary);font-weight:600;font-family:var(--font-data);font-size:10px;margin-left:var(--space-2)}
  .pf-val.green{color:var(--positive)}
  .pf-val.red{color:var(--negative)}
  .pf-val.blue{color:var(--accent)}
  .pf-val.gold{color:var(--warning)}
  .pf-bar{height:2px;background:var(--bg-elevated);margin:var(--space-2) 0 var(--space-1)}
  .pf-bar .fill{height:100%;transition:width 0.1s}
  .pf-bar .fill.green{background:var(--positive)}
  .pf-bar .fill.yellow{background:var(--warning)}
  .pf-bar .fill.red{background:var(--negative)}
  .pf-stats{display:flex;justify-content:space-between;padding:0 var(--space-1);font-size:9px;color:var(--text-muted);font-family:var(--font-data)}

  /* ── Order Book ── */
  .ob-table{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  .ob-side{background:var(--bg-surface);padding:var(--space-2) var(--space-2);border:1px solid var(--border)}
  .ob-header{font-size:9px;color:var(--positive);font-weight:600;margin-bottom:var(--space-2);padding-bottom:var(--space-1);border-bottom:1px solid rgba(52,183,122,0.15)}
  .ob-header.asks-hdr{color:var(--negative);border-bottom-color:rgba(212,90,90,0.15)}
  .ob-row{display:flex;justify-content:space-between;align-items:center;padding:6px 8px;font-size:11px;font-family:var(--font-data);background:rgba(4,8,16,0.3);margin-bottom:2px;transition:background 0.1s}
  .ob-row:hover{background:rgba(255,255,255,0.03)}
  .ob-price{color:var(--accent);font-weight:600}
  .ob-size{color:var(--text-primary);text-align:right}
  .ob-src{color:var(--text-muted);font-size:9px}
  .ob-empty{padding:var(--space-3) 0;color:var(--text-muted);font-size:10px;text-align:center}
  .ob-foot{margin-top:var(--space-2);font-size:9px;color:var(--text-muted);font-family:var(--font-data);text-align:center}

  /* ── Depth Bars ── */
  .depth-bar-wrap{flex:1;height:8px;background:var(--bg-primary);overflow:hidden;margin:0 2px;min-width:24px}
  .depth-bar{height:100%;transition:width 0.1s}
  .depth-bar.bid{background:rgba(52,183,122,0.15)}
  .depth-bar.ask{background:rgba(212,90,90,0.15)}

  /* ── Actions ── */
  .btn-group{display:flex;gap:var(--space-2);flex-wrap:wrap}
  .btn{padding:6px 14px;font-size:10px;font-weight:600;cursor:pointer;transition:background 0.1s;background:#2A3550;color:#B0B8C8;border:1px solid rgba(255,255,255,0.12)}
  .btn:hover{background:#354566;color:#E0E4EC;border-color:rgba(255,255,255,0.2)}
  .btn:disabled{opacity:0.3;cursor:not-allowed}
  .btn-primary{background:#2A4570;color:#7AB5F0;border-color:rgba(74,144,217,0.25)}
  .btn-primary:hover{background:#355A8A;color:#8EC4F8;border-color:rgba(74,144,217,0.4)}
  .btn-danger{background:#502A2A;color:#E89090;border-color:rgba(212,90,90,0.25)}
  .btn-danger:hover{background:#6A3535;color:#F0A0A0;border-color:rgba(212,90,90,0.4)}
  .btn-success{background:#2A5035;color:#80D0A0;border-color:rgba(52,183,122,0.25)}
  .btn-success:hover{background:#356A44;color:#90E0B0;border-color:rgba(52,183,122,0.4)}
  .btn-warning{background:#504A2A;color:#E0D080;border-color:rgba(201,168,76,0.25)}
  .btn-warning:hover{background:#6A5E35;color:#F0E090;border-color:rgba(201,168,76,0.4)}

  /* ── Score Rows ── */
  .score-row{display:flex;justify-content:space-between;align-items:center;padding:6px 8px;font-size:10px;border:1px solid var(--border);margin-bottom:var(--space-1);background:var(--bg-surface)}
  .score-row:last-child{margin-bottom:0}
  .score-day{color:var(--text-muted);font-weight:500}
  .score-val{color:var(--text-primary);font-weight:600;font-family:var(--font-data);font-size:10px}
  .tag{display:inline-block;padding:1px 8px;font-size:9px;font-weight:600}
  .tag-pass{background:var(--positive-bg);color:var(--positive)}
  .tag-fail{background:var(--negative-bg);color:var(--negative)}

  /* ── Change indicator (inline, no pill) ── */
  .chg{font-family:var(--font-data);font-size:11px;font-weight:600;margin-left:var(--space-1)}
  .chg.up{color:var(--positive)}
  .chg.down{color:var(--negative)}

  /* ── Change pill ── */
  .chg-pill{display:inline-block;padding:1px 6px;font-size:9px;font-weight:600;font-family:var(--font-data)}
  .chg-pill.up{background:var(--positive-bg);color:var(--positive);border:1px solid rgba(52,183,122,0.15)}
  .chg-pill.down{background:var(--negative-bg);color:var(--negative);border:1px solid rgba(212,90,90,0.15)}

  /* ── Briefing ── */
  .briefing-content{background:var(--bg-surface);border:1px solid var(--border);padding:var(--space-5);font-size:12px;line-height:1.7;color:var(--text-primary)}

  /* ── Results ── */
  .result-card{background:var(--bg-surface);border:1px solid var(--border);padding:var(--space-4);margin-bottom:var(--space-2)}
  .result-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--space-2)}
  .result-day{font-weight:600;color:var(--text-primary);font-size:11px}
  .result-score{font-size:16px;font-weight:700;font-family:var(--font-data)}
  .result-issues{margin-top:var(--space-2)}
  .result-ledger{margin-top:var(--space-1);font-size:10px}

  /* ── Code / Pre ── */
  .code-block{background:var(--bg-primary);border:1px solid var(--border);padding:var(--space-4);font-family:var(--font-data);font-size:11px;color:var(--text-secondary);white-space:pre-wrap;overflow:auto;max-height:500px;line-height:1.6}

  /* ── Issues ── */
  .issue-list{list-style:none;margin-top:var(--space-1)}
  .issue-item{padding:4px 8px;margin:1px 0;font-size:10px;border-left:2px solid transparent;font-family:var(--font-data);background:var(--bg-primary)}
  .issue-item.critical{background:var(--negative-bg);border-color:var(--negative);color:var(--negative)}
  .issue-item.warning{background:rgba(201,168,76,0.06);border-color:var(--warning);color:var(--warning)}
  .issue-item.info{background:rgba(74,144,217,0.06);border-color:var(--accent);color:var(--accent)}

  /* ── Ledger table ── */
  .table-wrap{overflow-x:auto;border:1px solid var(--border)}
  .ledger-table{width:100%;border-collapse:collapse;font-size:10px}
  .ledger-table th{text-align:left;padding:6px 8px;color:var(--text-muted);font-weight:600;font-size:9px;border-bottom:1px solid var(--border);background:var(--bg-primary)}
  .ledger-table td{padding:4px 8px;border-bottom:1px solid var(--border-subtle);color:var(--text-secondary)}
  .ledger-table tr:hover td{background:rgba(255,255,255,0.02)}
  .ledger-table .amt{font-family:var(--font-data);text-align:right}

  /* ── Code Editor ── */
  .editor-wrap{border:1px solid var(--border)}
  .editor-header{display:flex;justify-content:space-between;align-items:center;padding:6px 12px;background:var(--bg-surface);border-bottom:1px solid var(--border);font-size:9px;color:var(--text-muted)}
  .editor-body{display:flex}
  .editor-gutter{padding:12px 8px;background:var(--bg-primary);color:var(--text-muted);font-family:var(--font-data);font-size:11px;line-height:1.6;text-align:right;user-select:none;min-width:28px;border-right:1px solid var(--border)}
  .editor-area{flex:1}
  .editor-area textarea{width:100%;min-height:400px;background:var(--bg-input);color:var(--text-primary);border:none;padding:12px;font-family:var(--font-data);font-size:11px;line-height:1.6;resize:vertical;outline:none;tab-size:2}
  .editor-area textarea:focus{background:var(--bg-primary)}
  .editor-status{display:flex;justify-content:space-between;padding:4px 12px;background:var(--bg-surface);border-top:1px solid var(--border);font-size:8px;color:var(--text-muted);font-family:var(--font-data)}

  /* ── Loading / States ── */
  .loading{text-align:center;padding:80px 20px;color:var(--text-muted)}
  .spinner{display:inline-block;width:20px;height:20px;border:2px solid var(--border);border-top-color:var(--accent);margin-bottom:var(--space-3)}
  .empty{text-align:center;padding:50px 20px;color:var(--text-muted);font-size:11px}
  .toast{position:fixed;bottom:var(--space-5);right:var(--space-5);padding:8px 16px;font-size:11px;font-weight:500;z-index:1000;transform:translateY(80px);opacity:0;transition:opacity 0.15s,transform 0.15s;max-width:360px}
  .toast.show{transform:translateY(0);opacity:1}
  .toast.success{background:var(--bg-surface);color:var(--positive);border:1px solid rgba(52,183,122,0.3)}
  .toast.error{background:var(--bg-surface);color:var(--negative);border:1px solid rgba(212,90,90,0.3)}
  .toast.info{background:var(--bg-surface);color:var(--text-primary);border:1px solid var(--border)}

  /* ── Utilities ── */
  .flex{display:flex}.gap-8{gap:8px}.gap-12{gap:12px}.mt-8{margin-top:8px}.mt-12{margin-top:12px}
  .mb-12{margin-bottom:12px}.text-center{text-align:center}
  .text-muted{color:var(--text-muted)}
  .hidden{display:none}

  /* ── Responsive ── */
  @media(max-width:768px){.sidebar{display:none}.content{padding:var(--space-3)}}
</style>
</head>
<body>

<header class="header">
  <div class="header-left">
    <div class="logo"><span class="logo-dot"></span>NovaCap Principal Strategist</div>
    <span class="phase-text" id="phaseLabel">Phase 1: Data Ingestion</span>
  </div>
  <div class="header-right">
    <span class="header-clock" id="headerClock">--:--:--</span>
    <span id="dayBadge" class="day-badge idle">Day 1 / 90</span>
  </div>
</header>

<div class="main">
  <aside class="sidebar">
    <div class="sidebar-title">Navigation</div>
    <nav class="sidebar-nav" id="sidebarNav">
      <div class="nav-item active" data-view="dashboard" onclick="switchView('dashboard')">
        <span class="icon">&#9679;</span> Dashboard</div>
      <div class="nav-item" data-view="briefing" onclick="switchView('briefing')">
        <span class="icon">&#9998;</span> Briefing</div>
      <div class="nav-item" data-view="editor" onclick="switchView('editor')">
        <span class="icon">&#128187;</span> Editor</div>
      <div class="nav-item" data-view="results" onclick="switchView('results')">
        <span class="icon">&#128202;</span> Results</div>
      <div class="nav-item" data-view="ledger" onclick="switchView('ledger')">
        <span class="icon">&#128214;</span> Ledger</div>
      <div class="nav-item" data-view="audit" onclick="switchView('audit')">
        <span class="icon">&#9881;</span> Audit</div>
      <div class="nav-item" data-view="exchange" onclick="switchView('exchange')">
        <span class="icon">&#8644;</span> Exchange</div>
    </nav>
  </aside>

  <main class="content" id="mainContent">
    <div class="loading" id="initialLoad"><div class="spinner"></div><div>Connecting to Principal Strategist engine...</div></div>
  </main>
</div>

<div id="toast" class="toast"></div>

<script>
let appData = { scores: [], current_day: 1, phase: 1 };
let currentView = 'dashboard';
let pollingInterval = null;
let editorDirty = false;

async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
  const resp = await fetch(path, opts);
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || 'Request failed');
  return data;
}

let toastTimer = null;
function showToast(msg, type='info') {
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = 'toast toast-' + type + ' show';
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 3500);
}

function updateClock() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2,'0');
  const m = String(now.getMinutes()).padStart(2,'0');
  const s = String(now.getSeconds()).padStart(2,'0');
  const el = document.getElementById('headerClock');
  if (el) el.textContent = h + ':' + m + ':' + s;
}

function switchView(view) {
  currentView = view;
  document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.view === view));
  const c = document.getElementById('mainContent');
  c.classList.remove('view-enter');
  void c.offsetWidth;
  c.classList.add('view-enter');
  renderView(view);
}

function renderView(view) {
  const c = document.getElementById('mainContent');
  const renderers = {
    dashboard: renderDashboard, briefing: renderBriefing, editor: renderEditor,
    results: renderResults, ledger: renderLedger, audit: renderAudit, exchange: renderExchange,
  };
  if (renderers[view]) renderers[view]();
  else c.innerHTML = '<div class="empty">Unknown view</div>';
}

async function renderDashboard() {
  const c = document.getElementById('mainContent');
  c.innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading terminal data...</div></div>';
  try {
    let status, ticker, ob;
    try { status = await api('GET', '/api/status'); } catch (e) { status = { current_day: 1, total_score: 0, max_score: 1, completed_days: 0, scores: [], phase: 1 }; }
    try { ticker = await api('GET', '/api/ticker'); } catch (e) { ticker = { running: false, prices: {} }; }
    try { ob = await api('GET', '/api/orderbook'); } catch (e) { ob = { bids: [], asks: [] }; }
    appData = status;
    const pct = status.max_score > 0 ? (status.total_score / status.max_score * 100) : 0;
    const barColor = pct >= 80 ? 'green' : pct >= 50 ? 'yellow' : 'red';
    const phaseLabel = status.phase === 1 ? 'Data Ingestion' : status.phase === 2 ? 'Arbitrage Logic' : 'Slippage & SOCPA';
    const pnl = status.total_score - (status.max_score - status.total_score) * 0.5;
    const pnlColor = pnl >= 0 ? 'green' : 'red';
    const running = ticker.running;

    function mktCard(symRaw, price, bid, ask, spread, regime) {
      const sym = symRaw.replace(/_/, '/');
      const chg = ((Math.random() - 0.47) * 1.6).toFixed(2);
      const up = parseFloat(chg) >= 0;
      return '<div class="mkt-card">' +
        '<div class="mkt-sym">' + sym + '</div>' +
        '<div class="mkt-price">$' + (price || 0).toLocaleString(undefined, {minimumFractionDigits: 2}) +
          ' <span class="mkt-chg ' + (up ? 'up' : 'down') + '">' + (up ? '&#9650;' : '&#9660;') + ' ' + Math.abs(parseFloat(chg)) + '%</span></div>' +
        '<div class="mkt-details">' +
        '<div class="mkt-row"><span class="mkt-lbl">Bid</span><span class="mkt-val">$' + (bid || 0).toLocaleString(undefined, {minimumFractionDigits: 2}) + '</span></div>' +
        '<div class="mkt-row"><span class="mkt-lbl">Ask</span><span class="mkt-val">$' + (ask || 0).toLocaleString(undefined, {minimumFractionDigits: 2}) + '</span></div>' +
        '<div class="mkt-row"><span class="mkt-lbl">Spread</span><span class="mkt-val">' + (spread || 0).toFixed(2) + ' bps</span></div>' +
        '<div class="mkt-row"><span class="mkt-lbl">Regime</span><span class="mkt-val">' + regime + '</span></div>' +
        '</div></div>';
    }

    function obRows(side, limit) {
      if (!ob || !ob[side] || ob[side].length === 0) return '<div class="ob-empty">No depth data</div>';
      return ob[side].slice(0, limit || 4).map(function(r) {
        return '<div class="ob-row"><span class="ob-price">$' + (r.price || 0).toFixed(2) + '</span><span class="ob-size">' + (r.quantity || 0).toFixed(3) + '</span><span class="ob-src">PRIMARY</span></div>';
      }).join('');
    }

    let scoresHtml = '';
    const recent = status.scores.slice(-5).reverse();
    if (recent.length > 0) {
      scoresHtml = recent.map(function(s) {
        return '<div class="score-row"><span class="score-day">Day ' + s.day + '</span><span class="score-val">' + s.score + '/' + s.max_score + '</span><span class="tag ' + (s.passed ? 'tag-pass' : 'tag-fail') + '">' + (s.passed ? 'PASS' : 'FAIL') + '</span></div>';
      }).join('');
    } else {
      scoresHtml = '<div class="text-muted" style="padding:8px">No evaluations yet</div>';
    }

    const tp = ticker.prices || {};
    const btcBid = ob.bids && ob.bids[0] ? ob.bids[0].price : (tp.BTC_USD || 0) * 0.999;
    const btcAsk = ob.asks && ob.asks[0] ? ob.asks[0].price : (tp.BTC_USD || 0) * 1.001;
    const ethBid = tp.ETH_USDT ? tp.ETH_USDT * 0.998 : 0;
    const ethAsk = tp.ETH_USDT ? tp.ETH_USDT * 1.002 : 0;

    c.innerHTML =
      '<div class="dash-grid">' +
        '<div class="card">' +
          '<div class="card-title"><span class="accent"></span>Market Overview</div>' +
          '<div class="mkt-grid">' +
            (running ? mktCard('BTC_USD', ob.price_BTC_USD || tp.BTC_USD, btcBid, btcAsk, ob.spread_bps || 11.0, ob.regime_name || 'LOW_VOL_TRENDING') : '<div class="mkt-card"><div class="text-muted">Exchange offline</div></div>') +
            (running && tp.ETH_USDT ? mktCard('ETH_USDT', ob.price_ETH_USDT || tp.ETH_USDT, ethBid, ethAsk, 14.5, ob.regime_name || 'LOW_VOL_TRENDING') : '') +
          '</div>' +
        '</div>' +
        '<div class="card">' +
          '<div class="card-title"><span class="accent"></span>Portfolio Matrix</div>' +
          '<div class="pf-grid">' +
            '<div class="pf-item"><span class="pf-lbl">Equity</span><span class="pf-val blue">$102,345</span></div>' +
            '<div class="pf-item"><span class="pf-lbl">P&amp;L</span><span class="pf-val ' + pnlColor + '">' + (pnl >= 0 ? '+' : '') + '$' + pnl.toFixed(2) + '</span></div>' +
            '<div class="pf-item"><span class="pf-lbl">VaR(95%)</span><span class="pf-val">1.23%</span></div>' +
            '<div class="pf-item"><span class="pf-lbl">Drawdown</span><span class="pf-val gold">2.34%</span></div>' +
            '<div class="pf-item"><span class="pf-lbl">Leverage</span><span class="pf-val">0.44x</span></div>' +
            '<div class="pf-item"><span class="pf-lbl">Positions</span><span class="pf-val">12</span></div>' +
            '<div class="pf-item"><span class="pf-lbl">Circuit</span><span class="pf-val green">INACTIVE</span></div>' +
            '<div class="pf-item"><span class="pf-lbl">Evaluation Score</span><span class="pf-val blue">' + status.total_score + '/' + status.max_score + '</span></div>' +
          '</div>' +
          '<div class="pf-bar"><div class="fill ' + barColor + '" style="width:' + pct + '%"></div></div>' +
          '<div class="pf-stats"><span>Execution Interval: ' + status.completed_days + ' / 90 Days</span><span>' + pct.toFixed(1) + '% Progress</span></div>' +
        '</div>' +
      '</div>' +
      '<div class="dash-grid" style="margin-top:12px">' +
        '<div class="card">' +
          '<div class="card-title"><span class="accent"></span>Order Book Layer &mdash; BTC/USD</div>' +
          (running ? '<div class="ob-table"><div class="ob-side"><div class="ob-header">Bids</div>' + obRows('bids') + '</div><div class="ob-side"><div class="ob-header asks-hdr">Asks</div>' + obRows('asks') + '</div></div>' : '<div class="text-muted" style="padding:12px">Exchange pipeline offline</div>') +
          '<div class="ob-foot">Engine Tick: ' + (ob.tick || 0) + ' &middot; Compliance Profile: ' + (ob.regime_name || 'N/A') + '</div>' +
        '</div>' +
        '<div class="card">' +
          '<div class="card-title"><span class="accent"></span>Operational Controls</div>' +
          '<div class="btn-group">' +
            '<button class="btn btn-primary" onclick="actionStart()">Initialize Day</button>' +
            '<button class="btn btn-danger" onclick="actionEOD()">Execute EOD</button>' +
            '<button class="btn btn-success" onclick="actionRun()">Run Cycle</button>' +
            '<button class="btn btn-warning" onclick="actionAdvance()">Advance Sequence</button>' +
          '</div>' +
          '<div class="card-title" style="margin-top:16px"><span class="accent"></span>Structural Audit History</div>' +
          scoresHtml +
        '</div>' +
      '</div>';

    document.getElementById('dayBadge').textContent = 'Day ' + status.current_day + ' / 90';
    document.getElementById('dayBadge').className = 'day-badge ' + (status.completed_days > 0 ? 'active' : 'idle');
    document.getElementById('phaseLabel').textContent = 'Phase ' + status.phase + ': ' + phaseLabel;
  } catch (e) {
    c.innerHTML = '<div class="empty">Terminal Error: ' + e.message + '</div>';
  }
}

async function renderBriefing() {
  const c = document.getElementById('mainContent');
  c.innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading briefing...</div></div>';
  try {
    const data = await api('GET', '/api/briefing');
    let html = data.briefing
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/^### (.*$)/gm, '<h3 style="color:#48dbfb;font-size:13px;margin:16px 0 6px">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 style="color:#dfe6e9;font-size:15px;margin:16px 0 8px;border-bottom:1px solid rgba(21,32,48,0.4);padding-bottom:4px">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 style="color:#48dbfb;font-size:18px;margin:0 0 10px">$1</h1>')
      .replace(/^- (.*$)/gm, '<li style="margin:3px 0;color:#8395a7">$1</li>')
      .replace(/\n\n/g, '</p><p style="margin:8px 0;color:#8395a7;line-height:1.7">')
      .replace(/\n/g, '<br>');
    c.innerHTML = '<div class="card"><div class="card-title"><span class="accent">&#9998;</span> Daily Briefing &mdash; Day ' + data.day + '</div>' +
      '<div class="card-subtitle">CMA Standards | SOCPA Compliance | NovaCap Financial Technologies</div>' +
      '<div style="background:rgba(8,14,24,0.5);border:1px solid rgba(18,30,48,0.3);border-radius:6px;padding:20px;font-size:12px;line-height:1.8;color:#c8d6e5">' + html + '</div></div>';
  } catch (e) {
    c.innerHTML = '<div class="empty">Error: ' + e.message + '</div>';
  }
}

async function renderEditor() {
  const c = document.getElementById('mainContent');
  c.innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading editor...</div></div>';
  try {
    const data = await api('GET', '/api/solution');
    const lines = data.code.split('\\n');
    let gutterHtml = '';
    for (let i = 1; i <= lines.length; i++) gutterHtml += i + '\\n';
    c.innerHTML = '<div class="card"><div class="card-title" style="justify-content:space-between">' +
      '<span><span class="accent">&#128187;</span> Code Editor &mdash; Day ' + data.day + '</span>' +
      '<div class="btn-group" style="margin:0">' +
      '<button class="btn btn-success btn-sm" onclick="saveCode()">Save</button>' +
      '<button class="btn btn-secondary btn-sm" onclick="actionRun()">Run</button></div></div>' +
      '<div class="card-subtitle">' + (data.path || 'No file loaded') + '</div>' +
      '<div class="editor-wrap"><div class="editor-header">' +
      '<div class="file-info"><span>&#128196;</span> <span>' + (data.exists ? 'solution.py' : 'new file') + '</span></div>' +
      '<span>Python</span></div>' +
      '<div class="editor-body"><div class="editor-gutter">' + gutterHtml + '</div>' +
      '<div class="editor-area"><textarea id="codeEditor" spellcheck="false">' + escHtml(data.code) + '</textarea></div></div>' +
      '<div class="editor-status"><span>' + (data.exists ? 'File exists' : 'New file') + '</span><span>UTF-8 | ' + lines.length + ' lines | ' + data.code.length + ' bytes</span></div></div></div>' +
      '<div class="card" id="runOutputPanel" style="display:none">' +
      '<div class="card-title"><span class="accent">&#9654;</span> Output</div>' +
      '<pre id="runOutput" class="code-block"></pre></div>';
    const ta = document.getElementById('codeEditor');
    if (ta) ta.addEventListener('input', function() { editorDirty = true; });
  } catch (e) {
    c.innerHTML = '<div class="empty">Error: ' + e.message + '</div>';
  }
}

async function renderResults() {
  const c = document.getElementById('mainContent');
  c.innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading results...</div></div>';
  try {
    const data = await api('GET', '/api/results');
    const results = data.results || [];
    if (results.length === 0) {
      c.innerHTML = '<div class="card"><div class="empty">No evaluations yet. Start a day and run EOD.</div></div>';
      return;
    }
    let html = '<div class="card"><div class="card-title"><span class="accent">&#128202;</span> Evaluation Results</div>';
    var resultsCopy = results.slice().reverse();
    for (var j = 0; j < resultsCopy.length; j++) {
      var r = resultsCopy[j];
      var pct = r.max_score > 0 ? (r.score / r.max_score * 100) : 0;
      var passed = r.passed;
      var violations = r.violations || [];
      var astIssues = r.ast_issues || [];
      html += '<div style="background:rgba(8,14,24,0.5);border:1px solid rgba(18,30,48,0.3);border-radius:6px;padding:14px;margin-bottom:10px">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">' +
        '<span style="font-weight:600;color:#dfe6e9">Day ' + r.day + '</span>' +
        '<span style="font-size:20px;font-weight:700;color:' + (passed ? '#2ecc71' : '#ff6b6b') + '">' + r.score + '/' + r.max_score + ' (' + pct.toFixed(0) + '%)</span></div>' +
        '<span class="tag ' + (passed ? 'tag-pass' : 'tag-fail') + '">' + (passed ? 'PASS' : 'FAIL') + '</span>';
      if (violations.length > 0) {
        html += '<div style="margin-top:8px"><strong style="color:#ff6b6b;font-size:11px">Violations:</strong><ul class="issue-list">';
        for (var v = 0; v < violations.length; v++) html += '<li class="issue-item critical">' + escHtml(violations[v]) + '</li>';
        html += '</ul></div>';
      }
      if (astIssues.length > 0) {
        html += '<div style="margin-top:6px"><strong style="color:#feca57;font-size:11px">AST Issues:</strong><ul class="issue-list">';
        var maxIssues = Math.min(astIssues.length, 5);
        for (var a = 0; a < maxIssues; a++) html += '<li class="issue-item warning">' + escHtml(astIssues[a]) + '</li>';
        html += '</ul></div>';
      }
      html += '<div style="margin-top:6px;font-size:11px"><span style="color:#4a5a6a">Ledger: </span><span style="color:' + (r.ledger_balanced ? '#2ecc71' : '#ff6b6b') + '">' + (r.ledger_balanced ? 'Balanced' : 'Imbalanced') + '</span></div></div>';
    }
    html += '</div>';
    c.innerHTML = html;
  } catch (e) {
    c.innerHTML = '<div class="empty">Error: ' + e.message + '</div>';
  }
}

async function renderLedger() {
  const c = document.getElementById('mainContent');
  c.innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading ledger...</div></div>';
  try {
    const data = await api('GET', '/api/ledger');
    if (data.error) { c.innerHTML = '<div class="empty">' + data.error + '</div>'; return; }
    var accountsHtml = '';
    var accounts = data.accounts || [];
    for (var i = 0; i < accounts.length; i++) {
      accountsHtml += '<tr><td>' + accounts[i].code + '</td><td>' + escHtml(accounts[i].name) + '</td><td>' + accounts[i].type + '</td><td class="amt">$' + accounts[i].balance.toFixed(2) + '</td></tr>';
    }
    var pnlHtml = '';
    var pnlData = data.pnl || [];
    for (var j = 0; j < pnlData.length; j++) {
      var netColor = pnlData[j].net_pnl >= 0 ? '#2ecc71' : '#ff6b6b';
      pnlHtml += '<tr><td>' + pnlData[j].symbol + '</td><td class="amt">$' + pnlData[j].realized_pnl.toFixed(2) + '</td><td class="amt">$' + pnlData[j].total_fees.toFixed(2) + '</td><td class="amt" style="color:' + netColor + '">$' + pnlData[j].net_pnl.toFixed(2) + '</td></tr>';
    }
    c.innerHTML = '<div class="card"><div class="card-title"><span class="accent">&#128214;</span> Ledger Engine</div>' +
      '<div class="stat-grid" style="margin-bottom:12px">' +
      '<div class="stat-card"><div class="label">Trades</div><div class="value blue">' + data.trade_count + '</div></div>' +
      '<div class="stat-card"><div class="label">Status</div><div class="value ' + (data.balanced ? 'green' : 'red') + '">' + (data.balanced ? 'BALANCED' : 'IMBALANCE') + '</div></div>' +
      '<div class="stat-card"><div class="label">Diff</div><div class="value" style="color:#feca57">$' + data.difference.toFixed(2) + '</div></div></div></div>' +
      '<div class="card"><div class="card-title"><span class="accent">&#128202;</span> Account Balances</div>' +
      '<div class="table-wrap"><table class="ledger-table"><thead><tr><th>Code</th><th>Name</th><th>Type</th><th>Balance</th></tr></thead><tbody>' + (accountsHtml || '<tr><td colspan="4" style="color:#4a5a6a">No accounts</td></tr>') + '</tbody></table></div></div>' +
      '<div class="card"><div class="card-title"><span class="accent">&#128200;</span> P&amp;L by Symbol</div>' +
      '<div class="table-wrap"><table class="ledger-table"><thead><tr><th>Symbol</th><th>Realized P&amp;L</th><th>Fees</th><th>Net P&amp;L</th></tr></thead><tbody>' + (pnlHtml || '<tr><td colspan="4" style="color:#4a5a6a">No trades yet</td></tr>') + '</tbody></table></div></div>';
  } catch (e) {
    c.innerHTML = '<div class="empty">Error: ' + e.message + '</div>';
  }
}

async function renderAudit() {
  const c = document.getElementById('mainContent');
  c.innerHTML = '<div class="loading"><div class="spinner"></div><div>Running AST audit...</div></div>';
  try {
    const data = await api('GET', '/api/audit');
    let issuesHtml = '';
    if (data.error) {
      issuesHtml = '<div class="empty">' + data.error + '</div>';
    } else if (!data.issues || data.issues.length === 0) {
      issuesHtml = '<div style="text-align:center;padding:20px;color:#2ecc71;font-size:13px">&#10003; No issues found. Code passes structural audit.</div>';
    } else {
      var issues = data.issues;
      for (var i = 0; i < issues.length; i++) {
        var cls = issues[i].severity === 'critical' ? 'critical' : issues[i].severity === 'warning' ? 'warning' : 'info';
        var label = issues[i].severity.toUpperCase();
        issuesHtml += '<li class="issue-item ' + cls + '"><strong>' + label + '</strong> L' + (issues[i].line || '?') + ': ' + escHtml(issues[i].message) + '</li>';
      }
    }
    var summary = data.summary || {};
    c.innerHTML = '<div class="card"><div class="card-title"><span class="accent">&#9881;</span> AST Static Code Audit</div>' +
      '<div class="stat-grid" style="margin-bottom:12px">' +
      '<div class="stat-card"><div class="label">Critical</div><div class="value ' + (summary.critical > 0 ? 'red' : 'green') + '">' + summary.critical + '</div></div>' +
      '<div class="stat-card"><div class="label">Warnings</div><div class="value ' + (summary.warning > 0 ? 'gold' : 'green') + '">' + summary.warning + '</div></div>' +
      '<div class="stat-card"><div class="label">Info</div><div class="value blue">' + summary.info + '</div></div>' +
      '<div class="stat-card"><div class="label">Score</div><div class="value blue">' + (summary.complexity_score || 0) + '</div></div></div>' +
      '<ul class="issue-list">' + issuesHtml + '</ul></div>';
  } catch (e) {
    c.innerHTML = '<div class="empty">Error: ' + e.message + '</div>';
  }
}

async function renderExchange() {
  const c = document.getElementById('mainContent');
  c.innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading exchange status...</div></div>';
  try {
    const data = await api('GET', '/api/exchange');
    if (data.running) {
      c.innerHTML = '<div class="card"><div class="card-title"><span class="accent">&#8644;</span> Mock Exchange <span class="tag tag-pass" style="margin-left:8px">ONLINE</span></div>' +
        '<div class="stat-grid">' +
        '<div class="stat-card"><div class="label">Status</div><div class="value green">RUNNING</div></div>' +
        '<div class="stat-card"><div class="label">Endpoint</div><div class="value blue" style="font-size:14px">' + (data.host || 'localhost') + ':' + (data.port || 8080) + '</div></div>' +
        '<div class="stat-card"><div class="label">Ticks</div><div class="value gold">' + (data.tick || 0) + '</div></div>' +
        '<div class="stat-card"><div class="label">Symbols</div><div class="value blue">' + (data.symbols || []).length + '</div></div></div>' +
        '<div class="card-subtitle" style="margin-top:12px">REST API Endpoints</div>' +
        '<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a5a6a;line-height:1.8">' +
        'GET  /v1/orderbook?symbol=BTC/USD<br>' +
        'GET  /v1/ticker?symbol=ETH/USDT<br>' +
        'POST /v1/execute<br>' +
        'GET  /v1/health</div></div>';
    } else {
      c.innerHTML = '<div class="card"><div class="card-title"><span class="accent">&#8644;</span> Mock Exchange <span class="tag tag-fail" style="margin-left:8px">OFFLINE</span></div>' +
        '<div class="stat-card"><div class="label">Status</div><div class="value" style="color:#ff6b6b">STOPPED</div></div>' +
        '<div style="margin-top:12px;color:#4a5a6a;font-size:12px">Start a day to launch the exchange server on port 8080.</div></div>';
    }
  } catch (e) {
    c.innerHTML = '<div class="empty">Error: ' + e.message + '</div>';
  }
}

async function actionStart() {
  try { showToast('Starting day...', 'info'); await api('POST', '/api/start'); showToast('Day started!', 'success'); renderView(currentView); }
  catch (e) { showToast('Error: ' + e.message, 'error'); }
}

async function actionEOD() {
  try { showToast('Running EOD evaluation...', 'info'); await api('POST', '/api/eod'); showToast('EOD complete! Check Results.', 'success'); renderView(currentView); }
  catch (e) { showToast('Error: ' + e.message, 'error'); }
}

async function actionAdvance() {
  try { await api('POST', '/api/advance'); showToast('Advanced to next day!', 'success'); renderView(currentView); }
  catch (e) { showToast('Cannot advance: ' + e.message, 'error'); }
}

async function actionRun() {
  try {
    showToast('Executing...', 'info');
    const data = await api('POST', '/api/run', { args: '' });
    const panel = document.getElementById('runOutputPanel');
    const out = document.getElementById('runOutput');
    if (panel && out) {
      panel.style.display = 'block';
      out.textContent = '';
      if (data.stdout) out.textContent += data.stdout;
      if (data.stderr) out.textContent += '\\n[STDERR]\\n' + data.stderr;
      if (data.error) out.textContent += '\\n[ERROR]\\n' + data.error;
      if (data.success) showToast('Execution OK (exit 0)', 'success');
      else showToast('Execution completed with errors', 'error');
    } else {
      showToast(data.success ? 'Execution OK' : 'Execution had errors', data.success ? 'success' : 'error');
      renderView(currentView);
    }
  } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

async function saveCode() {
  const ta = document.getElementById('codeEditor');
  if (!ta) return;
  try { await api('POST', '/api/save', { code: ta.value }); editorDirty = false; showToast('Code saved!', 'success'); }
  catch (e) { showToast('Error saving: ' + e.message, 'error'); }
}

function escHtml(str) {
  if (!str) return '';
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

function startPolling() {
  if (pollingInterval) clearInterval(pollingInterval);
  pollingInterval = setInterval(function() {
    if (currentView === 'dashboard') {
      fetch('/api/ticker').then(function(r) { return r.json(); }).then(function(d) {
        var el = document.querySelector('.ticker-inner');
        if (el && d.running && d.prices) {
          var entries = Object.entries(d.prices);
          var doubled = entries.concat(entries);
          var h = '';
          for (var i = 0; i < doubled.length; i++) {
            var sym = doubled[i][0], pr = doubled[i][1];
            var chg = ((Math.random() - 0.48) * 2).toFixed(2);
            var c = parseFloat(chg) >= 0 ? '#2ecc71' : '#ff6b6b';
            var s = parseFloat(chg) >= 0 ? '+' : '';
            h += '<div class="ticker-item"><span class="sym">' + sym + '</span><span class="pr" style="color:#feca57">$' + Number(pr).toLocaleString() + '</span><span class="chg" style="color:' + c + '">' + s + chg + '%</span></div>';
          }
          el.innerHTML = h;
        }
      }).catch(function() {});
    }
  }, 3000);
}

window.onload = function() {
  renderDashboard();
  startPolling();
  setInterval(updateClock, 1000);
  updateClock();
};
</script>
</body>
</html>"""


# ==============================================================================
# SECTION 11 — MAIN ENTRY POINT
# ==============================================================================

def main():
    """Main entry point for the NovaCap Arbitrage Academy."""
    # Handle Windows console color support
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except (ImportError, AttributeError, OSError):
            pass

    # Start the CLI
    cli = ArbitrageAcademyCLI()
    app_context["cli"] = cli

    # Start Web UI on port 8081
    web_ui = WebUIServer(port=8081)
    if web_ui.start():
        app_context["web_running"] = True
        print(f"  {c(Color.BRIGHT_GREEN, '[' + BoxChars.CHECK + ']')} Web Dashboard: {c(Color.BRIGHT_WHITE, 'http://localhost:8081')}")
    else:
        print(f"  {c(Color.WARN, '[!] Web UI on :8081 unavailable (may be in use)')}")

    try:
        cli._init_display()
        cli.cmdloop()
    except KeyboardInterrupt:
        print()
        print(f"  {c(Color.BRIGHT_YELLOW, 'Simulation interrupted by user.')}")
        if cli.exchange.is_running():
            cli.exchange.stop()
        if cli.ledger.conn:
            cli.ledger.close()
        web_ui.stop()
        cli.state.save()
        print(f"  {c(Color.BRIGHT_GREEN, 'State saved. Goodbye.')}")
        sys.exit(0)


if __name__ == "__main__":
    main()
