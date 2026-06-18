#!/usr/bin/env python3
"""
================================================================================
 CORPORATE FINANCE DAILY SIMULATION — Interactive Training Environment
 Role: Financial Analyst / FinTech Arbitrage Specialist
 Firm: A mid-sized technology-driven financial firm operating in global markets
 Standards: CMA (Certified Management Accountant) & SOCPA (Saudi CPA) alignment
================================================================================

This application simulates a daily corporate finance work environment with:
  - Morning market briefings with synthetic data
  - Randomly generated task sets from 3 categories
  - Interactive task execution via cmd-based CLI
  - End-of-day evaluation with strict 0-100 scoring and variance analysis
  - ANSI color-coded professional terminal output

Usage:
    python finance_sim.py

Requirements: Python 3.8+ (standard library only — no pip dependencies)
"""

import cmd
import json
import math
import os
import random
import re
import sys
import textwrap
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


# ==============================================================================
# SECTION 1 — ANSI COLOR UTILITIES
# ==============================================================================

class Color:
    """Terminal ANSI escape codes for professional color-coded output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"

    # Foreground (text)
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    # Bright variants
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_DARK_GRAY = "\033[100m"

    # Formatting shortcuts
    H1 = f"{BOLD}{BRIGHT_CYAN}"
    H2 = f"{BOLD}{BRIGHT_YELLOW}"
    H3 = f"{BOLD}{WHITE}"
    SUCCESS = f"{BOLD}{BRIGHT_GREEN}"
    ERROR = f"{BOLD}{BRIGHT_RED}"
    WARNING = f"{BOLD}{BRIGHT_YELLOW}"
    INFO = f"{BRIGHT_BLUE}"
    MUTED = f"{GRAY}"
    PROMPT = f"{BOLD}{BRIGHT_GREEN}"
    SYSTEM = f"{BOLD}{BRIGHT_MAGENTA}"

    @staticmethod
    def supports_color() -> bool:
        """Check if terminal supports ANSI color codes."""
        if not sys.stdout.isatty():
            return False
        if os.name == "nt":
            # Windows: check for color support
            return True
        return os.environ.get("TERM") is not None

    @classmethod
    def strip(cls, text: str) -> str:
        """Strip ANSI codes from a string."""
        return re.sub(r"\033\[[0-9;]*m", "", text)


# Determine if we can use colors
_USE_COLOR = Color.supports_color()


# ----- Unicode / Box-Drawing Character Support -----

def _supports_unicode() -> bool:
    """Check if terminal supports Unicode box-drawing characters."""
    if os.name == "nt":
        # Windows 10+ with new terminal supports Unicode
        try:
            # Check if we can encode Unicode box-drawing chars
            "\u2502".encode(sys.stdout.encoding or "utf-8")
            return True
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
            return False
    return True


_USE_UNICODE = _supports_unicode()


class BoxChars:
    """Box-drawing characters with ASCII fallback for legacy terminals."""

    if _USE_UNICODE:
        H = "\u2500"      # ─ horizontal
        V = "\u2502"      # │ vertical
        TL = "\u250c"     # ┌ top-left
        TR = "\u2510"     # ┐ top-right
        ML = "\u251c"     # ├ middle-left (tee down)
        MR = "\u2524"     # ┤ middle-right (tee up)
        BL = "\u2514"     # └ bottom-left
        BR = "\u2518"     # ┘ bottom-right
        H2 = "\u2550"     # ═ double horizontal
        V2 = "\u2551"     # ║ double vertical
        TL2 = "\u2554"    # ╔ double top-left
        TR2 = "\u2557"    # ╗ double top-right
        BL2 = "\u255a"    # ╚ double bottom-left
        BR2 = "\u255d"    # ╝ double bottom-right
        BULLET = "\u25b8" # ▸ triangle bullet
        CHECK = "\u2713"  # ✓ checkmark
        CROSS = "\u2717"  # ✗ cross
        STAR = "\u2726"   # ✦ star
        SUN = "\u2600"    # ☀ sun
        ARROW = "\u2937"  # ↷ arrow
        DASH = "\u2500"   # ─ horizontal thin for separators
    else:
        H = "-"
        V = "|"
        TL = "."
        TR = "."
        ML = "+"
        MR = "+"
        BL = "'"
        BR = "'"
        H2 = "="
        V2 = "|"
        TL2 = "."
        TR2 = "."
        BL2 = "'"
        BR2 = "'"
        BULLET = ">"
        CHECK = "v"
        CROSS = "x"
        STAR = "*"
        SUN = "O"
        ARROW = "->"
        DASH = "-"


def c(color_code: str, text: str) -> str:
    """Apply color if terminal supports it, else return plain text."""
    return f"{color_code}{text}{Color.RESET}" if _USE_COLOR else text


def h1(text: str) -> str:
    """Heading level 1 — bright cyan bold."""
    return c(Color.H1, text)


def h2(text: str) -> str:
    """Heading level 2 — bright yellow bold."""
    return c(Color.H2, text)


def h3(text: str) -> str:
    """Heading level 3 — white bold."""
    return c(Color.H3, text)


def success(text: str) -> str:
    """Success/green message."""
    return c(Color.SUCCESS, text)


def error(text: str) -> str:
    """Error/red message."""
    return c(Color.ERROR, text)


def warning(text: str) -> str:
    """Warning/yellow message."""
    return c(Color.WARNING, text)


def info(text: str) -> str:
    """Info/blue message."""
    return c(Color.INFO, text)


def muted(text: str) -> str:
    """Muted/gray text."""
    return c(Color.MUTED, text)


def system(text: str) -> str:
    """System/purple message."""
    return c(Color.SYSTEM, text)


def box(text: str, color: str = Color.BRIGHT_CYAN, width: int = 72) -> str:
    """Draw a bordered box around text."""
    Bc = BoxChars
    lines = text.split("\n")
    top = f"{color}{Bc.TL}{Bc.H * width}{Bc.TR}{Color.RESET}"
    bottom = f"{color}{Bc.BL}{Bc.H * width}{Bc.BR}{Color.RESET}"
    inner = []
    for line in lines:
        stripped = Color.strip(line)
        visible_len = len(stripped)
        if visible_len > width:
            inner.append(f"{color}{Bc.V} {Color.RESET}{line}")
        else:
            padding = width - visible_len
            inner.append(f"{color}{Bc.V} {Color.RESET}{line}{' ' * padding}{color} {Bc.V}{Color.RESET}")
    return "\n".join([top] + inner + [bottom])


def separator(char: str = None, color: str = Color.GRAY, width: int = 74) -> str:
    """Print a horizontal separator."""
    if char is None:
        char = BoxChars.H2
    return c(color, char * width)


def typewriter(text: str, delay: float = 0.002) -> None:
    """Print text with a slight typewriter effect for dramatic briefings."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


# ==============================================================================
# SECTION 2 — CONFIGURATION & COMPANY PROFILE
# ==============================================================================

class CompanyConfig:
    """Simulated company profile and operational framework."""

    NAME = "NovaCap Financial Technologies Ltd."
    HEADQUARTERS = "Dubai International Financial Centre (DIFC)"
    REGIONS = ["MENA", "Southeast Asia", "Western Europe", "North America"]
    FOCUS = [
        "Algorithmic Arbitrage Trading",
        "Cross-Border Corporate Finance",
        "FinTech Risk Management",
        "Digital Asset Portfolio Optimization",
    ]
    ASSETS_UNDER_MANAGEMENT = "$2.4B (simulated)"
    EMPLOYEES = 347
    FOUNDED = 2018
    STANDARDS = {
        "accounting": "IFRS (International Financial Reporting Standards)",
        "management_accounting": "CMA (Certified Management Accountant) framework",
        "compliance": "SOCPA (Saudi Organization for Certified Public Accountants)",
        "reporting": "GAAP-aligned management reporting",
    }


class RoleConfig:
    """User role definition."""

    TITLE = "Financial Analyst — FinTech Arbitrage Specialist"
    DEPARTMENT = "Strategic Arbitrage & Corporate Finance"
    REPORTS_TO = "Director of Financial Operations"
    TEAM_SIZE = 5
    RESPONSIBILITIES = [
        "Algorithmic arbitrage strategy analysis and backtesting",
        "Corporate financial reporting and variance analysis",
        "Cross-border transaction compliance and risk assessment",
        "Portfolio optimization and rebalancing recommendations",
        "Automated trading algorithm auditing and validation",
    ]
    REQUIRED_CERTIFICATIONS = ["CMA (in progress)", "SOCPA familiarity"]


# ==============================================================================
# SECTION 3 — PRE-DEFINED TASK DATABASE (10 highly detailed tasks)
# ==============================================================================

TASK_DATABASE = [
    # -----------------------------------------------------------------------
    # TASK 1: Quantitative — Moving Average Crossover Analysis
    # -----------------------------------------------------------------------
    {
        "id": 1,
        "category": "quantitative",
        "category_label": "Quantitative & Algorithmic Analysis",
        "title": "Moving Average Crossover Signal Detection",
        "difficulty": "medium",
        "briefing": (
            "Our algorithmic trading desk runs a trend-following strategy on "
            "BTC/USD. The strategy generates signals when the 5-period simple "
            "moving average (SMA5) crosses the 20-period simple moving average "
            "(SMA20). You are provided with the last 30 days of daily closing prices."
        ),
        "description": (
            "Analyze the closing price data below and determine:\n"
            "  1. On which days do SMA5/SMA20 crossovers occur?\n"
            "  2. Classify each crossover as a BULLISH (golden cross) or "
            "BEARISH (death cross) signal.\n"
            "  3. Based on the most recent crossover, what trading action "
            "would you recommend?"
        ),
        "data_provided": json.dumps(
            {
                "asset": "BTC/USD",
                "period": "30 days (daily closing prices)",
                "prices": [
                    42350, 42780, 43120, 42890, 43560,  # Days 1-5
                    43900, 44210, 43850, 44100, 44530,  # Days 6-10
                    44980, 45200, 44750, 45010, 45380,  # Days 11-15
                    45120, 44890, 44500, 44120, 43800,  # Days 16-20
                    43550, 43210, 42980, 43340, 43700,  # Days 21-25
                    44150, 44620, 45010, 45300, 45800,  # Days 26-30
                ],
                "sma5": [
                    None, None, None, None, 42940.0,  # Days 1-5
                    43250.0, 43536.0, 43730.0, 44036.0, 44318.0,  # Days 6-10
                    44538.0, 44774.0, 44878.0, 44878.0, 44914.0,  # Days 11-15
                    45112.0, 45052.0, 44946.0, 44716.0, 44428.0,  # Days 16-20
                    44092.0, 43716.0, 43370.0, 43146.0, 43094.0,  # Days 21-25
                    43188.0, 43468.0, 43850.0, 44304.0, 44756.0,  # Days 26-30
                ],
                "sma20": [None] * 19 + [  # Days 1-19 are None (not enough data)
                    44260.5, 44271.0, 44276.5, 44254.0, 44228.0,
                    44182.5, 44121.5, 44045.5, 43926.0, 43811.5,
                    43711.5,
                ],
            },
            indent=2,
        ),
        "expected_answer": (
            "Analysis Summary:\n"
            "  SMA5/SMA20 Crossovers occur at:\n"
            "  - Day 20: SMA5 (44428.0) crosses BELOW SMA20 (44228.0) → "
            "SMA5 is ABOVE SMA20. NO CROSSOVER at day 20.\n"
            "  Correct crossovers:\n"
            "  - Day 19→20: SMA5 drops below SMA20 → BEARISH (Death Cross)\n"
            "    SMA5(44428.0) < SMA20(44228.0). First time SMA5 goes below SMA20.\n"
            "  - Day 26→27: SMA5 rises above SMA20 → BULLISH (Golden Cross)\n"
            "    SMA5(43468.0) > SMA20(43711.5) initially NOT, but by day 26-27 "
            "the crossover occurs.\n\n"
            "  Most recent action: Based on the last crossover (Golden Cross ~Day 26-27),\n"
            "  the recommendation is to initiate a LONG position on BTC/USD, "
            "as the trend has shifted bullish.\n"
            "  Risk management: Place stop-loss at recent support level (~43,200)."
        ),
        "checks": [
            {"type": "keyword", "target": "death cross", "points": 15,
             "description": "Identifies the bearish death cross around Day 19-20"},
            {"type": "keyword", "target": "golden cross", "points": 15,
             "description": "Identifies the bullish golden cross around Day 26-27"},
            {"type": "keyword", "target": "long", "points": 15,
             "description": "Recommends LONG/buy position based on current trend"},
            {"type": "keyword", "target": "stop", "points": 10,
             "description": "Mentions stop-loss or risk management"},
            {"type": "keyword", "target": "SMA5", "points": 10,
             "description": "Correctly references SMA5 values"},
            {"type": "keyword", "target": "SMA20", "points": 10,
             "description": "Correctly references SMA20 values"},
            {"type": "concept", "target": "trend analysis", "points": 15,
             "description": "Demonstrates understanding of trend-following logic"},
            {"type": "keyword", "target": "bearish", "points": 10,
             "description": "Correctly classifies bearish signal"},
        ],
        "max_score": 100,
        "key_concepts": ["moving average", "golden cross", "death cross",
                          "trend following", "technical analysis"],
    },

    # -----------------------------------------------------------------------
    # TASK 2: Quantitative — Arbitrage Spread Detection
    # -----------------------------------------------------------------------
    {
        "id": 2,
        "category": "quantitative",
        "category_label": "Quantitative & Algorithmic Analysis",
        "title": "Cross-Exchange Arbitrage Opportunity Analysis",
        "difficulty": "hard",
        "briefing": (
            "Our arbitrage desk monitors price discrepancies across three major "
            "cryptocurrency exchanges. You have been provided with the current "
            "order book snapshots for ETH/USDT. Identify triangular & cross-exchange "
            "arbitrage opportunities net of fees."
        ),
        "description": (
            "Given the order book data below, calculate:\n"
            "  1. The best bid-ask spread on each exchange.\n"
            "  2. Whether a two-leg arbitrage (buy on Exchange A, sell on "
            "Exchange B) is profitable after a 0.1% transaction fee per leg.\n"
            "  3. The maximum risk-free profit (in USDT) for a $100,000 trade.\n"
            "  4. Any triangular arbitrage opportunity involving ETH/BTC and BTC/USDT pairs."
        ),
        "data_provided": json.dumps(
            {
                "pairs": ["ETH/USDT", "ETH/BTC", "BTC/USDT"],
                "fee_per_leg_pct": 0.10,
                "capital_usdt": 100000,
                "exchange_A": {
                    "name": "CryptoX",
                    "ETH/USDT": {"bid": 3125.40, "ask": 3127.80, "depth_bid": 850, "depth_ask": 720},
                    "ETH/BTC": {"bid": 0.0512, "ask": 0.0514, "depth_bid": 400, "depth_ask": 380},
                    "BTC/USDT": {"bid": 60800, "ask": 60950, "depth_bid": 120, "depth_ask": 100},
                },
                "exchange_B": {
                    "name": "Quantex",
                    "ETH/USDT": {"bid": 3140.20, "ask": 3143.50, "depth_bid": 600, "depth_ask": 550},
                    "ETH/BTC": {"bid": 0.0509, "ask": 0.0511, "depth_bid": 350, "depth_ask": 320},
                    "BTC/USDT": {"bid": 60980, "ask": 61100, "depth_bid": 90, "depth_ask": 80},
                },
                "exchange_C": {
                    "name": "BlockSwap",
                    "ETH/USDT": {"bid": 3130.00, "ask": 3133.00, "depth_bid": 750, "depth_ask": 680},
                    "ETH/BTC": {"bid": 0.0515, "ask": 0.0517, "depth_bid": 280, "depth_ask": 260},
                    "BTC/USDT": {"bid": 60750, "ask": 60880, "depth_bid": 110, "depth_ask": 95},
                },
            },
            indent=2,
        ),
        "expected_answer": (
            "Arbitrage Analysis:\n\n"
            "1. Best Bid-Ask Spreads:\n"
            "   - CryptoX ETH/USDT: Spread = $2.40 (3127.80 - 3125.40)\n"
            "   - Quantex ETH/USDT: Spread = $3.30\n"
            "   - BlockSwap ETH/USDT: Spread = $3.00\n\n"
            "2. Two-Leg Cross-Exchange Arbitrage:\n"
            "   BUY on CryptoX @ $3,127.80 (ask) → SELL on Quantex @ $3,140.20 (bid)\n"
            "   Gross profit = $12.40/ETH\n"
            "   Fees: 0.1% × $3,127.80 = $3.13 (buy) + 0.1% × $3,140.20 = $3.14 (sell)\n"
            "   Net profit = $12.40 - $6.27 = $6.13/ETH\n"
            "   For $100k: Buy 31.97 ETH → Net profit ≈ $196.00\n"
            "   Conclusion: PROFITABLE.\n\n"
            "3. Triangular Arbitrage (ETH→BTC→USDT→ETH):\n"
            "   Route: Sell ETH for BTC on BlockSwap (best ETH/BTC bid: 0.0515)\n"
            "         → Sell BTC for USDT on Quantex (best BTC/USDT bid: 60,980)\n"
            "         → Buy ETH on CryptoX (lowest ETH/USDT ask: $3,127.80)\n"
            "   No significant triangular profit after fees.\n"
            "   OR: Check reverse route...\n\n"
            "4. Recommended Trade: Execute two-leg arbitrage CryptoX→Quantex.\n"
            "   Expected net profit: ~$196 (0.196% return)."
        ),
        "checks": [
            {"type": "number", "target": 3.13, "tolerance": 0.50, "points": 15,
             "description": "Correct buy-side fee calculation"},
            {"type": "number", "target": 6.13, "tolerance": 1.0, "points": 20,
             "description": "Correct net profit per ETH calculation"},
            {"type": "keyword", "target": "profitable", "points": 15,
             "description": "Correctly identifies the trade as profitable"},
            {"type": "keyword", "target": "triangular", "points": 10,
             "description": "Evaluates triangular arbitrage opportunity"},
            {"type": "number", "target": 196, "tolerance": 50, "points": 15,
             "description": "Correct total profit for $100k position"},
            {"type": "keyword", "target": "fee", "points": 10,
             "description": "Accounts for transaction fees in analysis"},
            {"type": "keyword", "target": "depth", "points": 15,
             "description": "Considers order book depth / liquidity constraints"},
        ],
        "max_score": 100,
        "key_concepts": ["arbitrage", "order book", "bid-ask spread",
                          "triangular arbitrage", "liquidity"],
    },

    # -----------------------------------------------------------------------
    # TASK 3: Corporate Finance — Variance Analysis
    # -----------------------------------------------------------------------
    {
        "id": 3,
        "category": "corporate_finance",
        "category_label": "Corporate Finance & Reporting",
        "title": "Monthly P&L Variance Analysis",
        "difficulty": "medium",
        "briefing": (
            "The CFO has requested a detailed variance analysis for the April 2026 "
            "management accounts. The budget was prepared in January 2026, and actual "
            "results have just been finalized. Identify all material variances and "
            "provide commentary."
        ),
        "description": (
            "Using the P&L data below, calculate:\n"
            "  1. Revenue variance ($ and %) — classify as favorable (F) or unfavorable (U).\n"
            "  2. Cost of Sales variance ($ and %).\n"
            "  3. Operating Expense variance by line item.\n"
            "  4. Net Income variance with explanation of the PRIMARY driver.\n"
            "  5. Any variance > 10% requires a commentary on possible causes."
        ),
        "data_provided": json.dumps(
            {
                "period": "April 2026",
                "currency": "USD ($)",
                "pl_statement": {
                    "revenue": {
                        "budget": 12500000,
                        "actual": 13250000,
                    },
                    "cost_of_sales": {
                        "budget": 5750000,
                        "actual": 6100000,
                    },
                    "gross_profit": {
                        "budget": 6750000,
                        "actual": 7150000,
                    },
                    "operating_expenses": {
                        "salaries_and_benefits": {
                            "budget": 2100000,
                            "actual": 2180000,
                        },
                        "technology_infrastructure": {
                            "budget": 890000,
                            "actual": 945000,
                        },
                        "marketing_and_sales": {
                            "budget": 450000,
                            "actual": 425000,
                        },
                        "professional_fees": {
                            "budget": 320000,
                            "actual": 385000,
                        },
                        "office_and_admin": {
                            "budget": 180000,
                            "actual": 175000,
                        },
                        "travel_and_entertainment": {
                            "budget": 95000,
                            "actual": 112000,
                        },
                    },
                    "total_opex": {
                        "budget": 4035000,
                        "actual": 4222000,
                    },
                    "operating_income": {
                        "budget": 2715000,
                        "actual": 2928000,
                    },
                    "interest_and_taxes": {
                        "budget_interest": 120000,
                        "actual_interest": 118000,
                        "budget_tax": 680000,
                        "actual_tax": 735000,
                    },
                    "net_income": {
                        "budget": 1915000,
                        "actual": 2075000,
                    },
                },
            },
            indent=2,
        ),
        "expected_answer": (
            "Variance Analysis Report — April 2026\n\n"
            "1. Revenue Variance:\n"
            "   Actual $13,250,000 vs Budget $12,500,000\n"
            "   Variance: +$750,000 (+6.0%) → FAVORABLE (F)\n\n"
            "2. Cost of Sales Variance:\n"
            "   Actual $6,100,000 vs Budget $5,750,000\n"
            "   Variance: +$350,000 (+6.09%) → UNFAVORABLE (U)\n"
            "   However, gross margin improved: 54.0% (actual) vs 54.0% (budget) — "
            "margin held steady despite revenue growth.\n\n"
            "3. Operating Expenses — Key Variances:\n"
            "   - Salaries: +$80,000 (+3.8%) U — within tolerance\n"
            "   - Technology: +$55,000 (+6.2%) U — cloud cost overrun\n"
            "   - Marketing: -$25,000 (-5.6%) F — under budget\n"
            "   - Professional Fees: +$65,000 (+20.3%) U — MATERIAL, needs explanation\n"
            "   - Office Admin: -$5,000 (-2.8%) F\n"
            "   - Travel: +$17,000 (+17.9%) U — MATERIAL, needs explanation\n\n"
            "4. Net Income Variance:\n"
            "   Actual $2,075,000 vs Budget $1,915,000\n"
            "   Variance: +$160,000 (+8.36%) FAVORABLE\n"
            "   PRIMARY DRIVER: Revenue over-performance (+$750k) partially "
            "offset by higher COGS (+$350k) and opex (+$187k).\n\n"
            "5. Commentary Required (variances > 10%):\n"
            "   - Professional Fees (+20.3%): Likely due to M&A advisory or "
            "regulatory compliance costs.\n"
            "   - Travel (+17.9%): Increased client-facing activity, new "
            "market development."
        ),
        "checks": [
            {"type": "number", "target": 750000, "tolerance": 50000, "points": 15,
             "description": "Correct revenue variance in dollars"},
            {"type": "keyword", "target": "favorable", "points": 10,
             "description": "Correctly classifies revenue variance as favorable"},
            {"type": "keyword", "target": "unfavorable", "points": 10,
             "description": "Correctly identifies unfavorable variances"},
            {"type": "keyword", "target": "professional fees", "points": 10,
             "description": "Flags professional fees as material variance"},
            {"type": "keyword", "target": "20.3%", "points": 15,
             "description": "Identifies 20.3% variance in professional fees"},
            {"type": "number", "target": 160000, "tolerance": 50000, "points": 15,
             "description": "Correct net income variance"},
            {"type": "keyword", "target": "driver", "points": 10,
             "description": "Identifies primary driver of net income variance"},
            {"type": "keyword", "target": "commentary", "points": 15,
             "description": "Provides plausible commentary on variance causes"},
        ],
        "max_score": 100,
        "key_concepts": ["variance analysis", "favorable/unfavorable",
                          "management accounts", "P&L", "budget vs actual"],
    },

    # -----------------------------------------------------------------------
    # TASK 4: Corporate Finance — Ledger Reconciliation
    # -----------------------------------------------------------------------
    {
        "id": 4,
        "category": "corporate_finance",
        "category_label": "Corporate Finance & Reporting",
        "title": "Inter-Ledger Reconciliation & Discrepancy Resolution",
        "difficulty": "hard",
        "briefing": (
            "The month-end close has revealed a discrepancy between the General "
            "Ledger (GL) and the Sub-Ledger (SL) for trade settlements. Your task "
            "is to reconcile the differences and recommend adjusting journal entries."
        ),
        "description": (
            "Two ledgers are provided below for the Trade Settlements account. "
            "Identify:\n"
            "  1. Which entries appear in only ONE ledger (the discrepancies).\n"
            "  2. The net dollar value of discrepancies.\n"
            "  3. The most likely root cause (timing error, data entry, or "
            "classification).\n"
            "  4. Provide adjusting journal entries to correct the GL balance."
        ),
        "data_provided": json.dumps(
            {
                "account": "Trade Settlements — GL Account #4012",
                "period": "March 2026",
                "general_ledger": [
                    {"entry_id": "GL-1001", "date": "2026-03-02", "description": "FX Forward Settlement", "debit": 0, "credit": 450000},
                    {"entry_id": "GL-1002", "date": "2026-03-05", "description": "Equity Trade Settlement", "debit": 280000, "credit": 0},
                    {"entry_id": "GL-1003", "date": "2026-03-08", "description": "Bond Coupon Payment", "debit": 0, "credit": 125000},
                    {"entry_id": "GL-1004", "date": "2026-03-12", "description": "Repo Agreement Settlement", "debit": 500000, "credit": 0},
                    {"entry_id": "GL-1005", "date": "2026-03-15", "description": "OTC Derivative Settlement", "debit": 0, "credit": 320000},
                    {"entry_id": "GL-1006", "date": "2026-03-19", "description": "Margin Call Payment", "debit": 0, "credit": 185000},
                    {"entry_id": "GL-1007", "date": "2026-03-22", "description": "Dividend Receipt", "debit": 45000, "credit": 0},
                    {"entry_id": "GL-1008", "date": "2026-03-26", "description": "Trade Commission Expense", "debit": 38000, "credit": 0},
                ],
                "sub_ledger": [
                    {"entry_id": "SL-2001", "date": "2026-03-02", "description": "FX Forward Settlement", "debit": 0, "credit": 450000},
                    {"entry_id": "SL-2002", "date": "2026-03-05", "description": "Equity Trade Settlement", "debit": 280000, "credit": 0},
                    {"entry_id": "SL-2003", "date": "2026-03-08", "description": "Bond Coupon Payment", "debit": 0, "credit": 125000},
                    {"entry_id": "SL-2004", "date": "2026-03-12", "description": "Repo Agreement Settlement", "debit": 500000, "credit": 0},
                    {"entry_id": "SL-2005", "date": "2026-03-16", "description": "OTC Derivative Settlement", "debit": 0, "credit": 320000},
                    {"entry_id": "SL-2006", "date": "2026-03-19", "description": "Margin Call Payment", "debit": 0, "credit": 162000},
                    {"entry_id": "SL-2007", "date": "2026-03-22", "description": "Dividend Receipt", "debit": 45000, "credit": 0},
                    {"entry_id": "SL-2008", "date": "2026-03-28", "description": "Trade Commission Expense", "debit": 38000, "credit": 0},
                ],
            },
            indent=2,
        ),
        "expected_answer": (
            "Reconciliation Report — Trade Settlements (GL #4012)\n\n"
            "1. Discrepancies Found:\n"
            "   a) GL-1005 / SL-2005: OTC Derivative Settlement\n"
            "      GL date: 2026-03-15 | SL date: 2026-03-16\n"
            "      Amount: $320,000 — MATCHES (timing difference only, not a value error)\n\n"
            "   b) GL-1006 / SL-2006: Margin Call Payment\n"
            "      GL: $185,000 | SL: $162,000\n"
            "      Difference: $23,000 — VALUE DISCREPANCY\n\n"
            "   c) GL-1008 / SL-2008: Trade Commission Expense\n"
            "      GL date: 2026-03-26 | SL date: 2026-03-28\n"
            "      Amount: $38,000 — MATCHES (timing difference only)\n\n"
            "2. Net Value of Discrepancies:\n"
            "   Margin Call: GL has $23,000 MORE than SL\n"
            "   Net discrepancy: $23,000 (GL overstated vs SL)\n\n"
            "3. Root Cause:\n"
            "   Most likely DATA ENTRY ERROR on GL-1006 — manual entry of "
            "$185,000 instead of correct $162,000. The $23,000 difference "
            "is not a timing issue since both entries have the same date.\n\n"
            "4. Adjusting Journal Entry:\n"
            "   Debit: Margin Call Payable (Liability) $23,000\n"
            "   Credit: Trade Settlements (GL #4012) $23,000\n"
            "   (To correct overstated margin call payment)"
        ),
        "checks": [
            {"type": "number", "target": 23000, "tolerance": 1000, "points": 20,
             "description": "Correctly identifies $23,000 discrepancy"},
            {"type": "keyword", "target": "margin call", "points": 15,
             "description": "Identifies margin call entry as the discrepancy source"},
            {"type": "keyword", "target": "data entry", "points": 15,
             "description": "Correctly identifies root cause as data entry error"},
            {"type": "keyword", "target": "adjusting", "points": 15,
             "description": "Provides adjusting journal entry"},
            {"type": "keyword", "target": "timing", "points": 10,
             "description": "Recognizes timing differences vs value discrepancies"},
            {"type": "number", "target": 185000, "tolerance": 1000, "points": 15,
             "description": "References the overstated $185,000 figure"},
            {"type": "keyword", "target": "overstated", "points": 10,
             "description": "Correctly identifies GL as overstated"},
        ],
        "max_score": 100,
        "key_concepts": ["reconciliation", "general ledger", "sub-ledger",
                          "journal entries", "discrepancy analysis"],
    },

    # -----------------------------------------------------------------------
    # TASK 5: Risk & Compliance — Transaction Audit
    # -----------------------------------------------------------------------
    {
        "id": 5,
        "category": "risk_compliance",
        "category_label": "Risk & Compliance",
        "title": "Suspicious Transaction Flagging (AML/KYC)",
        "difficulty": "medium",
        "briefing": (
            "The compliance officer has requested an audit of recent cross-border "
            "transactions. Under SOCPA and local AML regulations, any transaction "
            "exceeding $10,000 requires enhanced due diligence (EDD). Transactions "
            "with rapid round-tripping (deposit-withdraw within 24h) must be flagged."
        ),
        "description": (
            "Review the transaction log below and:\n"
            "  1. Flag ALL transactions requiring EDD ($10k+ threshold).\n"
            "  2. Identify any round-tripping patterns (same counterparty, "
            "inflow then outflow within 24 hours).\n"
            "  3. Identify any structuring patterns (multiple transactions just "
            "under $10k to avoid reporting).\n"
            "  4. Calculate the total value of flagged transactions."
        ),
        "data_provided": json.dumps(
            {
                "reporting_threshold_usd": 10000,
                "edd_threshold_usd": 10000,
                "transactions": [
                    {"id": "TX-001", "date": "2026-04-01 09:15", "type": "inbound_wire", "counterparty": "Alpha Trading Ltd", "amount": 25000, "currency": "USD", "country": "UAE"},
                    {"id": "TX-002", "date": "2026-04-01 10:30", "type": "outbound_wire", "counterparty": "Beta Investments", "amount": 9800, "currency": "USD", "country": "Cayman Islands"},
                    {"id": "TX-003", "date": "2026-04-01 11:00", "type": "inbound_wire", "counterparty": "Gamma Corp", "amount": 9850, "currency": "USD", "country": "Panama"},
                    {"id": "TX-004", "date": "2026-04-01 14:45", "type": "outbound_wire", "counterparty": "Delta LLC", "amount": 30000, "currency": "USD", "country": "Switzerland"},
                    {"id": "TX-005", "date": "2026-04-01 15:00", "type": "inbound_wire", "counterparty": "Gamma Corp", "amount": 9900, "currency": "USD", "country": "Panama"},
                    {"id": "TX-006", "date": "2026-04-01 16:20", "type": "outbound_wire", "counterparty": "Epsilon Finance", "amount": 7500, "currency": "USD", "country": "Singapore"},
                    {"id": "TX-007", "date": "2026-04-02 08:00", "type": "outbound_wire", "counterparty": "Alpha Trading Ltd", "amount": 24000, "currency": "USD", "country": "UK"},
                    {"id": "TX-008", "date": "2026-04-02 09:15", "type": "inbound_wire", "counterparty": "Zeta Holdings", "amount": 45000, "currency": "USD", "country": "BVI"},
                    {"id": "TX-009", "date": "2026-04-02 09:30", "type": "outbound_wire", "counterparty": "Gamma Corp", "amount": 9750, "currency": "USD", "country": "Panama"},
                    {"id": "TX-010", "date": "2026-04-02 11:00", "type": "inbound_wire", "counterparty": "Theta AG", "amount": 12000, "currency": "USD", "country": "Germany"},
                    {"id": "TX-011", "date": "2026-04-02 14:30", "type": "inbound_wire", "counterparty": "Gamma Corp", "amount": 10100, "currency": "USD", "country": "Panama"},
                    {"id": "TX-012", "date": "2026-04-03 08:00", "type": "outbound_wire", "counterparty": "Alpha Trading Ltd", "amount": 26000, "currency": "USD", "country": "UK"},
                ],
            },
            indent=2,
        ),
        "expected_answer": (
            "AML/KYC Transaction Audit Report\n\n"
            "1. Transactions Requiring EDD ($10k threshold):\n"
            "   - TX-001: $25,000 — Alpha Trading Ltd (UAE) — INBOUND\n"
            "   - TX-004: $30,000 — Delta LLC (Switzerland) — OUTBOUND\n"
            "   - TX-007: $24,000 — Alpha Trading Ltd (UK) — OUTBOUND\n"
            "   - TX-008: $45,000 — Zeta Holdings (BVI) — INBOUND\n"
            "   - TX-010: $12,000 — Theta AG (Germany) — INBOUND\n"
            "   - TX-011: $10,100 — Gamma Corp (Panama) — INBOUND\n"
            "   - TX-012: $26,000 — Alpha Trading Ltd (UK) — OUTBOUND\n\n"
            "2. Round-Tripping Pattern:\n"
            "   ALPHA TRADING LTD — Pattern detected!\n"
            "     TX-001 (Apr 1, +$25k inbound from UAE)\n"
            "     TX-007 (Apr 2, -$24k outbound to UK) → 22h 45min gap\n"
            "     TX-012 (Apr 3, -$26k outbound to UK)\n"
            "     Net outflow of $25,000 after round-tripping. HIGHLY SUSPICIOUS.\n\n"
            "3. Structuring Pattern:\n"
            "   GAMMA CORP — Multiple transactions just below $10k:\n"
            "     TX-003: $9,850 (below threshold)\n"
            "     TX-005: $9,900 (below threshold)\n"
            "     TX-009: $9,750 (below threshold)\n"
            "     Then TX-011: $10,100 (just over threshold)\n"
            "     Total: $39,600 — Clear structuring attempt to avoid $10k reporting.\n\n"
            "4. Total Flagged Value:\n"
            "   EDD transactions: $25k + $30k + $24k + $45k + $12k + $10.1k + $26k = $172,100\n"
            "   Plus structuring transactions: $39,600\n"
            "   GRAND TOTAL: ~$211,700"
        ),
        "checks": [
            {"type": "keyword", "target": "Alpha Trading", "points": 15,
             "description": "Identifies Alpha Trading round-tripping pattern"},
            {"type": "keyword", "target": "Gamma Corp", "points": 15,
             "description": "Identifies Gamma Corp structuring pattern"},
            {"type": "keyword", "target": "structuring", "points": 15,
             "description": "Correctly identifies structuring behavior"},
            {"type": "keyword", "target": "round-tripping", "points": 15,
             "description": "Correctly identifies round-tripping pattern"},
            {"type": "number", "target": 7, "tolerance": 2, "points": 15,
             "description": "Flags appropriate number of EDD transactions"},
            {"type": "keyword", "target": "EDD", "points": 10,
             "description": "References Enhanced Due Diligence requirements"},
            {"type": "keyword", "target": "10,000", "points": 15,
             "description": "Correctly references the $10k reporting threshold"},
        ],
        "max_score": 100,
        "key_concepts": ["AML", "KYC", "suspicious transaction", "structuring",
                          "round-tripping", "enhanced due diligence"],
    },

    # -----------------------------------------------------------------------
    # TASK 6: Risk & Compliance — Value-at-Risk Calculation
    # -----------------------------------------------------------------------
    {
        "id": 6,
        "category": "risk_compliance",
        "category_label": "Risk & Compliance",
        "title": "Portfolio Value-at-Risk (VaR) Estimation",
        "difficulty": "hard",
        "briefing": (
            "The risk committee requires a daily VaR report for the firm's "
            "multi-asset trading portfolio. Use the historical simulation method "
            "to calculate VaR at 95% and 99% confidence levels."
        ),
        "description": (
            "Given the portfolio's daily returns over the past 100 trading days:\n"
            "  1. Sort the returns and determine the 95% and 99% Value-at-Risk "
            "using the historical simulation method.\n"
            "  2. Calculate the Expected Shortfall (Conditional VaR) at 95%.\n"
            "  3. The portfolio is currently worth $50M. Express VaR in dollars.\n"
            "  4. Interpret the results: what does this mean for the firm's "
            "daily risk exposure?"
        ),
        "data_provided": json.dumps(
            {
                "portfolio_value": 50000000,
                "method": "Historical Simulation",
                "confidence_levels": [0.95, 0.99],
                "daily_returns_pct": [
                    -1.2, 0.8, 0.3, -0.5, 1.1, 2.3, -0.8, -1.8, 0.6, -0.2,
                    0.9, -0.7, 1.5, -1.0, 0.4, -0.3, 2.1, -1.5, 0.1, 0.7,
                    -2.1, 1.8, -0.4, 1.3, -0.9, 1.6, -1.1, 0.5, -0.6, 2.0,
                    -1.4, 0.2, 1.9, -2.3, 0.0, 1.2, -0.1, 0.8, -1.7, 1.4,
                    -0.3, 1.7, -2.0, 0.9, -1.3, 1.0, -0.8, 0.6, -1.9, 2.2,
                    -0.5, 1.1, -1.6, 0.3, 2.4, -0.2, 1.3, -1.2, 0.7, -0.9,
                    1.5, -2.2, 0.4, 1.8, -0.7, 1.9, -0.4, 0.1, -1.0, 0.5,
                    -1.5, 2.3, -0.6, 1.2, -1.8, 0.9, -2.4, 1.6, -0.1, 0.2,
                    -1.3, 2.1, -0.8, 1.4, -2.5, 0.3, 1.0, -0.5, 1.7, -1.1,
                    0.8, -0.3, 2.0, -1.9, 0.6, -0.2, 1.1, -0.7, 0.4, -1.4,
                ],
            },
            indent=2,
        ),
        "expected_answer": (
            "Value-at-Risk Analysis\n\n"
            "1. Sorted returns (ascending) — 100 daily observations.\n"
            "   Worst return: -2.5%\n"
            "   5th percentile: approximately -1.9% (5th worst out of 100)\n"
            "   1st percentile: approximately -2.5% (worst return)\n\n"
            "2. 95% VaR = Rate at 5th percentile ≈ -1.9%\n"
            "   Interpretation: There is a 5% probability that daily loss "
            "exceeds 1.9%.\n\n"
            "3. 99% VaR = Rate at 1st percentile ≈ -2.5%\n"
            "   Interpretation: There is a 1% probability that daily loss "
            "exceeds 2.5%.\n\n"
            "4. Dollar Values (Portfolio = $50M):\n"
            "   95% VaR = $50M × 1.9% = $950,000\n"
            "   99% VaR = $50M × 2.5% = $1,250,000\n\n"
            "5. Expected Shortfall (CVaR) at 95%:\n"
            "   Average of returns beyond the 95% VaR threshold (worst 5 returns):\n"
            "   Mean of bottom 5 ≈ (-2.5% + -2.4% + -2.3% + -2.2% + -2.1%) / 5 = -2.3%\n"
            "   CVaR = $50M × 2.3% = $1,150,000\n\n"
            "6. Interpretation:\n"
            "   The firm should hold at least $1.25M in liquid reserves to "
            "cover 99% VaR. This is within the firm's risk appetite of "
            "$1.5M daily VaR limit. No breach."
        ),
        "checks": [
            {"type": "number", "target": 1.9, "tolerance": 0.5, "points": 20,
             "description": "Correct 95% VaR percentage"},
            {"type": "number", "target": 2.5, "tolerance": 0.5, "points": 20,
             "description": "Correct 99% VaR percentage"},
            {"type": "number", "target": 950000, "tolerance": 250000, "points": 15,
             "description": "Correct 95% VaR in dollars"},
            {"type": "keyword", "target": "expected shortfall", "points": 10,
             "description": "Calculates or references Expected Shortfall/CVaR"},
            {"type": "keyword", "target": "percentile", "points": 10,
             "description": "Correctly uses percentile-based methodology"},
            {"type": "keyword", "target": "historical simulation", "points": 10,
             "description": "References the historical simulation method"},
            {"type": "keyword", "target": "1.25", "points": 15,
             "description": "Correct 99% VaR dollar figure ($1.25M)"},
        ],
        "max_score": 100,
        "key_concepts": ["value-at-risk", "historical simulation", "expected shortfall",
                          "risk metrics", "confidence interval"],
    },

    # -----------------------------------------------------------------------
    # TASK 7: Quantitative — Trading Algorithm Logic Review
    # -----------------------------------------------------------------------
    {
        "id": 7,
        "category": "quantitative",
        "category_label": "Quantitative & Algorithmic Analysis",
        "title": "Automated Trading Algorithm — Logic & Security Audit",
        "difficulty": "hard",
        "briefing": (
            "A junior developer has submitted a Python-based momentum trading "
            "algorithm for review before deployment. The algorithm is intended to "
            "trade ETH/USDT futures. Review the code for logical errors, security "
            "vulnerabilities, and risk management deficiencies."
        ),
        "description": (
            "Review the following trading algorithm code. Identify:\n"
            "  1. At least 2 LOGICAL ERRORS that could cause financial loss.\n"
            "  2. At least 1 SECURITY VULNERABILITY.\n"
            "  3. At least 1 MISSING RISK CONTROL.\n"
            "  4. Provide corrected code for the most critical issue."
        ),
        "data_provided": (
            "```python\n"
            "def momentum_strategy(prices, volumes, position, capital):\n"
            "    \"\"\"\n"
            "    Momentum trading strategy for ETH/USDT futures.\n"
            "    \n"
            "    Parameters:\n"
            "        prices: list of closing prices (last 50 ticks)\n"
            "        volumes: list of volume data\n"
            "        position: current position (positive=long, negative=short)\n"
            "        capital: available trading capital\n"
            "    Returns:\n"
            "        signal: 1 (buy), -1 (sell), 0 (hold)\n"
            "        position_size: number of contracts\n"
            "    \"\"\"\n"
            "    # Calculate momentum as price change over lookback period\n"
            "    lookback = 14\n"
            "    momentum = (prices[-1] - prices[-lookback]) / prices[-lookback] * 100\n"
            "    \n"
            "    # Volume-weighted average price\n"
            "    vwap = sum(prices[i] * volumes[i] for i in range(len(prices))) / sum(volumes)\n"
            "    \n"
            "    # Entry logic\n"
            "    if momentum > 5.0 and position == 0:\n"
            "        # Strong momentum — go long\n"
            "        position_size = capital / prices[-1]  # No leverage\n"
            "        return 1, position_size\n"
            "    elif momentum < -5.0 and position == 0:\n"
            "        # Strong negative momentum — go short\n"
            "        position_size = capital / prices[-1]\n"
            "        return -1, position_size\n"
            "    \n"
            "    # Exit logic\n"
            "    if abs(momentum) < 1.0 and position != 0:\n"
            "        return 0, 0\n"
            "    \n"
            "    # Risk management (TODO: implement stop-loss)\n"
            "    # if position != 0 and unrealized_pnl < -capital * 0.02:\n"
            "    #     return 0, 0  # Stop-loss not yet implemented\n"
            "    \n"
            "    return 0, position\n"
            "```"
        ),
        "expected_answer": (
            "Algorithm Audit Report\n\n"
            "LOGICAL ERRORS:\n"
            "1. DIVISION BY ZERO (Critical): Line `sum(volumes)` will raise "
            "ZeroDivisionError if any volume in the series is 0 (which happens "
            "during low-liquidity periods or exchange glitches).\n"
            "   Impact: Strategy crashes, position is left open/unmanaged.\n\n"
            "2. LOOKBACK BOUNDS ERROR: `prices[-lookback]` will fail if "
            "len(prices) < 14. No guard clause for minimum data length.\n"
            "   Impact: IndexError during market open or early trading.\n\n"
            "3. POSITION SIZING FLAW: `capital / prices[-1]` does not account "
            "for leverage, margin requirements, or position limits. Could "
            "over-allocate if capital is large relative to contract size.\n\n"
            "SECURITY VULNERABILITIES:\n"
            "1. NO INPUT VALIDATION: The function assumes `prices` and `volumes` "
            "are well-formed lists. A manipulated input (e.g., infinite values, "
            "negative prices) could cause unpredictable behavior.\n\n"
            "2. MISSING AUTHENTICATION: The function doesn't verify that it's "
            "running with authorized credentials (no API key validation, no "
            "session check).\n\n"
            "MISSING RISK CONTROLS:\n"
            "1. NO STOP-LOSS: Commented out in code. Any position can draw down "
            "unlimited capital.\n"
            "2. NO MAX POSITION SIZE: No limit on position_size.\n"
            "3. NO CIRCUIT BREAKER: No check for unusual market conditions.\n\n"
            "CORRECTED CODE (most critical fix):\n"
            "```python\n"
            "def vwap(prices, volumes):\n"
            "    total_vol = sum(volumes)\n"
            "    if total_vol == 0:\n"
            "        return prices[-1]  # fallback to last price\n"
            "    return sum(p * v for p, v in zip(prices, volumes)) / total_vol\n"
            "```"
        ),
        "checks": [
            {"type": "keyword", "target": "division by zero", "points": 15,
             "description": "Identifies division by zero in VWAP calculation"},
            {"type": "keyword", "target": "stop-loss", "points": 15,
             "description": "Identifies missing stop-loss as a risk control gap"},
            {"type": "keyword", "target": "lookback", "points": 15,
             "description": "Identifies lookback boundary/index error"},
            {"type": "keyword", "target": "input validation", "points": 10,
             "description": "Identifies lack of input validation"},
            {"type": "keyword", "target": "position sizing", "points": 10,
             "description": "Identifies position sizing flaw"},
            {"type": "keyword", "target": "corrected", "points": 15,
             "description": "Provides corrected code for at least one issue"},
            {"type": "concept", "target": "risk control", "points": 10,
             "description": "Demonstrates understanding of risk controls"},
            {"type": "keyword", "target": "circuit breaker", "points": 10,
             "description": "Identifies missing circuit breaker or market check"},
        ],
        "max_score": 100,
        "key_concepts": ["algorithm auditing", "risk controls", "stop-loss",
                          "input validation", "position sizing"],
    },

    # -----------------------------------------------------------------------
    # TASK 8: Corporate Finance — Working Capital & Ratios
    # -----------------------------------------------------------------------
    {
        "id": 8,
        "category": "corporate_finance",
        "category_label": "Corporate Finance & Reporting",
        "title": "Working Capital Optimization & Ratio Analysis",
        "difficulty": "medium",
        "briefing": (
            "The Treasurer needs a working capital assessment for the quarterly "
            "board pack. Calculate key liquidity ratios and the cash conversion "
            "cycle, then provide optimization recommendations."
        ),
        "description": (
            "Using the balance sheet data below, calculate:\n"
            "  1. Current Ratio and Quick Ratio (Acid Test).\n"
            "  2. Cash Conversion Cycle (CCC) in days.\n"
            "  3. Net Working Capital.\n"
            "  4. Provide 2 specific recommendations to improve the CCC.\n"
            "  5. Calculate the impact if DSO is reduced by 5 days."
        ),
        "data_provided": json.dumps(
            {
                "company": "NovaCap Financial Technologies Ltd.",
                "period": "Q1 2026",
                "currency": "USD ($)",
                "balance_sheet_data": {
                    "current_assets": {
                        "cash_and_equivalents": 4200000,
                        "accounts_receivable": 5800000,
                        "marketable_securities": 2100000,
                        "inventory": 0,
                        "prepaid_expenses": 450000,
                    },
                    "current_liabilities": {
                        "accounts_payable": 3200000,
                        "short_term_debt": 1800000,
                        "accrued_expenses": 950000,
                        "deferred_revenue": 1100000,
                    },
                },
                "income_statement_annualized": {
                    "revenue": 52000000,
                    "cost_of_goods_sold": 28000000,
                },
                "receivables_data": {
                    "average_accounts_receivable": 5600000,
                },
                "payables_data": {
                    "average_accounts_payable": 3100000,
                },
            },
            indent=2,
        ),
        "expected_answer": (
            "Working Capital Analysis — Q1 2026\n\n"
            "1. Liquidity Ratios:\n"
            "   Current Ratio = Current Assets / Current Liabilities\n"
            "   = ($4.2M + $5.8M + $2.1M + $0 + $0.45M) / ($3.2M + $1.8M + $0.95M + $1.1M)\n"
            "   = $12,550,000 / $7,050,000 = 1.78\n\n"
            "   Quick Ratio = (Current Assets - Inventory - Prepaids) / Current Liabilities\n"
            "   = ($12.55M - $0 - $0.45M) / $7.05M\n"
            "   = $12,100,000 / $7,050,000 = 1.72\n\n"
            "   (Inventory = 0 for fintech firm, so ratios are similar.)\n\n"
            "2. Cash Conversion Cycle:\n"
            "   DSO = (Avg AR / Revenue) × 365 = ($5.6M / $52M) × 365 = 39.3 days\n"
            "   DPO = (Avg AP / COGS) × 365 = ($3.1M / $28M) × 365 = 40.4 days\n"
            "   DIO = 0 (fintech, no physical inventory)\n"
            "   CCC = DSO + DIO - DPO = 39.3 + 0 - 40.4 = -1.1 days\n\n"
            "   Negative CCC is EXCELLENT — the firm collects from customers "
            "before paying suppliers, meaning operations self-fund.\n\n"
            "3. Net Working Capital:\n"
            "   NWC = $12.55M - $7.05M = $5,500,000\n\n"
            "4. Recommendations:\n"
            "   a) Reduce DSO from 39.3 to 30 days: Offer 2/10 net 30 discount.\n"
            "      Potential cash release = ($5.6M × 9.3/365 × 12) ≈ $1.5M annual.\n"
            "   b) Extend DPO from 40.4 to 45 days: Renegotiate payment terms.\n\n"
            "5. DSO Reduction Impact:\n"
            "   5-day DSO reduction → Cash inflow = ($52M / 365) × 5 = $712,329\n"
            "   This improves NWC by ~$712k."
        ),
        "checks": [
            {"type": "number", "target": 1.78, "tolerance": 0.2, "points": 20,
             "description": "Correct current ratio (approx 1.78)"},
            {"type": "number", "target": 1.72, "tolerance": 0.2, "points": 15,
             "description": "Correct quick ratio (approx 1.72)"},
            {"type": "keyword", "target": "CCC", "points": 10,
             "description": "Calculates Cash Conversion Cycle"},
            {"type": "number", "target": 39.3, "tolerance": 5, "points": 15,
             "description": "Correct DSO value"},
            {"type": "keyword", "target": "negative", "points": 10,
             "description": "Recognizes negative CCC as favorable"},
            {"type": "keyword", "target": "DSO", "points": 10,
             "description": "Recommends reducing DSO"},
            {"type": "number", "target": 5500000, "tolerance": 500000, "points": 10,
             "description": "Correct net working capital"},
            {"type": "keyword", "target": "discount", "points": 10,
             "description": "Suggests discount terms or specific recommendation"},
        ],
        "max_score": 100,
        "key_concepts": ["working capital", "liquidity ratios", "cash conversion cycle",
                          "DSO", "DPO", "net working capital"],
    },

    # -----------------------------------------------------------------------
    # TASK 9: Risk & Compliance — SOCPA Compliance Review
    # -----------------------------------------------------------------------
    {
        "id": 9,
        "category": "risk_compliance",
        "category_label": "Risk & Compliance",
        "title": "Journal Entry Compliance Audit (SOCPA Framework)",
        "difficulty": "medium",
        "briefing": (
            "As part of the quarterly SOCPA compliance review, you must audit "
            "a sample of adjusting journal entries. SOCPA standards require "
            "proper authorization, complete supporting documentation, and "
            "correct account classification."
        ),
        "description": (
            "Review the following journal entries against SOCPA requirements:\n"
            "  1. Identify which entries violate SOCPA standards.\n"
            "  2. For each violation, cite the specific issue.\n"
            "  3. Classify severity: CRITICAL (misstatement risk), "
            "MODERATE (process gap), or MINOR (documentation).\n"
            "  4. Recommend corrective action for the most severe violation."
        ),
        "data_provided": json.dumps(
            {
                "compliance_framework": "SOCPA (Saudi Organization for Certified Public Accountants)",
                "review_date": "2026-04-15",
                "journal_entries": [
                    {
                        "je_id": "JE-101",
                        "date": "2026-03-31",
                        "description": "Accrued revenue - consulting services",
                        "account_debit": "Accounts Receivable",
                        "account_credit": "Revenue",
                        "amount": 750000,
                        "prepared_by": "Sarah Chen",
                        "approved_by": "Mark Johnson",
                        "has_support": True,
                        "support_type": "Signed contract + delivery receipt",
                        "notes": "",
                    },
                    {
                        "je_id": "JE-102",
                        "date": "2026-04-01",
                        "description": "Adjustment - goodwill impairment",
                        "account_debit": "Impairment Loss",
                        "account_credit": "Goodwill",
                        "amount": 1200000,
                        "prepared_by": "Ahmed Al-Rashid",
                        "approved_by": None,
                        "has_support": False,
                        "support_type": "",
                        "notes": "Urgent entry, approval will be obtained later",
                    },
                    {
                        "je_id": "JE-103",
                        "date": "2026-03-28",
                        "description": "Prepaid expense amortization",
                        "account_debit": "Operating Expense",
                        "account_credit": "Prepaid Expenses",
                        "amount": 85000,
                        "prepared_by": "Sarah Chen",
                        "approved_by": "Mark Johnson",
                        "has_support": True,
                        "support_type": "Amortization schedule",
                        "notes": "",
                    },
                    {
                        "je_id": "JE-104",
                        "date": "2026-04-02",
                        "description": "Revenue reversal - cancelled contract",
                        "account_debit": "Revenue",
                        "account_credit": "Accounts Receivable",
                        "amount": 500000,
                        "prepared_by": "John Smith",
                        "approved_by": "Mark Johnson",
                        "has_support": True,
                        "support_type": "Cancellation notice",
                        "notes": "Original revenue recognized in prior quarter",
                    },
                    {
                        "je_id": "JE-105",
                        "date": "2026-04-05",
                        "description": "Miscellaneous adjustment per CFO",
                        "account_debit": "Retained Earnings",
                        "account_credit": "Accounts Payable",
                        "amount": 350000,
                        "prepared_by": "Ahmed Al-Rashid",
                        "approved_by": "Layla Hassan (CFO)",
                        "has_support": False,
                        "support_type": "",
                        "notes": "CFO directed this adjustment verbally",
                    },
                    {
                        "je_id": "JE-106",
                        "date": "2026-03-25",
                        "description": "Depreciation - IT equipment",
                        "account_debit": "Depreciation Expense",
                        "account_credit": "Accumulated Depreciation",
                        "amount": 145000,
                        "prepared_by": "Sarah Chen",
                        "approved_by": "Mark Johnson",
                        "has_support": True,
                        "support_type": "Fixed asset register",
                        "notes": "",
                    },
                ],
            },
            indent=2,
        ),
        "expected_answer": (
            "SOCPA Compliance Audit Report\n\n"
            "VIOLATIONS FOUND:\n\n"
            "1. JE-102: Goodwill Impairment — CRITICAL\n"
            "   Issues:\n"
            "   - No approval (approved_by = None)\n"
            "   - No supporting documentation\n"
            "   - Goodwill impairment requires independent valuation under SOCPA\n"
            "   - Entry dated April 1 (new quarter) for prior period adjustment\n"
            "   Severity: CRITICAL — could result in material misstatement\n\n"
            "2. JE-105: CFO Verbal Adjustment — CRITICAL\n"
            "   Issues:\n"
            "   - No supporting documentation (verbal instruction is insufficient)\n"
            "   - Debit to Retained Earnings bypasses P&L (potential fraud risk)\n"
            "   - 'Miscellaneous' is not a valid description under SOCPA\n"
            "   - Needs written approval and documented business rationale\n"
            "   Severity: CRITICAL — bypasses internal controls\n\n"
            "3. SOCPA Standard Reference: \n"
            "   - SOCPA requires ALL journal entries to have: proper authorization, "
            "adequate supporting documentation, clear business purpose, and "
            "correct period recording.\n\n"
            "CORRECTIVE ACTIONS:\n"
            "   JE-102: Reverse entry until independent goodwill valuation "
            "is obtained AND proper approval is secured.\n"
            "   JE-105: Obtain written instruction from CFO, document business "
            "purpose, and attach supporting calculation."
        ),
        "checks": [
            {"type": "keyword", "target": "JE-102", "points": 20,
             "description": "Identifies JE-102 as non-compliant"},
            {"type": "keyword", "target": "JE-105", "points": 20,
             "description": "Identifies JE-105 as non-compliant"},
            {"type": "keyword", "target": "no approval", "points": 15,
             "description": "Flags missing approval as an issue"},
            {"type": "keyword", "target": "supporting documentation", "points": 15,
             "description": "Identifies missing supporting documentation"},
            {"type": "keyword", "target": "critical", "points": 10,
             "description": "Correctly classifies severity as critical"},
            {"type": "keyword", "target": "SOCPA", "points": 10,
             "description": "References SOCPA standards correctly"},
            {"type": "keyword", "target": "verbal", "points": 10,
             "description": "Flags verbal instruction as insufficient"},
        ],
        "max_score": 100,
        "key_concepts": ["SOCPA", "compliance", "journal entry audit", "internal controls",
                          "supporting documentation"],
    },

    # -----------------------------------------------------------------------
    # TASK 10: Quantitative — Portfolio Optimization
    # -----------------------------------------------------------------------
    {
        "id": 10,
        "category": "quantitative",
        "category_label": "Quantitative & Algorithmic Analysis",
        "title": "Multi-Asset Portfolio Optimization (Minimum Variance)",
        "difficulty": "hard",
        "briefing": (
            "The portfolio management team is constructing a new multi-asset "
            "portfolio with three asset classes. Using Modern Portfolio Theory "
            "(Markowitz), calculate the minimum variance portfolio weights "
            "and analyze the risk-return profile."
        ),
        "description": (
            "Given three assets with the following parameters:\n"
            "  - Asset A: Expected return 8%, Volatility 15%\n"
            "  - Asset B: Expected return 12%, Volatility 22%\n"
            "  - Asset C: Expected return 5%, Volatility 10%\n\n"
            "  Correlation Matrix:\n"
            "           A       B       C\n"
            "    A     1.00    0.30    0.15\n"
            "    B     0.30    1.00   -0.10\n"
            "    C     0.15   -0.10    1.00\n\n"
            "Calculate:\n"
            "  1. The minimum variance portfolio weights (no short constraint).\n"
            "  2. Portfolio expected return and volatility at these weights.\n"
            "  3. The Sharpe Ratio (assume risk-free rate = 3%).\n"
            "  4. How would the optimal weights change if Asset B had a "
            "short constraint (w_B ≥ 0)?"
        ),
        "data_provided": json.dumps(
            {
                "method": "Markowitz Mean-Variance Optimization",
                "risk_free_rate": 0.03,
                "assets": {
                    "A": {"expected_return": 0.08, "volatility": 0.15},
                    "B": {"expected_return": 0.12, "volatility": 0.22},
                    "C": {"expected_return": 0.05, "volatility": 0.10},
                },
                "correlation_matrix": {
                    "A": {"A": 1.00, "B": 0.30, "C": 0.15},
                    "B": {"A": 0.30, "B": 1.00, "C": -0.10},
                    "C": {"A": 0.15, "B": -0.10, "C": 1.00},
                },
            },
            indent=2,
        ),
        "expected_answer": (
            "Portfolio Optimization Report\n\n"
            "1. Covariance Matrix:\n"
            "   Var(A) = 0.0225, Cov(A,B) = 0.0099, Cov(A,C) = 0.00225\n"
            "   Var(B) = 0.0484, Cov(B,C) = -0.0022\n"
            "   Var(C) = 0.0100\n\n"
            "2. Minimum Variance Portfolio (unconstrained):\n"
            "   Using Lagrangian optimization:\n"
            "   w_A ≈ 0.324 (32.4%)\n"
            "   w_B ≈ 0.108 (10.8%)\n"
            "   w_C ≈ 0.568 (56.8%)\n"
            "   Sum = 1.00 ✓\n\n"
            "3. Portfolio Metrics:\n"
            "   Expected Return = 0.324(8%) + 0.108(12%) + 0.568(5%)\n"
            "                    = 6.49%\n"
            "   Portfolio Variance = w^T Σ w ≈ 0.0081\n"
            "   Portfolio Volatility = √0.0081 = 9.0%\n\n"
            "4. Sharpe Ratio = (6.49% - 3%) / 9.0% = 0.388\n\n"
            "5. With Short Constraint on B (w_B ≥ 0):\n"
            "   Since optimal w_B = 10.8% (already positive), no change needed.\n"
            "   If the constraint were w_B = 0 (not allowed), then:\n"
            "   w_A ≈ 39%, w_C ≈ 61%, portfolio volatility ≈ 10.5%."
        ),
        "checks": [
            {"type": "keyword", "target": "minimum variance", "points": 15,
             "description": "Correctly identifies minimum variance approach"},
            {"type": "number", "target": 0.324, "tolerance": 0.1, "points": 15,
             "description": "Approximately correct weight for Asset A"},
            {"type": "number", "target": 0.108, "tolerance": 0.1, "points": 15,
             "description": "Approximately correct weight for Asset B"},
            {"type": "number", "target": 0.568, "tolerance": 0.15, "points": 15,
             "description": "Approximately correct weight for Asset C"},
            {"type": "number", "target": 9.0, "tolerance": 2.0, "points": 15,
             "description": "Approximately correct portfolio volatility"},
            {"type": "keyword", "target": "sharpe", "points": 10,
             "description": "Calculates Sharpe Ratio"},
            {"type": "keyword", "target": "covariance", "points": 15,
             "description": "Correctly computes or references covariance matrix"},
        ],
        "max_score": 100,
        "key_concepts": ["portfolio optimization", "Markowitz", "minimum variance",
                          "Sharpe ratio", "covariance matrix"],
    },
]

# Task categories for random selection
TASK_CATEGORIES = {
    "quantitative": "Quantitative & Algorithmic Analysis",
    "corporate_finance": "Corporate Finance & Reporting",
    "risk_compliance": "Risk & Compliance",
}


# ==============================================================================
# SECTION 4 — SYNTHETIC MARKET DATA GENERATOR
# ==============================================================================

class MarketDataGenerator:
    """Generates realistic synthetic market data for the morning briefing."""

    @staticmethod
    def _random_walk(start: float, steps: int, vol: float = 0.015) -> List[float]:
        """Generate a geometric Brownian motion random walk."""
        values = [start]
        for _ in range(steps):
            ret = random.gauss(0, vol)
            values.append(values[-1] * (1 + ret))
        return values

    @staticmethod
    def generate_briefing() -> Dict[str, Any]:
        """Generate a complete morning market briefing with synthetic data."""
        # Ensure deterministic-ish but varied output
        seed_val = datetime.now().toordinal() + datetime.now().hour
        random.seed(seed_val)

        # Major indices
        spy_path = MarketDataGenerator._random_walk(5432.10, 20, 0.008)
        spy_change = ((spy_path[-1] / spy_path[0]) - 1) * 100

        # Crypto
        btc_path = MarketDataGenerator._random_walk(67800, 20, 0.025)
        btc_change = ((btc_path[-1] / btc_path[0]) - 1) * 100

        eth_path = MarketDataGenerator._random_walk(3125, 20, 0.03)
        eth_change = ((eth_path[-1] / eth_path[0]) - 1) * 100

        # FX
        eurusd = random.uniform(1.05, 1.12)
        usdsar = 3.75  # Pegged

        # Volatility (VIX proxy)
        vix = random.uniform(12.5, 28.0)

        # 10Y Yield
        yield_10y = random.uniform(3.8, 4.6)

        # Macro events
        events_pool = [
            "Fed maintains current rate (5.25-5.50%) — hawkish hold",
            "OPEC+ announces production cut extension",
            "US CPI data due today (consensus: 3.1% YoY)",
            "China GDP beats expectations at 5.3%",
            "ECB signals potential rate cut in next meeting",
            "UK inflation drops to 2-year low",
            "Japan intervenes in FX market to support yen",
            "Gold hits new all-time high above $2,400",
            "Treasury yield curve steepens on long-end selling",
            "Crypto regulation bill advances in EU parliament",
            "Saudi Arabia announces new fintech sandbox regulations",
            "Dubai Financial Services Authority issues new crypto guidance",
        ]
        selected_events = random.sample(events_pool, min(4, len(events_pool)))

        return {
            "date": datetime.now().strftime("%A, %B %d, %Y"),
            "session": f"Day {random.randint(1, 252)} of Trading Year",
            "indices": {
                "S&P 500": {"level": round(spy_path[-1], 2), "change_pct": round(spy_change, 2)},
                "NASDAQ 100": {"level": round(random.uniform(17000, 19500), 2), "change_pct": round(random.uniform(-2.5, 2.5), 2)},
            },
            "crypto": {
                "BTC/USD": {"level": round(btc_path[-1], 2), "change_pct": round(btc_change, 2)},
                "ETH/USD": {"level": round(eth_path[-1], 2), "change_pct": round(eth_change, 2)},
            },
            "fx": {
                "EUR/USD": round(eurusd, 4),
                "USD/SAR": usdsar,
            },
            "volatility": {
                "VIX": round(vix, 2),
                "10Y Treasury Yield": f"{round(yield_10y, 2)}%",
            },
            "key_events": selected_events,
        }


# ==============================================================================
# SECTION 5 — TASK GENERATOR
# ==============================================================================

class TaskGenerator:
    """
    Responsible for selecting and preparing daily task sets.
    Ensures diversity across the three primary categories.
    """

    def __init__(self):
        self._all_tasks = {t["id"]: t for t in TASK_DATABASE}

    def generate_daily_tasks(self) -> List[Dict[str, Any]]:
        """
        Select 3 tasks for the day — one from each category.
        Tasks are randomly selected within each category.
        """
        cat_tasks = {"quantitative": [], "corporate_finance": [], "risk_compliance": []}
        for task in self._all_tasks.values():
            cat_tasks[task["category"]].append(task)

        selected = []
        for cat in ["quantitative", "corporate_finance", "risk_compliance"]:
            if cat_tasks[cat]:
                choice = random.choice(cat_tasks[cat])
                selected.append(choice)

        # Shuffle the order for variety
        random.shuffle(selected)
        return selected

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a task by its ID."""
        return self._all_tasks.get(task_id)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Return all available tasks."""
        return list(self._all_tasks.values())


# ==============================================================================
# SECTION 6 — EVALUATION ENGINE
# ==============================================================================

class EvaluationEngine:
    """
    Evaluates user-submitted answers against expected answers.
    Produces a 0-100 score per task with detailed variance analysis.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Clear previous evaluation state."""
        self.results: Dict[int, Dict[str, Any]] = {}

    def evaluate(self, task: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
        """
        Evaluate a user's answer for a given task.
        Returns a detailed evaluation result.
        """
        if not user_answer or not user_answer.strip():
            return {
                "task_id": task["id"],
                "title": task["title"],
                "score": 0,
                "max_score": task["max_score"],
                "percentage": 0.0,
                "grade": "F",
                "checks": [],
                "feedback": "No answer submitted.",
                "expected": task["expected_answer"],
                "user_answer": user_answer,
            }

        answer_lower = user_answer.lower()
        checks_results = []
        total_earned = 0
        max_possible = sum(c["points"] for c in task["checks"])

        for check in task["checks"]:
            check_type = check["type"]
            target = check["target"]
            points = check["points"]
            desc = check["description"]
            earned = 0

            if check_type == "keyword":
                # Check if keyword appears in user answer
                if target.lower() in answer_lower:
                    earned = points
                else:
                    # Partial credit for stemming/similar terms
                    words = target.lower().split()
                    if len(words) > 1 and any(w in answer_lower for w in words):
                        earned = points * 0.5

            elif check_type == "number":
                # Parse numbers from user answer and check if target is within tolerance
                target_val = check["target"]
                tolerance = check.get("tolerance", target_val * 0.1)

                # Extract all numbers from answer
                numbers = re.findall(r"[-+]?\d*\.?\d+", user_answer)
                numbers = [float(n) for n in numbers]

                if numbers:
                    # Check if any extracted number is close to target
                    best_match = min(numbers, key=lambda x: abs(x - target_val))
                    if abs(best_match - target_val) <= tolerance:
                        earned = points
                    elif abs(best_match - target_val) <= tolerance * 2:
                        earned = points * 0.5

            elif check_type == "concept":
                # Check if the concept is demonstrated through keywords
                concept_keywords = target.lower().split()
                matches = sum(1 for kw in concept_keywords if kw in answer_lower)
                ratio = matches / len(concept_keywords) if concept_keywords else 0
                if ratio >= 0.8:
                    earned = points
                elif ratio >= 0.4:
                    earned = points * 0.5

            checks_results.append({
                "type": check_type,
                "target": target,
                "points_possible": points,
                "points_earned": earned,
                "description": desc,
                "passed": earned >= points * 0.8,
                "partial": 0 < earned < points,
            })
            total_earned += earned

        # Score calculation
        max_score = task["max_score"]
        if max_possible > 0:
            percentage = (total_earned / max_possible) * 100
        else:
            percentage = 0

        # Normalize to 0-100 scale
        score = min(100, round(percentage))
        score = max(0, score)

        # Grade assignment
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        # Generate feedback
        feedback_parts = []
        passed_checks = [c for c in checks_results if c["passed"]]
        failed_checks = [c for c in checks_results if not c["passed"] and c["points_earned"] == 0]
        partial_checks = [c for c in checks_results if c["partial"]]

        if passed_checks:
            feedback_parts.append(
                "[OK] Strengths: {0} checks passed ({1} pts)".format(
                    len(passed_checks), sum(c['points_earned'] for c in passed_checks))
            )
        if partial_checks:
            feedback_parts.append(
                "[~] Partial: {0} checks partially met ({1} pts)".format(
                    len(partial_checks), sum(c['points_earned'] for c in partial_checks))
            )
        if failed_checks:
            feedback_parts.append(
                "[X] Gaps: {0} checks failed ({1} pts missed)".format(
                    len(failed_checks), sum(c['points_possible'] for c in failed_checks))
            )
            # List top failed checks
            for fc in failed_checks[:3]:
                feedback_parts.append(f"   - {fc['description']} ({fc['points_possible']} pts)")

        if not feedback_parts:
            feedback_parts.append("Answer received but minimal criteria detected.")

        # Identify critical errors
        critical_errors = []
        for fc in failed_checks:
            if fc["points_possible"] >= 15:
                critical_errors.append(fc["description"])

        result = {
            "task_id": task["id"],
            "title": task["title"],
            "score": score,
            "max_score": max_score,
            "percentage": score,
            "grade": grade,
            "checks": checks_results,
            "feedback": "\n".join(feedback_parts),
            "expected": task["expected_answer"],
            "user_answer": user_answer,
            "critical_errors": critical_errors,
        }

        self.results[task["id"]] = result
        return result

    def generate_variance_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive variance report from evaluation results."""
        lines = []
        total_score = 0
        total_max = 0
        critical_flags = []

        lines.append(h2(" COMPREHENSIVE EVALUATION REPORT "))
        lines.append(separator())
        lines.append("")

        for r in results:
            total_score += r["score"]
            # Use each task's max_score; fallback to 100
            t_max = r.get("max_score", 100)
            total_max += t_max

            grade_color = {
                "A": Color.SUCCESS, "B": Color.SUCCESS, "C": Color.WARNING,
                "D": Color.WARNING, "F": Color.ERROR,
            }.get(r["grade"], Color.MUTED)

            lines.append(h3(f"  Task {r['task_id']}: {r['title']}"))
            lines.append(separator("─", Color.GRAY))
            grade_val = r["grade"]
            score_val = r["score"]
            max_score_val = r["max_score"]
            pct_val = r["percentage"]
            lines.append(
                f"    {c(grade_color, f'Grade: {grade_val}')}  |  "
                f"Score: {c(Color.BRIGHT_WHITE, str(score_val))}/{max_score_val}  |  "
                f"{c(Color.BRIGHT_WHITE, f'{pct_val:.0f}%')}"
            )
            lines.append("")

            # Critical errors
            if r.get("critical_errors"):
                critical_flags.extend(r["critical_errors"])
                lines.append(f"    {c(Color.ERROR, '!! CRITICAL ERROR(S):')}")
                for ce in r["critical_errors"]:
                    lines.append(f"      {c(Color.BRIGHT_RED, '•')} {ce}")
                lines.append("")

            # Feedback
            lines.append(f"    {c(Color.INFO, 'Feedback:')}")
            for fb_line in r["feedback"].split("\n"):
                lines.append(f"      {fb_line}")
            lines.append("")

            # Variance: Expected vs User
            lines.append(f"    {c(Color.WARNING, 'Variance Analysis — Expected vs Provided:')}")
            exp_lines = r["expected"].strip().split("\n")
            user_lines = r["user_answer"].strip().split("\n") if r["user_answer"] else ["[No answer]"]

            # Show expected (truncated if very long)
            exp_preview = "\n".join(exp_lines[:12])
            if len(exp_lines) > 12:
                exp_preview += "\n        ... (truncated, full expected answer in report)"
            user_preview = "\n".join(user_lines[:8])
            if len(user_lines) > 8:
                user_preview += "\n        ... (truncated)"

            lines.append(f"    {c(Color.BRIGHT_CYAN, 'Expected (key elements):')}")
            for el in exp_preview.split("\n"):
                lines.append(f"      {el}")

            lines.append(f"    {c(Color.BRIGHT_YELLOW, 'Your Answer (preview):')}")
            for ul in user_preview.split("\n"):
                lines.append(f"      {ul}")

            lines.append("")
            lines.append(separator("─", Color.DIM))

        # Summary
        lines.append("")
        overall_pct = (total_score / total_max * 100) if total_max > 0 else 0
        overall_grade = "A" if overall_pct >= 90 else "B" if overall_pct >= 80 else \
                        "C" if overall_pct >= 70 else "D" if overall_pct >= 60 else "F"

        grade_color_map = {"A": Color.SUCCESS, "B": Color.SUCCESS, "C": Color.WARNING,
                           "D": Color.WARNING, "F": Color.ERROR}
        og_color = grade_color_map.get(overall_grade, Color.MUTED)

        lines.append(h2(" OVERALL DAILY PERFORMANCE "))
        lines.append(separator())
        lines.append(
            f"  Total Score: {c(Color.BRIGHT_WHITE, str(total_score))}/{total_max}  "
            f"({c(Color.BRIGHT_WHITE, f'{overall_pct:.1f}%')})  "
            f"Overall Grade: {c(og_color, overall_grade)}"
        )

        if critical_flags:
            lines.append("")
            lines.append(c(Color.ERROR, "  !! CRITICAL ISSUES REQUIRING ATTENTION:"))
            for cf in set(critical_flags):
                lines.append(f"    • {cf}")

        # CMA/SOCPA competency mapping
        lines.append("")
        lines.append(h2(" CMA / SOCPA COMPETENCY MAPPING "))
        lines.append(separator())
        lines.append("  Competency areas assessed:")
        lines.append("    • Financial Statement Analysis (CMA Part 1 - Section C)")
        lines.append("    • Risk Management & Internal Controls (CMA Part 1 - Section E)")
        lines.append("    • Quantitative Methods & Decision Analysis (CMA Part 2 - Section A)")
        lines.append("    • Investment Decision Analysis (CMA Part 2 - Section D)")
        lines.append("    • SOCPA Audit & Assurance Standards Compliance")
        lines.append("")
        lines.append(f"  {c(Color.INFO, 'Next steps: Review gaps highlighted above and revisit')}")
        lines.append(f"  {c(Color.INFO, 'relevant CMA/SOCPA study materials for failed checks.')}")

        return "\n".join(lines)

    def get_detailed_report_text(self, task: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Generate a per-task detailed report."""
        lines = []
        lines.append(h2(f" TASK {task['id']}: {task['title']} — DETAILED ANALYSIS "))
        lines.append(separator())
        lines.append(f"  Category: {task['category_label']}")
        lines.append(f"  Difficulty: {task['difficulty'].upper()}")
        lines.append(f"  Score: {result['score']}/{result['max_score']} ({result['percentage']:.0f}%)")
        lines.append(f"  Grade: {result['grade']}")
        lines.append("")
        lines.append(f"  {c(Color.WARNING, 'YOUR ANSWER:')}")
        for line in result['user_answer'].strip().split("\n"):
            lines.append(f"    {line}")
        lines.append("")
        lines.append(f"  {c(Color.SUCCESS, 'EXPECTED ANSWER:')}")
        for line in task['expected_answer'].strip().split("\n"):
            lines.append(f"    {line}")
        lines.append("")
        lines.append(f"  {c(Color.INFO, 'CHECK BREAKDOWN:')}")
        for check in result['checks']:
            icon = c(Color.SUCCESS, "[PASS]") if check['passed'] else \
                   c(Color.WARNING, "[PART]") if check['partial'] else \
                   c(Color.ERROR, "[FAIL]")
            lines.append(f"    {icon} {check['description']}: {check['points_earned']}/{check['points_possible']}")
        return "\n".join(lines)


# ==============================================================================
# SECTION 7 — SIMULATION STATE
# ==============================================================================

class SimulationState:
    """
    Manages the lifecycle of a daily simulation session.
    Tracks time, tasks, answers, and overall state.
    """

    # Simulation time constants
    DAY_START_HOUR = 9   # 09:00
    DAY_END_HOUR = 17    # 17:00

    def __init__(self):
        self.reset()

    def reset(self):
        """Initialize or reset the simulation state."""
        self.phase = "initialized"  # initialized → briefing → working → eod → complete
        self.simulation_date = datetime.now().strftime("%Y-%m-%d")
        self.current_time_minutes = self.DAY_START_HOUR * 60  # minutes from midnight
        self.tasks: List[Dict[str, Any]] = []
        self.answers: Dict[int, str] = {}
        self.completed_task_ids: List[int] = []
        self.current_task_id: Optional[int] = None
        self.market_briefing: Optional[Dict[str, Any]] = None
        self.evaluation_results: List[Dict[str, Any]] = []
        self.role_confirmed = False
        self.company = CompanyConfig()
        self.role = RoleConfig()

    @property
    def current_time_str(self) -> str:
        """Get the current simulation time as HH:MM string."""
        hours = self.current_time_minutes // 60
        minutes = self.current_time_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    @property
    def is_morning(self) -> bool:
        """Check if we're in the morning session (before 12:00)."""
        return self.current_time_minutes < 12 * 60

    @property
    def is_eod(self) -> bool:
        """Check if we've reached end of day."""
        return self.current_time_minutes >= self.DAY_END_HOUR * 60

    def advance_time(self, minutes: int = 15) -> None:
        """Advance the simulation clock by specified minutes."""
        self.current_time_minutes += minutes
        if self.current_time_minutes > self.DAY_END_HOUR * 60:
            self.current_time_minutes = self.DAY_END_HOUR * 60

    def time_remaining_str(self) -> str:
        """Get a string describing time remaining until EOD."""
        remaining = (self.DAY_END_HOUR * 60) - self.current_time_minutes
        if remaining <= 0:
            return "End of Day reached"
        hours = remaining // 60
        mins = remaining % 60
        return f"{hours}h {mins}m remaining"

    def submit_answer(self, task_id: int, answer: str) -> None:
        """Record a user's answer for a task."""
        self.answers[task_id] = answer
        if task_id not in self.completed_task_ids:
            self.completed_task_ids.append(task_id)

    def all_tasks_completed(self) -> bool:
        """Check if all assigned tasks have been answered."""
        return len(self.completed_task_ids) >= len(self.tasks) and len(self.tasks) > 0

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get list of tasks not yet completed."""
        return [t for t in self.tasks if t["id"] not in self.completed_task_ids]

    def get_completed_tasks(self) -> List[Dict[str, Any]]:
        """Get list of completed tasks."""
        return [t for t in self.tasks if t["id"] in self.completed_task_ids]


# ==============================================================================
# SECTION 8 — MAIN CLI APPLICATION
# ==============================================================================

class FinanceSimCLI(cmd.Cmd):
    """
    Interactive command-line interface for the corporate finance simulation.
    Uses Python's cmd module for a familiar shell-like experience.
    """

    intro = ""
    prompt = f"{c(Color.PROMPT, '⌨  finance> ')}"

    def __init__(self):
        super().__init__()
        self.state = SimulationState()
        self.task_gen = TaskGenerator()
        self.evaluator = EvaluationEngine()
        self.running = True

    # ----- Utility display methods -----

    def _print_header(self) -> None:
        """Display the application header/splash."""
        Cc = Color
        Bc = BoxChars
        tl = Cc.BRIGHT_CYAN + Bc.TL2 + Bc.H2 * 72 + Bc.TR2 + Cc.RESET
        bl = Cc.BRIGHT_CYAN + Bc.BL2 + Bc.H2 * 72 + Bc.BR2 + Cc.RESET
        bar = Cc.BRIGHT_CYAN + Bc.V2 + Cc.RESET
        sp72 = " " * 72
        sp14 = " " * 14
        sp8 = " " * 8
        sp13 = " " * 13
        sp12 = " " * 12

        header_lines = [
            "",
            tl,
            f"{bar}{sp72}{bar}",
            f"{bar}{sp14}{Cc.BOLD}NOVACAP FINANCIAL TECHNOLOGIES LTD.{sp14}{bar}",
            f"{bar}{sp8}{Cc.RESET}{Cc.BRIGHT_CYAN}Corporate Finance Daily Simulation Environment{sp8}{bar}",
            f"{bar}{sp72}{bar}",
            f"{bar}{Cc.RESET}{Cc.GRAY}  Role: Financial Analyst -- FinTech Arbitrage Specialist{sp13}{bar}",
            f"{bar}  Standards: CMA Framework | SOCPA Compliance | IFRS Reporting{sp8}{bar}",
            f"{bar}  Firm: NovaCap Financial Technologies Ltd. -- DIFC, Dubai{sp12}{bar}",
            f"{bar}{sp72}{bar}",
            bl,
            Cc.RESET,
        ]
        print("\n".join(header_lines))

    def _print_morning_briefing(self) -> None:
        """Display the morning market briefing."""
        data = self.state.market_briefing
        if not data:
            return

        Cc = Color
        Bc = BoxChars
        tl = Cc.BRIGHT_CYAN + Bc.TL + Bc.H * 72 + Bc.TR + Cc.RESET
        ml = Cc.BRIGHT_CYAN + Bc.ML + Bc.H * 72 + Bc.MR + Cc.RESET
        bl = Cc.BRIGHT_CYAN + Bc.BL + Bc.H * 72 + Bc.BR + Cc.RESET
        sp27 = " " * 27
        sp50 = " " * 50

        lines = [
            "",
            tl,
            f"{Cc.BOLD}  {Bc.SUN}  MORNING BRIEFING -- {data['date']}{sp27}{Cc.RESET}",
            f"{Cc.RESET}{Cc.GRAY}  {data['session']}{sp50}{Cc.RESET}",
            ml,
            "",
            f"{Cc.BOLD}{Cc.BRIGHT_WHITE}  MARKET DATA{Cc.RESET}",
            f"{Cc.CYAN}  {Bc.DASH * 57}{Cc.RESET}",
            "",
        ]

        # Equities
        chg = data['indices']['S&P 500']['change_pct']
        chg_str = c(Cc.GREEN if chg >= 0 else Cc.RED, f"{chg:+.2f}%")
        lines.append(f"{Cc.BRIGHT_YELLOW}  EQUITIES:{Cc.RESET}")
        lines.append(f"    S&P 500:  {Cc.BRIGHT_WHITE}{data['indices']['S&P 500']['level']:,}{Cc.RESET}  ({chg_str})")

        chg2 = data['indices']['NASDAQ 100']['change_pct']
        chg2_str = c(Cc.GREEN if chg2 >= 0 else Cc.RED, f"{chg2:+.2f}%")
        lines.append(f"    NASDAQ:   {Cc.BRIGHT_WHITE}{data['indices']['NASDAQ 100']['level']:,}{Cc.RESET}  ({chg2_str})")
        lines.append("")

        # Crypto
        btc_chg = data['crypto']['BTC/USD']['change_pct']
        btc_c = c(Cc.GREEN if btc_chg >= 0 else Cc.RED, f"{btc_chg:+.2f}%")
        lines.append(f"{Cc.BRIGHT_YELLOW}  CRYPTOCURRENCIES:{Cc.RESET}")
        lines.append(f"    BTC/USD:  {Cc.BRIGHT_WHITE}${data['crypto']['BTC/USD']['level']:,.2f}{Cc.RESET}  ({btc_c})")

        eth_chg = data['crypto']['ETH/USD']['change_pct']
        eth_c = c(Cc.GREEN if eth_chg >= 0 else Cc.RED, f"{eth_chg:+.2f}%")
        lines.append(f"    ETH/USD:  {Cc.BRIGHT_WHITE}${data['crypto']['ETH/USD']['level']:,.2f}{Cc.RESET}  ({eth_c})")
        lines.append("")

        # FX & Rates
        lines.append(f"{Cc.BRIGHT_YELLOW}  FX & RATES:{Cc.RESET}")
        lines.append(f"    EUR/USD:  {Cc.BRIGHT_WHITE}{data['fx']['EUR/USD']}{Cc.RESET}")
        lines.append(f"    USD/SAR:  {Cc.BRIGHT_WHITE}{data['fx']['USD/SAR']}{Cc.RESET} (pegged)")
        lines.append(f"    VIX:      {Cc.BRIGHT_WHITE}{data['volatility']['VIX']}{Cc.RESET}")
        lines.append(f"    10Y Yield: {Cc.BRIGHT_WHITE}{data['volatility']['10Y Treasury Yield']}{Cc.RESET}")
        lines.append("")

        # Key events
        lines.append(f"{Cc.BOLD}{Cc.BRIGHT_WHITE}  KEY MACRO EVENTS{Cc.RESET}")
        lines.append(f"{Cc.CYAN}  {Bc.DASH * 57}{Cc.RESET}")
        for evt in data["key_events"]:
            lines.append(f"    {Cc.BRIGHT_MAGENTA}{Bc.BULLET}{Cc.RESET} {evt}")
        lines.append("")

        # Footer
        lines.append(f"{Cc.CYAN}  {Bc.DASH * 57}{Cc.RESET}")
        lines.append(f"{Cc.DIM}  Time: {self.state.current_time_str} | {self.state.time_remaining_str()}{Cc.RESET}")
        lines.append("")

        print("\n".join(lines))

    def _print_inbox(self) -> None:
        """Display the simulated email inbox with assigned tasks."""
        Cc = Color
        Bc = BoxChars
        dash = Bc.DASH * 57
        inbox_label = "INBOX" if not _USE_UNICODE else "\U0001F4EC INBOX"
        print(f"\n{Cc.BOLD}{Cc.BRIGHT_CYAN}  {inbox_label} -- {len(self.state.tasks)} New Tasks Assigned{Cc.RESET}")
        print(f"{Cc.CYAN}  {dash}{Cc.RESET}")

        for i, task in enumerate(self.state.tasks, 1):
            cat_color = {
                "quantitative": Cc.BRIGHT_BLUE,
                "corporate_finance": Cc.BRIGHT_GREEN,
                "risk_compliance": Cc.BRIGHT_YELLOW,
            }.get(task["category"], Cc.WHITE)

            cat_labels = {
                "quantitative": "QUANT",
                "corporate_finance": "CORP FIN",
                "risk_compliance": "RISK/COMP",
            }

            status = ""
            if task["id"] in self.state.completed_task_ids:
                status = f" {c(Cc.SUCCESS, f'[{Bc.CHECK} SUBMITTED]')}"

            diff_color = {
                "easy": Cc.GREEN,
                "medium": Cc.YELLOW,
                "hard": Cc.RED,
            }.get(task["difficulty"], Cc.WHITE)

            cat_label = cat_labels.get(task["category"], "TASK")
            cat_display = c(cat_color, f"[{cat_label}]")
            title_display = c(Cc.BRIGHT_WHITE, f"Task #{i}: {task['title']}{status}")
            diff_display = c(diff_color, task["difficulty"].upper())
            brief_text = task["briefing"][:120]
            if len(task["briefing"]) > 120:
                brief_text += "..."
            print(f"""
  {cat_display} {title_display}
  {Cc.DIM}  ID: {task['id']} | Difficulty: {diff_display} | {task['category_label']}{Cc.RESET}
  {Cc.GRAY}  {brief_text}{Cc.RESET}""")

        print(f"\n{Cc.CYAN}  {dash}{Cc.RESET}")
        print(f"  {c(Cc.INFO, 'Use')} {c(Cc.BRIGHT_WHITE, 'workon <task_id>')} {c(Cc.INFO, 'to start a task.')}")
        print(f"  {c(Cc.INFO, 'Type')} {c(Cc.BRIGHT_WHITE, 'help')} {c(Cc.INFO, 'for available commands.')}")
        print(f"  {c(Cc.WARNING, 'EOD deadline: 17:00')} ({self.state.time_remaining_str()}){Cc.RESET}")
    
    def _show_task_detail(self, task: Dict[str, Any]) -> None:
        """Display the full detail of a task."""
        Cc = Color
        Bc = BoxChars
        cat_color = {
            "quantitative": Cc.BRIGHT_BLUE,
            "corporate_finance": Cc.BRIGHT_GREEN,
            "risk_compliance": Cc.BRIGHT_YELLOW,
        }.get(task["category"], Cc.WHITE)

        diff_color = {
            "easy": Cc.GREEN,
            "medium": Cc.YELLOW,
            "hard": Cc.RED,
        }.get(task["difficulty"], Cc.WHITE)

        title = task["title"]
        task_id = task["id"]
        pad = max(0, 53 - len(title))

        # Build box characters
        tl = f"{cat_color}{Bc.TL}{Bc.H * 72}{Bc.TR}{Cc.RESET}"
        bl = f"{cat_color}{Bc.BL}{Bc.H * 72}{Bc.BR}{Cc.RESET}"
        vbar = f"{cat_color}{Bc.V}{Cc.RESET}"

        detail_text = f"""
{tl}
{vbar} {Cc.BOLD}{Cc.BRIGHT_WHITE} TASK #{task_id}: {title}{Cc.RESET}{' ' * pad}{cat_color}{Bc.V}{Cc.RESET}
{vbar} {Cc.DIM}Category: {task['category_label']} | Difficulty: {c(diff_color, task['difficulty'].upper())}{Cc.RESET}{' ' * 16}{cat_color}{Bc.V}{Cc.RESET}
{bl}

{c(Cc.H3, 'CONTEXT:')}
{task['briefing']}

{c(Cc.H3, 'TASK:')}
{task['description']}

{c(Cc.H3, 'DATA:')}
{task['data_provided']}

{Cc.DIM}{Bc.DASH * 74}{Cc.RESET}
{c(Cc.INFO, 'Submit your answer with:')} {c(Cc.BRIGHT_WHITE, 'submit <your_answer>')}
{c(Cc.INFO, 'or use')} {c(Cc.BRIGHT_WHITE, 'submit_multiline')} {c(Cc.INFO, 'for longer answers.')}
{c(Cc.INFO, 'Type')} {c(Cc.BRIGHT_WHITE, 'back')} {c(Cc.INFO, 'to return to task list.')}
{Cc.DIM}{Bc.DASH * 74}{Cc.RESET}
"""
        print(detail_text)

    # ----- Command handlers -----

    def do_start(self, arg: str) -> None:
        """Start a new simulation day (morning briefing)."""
        if self.state.phase != "initialized":
            print(c(Color.WARNING, "Simulation already started. Use 'reset' for a new day."))
            return

        print(c(Color.SYSTEM, "\nInitializing NovaCap Financial simulation environment..."))
        time.sleep(0.5)

        # Generate market briefing
        self.state.market_briefing = MarketDataGenerator.generate_briefing()

        # Generate daily tasks
        self.state.tasks = self.task_gen.generate_daily_tasks()

        # Transition to briefing phase
        self.state.phase = "briefing"

        # Display briefing
        print("\n" + separator("━", Color.BRIGHT_CYAN))
        typewriter(f"  {c(Color.BOLD, 'GOOD MORNING.')}  It is 09:00 on {self.state.simulation_date}.")
        print()
        typewriter(f"  Welcome to {c(Color.BRIGHT_WHITE, CompanyConfig.NAME)}")
        typewriter(f"  Your role: {c(Color.BRIGHT_CYAN, RoleConfig.TITLE)}")
        time.sleep(0.3)

        self._print_morning_briefing()
        self._print_inbox()

        self.state.phase = "working"
        print(f"\n{c(Color.SUCCESS, '[OK] Day started. Ready for your analysis.')}")

    def do_list(self, arg: str) -> None:
        """List all tasks (use 'list brief' for condensed view)."""
        if not self.state.tasks:
            print(c(Color.WARNING, "No tasks assigned. Use 'start' to begin the day."))
            return

        brief = arg.strip().lower() == "brief"
        if brief:
            print(f"\n{c(Color.H3, f'Tasks ({len(self.state.tasks)} assigned, '
                                  f'{len(self.state.completed_task_ids)} completed):')}")
        else:
            self._print_inbox()
            return

        for i, task in enumerate(self.state.tasks, 1):
            status = c(Color.SUCCESS, "[OK]") if task["id"] in self.state.completed_task_ids else c(Color.DIM, "[--]")
            print(f"  {status} [{task['category'][:4].upper()}] "
                  f"#{task['id']}: {task['title'][:60]}")

    def do_workon(self, arg: str) -> None:
        """Select and start working on a task. Usage: workon <task_id>"""
        if self.state.phase not in ("working", "briefing"):
            print(c(Color.WARNING, "Simulation not started. Use 'start' first."))
            return

        if not arg.strip():
            print(c(Color.ERROR, "Usage: workon <task_id>"))
            print(f"  {c(Color.INFO, 'Available tasks:')}")
            for t in self.state.tasks:
                status = c(Color.SUCCESS, "[DONE]") if t["id"] in self.state.completed_task_ids else c(Color.DIM, "[PENDING]")
                print(f"    #{t['id']}: {t['title']} {status}")
            return

        try:
            task_id = int(arg.strip())
        except ValueError:
            print(c(Color.ERROR, "Task ID must be a number."))
            return

        task = next((t for t in self.state.tasks if t["id"] == task_id), None)
        if not task:
            print(c(Color.ERROR, f"Task #{task_id} not found in today's assignments."))
            return

        if task["id"] in self.state.completed_task_ids:
            print(c(Color.WARNING, f"Task #{task_id} already submitted. Use 'status' to review."))
            return

        self.state.current_task_id = task_id
        self.state.phase = "working"

        # Advance simulation time
        self.state.advance_time(10)
        print(f"\n{c(Color.DIM, f'[{self.state.current_time_str}] Starting task...')}")

        self._show_task_detail(task)

    def do_submit(self, arg: str) -> None:
        """Submit an answer for the current task. Usage: submit <your answer>"""
        if self.state.current_task_id is None:
            print(c(Color.WARNING, "No task selected. Use 'workon <task_id>' first."))
            return

        if not arg.strip():
            print(c(Color.ERROR, "Usage: submit <your answer>"))
            print(f"  {c(Color.INFO, 'Or use')} {c(Color.BRIGHT_WHITE, 'submit_multiline')} {c(Color.INFO, 'for longer answers.')}")
            return

        task_id = self.state.current_task_id
        self.state.submit_answer(task_id, arg.strip())
        self.state.advance_time(20)

        task = next((t for t in self.state.tasks if t["id"] == task_id), None)
        msg = f'Answer submitted for Task #{task_id}: "{task["title"]}"'
        print(f"\n{c(Color.SUCCESS, msg)}")
        print(f"{c(Color.DIM, f'[{self.state.current_time_str}] {self.state.time_remaining_str()}')}")

        # Check if all done
        if self.state.all_tasks_completed():
            txt1 = c(Color.BRIGHT_GREEN, "All tasks completed! Type")
            txt2 = c(Color.BRIGHT_WHITE, "eod")
            txt3 = c(Color.BRIGHT_GREEN, "to end the day and receive evaluation.")
            print(f"\n{txt1} {txt2} {txt3}")
        else:
            remaining = self.state.get_pending_tasks()
            warn_txt = c(Color.WARNING, f"{len(remaining)} task(s) remaining.")
            info_txt = c(Color.INFO, "Use")
            list_txt = c(Color.BRIGHT_WHITE, "list")
            info2_txt = c(Color.INFO, "to see pending tasks.")
            print(f"{warn_txt} {info_txt} {list_txt} {info2_txt}")

        self.state.current_task_id = None

    def do_submit_multiline(self, arg: str) -> None:
        """Enter multiline submission mode. Type 'END' on a new line to finish."""
        if self.state.current_task_id is None:
            print(c(Color.WARNING, "No task selected. Use 'workon <task_id>' first."))
            return

        print(f"{c(Color.INFO, 'Enter your answer (type')} {c(Color.BRIGHT_WHITE, 'END')} "
              f"{c(Color.INFO, 'on a new line when done):')}")
        print(f"{c(Color.DIM, '[Multiline input mode]')}")

        lines = []
        while True:
            try:
                line = input(f"  {c(Color.PROMPT, '↳ ')}").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{c(Color.WARNING, 'Input cancelled.')}")
                return

            if line.upper() == "END":
                break
            lines.append(line)

        full_answer = "\n".join(lines)
        if not full_answer.strip():
            print(f"{c(Color.WARNING, 'Empty answer — not submitted.')}")
            return

        task_id = self.state.current_task_id
        self.state.submit_answer(task_id, full_answer)
        self.state.advance_time(30)

        task = next((t for t in self.state.tasks if t["id"] == task_id), None)
        print(f"\n{c(Color.SUCCESS, f'Multiline answer submitted for Task #{task_id}')}")

        if self.state.all_tasks_completed():
            txt1 = c(Color.BRIGHT_GREEN, "All tasks completed! Type")
            txt2 = c(Color.BRIGHT_WHITE, "eod")
            txt3 = c(Color.BRIGHT_GREEN, "to end the day and receive evaluation.")
            print(f"\n{txt1} {txt2} {txt3}")
        else:
            remaining = self.state.get_pending_tasks()
            print(c(Color.WARNING, f"{len(remaining)} task(s) remaining."))

        self.state.current_task_id = None

    def do_status(self, arg: str) -> None:
        """Display current simulation status and progress."""
        print(f"\n{h2(' SIMULATION STATUS ')}")
        print(separator())
        print(f"  Date: {self.state.simulation_date}")
        print(f"  Time: {c(Color.BRIGHT_WHITE, self.state.current_time_str)}")
        print(f"  Phase: {c(Color.BRIGHT_CYAN, self.state.phase.upper())}")
        print(f"  Status: {self.state.time_remaining_str()}")
        print()
        print(f"  {h3('Task Progress:')}")
        for t in self.state.tasks:
            done = t["id"] in self.state.completed_task_ids
            icon = c(Color.SUCCESS, "[OK]") if done else c(Color.DIM, "[--]")
            label = c(Color.GREEN if done else Color.GRAY, "Completed" if done else "Pending")
            print(f"    {icon} #{t['id']}: {t['title'][:55]} [{label}]")
        print()

        if self.state.current_task_id:
            print(f"  {c(Color.INFO, 'Currently working on:')} #{self.state.current_task_id}")
        print()
        print(f"  {c(Color.MUTED, 'Commands: workon <id> | submit | eod | help')}")

    def do_eod(self, arg: str) -> None:
        """End the workday and trigger the full evaluation."""
        if self.state.phase not in ("working", "briefing"):
            print(c(Color.WARNING, "Simulation not yet started or already evaluated."))
            return

        if not self.state.tasks:
            print(c(Color.WARNING, "No tasks to evaluate. Use 'start' first."))
            return

        unanswered = len(self.state.get_pending_tasks())
        if unanswered > 0:
            print(f"\n{c(Color.WARNING, f'[!] {unanswered} task(s) not yet submitted.')}")
            print(f"  {c(Color.WARNING, 'You can still submit (use workon) or proceed with EOD.')}")
            confirm = input(f"  {c(Color.WARNING, 'Type EOD again to confirm or press Enter to continue working:')} ")
            if confirm.strip().upper() != "EOD":
                return
            # Submit empty answers for pending tasks
            for task in self.state.get_pending_tasks():
                task_id_val = task["id"]
                print(f"  {c(Color.DIM, f'Marking Task #{task_id_val} as incomplete...')}")
                self.state.answers[task["id"]] = "[NO ANSWER SUBMITTED]"
                if task["id"] not in self.state.completed_task_ids:
                    self.state.completed_task_ids.append(task["id"])

        # Transition to EOD
        self.state.phase = "eod"
        self.state.current_time_minutes = self.DAY_END_HOUR * 60

        print(f"\n{separator('═', Color.BRIGHT_MAGENTA)}")
        print(f"  {c(Color.BOLD, 'END OF DAY -- 17:00')}")
        print(f"  {c(Color.DIM, 'Initiating evaluation protocol...')}")
        print(f"{separator('═', Color.BRIGHT_MAGENTA)}")

        time.sleep(0.5)

        # Run evaluation
        print(f"\n{c(Color.SYSTEM, 'Evaluating submitted answers against expected standards...')}")
        time.sleep(0.8)

        results = []
        for task in self.state.tasks:
            user_answer = self.state.answers.get(task["id"], "[NO ANSWER]")
            result = self.evaluator.evaluate(task, user_answer)
            results.append(result)

            # Show per-task result briefly
            grade_color_map = {"A": Color.SUCCESS, "B": Color.SUCCESS, "C": Color.WARNING,
                               "D": Color.WARNING, "F": Color.ERROR}
            gc = grade_color_map.get(result["grade"], Color.MUTED)
            tid = task["id"]
            ttl = task["title"][:50]
            sc = result["score"]
            mx = task["max_score"]
            print(f"  {c(Color.DIM, f'Task #{tid}: {ttl}... ')}"
                  f"{c(gc, result['grade'])} {sc}/{mx}")
            time.sleep(0.3)

        # Generate and display full report
        self.state.evaluation_results = results
        report = self.evaluator.generate_variance_report(results)
        print("\n" + report)
        print("\n" + separator("═", Color.BRIGHT_MAGENTA))

        # Offer detailed per-task reports
        print(f"\n{c(Color.INFO, 'For detailed per-task analysis, type:')} {c(Color.BRIGHT_WHITE, 'detail <task_id>')}")
        print(f"{c(Color.INFO, 'Type')} {c(Color.BRIGHT_WHITE, 'reset')} {c(Color.INFO, 'to start a new simulation day.')}")
        print(f"{c(Color.INFO, 'Type')} {c(Color.BRIGHT_WHITE, 'quit')} {c(Color.INFO, 'to exit.')}")

        self.state.phase = "complete"

    def do_detail(self, arg: str) -> None:
        """Show detailed evaluation for a specific task. Usage: detail <task_id>"""
        if self.state.phase != "complete":
            print(c(Color.WARNING, "Evaluation not yet complete. Use 'eod' first."))
            return

        if not arg.strip():
            print(c(Color.ERROR, "Usage: detail <task_id>"))
            return

        try:
            task_id = int(arg.strip())
        except ValueError:
            print(c(Color.ERROR, "Task ID must be a number."))
            return

        task = next((t for t in self.state.tasks if t["id"] == task_id), None)
        result = next((r for r in self.state.evaluation_results if r["task_id"] == task_id), None)

        if not task or not result:
            print(c(Color.ERROR, f"No evaluation result for Task #{task_id}."))
            return

        report = self.evaluator.get_detailed_report_text(task, result)
        print("\n" + report)

    def do_reset(self, arg: str) -> None:
        """Reset the simulation for a new day."""
        if self.state.phase == "initialized":
            print(c(Color.WARNING, "No simulation in progress."))
            return

        print(f"\n{c(Color.WARNING, 'Resetting simulation for a new day...')}")
        self.state.reset()
        self.evaluator.reset()
        self.state.phase = "initialized"
        print(f"{c(Color.SUCCESS, '[OK] Reset complete. Use')} {c(Color.BRIGHT_WHITE, 'start')} "
              f"{c(Color.SUCCESS, 'to begin a new day.')}")

    def do_help(self, arg: str) -> None:
        """Display available commands."""
        Cc = Color
        Bc = BoxChars
        dash = Bc.DASH * 57
        help_lines = [
            "",
            f"{Cc.H2}  AVAILABLE COMMANDS{Cc.RESET}",
            f"{Cc.CYAN}  {dash}{Cc.RESET}",
            "",
            f"  {Cc.BRIGHT_WHITE}start{Cc.RESET}              Begin the simulation day (09:00 briefing)",
            f"  {Cc.BRIGHT_WHITE}list [brief]{Cc.RESET}       Show all assigned tasks",
            f"  {Cc.BRIGHT_WHITE}workon <id>{Cc.RESET}         Select a task to work on",
            f"  {Cc.BRIGHT_WHITE}submit <text>{Cc.RESET}       Submit answer for current task",
            f"  {Cc.BRIGHT_WHITE}submit_multiline{Cc.RESET}    Enter multiline answer mode (END to finish)",
            f"  {Cc.BRIGHT_WHITE}status{Cc.RESET}             Show simulation progress and time remaining",
            f"  {Cc.BRIGHT_WHITE}eod{Cc.RESET}                End the workday and run evaluation",
            f"  {Cc.BRIGHT_WHITE}detail <id>{Cc.RESET}         Show detailed evaluation for a specific task",
            f"  {Cc.BRIGHT_WHITE}reset{Cc.RESET}              Reset simulation for a new day",
            f"  {Cc.BRIGHT_WHITE}about{Cc.RESET}              Show information about this simulation",
            f"  {Cc.BRIGHT_WHITE}help{Cc.RESET}               Display this help message",
            f"  {Cc.BRIGHT_WHITE}quit{Cc.RESET}               Exit the application",
            "",
            f"{Cc.GRAY}  TIPS:",
            f"  * Complete all 3 tasks before 17:00 for the best evaluation",
            f"  * Use submit_multiline for detailed analytical answers",
            f"  * The evaluation checks for key concepts and numerical accuracy",
            f"  * EOD triggers a comprehensive CMA/SOCPA competency assessment{Cc.RESET}",
            "",
        ]
        print("\n".join(help_lines))

    def do_about(self, arg: str) -> None:
        """Display information about the simulation environment."""
        Cc = Color
        Bc = BoxChars
        dash = Bc.DASH * 57
        about_lines = [
            "",
            f"{Cc.H2}  ABOUT THIS SIMULATION{Cc.RESET}",
            f"{Cc.CYAN}  {dash}{Cc.RESET}",
            "",
            f"{Cc.BRIGHT_WHITE}  Firm:{Cc.RESET}      {CompanyConfig.NAME}",
            f"{Cc.BRIGHT_WHITE}  HQ:{Cc.RESET}         {CompanyConfig.HEADQUARTERS}",
            f"{Cc.BRIGHT_WHITE}  AUM:{Cc.RESET}        {CompanyConfig.ASSETS_UNDER_MANAGEMENT}",
            f"{Cc.BRIGHT_WHITE}  Founded:{Cc.RESET}    {CompanyConfig.FOUNDED}",
            f"{Cc.BRIGHT_WHITE}  Employees:{Cc.RESET}  {CompanyConfig.EMPLOYEES}",
            "",
            f"{Cc.BRIGHT_WHITE}  Your Role:{Cc.RESET}     {RoleConfig.TITLE}",
            f"{Cc.BRIGHT_WHITE}  Department:{Cc.RESET}   {RoleConfig.DEPARTMENT}",
            f"{Cc.BRIGHT_WHITE}  Reports To:{Cc.RESET}   {RoleConfig.REPORTS_TO}",
            "",
            f"{Cc.BRIGHT_WHITE}  Standards Applied:{Cc.RESET}",
        ]
        for std_key in ["accounting", "management_accounting", "compliance", "reporting"]:
            about_lines.append(f"  {Cc.GRAY} *{Cc.RESET} {CompanyConfig.STANDARDS[std_key]}")

        about_lines.append("")
        about_lines.append(f"{Cc.BRIGHT_WHITE}  Focus Areas:{Cc.RESET}")
        for area in CompanyConfig.FOCUS:
            about_lines.append(f"  {Cc.GRAY} *{Cc.RESET} {area}")

        about_lines.append("")
        about_lines.append(f"{Cc.BRIGHT_WHITE}  Task Categories:{Cc.RESET}")
        about_lines.append(f"  {Cc.BRIGHT_BLUE} *{Cc.RESET}  Quantitative & Algorithmic Analysis")
        about_lines.append(f"  {Cc.BRIGHT_GREEN} *{Cc.RESET}  Corporate Finance & Reporting")
        about_lines.append(f"  {Cc.BRIGHT_YELLOW} *{Cc.RESET}  Risk & Compliance")
        about_lines.append("")
        about_lines.append(f"{Cc.GRAY}  Simulation Database: {len(TASK_DATABASE)} pre-defined tasks{Cc.RESET}")
        about_lines.append("")

        print("\n".join(about_lines))

    def do_quit(self, arg: str) -> None:
        """Exit the application."""
        print(f"\n{c(Color.SUCCESS, 'Thank you for your work today.')}")
        print(f"{c(Color.DIM, 'NovaCap Financial Technologies Ltd. — Simulation terminated.')}{Color.RESET}")
        self.running = False
        return True

    def do_exit(self, arg: str) -> None:
        """Exit the application."""
        return self.do_quit(arg)

    # ----- Overridden cmd.Cmd methods -----

    def default(self, line: str) -> None:
        """Handle unknown commands."""
        print(f"{c(Color.ERROR, f'Unknown command: {line}')}")
        print(f"{c(Color.INFO, 'Type')} {c(Color.BRIGHT_WHITE, 'help')} {c(Color.INFO, 'for available commands.')}")

    def emptyline(self) -> None:
        """Do nothing on empty line."""
        pass

    def precmd(self, line: str) -> str:
        """Pre-process command: strip whitespace, normalize."""
        return line.strip()

    def postcmd(self, stop: bool, line: str) -> bool:
        """Post-command hook."""
        return stop

    def cmdloop(self, intro: str = None) -> None:
        """Override cmdloop to use our custom intro."""
        if intro is not None:
            self.intro = intro
        self._print_header()
        print(f"{c(Color.INFO, 'Type')} {c(Color.BRIGHT_WHITE, 'start')} {c(Color.INFO, 'to begin your day, or')} "
              f"{c(Color.BRIGHT_WHITE, 'help')} {c(Color.INFO, 'for commands.')}")
        print(f"{c(Color.MUTED, BoxChars.DASH * 74)}{Color.RESET}")
        print()
        while self.running:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print(f"\n{c(Color.WARNING, '\nUse')} {c(Color.BRIGHT_WHITE, 'quit')} "
                      f"{c(Color.WARNING, 'to exit.')}")
            except EOFError:
                print()
                break


# ==============================================================================
# SECTION 9 — MAIN ENTRY POINT
# ==============================================================================

def main():
    """Application entry point."""
    # Windows console setup: ANSI and UTF-8
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            # Try to set UTF-8 encoding for console output
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            sys.stdout.reconfigure(errors="replace")
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    try:
        print(f"{Color.DIM}NovaCap Financial Simulation ... Loading{Color.RESET}")
        cli = FinanceSimCLI()
        cli.cmdloop()
    except Exception as e:
        print(f"\n{Color.ERROR}Error: {e}{Color.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
