# Engineering Breakdown: Orchestrating Multi-Agent State Management in a Zero-Dependency Trading Simulation

---

## The Problem

Building a multi-agent algorithmic trading system where each agent (data ingestion, execution, accounting, risk, evaluation) runs concurrently with distinct lifecycle requirements introduces a classic distributed state management problem — but without any of the usual tooling (no message queue, no database with pub/sub, not even `threading.Event` coordination in any sophisticated way). The constraint: the entire system must run on Python 3.8+ standard library only. No `asyncio`, no `celery`, no `redis`, no `zmq`.

The agents in question:

| Agent | Thread | Persistence Mechanism | State Scope |
|-------|--------|----------------------|-------------|
| CLI Orchestrator | Main thread | `save_state.json` (JSON) | Day progression, scores |
| Mock Exchange | Daemon thread | In-memory (`MockPriceGenerator`) | Market state (prices, order books) |
| Web UI Dashboard | Daemon thread | In-memory + ledger queries | Display state |
| SQLite Ledger | Shared (Mutex via `sqlite3`) | `training_ledger.db` | Trade records, P&L, account balances |
| Evaluation Engine | Subprocess (caller thread) | File system + ledger queries | Audit results, test output |

The challenge: these agents have to share three critical pieces of mutable state — (1) the current trading day and phase, (2) the market data snapshot, and (3) the ledger integrity — without race conditions, stale reads, or deadlocks. And all of this must be debuggable by a trainee who only wrote a 50-line strategy file.

---

## The Solution: Constrained Shared-State Architecture

### Principle 1: Single Writer per State Domain

Rather than implementing a generic lock manager, we constrained each mutable state domain to a single writer:

| State Domain | Writer | Reader(s) | Coordination |
|-------------|--------|-----------|-------------|
| Day/phase progression | `StateManager` (CLI thread) | CLI, Web UI, Evaluation Engine | File-based snapshot (`save_state.json`), read on init |
| Market prices | `MockPriceGenerator` (exchange thread) | User strategies (HTTP), Web UI (HTTP) | REST request-response; no shared memory |
| Ledger | `LedgerEngine` (CLI thread) | CLI, Web UI, Evaluation Engine | SQLite transactions with WAL mode |

The key insight: by routing all writes to a single thread per domain, we eliminated the need for explicit locks on those data structures. The HTTP boundary between the exchange and consuming strategies provides natural serialization — every `GET /v1/orderbook` returns a point-in-time snapshot.

### Principle 2: Journaled State Transitions via JSON Snapshot

The `StateManager` tracks day progression through a finite-state machine with 90 states (one per day). Instead of a database, we persist to `save_state.json`:

```python
# Core state machine — arbitrage_academy.py:1164
class StateManager:
    STATE_FILE = "save_state.json"

    def __init__(self):
        self.current_day: int = 1
        self.phase: int = 1
        self.completed_days: List[int] = []
        self.scores: Dict[str, Any] = {}
        self.load()  # Deserialize from disk

    def advance_day(self) -> bool:
        """Transition to next day. Persists immediately."""
        if self.current_day >= 90:
            return False
        self.completed_days.append(self.current_day)
        self.current_day += 1
        self.phase = self._compute_phase(self.current_day)
        self.save()  # Atomic JSON write
        return True

    def _compute_phase(self, day: int) -> int:
        if 1 <= day <= 30:   return 1
        if 31 <= day <= 60:  return 2
        return 3
```

Every state transition triggers an atomic JSON `save()`. This means if the process is killed mid-evaluation, the next `start` call recovers the last consistent state. The trade-off: no transactional guarantees across the state file and the ledger — if `advance_day()` succeeds but the Web UI crashes before refreshing, the user sees stale data on reload until they hit `status`.

### Principle 3: Evaluation Isolation via Subprocess

The `EvaluationEngine` runs each day's hidden test suite in a child `subprocess`:

```python
# Evaluation execution — arbitrage_academy.py:1514
result = subprocess.run(
    [sys.executable, test_runner],
    capture_output=True,
    text=True,
    timeout=30,
    cwd=workspace_parent,
)
```

This provides three guarantees:
1. **Memory isolation** — a buggy strategy cannot corrupt the evaluator's heap
2. **Timeout enforcement** — `subprocess.run(timeout=30)` kills runaway loops
3. **Independent namespace** — the test runner has its own `sys.path`, preventing import pollution

The AST auditor, by contrast, runs in-process because it operates on the source string, not on executed code. This is safe because `ast.parse()` does not execute the code — it builds a syntax tree without side effects.

### Principle 4: Verifiable Ledger with Double-Entry Invariants

The ledger audit acts as the system's consistency check. Every trade produces two or four journal entries that must sum to zero:

```python
def record_trade(self, trade_id, day, symbol, side, price, quantity, total, fee=0.0):
    # For a buy: Debit asset account, Credit cash account
    # For a fee: Debit expense account, Credit cash account
    # ...
    self.conn.commit()
```

The verify function provides the invariant:

```python
def verify_double_entry(self) -> Tuple[bool, float]:
    cur = self.conn.execute(
        "SELECT COALESCE(SUM(debit), 0) as total_debit, "
        "COALESCE(SUM(credit), 0) as total_credit FROM ledger_entries"
    )
    row = cur.fetchone()
    diff = abs(row["total_debit"] - row["total_credit"])
    return diff < 0.001, diff
```

If a strategy fails to record both sides of a trade, the verification catches it — and the evaluation scores 0 for that day.

---

## What We Gave Up

- **No event-driven architecture.** Agents communicate by polling (Web UI re-renders on interval) or by file read (evaluation reads solution from disk). This is acceptable for a single-user training simulator but would not scale to sub-millisecond tick-to-order latency.
- **No concurrent ledger writes.** The evaluation engine and the user's strategy never write to the ledger simultaneously. The CLI serializes: `run` (strategy writes) → then `eod` (evaluation reads). This avoids SQLite `SQLITE_BUSY` but limits the system to synchronous operation.
- **No in-memory cache invalidation.** The Web UI queries the ledger directly on every page render. For the dataset sizes involved (<100 trades per day), this is negligible; for production scale it would be prohibitive.

---

## Code Snippet: Bringing Up the Agents

```python
# Simplified agent bootstrap — arbitrage_academy.py
def main():
    state = StateManager()
    ledger = LedgerEngine(state.ledger_db)
    ledger.connect()

    exchange = MockExchangeServer()
    exchange.start()            # Daemon thread :8080

    dashboard = WebUIServer()
    dashboard.start()           # Daemon thread :8081

    app = PrincipalStrategistApp(state, ledger, exchange, dashboard)
    app.cmdloop()               # Main thread, blocking

    exchange.stop()
    dashboard.stop()
    ledger.close()
```

Each agent starts independently. The `cmd.Cmd` loop on the main thread orchestrates by reading keystrokes — not by reacting to market events. This is deliberately synchronous: the trainee controls the simulation clock via `run` and `eod`.

---

## Latency Profile (Single-Threaded Appraisal)

```
Operation                         Mean Latency (n=100)
───────────────────────────────────────────────────────
Order book fetch (HTTP localhost)     0.8 ms
Trade execution (POST + ledger write) 3.2 ms
AST audit (100 LOC file)              1.1 ms
EOD evaluation (full pipeline)       35–120 ms
```

The primary bottleneck is the hidden test subprocess (fork + import + run), which accounts for ~80% of EOD latency. Mitigation would require either test caching or in-process execution with namespace isolation — both of which would sacrifice the fault isolation guarantee.

---

## Repository

The full implementation is available at [github.com/mutima89/NovaCap](https://github.com/mutima89/NovaCap). The relevant files are:

- **`arbitrage_academy.py`** — All agent layers, state machine, ledger, AST auditor, evaluation engine (~3,961 LOC)
- **`server.py`** — Web UI dashboard (~1,292 LOC)
- **`README.md`** — Architecture docs and setup

The `StateManager`, `LedgerEngine`, and `CodeAuditor` classes are standalone and can be extracted for use in other simulation or backtesting frameworks.

---

*This is not financial advice. All market data is synthetic. The repository is an educational tool for software engineering and quantitative finance practice, not a production trading system.*
