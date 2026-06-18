# Principal Strategist — Training Program

## Master Algorithmic Arbitrage Trading with Python

> A structured 90-day journey from data ingestion to SOCPA-compliant trading systems.
> No external dependencies. No shortcuts. Real standards.

---

## How This Program Works

The Principal Strategist simulator generates **90 daily challenges** across three phases.
Each day follows the same cycle:

```
START → Briefing → Code → Run → EOD → Score ≥ 100? → ADVANCE
               ↑                                    ↓
           Fix violations ←── Score < 100 ←─────────┘
```

**The rule is simple:** score 100/100 on every day's evaluation, or you do not advance.
There is no partial credit. There is no "good enough."

---

## Prerequisites

Before you begin, you should be comfortable with:

| Skill | Level Required | How It's Tested |
|-------|---------------|-----------------|
| Python syntax | Write functions, loops, conditionals | Day 1 boilerplate |
| Type annotations | PEP 484 — `def f(x: int) -> str:` | AST auditor checks |
| Exception handling | `try/except/finally` blocks | Critical AST violation if missing |
| Basic SQL | `SELECT`, `INSERT`, `CREATE TABLE` | Ledger Engine tasks |
| HTTP concepts | GET/POST, JSON, status codes | Mock Exchange interaction |
| Command line | Running Python scripts, navigating directories | CLI interaction |

**If you cannot do all of the above, start with Days 1–3 in "learning mode"**
(score is informational, not blocking) until you're comfortable.

---

## The Three Phases

### Phase 1: Data Ingestion & Foundational Risk Math (Days 1–30)

**Theme:** You are a data pipeline. Fetch, calculate, log, repeat.

| Day Span | Focus Area | Key Skills |
|----------|-----------|------------|
| **1–5** | REST API data ingestion | `urllib.request`, JSON parsing, error handling, exponential backoff |
| **6–10** | Technical indicators | SMA, EMA, Bollinger Bands, RSI from scratch |
| **11–15** | SQLite mastery | Schema design, `INSERT`, `SELECT`, aggregation, double-entry logging |
| **16–20** | Statistical risk metrics | Variance, standard deviation, Sharpe ratio, max drawdown |
| **21–25** | Data pipeline architecture | Batching, windowing, memory-efficient streaming |
| **26–30** | **Phase 1 Capstone** | Build a complete ingestion → calculation → logging pipeline. AST audit must pass all critical checks. |

**Phase 1 Score Target:** 100/100 on every day by Day 30.

**Common Failure Modes:**
- Missing try-except on network calls **(automatic 0)**
- Nested O(n²) loops on large datasets **(AST warning → -10 pts)**
- Ledger imbalance (debits ≠ credits) **(test failure → -30 pts)**
- Missing type annotations on function signatures **(AST info → -10 pts)**

---

### Phase 2: Arbitrage Logic (Days 31–60)

**Theme:** Find the spread. Execute before it's gone.

| Day Span | Focus Area | Key Skills |
|----------|-----------|------------|
| **31–35** | Cross-exchange detection | Poll PRIMARY vs SECONDARY, calculate spread, threshold detection |
| **36–40** | Arbitrage execution | POST `/v1/execute`, position sizing, fee-aware P&L |
| **41–45** | Triangular arbitrage | 3-asset cycles (BTC→ETH→USDT→BTC), rate conversion, opportunity scanning |
| **46–50** | Risk controls | Kelly Criterion position sizing, stop-loss, max exposure limits |
| **51–55** | Latency simulation | Timestamp diff analysis, slippage models, fill probability |
| **56–60** | **Phase 2 Capstone** | Real-time triangular scanner with auto-execution, risk limits, and full ledger reconciliation |

**Phase 2 Score Target:** 100/100 consistently. By now, failing a day should be rare.

**Common Failure Modes:**
- Trading without checking spread threshold **(logic error → test failure)**
- Executing without sufficient balance **(ledger inconsistency)**
- Missing fee calculations in P&L **(SOCPA compliance violation)**
- No rate limiting on exchange calls **(simulated ban → day reset)**

---

### Phase 3: Slippage & SOCPA Compliance (Days 61–90)

**Theme:** It's not enough to be profitable. You must be provably correct.

| Day Span | Focus Area | Key Skills |
|----------|-----------|------------|
| **61–65** | SOCPA audit trails | Every trade has a complete provenance record, timestamps, and authorization chain |
| **66–70** | IFRS 9 reporting | Financial instrument classification, impairment calculations, disclosure notes |
| **71–75** | VaR & CVaR | Historical simulation VaR (95%/99%), expected shortfall, stress scenario analysis |
| **76–80** | Compliance report generation | Automated PDF/JSON reports, auditor-ready output, exception logging |
| **81–85** | System resilience | Graceful degradation, exchange downtime handling, data recovery |
| **86–90** | **Final Capstone** | Full 5-day audit simulation: run all 90 days, produce complete compliance package, pass external audit scenario |

**Phase 3 Score Target:** 100/100. The evaluation engine becomes stricter. Partial credit is removed for any compliance violation.

**Common Failure Modes:**
- Missing audit timestamps **(automatic 0 — SOCPA violation)**
- IFRS classification errors **(test failure → -30 pts)**
- VaR calculation off by more than 1% **(precision failure → day reset)**
- Any ledger imbalance after reconciliation **(compliance breach)**
- System crash during exchange downtime **(resilience failure)**

---

## Weekly Schedule

Each week follows a rhythm:

| Day | Activity | Estimated Time |
|-----|----------|---------------|
| **Monday** | Receive briefing, review objectives | 15 min |
| **Tuesday** | Write solution code | 1–3 hours |
| **Wednesday** | Debug, run, iterate | 1–2 hours |
| **Thursday** | Finalize, run EOD, fix violations | 1–2 hours |
| **Friday** | Advance, review learnings | 30 min |
| **Saturday** | Optional: refactor or extend previous days | – |
| **Sunday** | Rest or catch up | – |

**Total weekly commitment:** 4–8 hours for most participants.

---

## Scoring System

| Component | Weight | Details |
|-----------|--------|---------|
| **AST Critical Violations** | –40 each | No try-except on network calls, eval/exec, prohibited imports. **Two = automatic 0.** |
| **AST Warnings** | –10 each | Nested loops, missing annotations, division by zero risk, infinite loops, global state |
| **Test Failures** | –30 each | Hidden test suite checks functional correctness |
| **Ledger Imbalance** | –30 each | Double-entry verification failure (debits ≠ credits) |
| **Manual Deductions** | Variable | Principal Strategist may apply situational penalties |

**Score = max(0, 100 – deductions)**

You need **100 exactly** to advance. One warning brings you to 90. One critical brings you to 60.

---

## Reference Materials

The simulator enforces three real-world accounting standards:

### CMA (Certified Management Accountant)
- **Part 1 — Financial Planning, Performance, and Analytics**
  - Section C: Financial Statement Analysis
  - Section E: Investment Decisions
- **Part 2 — Strategic Financial Management**
  - Section A: Financial Statement Analysis
  - Section D: Risk Management

### SOCPA (Saudi Organization for Chartered and Professional Accountants)
- **Standard 4:** Documentation and audit trail requirements
- **Standard 7:** Financial instrument recognition and measurement
- **Standard 12:** Revenue recognition and trade recording

### IFRS (International Financial Reporting Standards)
- **IFRS 9:** Financial Instruments — classification, measurement, impairment
- **IFRS 13:** Fair Value Measurement — hierarchy levels, disclosure
- **IFRS 15:** Revenue from Contracts with Customers — trade revenue recognition

---

## AST Auditor — What It Checks

The AST auditor parses your code and flags these issues:

### Critical (Score –40)
| Code | Pattern | Why It Matters |
|------|---------|---------------|
| `NO_NETWORK_EXCEPT` | `urllib.request.urlopen(...)` without `try` | Exchange goes down → your pipeline crashes |
| `NO_NETWORK_EXCEPT` | `urllib.request.Request(...)` without `try` | Same — every network call must be guarded |
| `EVAL_EXEC` | `eval(...)` or `exec(...)` | Arbitrary code execution — security risk |
| `PROHIBITED_IMPORT` | `pickle`, `shelve`, `marshal` | Deserialization vulnerabilities |

### Warning (Score –10)
| Code | Pattern | Why It Matters |
|------|---------|---------------|
| `NESTED_LOOP` | `for i in range(n): for j in range(m):` | O(n²) complexity — doesn't scale |
| `DIVISION_BY_ZERO` | `a / b` without `b != 0` check | Runtime crash |
| `INFINITE_WHILE` | `while True:` without `break` | Never-terminating loop |
| `GLOBAL_STATE` | `global x` at module level | Side effects, untestable code |

### Info (Score –0, but recorded)
| Code | Pattern | Why It Matters |
|------|---------|---------------|
| `MISSING_ANNOTATION` | Function parameter or return without type hint | PEP 484 compliance |

---

## Study Resources

### Python Standard Library (all you need)
| Module | Use Case | Relevant Days |
|--------|----------|--------------|
| `urllib.request` | HTTP GET/POST to exchange | 1–60 |
| `urllib.error` | HTTP error handling | 1–60 |
| `json` | Parse exchange responses | 1–90 |
| `sqlite3` | Ledger database | 1–90 |
| `ast` | Static code analysis (used by auditor) | Understanding only |
| `subprocess` | Run tests in isolated processes | Understanding only |
| `threading` | Background servers (exchange + web UI) | Understanding only |
| `http.server` | Exchange and dashboard servers | Understanding only |
| `cmd` | CLI interface | Understanding only |
| `math` | Statistical calculations | 11–30, 71–75 |
| `statistics` | Mean, stdev for risk metrics | 16–20 |

### External Concepts (you'll need to learn)
| Concept | Where It Appears | Resource |
|---------|-----------------|----------|
| SMA / EMA | Days 1–10 | Investopedia: Moving Average |
| Bollinger Bands | Days 6–10 | Investopedia: Bollinger Bands |
| Sharpe Ratio | Days 16–20 | Wikipedia: Sharpe Ratio |
| Cross-exchange arbitrage | Days 31–35 | QuantConnect: Arbitrage |
| Triangular arbitrage | Days 41–45 | Binance Academy: Triangular Arbitrage |
| Kelly Criterion | Days 46–50 | Investopedia: Kelly Criterion |
| Value at Risk (VaR) | Days 71–75 | CFA Institute: VaR |
| CVaR / Expected Shortfall | Days 71–75 | Wikipedia: Expected Shortfall |

---

## Progress Tracking

Use the simulator's built-in tracking:

```bash
strategist> status
```

Expected output by phase:

```
Phase 1 (Day 30):  Days passed: 30/30  Cum. score: 3000/3000  ⭐⭐⭐
Phase 2 (Day 60):  Days passed: 60/60  Cum. score: 6000/6000  ⭐⭐⭐
Phase 3 (Day 90):  Days passed: 90/90  Cum. score: 9000/9000  ⭐⭐⭐🏆
```

---

## Graduation Criteria

To complete the Principal Strategist program:

1. **All 90 days passed** with score 100/100
2. **Zero critical AST violations** across all days
3. **Ledger balanced** at all times (verified after each day)
4. **Final capstone compliance package** generated and complete

**Graduates receive:**
- Completion certificate (generated by the simulator on Day 90)
- Their name added to the NovaCap "Honor Roll" (a JSON file in the workspace)
- The satisfaction of surviving the most demanding Python training simulation ever built

---

*"This is not a course. This is a simulation of the most demanding trading desk in the region."*
