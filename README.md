# NovaCap — Multi-Agent Algorithmic Trading Simulation Framework

**Version:** 1.0.0 | **Python:** 3.8+ | **Dependencies:** None (stdlib only)

NovaCap is a self-contained, multi-agent algorithmic trading simulation environment built entirely with the Python standard library. It implements a layered agent hierarchy — data ingestion, signal generation, execution, and risk management — orchestrated via concurrent HTTP servers, a SQLite double-entry ledger, and an AST-level static analysis pipeline. The system spans a 90-day escalating curriculum across three market regimes.

**Risk Disclosure:** This software generates entirely synthetic market data. Nothing herein constitutes financial advice, trading recommendations, or investment guidance. All performance metrics produced by the simulator are for educational purposes only and do not imply real-world profitability.

---

## Architecture Overview

The system is decomposed into five agent layers, each running in its own thread or process, communicating via HTTP REST and a shared SQLite database:

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
│  │                    LAYER 1: DATA INGESTION                        │    │
│  │  Mock Exchange Server (HTTP :8080) — 5 synthetic symbols          │    │
│  │  Configurable volatility, spread, order book depth               │    │
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
│  │                    LAYER 3: EXECUTION ENGINE                      │    │
│  │  REST-based order placement (POST /v1/execute)                   │    │
│  │  Position sizing, fee deduction, trade confirmation              │    │
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
│  │                    LAYER 5: RISK & EVALUATION                      │    │
│  │  AST static code auditor — 9 check categories                     │    │
│  │  Hidden test suite execution — subprocess isolation               │    │
│  │  Ledger integrity verification (debits = credits)                 │    │
│  │  Composite scoring 0–100                                          │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Inter-Agent Communication

- **Layer 1 ↔ Layer 2:** HTTP REST. The mock exchange exposes `GET /v1/orderbook`, `GET /v1/ticker`, `POST /v1/execute`. User strategies use `urllib.request` to consume these endpoints.
- **Layer 2 ↔ Layer 4:** SQLite. Trade executions are recorded via `LedgerEngine.record_trade()`, which creates double-entry journal entries.
- **Layer 5 ↔ All:** File system + subprocess. The evaluation engine reads user solution files from disk, parses them with the `ast` module, executes hidden test runners in isolated subprocesses, and queries the ledger for balance verification.

### Asynchronous Design

The CLI orchestrator, mock exchange, and web dashboard each run on independent threads:

| Component | Threading Model | Port |
|-----------|----------------|------|
| CLI (`PrincipalStrategistApp`) | Main thread (blocking `cmdloop`) | stdin/stdout |
| Mock Exchange (`MockExchangeServer`) | Daemon thread (`HTTPServer.serve_forever`) | 8080 |
| Web UI (`WebUIServer`) | Daemon thread (`HTTPServer.serve_forever`) | 8081 |

The `StateManager` persists progression state to `save_state.json`, enabling crash recovery across sessions.

---

## Strategy Mechanics

### Alpha Generation Framework

The curriculum structures alpha generation across three market regimes, each corresponding to a 30-day phase:

| Phase | Days | Regime | Alpha Mechanism |
|-------|------|--------|----------------|
| 1 | 1–30 | Trending / Mean-Reverting | Moving average crossovers (SMA-5 / SMA-20), Bollinger Band reversion, RSI thresholding |
| 2 | 31–60 | Arbitrage / Fragmented | Cross-exchange spread detection, triangular arbitrage (BTC→ETH→USDT→BTC), Kelly Criterion sizing |
| 3 | 61–90 | Regulated / High-Latency | Latency-aware execution, slippage modeling, SOCPA/IFRS 9 compliance, VaR/CVaR stress testing |

### Market Data Model

The `MockPriceGenerator` (internal to `MockExchangeServer`) produces synthetic tick data for five symbols with configurable parameters:

```
BTC/USD, ETH/USDT, SOL/USD, AVAX/USDT, LINK/USD
```

Each symbol's price evolves via a Gaussian random walk with:
- Per-tick volatility `σ ∈ [0.001, 0.02]`
- Bid-ask spread proportional to volatility
- Order book depth modeled as a limited-liquidity L2 snapshot (15 levels per side)

### Technical Indicator Computation

User strategies compute indicators from fetched order book mid-prices:

```python
# Example: SMA calculation within user strategy
def compute_sma(prices: list[float], window: int) -> float:
    if len(prices) < window:
        return 0.0
    return sum(prices[-window:]) / window
```

The AST auditor enforces that all functions carry PEP 484 type annotations and that network calls are wrapped in `try`/`except`.

---

## Execution & Risk Protocols

### Position Sizing

The simulated exchange executes trades at the posted quantity and price from the order book. Partial fills are not modeled — orders execute fully at the best available price or are rejected. Position sizing parameters are defined per user strategy; the system enforces no hard cap beyond available account balances in the ledger.

### Fee & Slippage Model

| Parameter | Default Value | Source |
|-----------|---------------|--------|
| Exchange fee | 0.1% per trade (`fee = total * 0.001`) | `MockExchangeHandler` |
| Spread | Variable, per symbol (proportional to σ) | `MockPriceGenerator` |
| Slippage | Not modeled in base simulation | Phase 3 introduces latency simulation |

Fees are recorded as double-entry: debit `4100 (Fee Expense)`, credit `1000 (Cash - USD)`.

### Risk Constraints (Phase 3)

Phase 3 introduces SOCPA-compliant risk controls:

- **Maximum Drawdown:** Strategies are evaluated on peak-to-trough drawdown; no automatic circuit breaker in the simulation, but evaluation scoring penalizes excessive drawdown.
- **Hard Stop-Loss:** Not enforced by the exchange — the user's strategy must implement stop-loss logic. The AST auditor checks for `while True` loops without break conditions (infinite loop risk).
- **Position limits:** No hard limit by the exchange, but the ledger model (9 accounts) enforces double-entry balance: total debits must equal total credits.

### Hard Stop-Loss Logic (User-Implemented)

```python
# Template from solution_day_XXX.py
MAX_DRAWDOWN_PCT = 0.05   # 5% max loss per session
POSITION_LIMIT_PCT = 0.10 # 10% of capital per position

def check_stop_loss(current_pnl: float, peak_pnl: float) -> bool:
    dd = (peak_pnl - current_pnl) / peak_pnl if peak_pnl > 0 else 0
    return dd >= MAX_DRAWDOWN_PCT
```

---

## Reproducibility

### Prerequisites

- Python 3.8+ (3.11+ recommended for f-string syntax)
- Ports 8080 and 8081 must be available
- No `pip install`, no `requirements.txt`, no Docker — zero external dependencies

### Baseline Backtest (5-Minute Setup)

```powershell
# 1. Clone and enter directory
git clone https://github.com/mutima89/NovaCap.git
cd NovaCap

# 2. Launch simulator
python arbitrage_academy.py

# 3. Start Day 1
# Inside CLI:
strategist> start

# 4. Navigate to generated workspace
# workspace/day_001/solution_day_001.py

# 5. Write strategy, then execute
strategist> run
strategist> eod
```

The mock exchange begins serving at `http://localhost:8080`, and the web dashboard is accessible at `http://localhost:8081`.

### Project Structure

```
NovaCap/
├── arbitrage_academy.py    # Master simulator: all 5 agent layers (~3,961 LOC)
├── finance_sim.py          # Corporate finance simulation (2,592 LOC)
├── server.py               # Web UI HTTP server (1,292 LOC)
├── generate_pdfs.py        # PDF export utility
├── docs/                   # Generated documentation (PDF)
├── workspace/              # Per-day generated workspaces (gitignored)
├── save_state.json         # Persistent state machine (gitignored)
├── training_ledger.db      # SQLite double-entry ledger (gitignored)
├── BEFORE_YOU_BEGIN.html   # Prep guide
├── TRAINING_PROGRAM.html   # 90-day syllabus
├── EULA.md                 # MIT License
└── README.md
```

### Verification

After running `eod`, verify the evaluation output:

```
Score: 100/100 (100.0%)
Status: PASS
Ledger Integrity: Verified (debits = credits)
```

Successful completion of each day requires a score of exactly 100/100.

---

## Evaluation Pipeline

The `EvaluationEngine` executes three serialized stages on `eod`:

```
Stage 1: AST Static Audit
├── Syntax validation
├── Network call exception coverage
├── Nested loop complexity (O(n²) detection)
├── Security patterns (eval/exec/pickle)
├── PEP 484 annotation compliance
├── Division-by-zero risk
├── Infinite loop detection
└── Global state prohibition

Stage 2: Subprocess Test Suite
├── Hidden unit tests per day
├── 30-second timeout
└── JSON-serialized results

Stage 3: Ledger Integrity
├── Total debits == Total credits (tolerance: 0.001)
└── Per-symbol P&L computation
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

## License

MIT License — see [`EULA.md`](EULA.md).

Copyright (c) 2026 Mutima — NovaCap Financial Technologies Ltd.
