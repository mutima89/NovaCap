<div align="center">
  <pre style="font-size: 1.2em; line-height: 1.4;">
███╗   ██╗ ██████╗ ██╗   ██╗ █████╗  ██████╗ █████╗ ██████╗ 
████╗  ██║██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗
██╔██╗ ██║██║   ██║██║   ██║███████║██║     ███████║██████╔╝
██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║     ██╔══██║██╔═══╝ 
██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║╚██████╗██║  ██║██║     
╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     
  </pre>
</div>

<h1 align="center">NovaCap</h1>
<h3 align="center">Multi-Agent Algorithmic Trading Simulation Framework</h3>

<p align="center">
  <img src="https://img.shields.io/github/stars/mutima89/NovaCap?style=for-the-badge&logo=github&logoColor=white&label=STARS" alt="Stars">
  <img src="https://img.shields.io/github/last-commit/mutima89/NovaCap?style=for-the-badge&logo=git&logoColor=white&label=LAST%20COMMIT" alt="Last Commit">
  <img src="https://img.shields.io/github/repo-size/mutima89/NovaCap?style=for-the-badge&logo=files&logoColor=white&label=SIZE" alt="Repo Size">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/dependencies-zero-success?style=for-the-badge&logo=zeromq&logoColor=white" alt="Zero Dependencies">
  <img src="https://img.shields.io/github/actions/workflow/status/mutima89/NovaCap/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CI%20PIPELINE" alt="CI">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT License">
  <img src="https://img.shields.io/badge/LOC-4%2C200+-FF6F00?style=for-the-badge&logo=codefactor&logoColor=white" alt="4,200+ LOC">
</p>

<br>

> <b>Write real Python strategies against a regime-switching market with a full limit order book,<br>
> double-entry accounting, institutional risk controls, and Monte Carlo backtesting —<br>
> in pure-Python standard library code. <b>Zero dependencies.</b>

<br>

<div align="center">
  <table>
    <tr>
      <td align="center">
        <sub><b>90-DAY<br>CURRICULUM</b></sub>
      </td>
      <td align="center">
        <sub><b>19<br>CLASSES</b></sub>
      </td>
      <td align="center">
        <sub><b>4,200+<br>LOC</b></sub>
      </td>
      <td align="center">
        <sub><b>6 AGENT<br>LAYERS</b></sub>
      </td>
      <td align="center">
        <sub><b>0<br>DEPS</b></sub>
      </td>
      <td align="center">
        <sub><b>5 PYTHON<br>VERSIONS</b></sub>
      </td>
    </tr>
  </table>
</div>

---

## 📖 About

<p align="center">
  <em>"This is not a course. This is a simulation of the most demanding trading desk in the region."</em>
</p>

NovaCap drops you into the role of a **quantitative trading strategist** aboard a proprietary trading desk. Every trade, every risk report, every backtest iteration runs through the same pipeline an actual quant firm would use:

<p align="center">
  <code>Market Data  →  Signal  →  Execution  →  Ledger  →  Risk  →  Evaluation</code>
</p>

The only difference? The market is synthetic and the capital is fake. **The lessons are not.**

Built on six integrated agent layers, NovaCap is a self-contained ecosystem with HMM regime-switching dynamics, price-time priority limit order books, SQLite double-entry accounting, VaR/CVaR risk guards, and AST-level code auditing — running on the **Python standard library alone**.

<br>

### 💡 Why NovaCap?

| Other Trading Simulators | NovaCap |
|--------------------------|---------|
| Require `pip install` packages | **Zero dependencies** — stdlib only |
| Pre-built GUIs, no real coding | Write **real Python** strategies |
| Multiple-choice quizzes | **AST code audits** + hidden test suites |
| Self-paced, no standards | **Score 100/100** or you don't advance |
| Opaque market dynamics | Observable **regime-switching HMM** |
| Single asset class | **7 correlated symbols** with order books |
| No risk framework | Institutional **VaR/CVaR/limits/circuit breakers** |
| Black-box evaluation | **Transparent scoring** with weighted deductions |

---

## ✨ Features

### 📊 Market Engine
- ✅ **Two-regime HMM** — low-vol trending (σ=0.003), high-vol mean-reverting (σ=0.025)
- ✅ **Jump diffusion** — Poisson-distributed shocks with configurable intensity
- ✅ **Regime-dependent depth** — 12-level book in trending, 6-level in volatile
- ✅ **7 correlated symbols** — BTC/USD, ETH/USDT, SOL/USD, EUR/USD, and more
- ✅ **Depth-based slippage** — walks book levels for VWAP estimation

### ⚡ Execution
- ✅ **Full limit order book** — price-time priority queues
- ✅ **4 order types** — Market, Limit (GTC), IOC, FOK
- ✅ **Partial fills** — queue-based matching with remainder logic
- ✅ **Order management** — track, cancel, and query live orders

### 📒 Accounting
- ✅ **SQLite double-entry** — 9 standard accounts (Cash, Inventory, Fees, P&L...)
- ✅ **Per-symbol P&L** — trade-level profit/loss with fee recording
- ✅ **Integrity verification** — automatic debits = credits check
- ✅ **Audit trail** — full trade history with timestamps

### 🛡️ Risk Management
- ✅ **Value at Risk (VaR)** — historical 95% confidence
- ✅ **Conditional VaR (CVaR)** — expected shortfall beyond VaR
- ✅ **Circuit breaker** — 5% drawdown over 10-bar window
- ✅ **Position limits** — 15% of capital per symbol
- ✅ **Leverage cap** — 2.0× gross exposure maximum
- ✅ **Portfolio correlation** — real-time inter-symbol tracking

### 🔬 Backtesting
- ✅ **Monte Carlo engine** — N iterations × D days on seeded markets, scored from exchange fills
- ✅ **Distribution statistics** — mean, median, P10, P90 final equity
- ✅ **Sharpe analysis** — probability of risk-adjusted return > 1.0
- ✅ **Max drawdown distribution** — severity range across all runs

### 🔍 Evaluation
- ✅ **AST static auditor** — 9 check categories (eval, loops, annotations, globals...)
- ✅ **Hidden test suite** — separate process, 30s timeout
- ✅ **Composite scoring** — 0–100 with weighted deductions
- ✅ **90-day curriculum** — 3 phases across 3 market regimes

### 🏗️ Infrastructure
- ✅ **Concurrent HTTP** — mock exchange on `:8080`, web UI on `:8081`
- ✅ **Persistent state** — `save_state.json` with crash recovery
- ✅ **CI/CD** — GitHub Actions: 19 stages × 5 Python versions (3.8–3.12)
- ✅ **Containerized** — Dockerfile with `python:3.11-slim`

---

## 🚀 Quick Start

```bash
git clone https://github.com/mutima89/NovaCap.git
cd NovaCap
python arbitrage_academy.py
```

```text
⚡ strategist> start       Launch exchange + generate Day 1 solution template
⚡ strategist> run         Execute today's Python strategy
⚡ strategist> eod         End-of-Day evaluation and scoring
⚡ strategist> risk        Display VaR, CVaR, circuit breaker, positions
⚡ strategist> backtest    Run Monte Carlo backtest (30 iterations × 30 days)
```

**Prerequisites:** Python 3.8+ · Ports `8080` and `8081` available · **No `pip install`**

> 💡 **Tip:** Run `strategist> help` inside the CLI for a full command reference.

---

## 📸 Screenshots

> **View the live dashboard**: Start NovaCap (`python arbitrage_academy.py`) and open [http://localhost:8081](http://localhost:8081) in your browser. A standalone HTML preview is also available at [`docs/dashboard-preview.html`](docs/dashboard-preview.html).

### 🖥️ Web Dashboard — Terminal View

The premium browser-based dashboard at `localhost:8081` features:

- **Live ticker tape** — scrolling price updates for BTC/USD and ETH/USDT
- **Market panel** — regime, spread, bid/ask with animated glass-morphism cards
- **Order book** — depth table with price, size, and source
- **Portfolio summary** — P&L, equity, VaR, leverage, circuit breaker status
- **Code editor** — line-numbered textarea for writing strategies inline
- **Navigation tabs** — Market, Strategy, Order Book, Portfolio, Log, Settings
- **Animated background** — grid animation with depth effect
- **Loading splash** — animated sequencer on page load
- **Real-time clock** — live HH:MM:SS in the header
- **Dark theme** — professional trading terminal aesthetic with JetBrains Mono font

### 🖥️ CLI — Primary Interface

```
NOVACAP ARBITRAGE PROTOCOL v2.0.0
══════════════════════════════════════════════════════

  PRINCIPAL STRATEGIST: Welcome to the most demanding
  trading desk in the region.

  DIRECTIVE: Type "start" to begin Day 1.
  Type "help" for available commands.

strategist>
```

### 📋 CLI Help

```
strategist> help

Documented commands (type help <topic>):
========================================
advance      backtest     eod          help        risk
risk_reset   run          start        reset       status

Undocumented commands:
======================
cancel_order  orders  quote  ticker
```

### 📊 CLI Risk Report

```
strategist> risk

==================================================
RISK REPORT — Day 15
Circuit Breaker: Inactive
Equity: $102,345.67  |  Max DD: 2.34%
VaR(95%): 1.23%  |  CVaR(95%): 2.45%
Gross Exposure: $45,000.00  |  Leverage: 0.44x (max 2.0x)
Correlation: BTC/USD: +0.723  |  ETH/USDT: +0.541
Positions: 12 trades today
```

### 📈 Order Book API

```json
GET /v1/orderbook?symbol=BTC/USD

{
  "symbol": "BTC/USD",
  "tick": 1042,
  "regime": 0,
  "regime_name": "LOW_VOL_TRENDING",
  "spread_bps": 1.24,
  "bids": [
    {"price": 69245.12, "size": 0.85, "source": "limit_book"},
    {"price": 69230.00, "size": 0.50, "source": "limit_book"}
  ],
  "asks": [
    {"price": 69253.78, "size": 1.20, "source": "limit_book"},
    {"price": 69270.00, "size": 0.75, "source": "limit_book"}
  ]
}
```

### 🩺 Health Check API

```json
GET /v1/health

{
  "status": "operational",
  "version": "2.0.0",
  "uptime_seconds": 42,
  "active_orders": 3,
  "limit_orders": 3,
  "total_trades": 127,
  "current_regime": 0
}
```

> **Note**: For full-resolution screenshots, open `http://localhost:8081` in your browser after starting NovaCap, or open `docs/dashboard-preview.html` for a standalone preview of the dashboard HTML.

---


## 🏛️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            NOVACAP                                       │
│                     Multi-Agent Trading Framework                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────────────┐  │
│  │  CLI Cmd     │   │  Web UI      │   │  Docker Container            │  │
│  │  stdin/stdout│──▶│  HTTP :8081  │   │  python:3.11-slim            │  │
│  └──────┬───────┘   └──────────────┘   └─────────────────────────────┘  │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 1    Data Ingestion     Mock Exchange HTTP :8080          │   │
│  │             Regime-Switching HMM · 7 symbols · Jump Diffusion     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 2    Signal Generation   User-written Python strategy      │   │
│  │             SMA/EMA/BB/RSI · Arbitrage detection · Kelly          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 3    Execution Engine   Limit Order Book · Price-Time Q    │   │
│  │             Market · Limit · IOC · FOK · Partial fills            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 4    Ledger & Accounting  SQLite Double-Entry              │   │
│  │             9 Accounts · Per-symbol P&L · Audit Trail             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 5    Risk Management     VaR/CVaR · Circuit Breaker        │   │
│  │             Position Limits · Leverage Cap · Correlation           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 6    Evaluation & Backtest  AST Audit · Hidden Tests       │   │
│  │             Monte Carlo · Composite Scoring · Ledger Integrity     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

### 🔗 Communication

| Between | Protocol | Mechanism |
|---------|----------|-----------|
| Layer 1 ↔ Layer 2 | HTTP REST | `GET /v1/orderbook`, `POST /v1/execute`, `GET /v1/regime` |
| Layer 2 ↔ Layer 4 | SQLite | `LedgerEngine.record_trade()` — double-entry journal |
| Layer 5 | Ledger queries | Reads equity curve, computes VaR/CVaR from returns |
| Layer 6 | Subprocess | Separate process with `NOVACAP_SEED` + `NOVACAP_DAY` env vars |

| Component | Threading | Port |
|-----------|-----------|------|
| CLI (`ArbitrageAcademyCLI`) | Main thread | stdin/stdout |
| Mock Exchange (`MockExchangeServer`) | Daemon thread | 8080 |
| Web UI (`WebUIServer`) | Daemon thread | 8081 |

---

## 🌪️ Regime-Switching Market Engine

The `MockPriceGenerator` implements a two-regime Markov-switching model:

| Regime | σ | Mean Reversion | Trend Bias | Spread | Jump λ | Book Depth |
|--------|----|----------------|------------|--------|--------|------------|
| 0 — LOW_VOL_TRENDING | `0.003` | `0.002` | `+0.0004` | `0.8×` | `0.002` | 12 levels |
| 1 — HIGH_VOL_MEAN_REVERTING | `0.025` | `0.08` | `−0.0001` | `1.8×` | `0.015` | 6 levels |

**Transition matrix:**
- `P(0 → 1) = 0.15` — minimum 30 ticks in regime 0
- `P(1 → 0) = 0.30` — minimum 20 ticks in regime 1

Regime state is exposed via `GET /v1/regime` and embedded in every order book and ticker response, allowing strategies to adapt to changing market conditions.

---

## 📋 Order Types & Execution

| Type | Behavior |
|------|----------|
| **Market** | Executes immediately against limit book. Unfilled portion fills at mid-price with slippage. |
| **Limit (GTC)** | Placed in price-time priority queue. Remains until filled or cancelled. |
| **IOC** | Immediate-or-Cancel — fills against available book, cancels remainder. |
| **FOK** | Fill-or-Kill — entire quantity must fill or order is cancelled. |

**Slippage model:**
```python
slippage_bps = pg.estimate_slippage_bps("BTC/USD", 1.0, "buy")
```

The model walks book levels until quantity is filled, computing volume-weighted average price vs. mid-price. Orders exceeding full depth incur a 5% penalty.

| Fee | Value |
|-----|-------|
| Exchange fee | 10 bps (0.1%) per trade |
| Recording | Debit `4100 Fee Expense`, Credit `1000 Cash - USD` |

---

## 🛡️ Risk Management

| Guard | Parameter | Threshold |
|-------|-----------|-----------|
| Historical VaR | 95% confidence | From return distribution |
| Conditional VaR | Expected shortfall | From tail beyond VaR |
| Circuit breaker | 10-bar window | 5% peak-to-current drawdown |
| Position limit | Per-symbol | 15% of current capital |
| Leverage limit | Gross exposure / capital | 2.0× max |
| Correlation | Symbol vs. portfolio | Risk report display |

```
strategist> risk

==================================================
RISK REPORT — Day 15
Circuit Breaker: Inactive
Equity: $102,345.67  |  Max DD: 2.34%
VaR(95%): 1.23%  |  CVaR(95%): 2.45%
Gross Exposure: $45,000.00  |  Leverage: 0.44x (max 2.0x)
Correlation: BTC/USD: +0.723  |  ETH/USDT: +0.541
Positions: 12 trades today
```

```
strategist> risk_reset       Reset circuit breaker and risk metrics
```

---

## 🔬 Monte Carlo Backtesting

```text
strategist> backtest [iterations=30] [days=30]
```

For each iteration the mock exchange quotes from a `MockPriceGenerator` seeded for that iteration, and your strategy runs once per simulated day as a separate process. **P&L is computed by the harness from the fills the exchange reports, marked to market at each day's prices** — nothing your script prints affects the score, so trade through `POST /v1/execute`. The same seed always produces the same market. Results aggregate into a distribution:

| Metric | What It Tells You |
|--------|-------------------|
| Mean / Median final equity | Expected terminal wealth |
| P10 / P90 final equity | Downside risk / upside potential |
| Mean Sharpe | Risk-adjusted return consistency |
| Median Max DD | Typical drawdown severity |
| Sharpe > 1.0 pct | Probability of acceptable returns |

---

## 📚 Curriculum

| Phase | Days | Regime | Focus |
|-------|------|--------|-------|
| 1 | 1–30 | 📈 LOW_VOL_TRENDING | Data ingestion, SMA/EMA crossovers, Bollinger Bands, RSI, Sharpe ratio, VaR |
| 2 | 31–60 | 📉 HIGH_VOL_MEAN_REVERTING | Cross-exchange arbitrage, triangular arbitrage, pairs trading, Kelly Criterion |
| 3 | 61–90 | 🔀 Mixed | Latency-aware execution, slippage impact, IFRS 9, TCA, circuit breakers |

---

## 🔍 Evaluation Pipeline

On `eod`, three stages execute in sequence:

```
Stage 1   AST Static Audit          CodeAuditor — 9 check categories
Stage 2   Hidden Test Suite         Separate process, 30s timeout
Stage 3   Ledger Integrity          Debits = Credits (tolerance 0.001)
```

| Condition | Deduction |
|-----------|-----------|
| Critical AST violation (eval/exec, missing try/except) | −40 each (≥2 = 0) |
| AST warning (nested loops, missing annotations, globals) | −10 each |
| Test failure | Proportional (up to −60) |
| Ledger imbalance | 0 — automatic failure |
| No solution file | 0 |

---

## 📁 Project Structure

```
NovaCap/
├── arbitrage_academy.py       ◆ 6 agent layers, 19 classes, ~4,200 LOC
├── finance_sim.py             Corporate finance simulation (2,592 LOC)
├── server.py                  Web UI HTTP server (1,292 LOC)
├── Dockerfile                 python:3.11-slim, ports 8080/8081
├── .github/workflows/ci.yml   CI pipeline — 19 stages, Python 3.8–3.12
├── generate_pdfs.py           PDF export utility
├── docs/                      Generated documentation (PDF)
├── workspace/                 Per-day solution templates (gitignored)
├── save_state.json            Persistent state machine (gitignored)
├── training_ledger.db         SQLite double-entry ledger (gitignored)
├── README.md                  This file
├── VALIDATION_REPORT_TEMPLATE.md
├── ENGINEERING_BREAKDOWN.md
├── BEFORE_YOU_BEGIN.html
├── TRAINING_PROGRAM.html
├── LICENSE                    MIT License
├── EULA.md                    MIT License (same text)
└── .gitignore
```

---

## 🔒 Security model

NovaCap runs your Python code, so its local servers are locked down:

- Both servers bind to `127.0.0.1` by default (`NOVACAP_BIND` overrides it; the Docker image sets `0.0.0.0` inside the container).
- Requests must be addressed to `localhost`/`127.0.0.1`, which blocks DNS-rebinding attacks from web pages.
- No cross-origin (CORS) access is granted.
- Every state-changing dashboard request must carry a random per-run token that only the dashboard page receives.

Strategies and tests run as separate processes with your user's permissions. That is a crash and timeout boundary, **not a sandbox**: the `CodeAuditor` is a teaching aid, not a security control. Only run code you have read.

## 🐳 Docker

```bash
docker build -t novacap .
docker run -p 127.0.0.1:8080:8080 -p 127.0.0.1:8081:8081 novacap
```

Publish the ports on `127.0.0.1` as shown. The dashboard can save and run Python files, so it must not be reachable from other machines.

---

## ✅ CI Pipeline

GitHub Actions runs **12 validation stages** across **Python 3.8, 3.9, 3.10, 3.11, and 3.12**:

1. Zero-dependency verification
2. AST parser validation
3. Mock exchange startup + health check
4. Regime switching activation (2 regimes)
5. Limit order book matching
6. CodeAuditor static analysis
7. LedgerEngine double-entry integrity
8. RiskManager VaR/CVaR computation
9. BacktestEngine initialization
10. CLI method completeness
11. Full integration smoke test (9 HTTP endpoints)
12. Dockerfile validation

---

## ⭐ Show Your Support

If NovaCap helped you learn something about algorithmic trading, consider giving it a star ⭐ — it helps others discover the project.

---

## ⚠️ Risk Disclosure

This software generates entirely synthetic market data. Nothing herein constitutes financial advice, trading recommendations, or investment guidance. All performance metrics produced by the simulator are for educational purposes only and do not imply real-world profitability.

---

<div align="center">
  <sub>Built with ❤️ and Python stdlib | MIT Licensed | © 2026 mutima89 — NovaCap Financial Technologies Ltd.</sub>
</div>
