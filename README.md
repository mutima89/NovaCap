# Principal Strategist — 90-Day FinTech Arbitrage Training Simulator

> *"This is not a course. This is a simulation of the most demanding trading desk in the region."*

A hard-mode, self-contained algorithmic trading training simulator. You write Python code against a live mock exchange, log trades to a double-entry SQLite ledger, pass AST static audits, and face ruthless EOD evaluations. **Score 100 or you don't advance.**

**One file. Zero dependencies. 90 days of rigorous training.**

---

## Quick Start

```bash
# No pip install. No requirements.txt. No setup.
python arbitrage_academy.py

# That's it. The Web UI starts on:
#   http://localhost:8081
# The Mock Exchange starts on:
#   http://localhost:8080
```

### What happens when you run it

```
strategist> start     # Launch exchange + generate Day 1 workspace
strategist> run       # Execute your solution code
strategist> eod       # End-of-Day: AST audit → tests → ledger check → score
strategist> advance   # Move to next day (requires 100/100)
strategist> status    # View training progress
```

---

## Features

| Module | What It Does |
|--------|-------------|
| **Mock Exchange** | Threaded HTTP server on `:8080` — order books, tickers, trade execution for BTC/USD, ETH/USDT, and more |
| **Web UI Dashboard** | Dark-themed dashboard on `:8081` with live ticker, code editor, eval history, ledger explorer |
| **Ledger Engine** | Double-entry SQLite bookkeeping with 9 accounts, P&L per symbol |
| **AST Code Auditor** | Static analysis via Python's `ast` — 9 check categories with scoring deductions |
| **Evaluation Engine** | EOD pipeline: AST audit → subprocess tests → ledger verify → score (0–100) |
| **Workspace Generator** | Per-day files: briefing, boilerplate code, hidden test suites |
| **CLI Interface** | Clinical Principal Strategist persona with 10 commands |
| **90-Day Curriculum** | 3 phases: Data Ingestion → Arbitrage Logic → SOCPA Compliance |

### Zero Dependencies

All built with Python standard library:

`http.server` · `socketserver` · `sqlite3` · `ast` · `threading` · `urllib` · `json` · `subprocess` · `cmd`

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CLI (cmd.Cmd) │────▶│  Mock Exchange   │◀────│  Web Dashboard  │
│  10 commands    │     │  :8080 REST API  │     │  :8081 Dark UI  │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                      │                         │
         ▼                      ▼                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    SQLite Ledger Engine                           │
│       9 accounts · Double-entry · P&L per symbol                 │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    EOD Evaluation Pipeline                        │
│  AST Audit → Subprocess Tests → Ledger Verify → Score (0-100)   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Documentation & Resources

All documentation is available in the `docs/` folder as PDFs:

| Document | Description |
|----------|-------------|
| [`promo.pdf`](docs/promo.pdf) | Product landing page with full feature showcase |
| [`product.pdf`](docs/product.pdf) | Technical README with architecture and CLI reference |
| [`sales-page.pdf`](docs/sales-page.pdf) | Sales / listing copy with pricing |
| [`eula.pdf`](docs/eula.pdf) | End-User License Agreement — 4 tiers |
| [`training-program.pdf`](docs/training-program.pdf) | Full 90-day syllabus with scoring system |
| [`before-you-begin.pdf`](docs/before-you-begin.pdf) | Comprehensive prep guide with Python & finance concepts |

Open [`docs/index.html`](docs/index.html) for a dark-themed hub linking to all PDFs.

---

## The Three Phases

### Phase 1 — Days 1–30: Data Ingestion & Risk Math
Fetch order books from REST APIs, calculate SMA/EMA/Bollinger Bands/RSI, log to double-entry SQLite ledger, pass AST audits.

### Phase 2 — Days 31–60: Arbitrage Logic
Cross-exchange spread detection, triangular arbitrage (BTC→ETH→USDT→BTC), Kelly Criterion position sizing, latency simulation.

### Phase 3 — Days 61–90: Slippage & SOCPA Compliance
SOCPA-compliant audit trails, IFRS 9 financial instrument reporting, VaR/CVaR stress testing, full compliance report generation.

---

## The Score System

| Issue | Penalty |
|-------|---------|
| Critical AST violation (missing try-except, eval/exec) | **–40 each** (2 = automatic 0) |
| Warning (nested loops, division by zero, global state) | **–10 each** |
| Test failure | **–30 each** |
| Ledger imbalance (debits ≠ credits) | **–30 each** |
| **Need 100/100 to advance.** | |

---

## Requirements

- **Python 3.8+** (3.11+ recommended for f-string support)
- **No pip packages** — standard library only
- **Ports 8080** (exchange) and **8081** (dashboard) must be free
- Works on **Windows, macOS, Linux**

---

## Licensing

| Tier | Price | Audience |
|------|-------|----------|
| **Individual** | $79 | Solo devs, students, personal use |
| **Professional** | $249 | Freelancers, commercial use |
| **Academy** | $750 | Classrooms, bootcamps (up to 30 seats) |
| **Enterprise** | $2,500+ | Unlimited seats, custom modules, white-label |

See [`EULA.md`](EULA.md) for full terms.

---

## Built With

<p>
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/dependencies-none-brightgreen?style=flat" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/license-Proprietary-blue?style=flat" alt="License">
  <img src="https://img.shields.io/badge/LOC-~4,000-48dbfb?style=flat" alt="~4,000 LOC">
</p>

---

*NovaCap Financial Technologies Ltd. — All market data is synthetic. This is a code training simulator, not financial advice.*
