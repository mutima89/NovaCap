<div align="center">
  <br>
  <h1>⚡ NovaCap · Principal Strategist</h1>
  <p><strong>90-Day FinTech Arbitrage Training Simulator</strong></p>
  <p>
    <em>"This is not a course. This is a simulation of the most demanding trading desk in the region."</em>
  </p>
  <br>
  <p>
    <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-⬇-6366f1?style=for-the-badge" alt="Quick Start"></a>
    <a href="#-features"><img src="https://img.shields.io/badge/Features-📋-8b5cf6?style=for-the-badge" alt="Features"></a>
    <a href="#-architecture"><img src="https://img.shields.io/badge/Architecture-🏗️-a855f7?style=for-the-badge" alt="Architecture"></a>
    <a href="#-cli-reference"><img src="https://img.shields.io/badge/CLI-⌨️-6366f1?style=for-the-badge" alt="CLI Reference"></a>
    <a href="#-documentation"><img src="https://img.shields.io/badge/Docs-📖-8b5cf6?style=for-the-badge" alt="Documentation"></a>
  </p>
  <br>
  <!-- Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.8+">
    <img src="https://img.shields.io/badge/dependencies-none-brightgreen?style=flat-square" alt="Zero Dependencies">
    <img src="https://img.shields.io/badge/LOC-~8,000-48dbfb?style=flat-square" alt="~8,000 LOC">
    <img src="https://img.shields.io/badge/license-Proprietary-64748b?style=flat-square" alt="License">
    <img src="https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-94a3b8?style=flat-square" alt="Platform">
    <img src="https://img.shields.io/badge/status-active-22c55e?style=flat-square" alt="Status: Active">
  </p>
  <br>
</div>

---

## 📋 Overview

**NovaCap Principal Strategist** is a hard-mode, self-contained algorithmic trading training simulator. You write Python code against a live mock exchange, log trades to a double-entry SQLite ledger, pass AST static audits, and face ruthless end-of-day evaluations.

> **Score 100 or you don't advance.**

Built entirely with the **Python standard library** — zero external dependencies, zero pip installs, zero configuration. A complete trading simulation environment in roughly 8,000 lines of Python across three integrated modules.

### Who Is This For?

| Audience | Use Case |
|----------|----------|
| **Quantitative Developers** | Practice algorithmic trading in a risk-free simulated environment |
| **Finance Students** | Build hands-on experience with order books, arbitrage strategies, and risk management |
| **Python Engineers** | Hone your skills against an unforgiving static AST auditor and test suite |
| **Bootcamps & Academies** | Run a 90-day structured curriculum with measurable scoring |

---

## 🚀 Quick Start

```bash
# No pip install. No requirements.txt. No setup. No configuration.
python arbitrage_academy.py

# The Web UI starts on:   http://localhost:8081
# The Mock Exchange on:   http://localhost:8080
```

### System Requirements

| Requirement | Minimum |
|-------------|---------|
| **Python** | 3.8+ (3.11+ recommended for f-string support) |
| **Dependencies** | None — standard library only |
| **Ports** | 8080 (exchange) and 8081 (dashboard) must be free |
| **OS** | Windows, macOS, Linux |

---

## 🎮 The Principal Strategist CLI

Once running, you are greeted by the **Principal Strategist** — a clinical, uncompromising CLI persona. Ten commands control your entire training pipeline:

```
strategist> start     Launch exchange + generate Day 1 workspace
strategist> run       Execute your solution code against the exchange
strategist> eod       End-of-Day: AST audit → tests → ledger check → score
strategist> advance   Move to next day (requires 100/100)
strategist> status    View training progress and current score
strategist> brief     Read today's mission briefing
strategist> audit     Run AST check only (no score impact)
strategist> reset     Regenerate current day's workspace
strategist> help      Show all commands
strategist> quit      Exit the simulator
```

---

## ✨ Features

### Core Modules

| Module | Description |
|--------|-------------|
| **Mock Exchange** | Threaded HTTP REST server on `:8080`. Maintains order books, tickers, and executes trades for BTC/USD, ETH/USDT, and more. Synthetic market data with configurable volatility. |
| **Web Dashboard** | Dark-themed browser UI on `:8081`. Live ticker feed, code editor with syntax highlighting, evaluation history timeline, and interactive ledger explorer. |
| **Double-Entry Ledger** | SQLite-backed accounting engine with 9 standard accounts. Tracks P&L per symbol, enforces debit/credit balance, and logs every transaction with full audit trail. |
| **AST Code Auditor** | Static analysis engine using Python's `ast` module. 9 check categories scan your solution code for violations — missing error handling, unsafe patterns, code complexity issues. |
| **Evaluation Pipeline** | End-of-Day engine that runs three stages in sequence: AST audit → subprocess test suite → ledger integrity verification. Produces a score from 0–100. |
| **Workspace Generator** | Generates per-day working directories containing a mission briefing, boilerplate solution template, and hidden test suites. Days are independent and cumulative. |
| **90-Day Curriculum** | Three escalating phases progressing from data ingestion fundamentals through multi-leg arbitrage strategies to SOCPA-compliant financial reporting. |

### Zero Dependencies

All functionality is built using Python's standard library:

```
http.server  ·  socketserver  ·  sqlite3  ·  ast  ·  threading
urllib      ·  json          ·  subprocess  ·  cmd  ·  pathlib
```

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                         NOVACAP SYSTEM ARCHITECTURE                      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────────┐      ┌──────────────────┐      ┌──────────────┐ │
│   │   CLI Interface  │      │  Mock Exchange   │      │   Web UI     │ │
│   │   (cmd.Cmd)      │─────▶│  HTTP :8080      │◀─────│  Dashboard   │ │
│   │   10 commands    │      │  REST API        │      │  :8081       │ │
│   └────────┬─────────┘      └────────┬─────────┘      └──────────────┘ │
│            │                         │                                 │
│            ▼                         ▼                                 │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    SQLite Ledger Engine                          │  │
│   │       9 accounts · Double-entry · P&L per symbol                │  │
│   │       Transaction log · Audit trail · Balance verification      │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│            │                                                           │
│            ▼                                                           │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                   EOD Evaluation Pipeline                        │  │
│   │                                                                  │  │
│   │   ┌──────────┐    ┌──────────────┐    ┌──────────────────┐      │  │
│   │   │  AST     │───▶│  Subprocess  │───▶│  Ledger Verify   │      │  │
│   │   │  Audit   │    │  Tests       │    │  (debits=credits) │      │  │
│   │   └──────────┘    └──────────────┘    └────────┬─────────┘      │  │
│   │                                                ▼                │  │
│   │                                       ┌──────────────────┐      │  │
│   │                                       │   Score 0–100    │      │  │
│   │                                       └──────────────────┘      │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Start** — CLI launches the mock exchange on `:8080` and generates Day 1 workspace with briefing, template, and tests
2. **Code** — You write Python strategy code in the generated solution file
3. **Run** — Your code executes against the live mock exchange, placing orders and logging trades to the SQLite ledger
4. **Evaluate** — End-of-Day runs three-stage evaluation producing a score
5. **Advance** — Score 100/100 to unlock the next day's challenge

---

## 📚 90-Day Curriculum

The training program is divided into three escalating phases:

### Phase 1 — Days 1–30: Data Ingestion & Risk Math

> **Focus:** Market data handling, technical indicators, risk calculation

- Fetch order books from REST API endpoints
- Calculate SMA, EMA, Bollinger Bands, RSI
- Log positions to double-entry SQLite ledger
- Pass AST audits for code quality
- Build foundational risk models

### Phase 2 — Days 31–60: Arbitrage Logic

> **Focus:** Multi-exchange strategies, position sizing, execution

- Cross-exchange spread detection and monitoring
- Triangular arbitrage: BTC → ETH → USDT → BTC
- Kelly Criterion optimal position sizing
- Latency simulation and slippage modeling
- Statistical arbitrage pair selection

### Phase 3 — Days 61–90: Slippage & SOCPA Compliance

> **Focus:** Risk management, regulatory compliance, reporting

- SOCPA-compliant audit trails
- IFRS 9 financial instrument reporting
- VaR/CVaR stress testing and scenario analysis
- Full compliance report generation
- Production-grade trade reconciliation

---

## 📊 Scoring System

| Violation | Penalty |
|-----------|---------|
| **Critical AST** — missing `try`/`except`, `eval()`/`exec()`, unsafe patterns | **−40 each** (2 violations = automatic 0) |
| **Warning AST** — deeply nested loops, division by zero risk, global state mutations | **−10 each** |
| **Test Failure** — any unit/integration test in the day's suite fails | **−30 each** |
| **Ledger Imbalance** — debits do not equal credits after your trading session | **−30 each** |

**You must score 100/100 to advance to the next day.**

---

## 🛠️ Project Structure

```
NovaCap/
├── arbitrage_academy.py      # Master simulator: CLI, exchange, ledger,
│                              #   AST auditor, evaluation engine (3,961 LOC)
├── finance_sim.py            # Corporate finance daily simulation (2,592 LOC)
├── server.py                 # HTTP web server for browser UI (1,292 LOC)
├── generate_pdfs.py          # Documentation PDF generator
├── BEFORE_YOU_BEGIN.html     # Comprehensive prep guide (Python + finance)
├── TRAINING_PROGRAM.html     # Full 90-day syllabus with scoring system
├── TRAINING_PROGRAM.md       # Markdown version of the syllabus
├── promo.html                # Product landing page
├── PRODUCT.md                # Technical product documentation
├── SALES_PAGE.md             # Sales and listing copy with pricing
├── EULA.md                   # End-User License Agreement — 4 tiers
├── docs/                     # Generated PDF documentation
│   ├── promo.pdf
│   ├── product.pdf
│   ├── sales-page.pdf
│   ├── eula.pdf
│   ├── training-program.pdf
│   ├── before-you-begin.pdf
│   └── index.html            # Dark-themed documentation hub
└── .gitignore
```

---

## 📖 Documentation

All documentation is available as rendered PDFs in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [📄 Promo](docs/promo.pdf) | Product landing page with full feature showcase |
| [📄 Product](docs/product.pdf) | Technical README with architecture and CLI reference |
| [📄 Sales Page](docs/sales-page.pdf) | Sales / listing copy with pricing tiers |
| [📄 EULA](docs/eula.pdf) | End-User License Agreement — 4 tiers |
| [📄 Training Program](docs/training-program.pdf) | Full 90-day syllabus with scoring breakdown |
| [📄 Before You Begin](docs/before-you-begin.pdf) | Comprehensive prep guide with Python & finance concepts |

Open [`docs/index.html`](docs/index.html) for a dark-themed hub linking to all documents.

---

## 📜 Licensing

| Tier | Price | Audience |
|------|-------|----------|
| **Individual** | $79 | Solo developers, students, personal use |
| **Professional** | $249 | Freelancers, commercial use |
| **Academy** | $750 | Classrooms, bootcamps (up to 30 seats) |
| **Enterprise** | $2,500+ | Unlimited seats, custom modules, white-label |

See [`EULA.md`](EULA.md) for complete terms and conditions.

---

## 🧪 Technical Highlights

- **3,961 lines** in the master simulator (`arbitrage_academy.py`) — a single-file marvel of Python standard library engineering
- **Threaded HTTP servers** — mock exchange and web dashboard run concurrently with the CLI
- **AST-level code analysis** — your Python source is parsed and checked for 9 categories of violations before tests even run
- **Double-entry accounting** — every trade is logged to SQLite with full audit trail; debits must equal credits
- **Synthetic market engine** — generates realistic order book dynamics with configurable volatility and spread
- **No dependencies** — zero pip packages, zero requirements.txt, zero setup.py

---

## 🤝 Contributing

NovaCap is a proprietary training platform. Contributions, bug reports, and feature requests are welcome via the [issue tracker](https://github.com/mutima89/NovaCap/issues).

Before contributing:

1. Review the [`EULA.md`](EULA.md) for licensing terms
2. Ensure your code passes the AST auditor checks
3. Maintain zero-dependency policy (standard library only)

---

## 🏢 About NovaCap Financial Technologies

NovaCap Financial Technologies Ltd. develops quantitative training simulations for finance professionals and software engineers. Our platforms bridge the gap between academic finance theory and production trading system development.

> **Disclaimer:** All market data generated by this simulator is entirely synthetic. This is a code training and education tool. Nothing in this software constitutes financial advice, trading recommendations, or investment guidance.

---

<div align="center">
  <br>
  <p>
    <sub>
      NovaCap Financial Technologies Ltd. &nbsp;·&nbsp;
      <a href="https://github.com/mutima89/NovaCap">GitHub</a> &nbsp;·&nbsp;
      <a href="docs/index.html">Documentation</a> &nbsp;·&nbsp;
      <a href="EULA.md">License</a>
    </sub>
  </p>
  <p>
    <sub>Built with Python standard library — zero dependencies, maximum rigor.</sub>
  </p>
  <br>
</div>
