<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/dependencies-zero-brightgreen?style=for-the-badge&logo=zeromq&logoColor=white" alt="Zero Dependencies">
  <img src="https://img.shields.io/github/actions/workflow/status/mutima89/NovaCap/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CI" alt="CI">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT License">
  <img src="https://img.shields.io/badge/LOC-4%2C200+-orange?style=for-the-badge&logo=codefactor&logoColor=white" alt="4,200+ LOC">
</p>

<h1 align="center">NovaCap</h1>
<h3 align="center">Multi-Agent Algorithmic Trading Simulation Framework</h3>
<p align="center"><em>One file. Zero dependencies. 90 days that will change how you write code.</em></p>

<br>

<p align="center">
  <b>Write real Python strategies against a regime-switching market with a full limit order book,<br>
  double-entry accounting, institutional risk controls, and Monte Carlo backtesting —<br>
  all inside a single <code>.py</code> file.</b>
</p>

<br>

---

## 📖 About

NovaCap drops you into the role of a **quantitative trading strategist** aboard a proprietary trading desk. Every trade, every risk report, every backtest iteration runs through the same pipeline an actual quant firm would use:

<p align="center">
  <code>Market Data → Signal → Execution → Ledger → Risk → Evaluation</code>
</p>

The only difference? The market is synthetic and the capital is fake. **The lessons are not.**

Built on six integrated agent layers, NovaCap is a self-contained ecosystem with HMM regime-switching dynamics, price-time priority limit order books, SQLite double-entry accounting, VaR/CVaR risk guards, and AST-level code auditing — running on the Python standard library alone.

---

## ✨ Capabilities

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
- ✅ **Monte Carlo engine** — N iterations × D days in subprocess isolation
- ✅ **Distribution statistics** — mean, median, P10, P90 final equity
- ✅ **Sharpe analysis** — probability of risk-adjusted return > 1.0
- ✅ **Max drawdown distribution** — severity range across all runs

### 🔍 Evaluation
- ✅ **AST static auditor** — 9 check categories (eval, loops, annotations, globals...)
- ✅ **Hidden test suite** — isolated subprocess, 30s timeout
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
strategist> start       Launch exchange + generate Day 1 solution template
strategist> run         Execute today's Python strategy
strategist> eod         End-of-Day evaluation and scoring
strategist> risk        Display VaR, CVaR, circuit breaker, positions
strategist> backtest    Run Monte Carlo backtest (30 iterations × 30 days)
```

**Prerequisites:** Python 3.8+ · Ports `8080` and `8081` available · **No `pip install`**

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

### Communication

| Between | Protocol | Mechanism |
|---------|----------|-----------|
| Layer 1 ↔ Layer 2 | HTTP REST | `GET /v1/orderbook`, `POST /v1/execute`, `GET /v1/regime` |
| Layer 2 ↔ Layer 4 | SQLite | `LedgerEngine.record_trade()` — double-entry journal |
| Layer 5 | Ledger queries | Reads equity curve, computes VaR/CVaR from returns |
| Layer 6 | Subprocess | Isolated process with `NOVACAP_SEED` + `NOVACAP_DAY` env vars |

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
| 0 — LOW_VOL_TRENDING | 0.003 | 0.002 | +0.0004 | 0.8× | 0.002 | 12 levels |
| 1 — HIGH_VOL_MEAN_REVERTING | 0.025 | 0.08 | −0.0001 | 1.8× | 0.015 | 6 levels |

**Transition matrix:**
- `P(0 → 1) = 0.15` — minimum 30 ticks in regime 0 before switching
- `P(1 → 0) = 0.30` — minimum 20 ticks in regime 1

Regime state is exposed via `GET /v1/regime` and embedded in every order book and ticker response, allowing strategies to condition behavior on detected market conditions.

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

Each iteration runs in an isolated subprocess with seeded `MockPriceGenerator` state. Results aggregate into a distribution:

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
Stage 2   Hidden Test Suite         Subprocess isolation, 30s timeout
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
├── EULA.md                    MIT License
└── .gitignore
```

---

## 🐳 Docker

```bash
docker build -t novacap .
docker run -p 8080:8080 -p 8081:8081 novacap
```

---

## ✅ CI Pipeline

GitHub Actions runs **19 validation stages** across **Python 3.8, 3.9, 3.10, 3.11, and 3.12**:

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

---

## 📄 License

MIT License — see [`EULA.md`](EULA.md).

Copyright (c) 2026 Mutima — NovaCap Financial Technologies Ltd.

---

<p align="center">
  <sub>⚠️ <strong>Risk Disclosure:</strong> This software generates entirely synthetic market data. Nothing herein constitutes financial advice, trading recommendations, or investment guidance. All performance metrics produced by the simulator are for educational purposes only and do not imply real-world profitability.</sub>
</p>
