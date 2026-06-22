# NovaCap — Multi-Agent Algorithmic Trading Simulation Framework

**Version:** 2.0.0 | **Python:** 3.8+ | **Dependencies:** None (stdlib only)

NovaCap is a self-contained, multi-agent algorithmic trading simulation environment built entirely with the Python standard library. It implements a six-layer agent hierarchy — data ingestion, signal generation, execution, accounting, risk management, and backtesting — orchestrated via concurrent HTTP servers, a SQLite double-entry ledger, an AST-level static analysis pipeline, and a two-regime Markov-switching market engine with a full limit order book.

**Risk Disclosure:** This software generates entirely synthetic market data. Nothing herein constitutes financial advice, trading recommendations, or investment guidance. All performance metrics produced by the simulator are for educational purposes only and do not imply real-world profitability.

---

## Architecture Overview

The system is decomposed into six agent layers, each running in its own thread or process:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     NOVACAP MULTI-AGENT ARCHITECTURE                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────┐    ┌─────────────────────┐                      │
│  │   CLI Orchestrator  │    │   Web UI Dashboard   │                      │
│  │   (cmd.Cmd)         │────│   HTTP :8081         │                      │
│  │   State Machine     │    │   Real-time Stats     │                      │
│  └─────────┬───────────┘    └─────────────────────┘                      │
│            │                                                             │
│            ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │          LAYER 1: DATA INGESTION (Regime-Switching)               │    │
│  │  Mock Exchange Server (HTTP :8080) — 7 synthetic symbols          │    │
│  │  2-state HMM: low-vol trending → high-vol mean-reverting          │    │
│  │  Jump diffusion (Poisson shocks) and regime-dependent depth       │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│            │                                                             │
│            ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    LAYER 2: SIGNAL GENERATION                      │    │
│  │  User-written Python strategy (per-day solution file)             │    │
│  │  SMA, EMA, Bollinger Bands, RSI, arbitrage detection             │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│            │                                                             │
│            ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │              LAYER 3: EXECUTION ENGINE (Limit Book)               │    │
│  │  Market / Limit (GTC) / IOC / FOK order types                    │    │
│  │  Partial fills via limit order queue matching                    │    │
│  │  Slippage estimation from order book depth                       │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│            │                                                             │
│            ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    LAYER 4: LEDGER & ACCOUNTING                    │    │
│  │  SQLite double-entry bookkeeping (9 standard accounts)            │    │
│  │  Per-symbol P&L, fee tracking, audit trail                       │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│            │                                                             │
│            ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │               LAYER 5: RISK MANAGEMENT                            │    │
│  │  Historical VaR(95%) / CVaR(95%) computation                     │    │
│  │  Portfolio correlation tracking, leverage limits (2.0x)          │    │
│  │  Per-symbol position limits (15% of capital)                     │    │
│  │  Circuit breaker: 5% drawdown over 10-bar window                 │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│            │                                                             │
│            ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │          LAYER 6: EVALUATION & BACKTESTING                        │    │
│  │  AST static code auditor — 9 check categories                     │    │
│  │  Hidden test suite execution — subprocess isolation               │    │
│  │  Ledger integrity verification (debits = credits)                 │    │
│  │  Monte Carlo backtesting — N iterations x D days                  │    │
│  │  Composite scoring 0–100                                          │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

### Inter-Agent Communication

- **Layer 1 ↔ Layer 2:** HTTP REST. The mock exchange exposes `GET /v1/orderbook`, `GET /v1/ticker`, `POST /v1/execute`, `GET /v1/regime`, `GET /v1/orders`, `POST /v1/cancel`.
- **Layer 2 ↔ Layer 4:** SQLite. Trade executions recorded via `LedgerEngine.record_trade()` — double-entry journal entries.
- **Layer 5:** Reads equity curve from ledger, computes VaR/CVaR from return distribution, checks circuit breaker thresholds.
- **Layer 6:** Evaluates via file system + subprocess. Backtest engine replays seeded runs.

### Asynchronous Design

| Component | Threading Model | Port |
|-----------|----------------|------|
| CLI (`ArbitrageAcademyCLI`) | Main thread (blocking `cmdloop`) | stdin/stdout |
| Mock Exchange (`MockExchangeServer`) | Daemon thread (`HTTPServer.serve_forever`) | 8080 |
| Web UI (`WebUIServer`) | Daemon thread (`HTTPServer.serve_forever`) | 8081 |

The `StateManager` persists progression state to `save_state.json`.

---

## Regime-Switching Market Engine

The `MockPriceGenerator` implements a two-regime Markov-switching model:

| Regime | Volatility (σ) | Mean Reversion | Trend Bias | Spread Mult | Jump Intensity | Book Depth |
|--------|---------------|----------------|------------|-------------|---------------|------------|
| 0 — LOW_VOL_TRENDING | 0.003 | 0.002 | +0.0004 | 0.8× | 0.002 (0.2%) | 12 levels |
| 1 — HIGH_VOL_MEAN_REVERTING | 0.025 | 0.08 | −0.0001 | 1.8× | 0.015 (1.5%) | 6 levels |

Regime transitions follow a 2×2 transition matrix:
- `P(0→1) = 0.15` after min 30 ticks in regime 0
- `P(1→0) = 0.30` after min 20 ticks in regime 1

The regime state is exposed via `GET /v1/regime` and embedded in every order book and ticker response. This lets strategies condition behavior on the detected regime.

### Jump Diffusion

Poisson-distributed price jumps occur at `λ = 0.002–0.015` per tick with magnitude drawn from an exponential distribution. This tests stop-loss logic and position sizing under tail events.

### Order Book Depth

The limit order book depth varies by regime — shallow (6 levels) during high volatility, deep (12 levels) during low volatility — impacting slippage estimates for large orders.

---

## Execution & Order Types

The `OrderBookManager` maintains a price-time priority limit order book:

| Order Type | Behavior |
|-----------|----------|
| **Market** | Executes immediately against the limit book. Unfilled quantity fills at mid-price with slippage from depth estimation. |
| **Limit (GTC)** | Placed in the book at specified price. Remains until filled or cancelled. |
| **IOC** | Immediate-or-Cancel — fills against available book, cancels remainder. |
| **FOK** | Fill-or-Kill — must fill entire quantity or the entire order is cancelled. |

### Slippage Model

Slippage is estimated from the order book depth:

```python
slippage_bps = pg.estimate_slippage_bps(symbol, quantity, side)
```

This walks the book levels until the quantity is filled, computing the volume-weighted average price vs. the mid-price. Orders exceeding the full depth are charged an additional 5% penalty.

### Fee Model

| Parameter | Value |
|-----------|-------|
| Exchange fee | 10 bps (0.1%) per trade |
| Fee recording | Debit `4100 Fee Expense`, Credit `1000 Cash - USD` |

---

## Risk Management Framework

The `RiskManager` layer provides continuous monitoring:

| Feature | Parameter | Threshold |
|---------|-----------|-----------|
| Historical VaR | 95% confidence | Computed from return distribution |
| Conditional VaR (CVaR) | Expected shortfall beyond VaR | Computed from tail |
| Circuit breaker | Rolling 10-bar window | 5% peak-to-current drawdown |
| Position limit | Per-symbol | 15% of current capital |
| Leverage limit | Gross exposure / capital | 2.0× max |
| Correlation | Symbol-level to portfolio | Displayed in risk report |

### Risk CLI Commands

```
strategist> risk          # Display full risk report
strategist> risk_reset    # Reset circuit breaker and risk metrics
```

### Example risk report output:

```
RISK REPORT — Day 15
==================================================
Circuit Breaker: Inactive
Equity: $102,345.67  |  Max DD: 2.34%
VaR(95%): 1.23%  |  CVaR(95%): 2.45%
Gross Exposure: $45,000.00  |  Leverage: 0.44x (max 2.0x)
Correlation: BTC/USD: +0.723  |  ETH/USDT: +0.541
Positions: 12 trades today
```

---

## Monte Carlo Backtesting

The `BacktestEngine` runs the user's strategy across multiple seeded iterations:

```
strategist> backtest [iterations=30] [days=30]
```

Each iteration spawns an isolated subprocess with `NOVACAP_SEED` and `NOVACAP_DAY` environment variables. Results are aggregated into a distribution:

| Statistic | Description |
|-----------|-------------|
| Mean / Median final equity | Central tendency across runs |
| P10 / P90 final equity | Dispersion / downside risk |
| Mean Sharpe | Risk-adjusted return distribution |
| Median Max DD | Typical worst drawdown |
| Sharpe > 1.0 pct | Probability of acceptable risk-adjusted returns |

---

## Strategy Mechanics

### Curriculum Structure

| Phase | Days | Regime | Alpha Mechanism |
|-------|------|--------|----------------|
| 1 | 1–30 | Data Ingestion & Risk Math | SMA/EMA crossovers, Bollinger Bands, RSI, Sharpe ratio, VaR |
| 2 | 31–60 | Algorithmic Arbitrage | Cross-exchange spread, triangular arbitrage, pairs trading, Kelly Criterion |
| 3 | 61–90 | Slippage & SOCPA Compliance | Latency-aware execution, slippage impact, IFRS 9, TCA, circuit breakers |

---

## Reproducibility

### Prerequisites

- Python 3.8+ (3.11+ recommended)
- Ports 8080 and 8081 must be available
- No `pip install` — zero external dependencies

### Quick Start

```bash
git clone https://github.com/mutima89/NovaCap.git
cd NovaCap
python arbitrage_academy.py

# Inside CLI:
strategist> start       # Launch exchange + generate Day 1 workspace
strategist> run         # Execute today's solution
strategist> eod         # End-of-Day evaluation
```

### Docker

```bash
docker build -t novacap .
docker run -p 8080:8080 -p 8081:8081 novacap
```

### Project Structure

```
NovaCap/
├── arbitrage_academy.py      # All 6 agent layers (~4,200 LOC)
├── finance_sim.py            # Corporate finance simulation (2,592 LOC)
├── server.py                 # Web UI HTTP server (1,292 LOC)
├── Dockerfile                # Containerized deployment
├── .github/workflows/ci.yml  # GitHub Actions CI (19 validation stages)
├── generate_pdfs.py          # PDF export utility
├── docs/                     # Generated documentation (PDF)
├── workspace/                # Per-day generated workspaces (gitignored)
├── save_state.json           # Persistent state machine (gitignored)
├── training_ledger.db        # SQLite double-entry ledger (gitignored)
├── README.md                 # This file
├── VALIDATION_REPORT_TEMPLATE.md  # Quantitative validation template
├── ENGINEERING_BREAKDOWN.md  # Multi-agent state management deep-dive
├── BEFORE_YOU_BEGIN.html     # Prep guide
├── TRAINING_PROGRAM.html     # 90-day syllabus
├── EULA.md                   # MIT License
└── .gitignore
```

---

## Evaluation Pipeline

The `EvaluationEngine` executes three serialized stages on `eod`:

```
Stage 1: AST Static Audit        (CodeAuditor — 9 check categories)
Stage 2: Subprocess Test Suite   (Hidden tests, 30s timeout)
Stage 3: Ledger Integrity        (Debits = Credits tolerance: 0.001)
```

### Scoring Matrix

| Condition | Deduction |
|-----------|-----------|
| Critical AST violation (missing try/except, eval/exec) | −40 each (≥2 = automatic 0) |
| AST warning (nested loops, missing annotations, global state) | −10 each |
| Test failure | Proportional deduction (up to −60) |
| Ledger imbalance | 0 (automatic failure) |
| No solution file | 0 |

---

## CI Pipeline

GitHub Actions runs 19 validation stages across Python 3.8–3.12:

1. Zero-dependency verification
2. AST parser validation
3. Mock exchange startup and health check
4. Regime switching activation test
5. Limit order book matching test
6. CodeAuditor static analysis test
7. LedgerEngine double-entry test
8. RiskManager VaR/CVaR test
9. BacktestEngine initialization test
10. CLI method completeness check
11. Full integration smoke test (9 HTTP endpoints)

---

## License

MIT License — see [`EULA.md`](EULA.md).

Copyright (c) 2026 Mutima — NovaCap Financial Technologies Ltd.
