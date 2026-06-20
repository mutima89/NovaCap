# Principal Strategist — 90-Day FinTech Arbitrage Training Simulator

> *"This is not a course. This is a simulation of the most demanding trading desk in the region."*

A hard-mode, self-contained algorithmic trading training simulator. You write Python code against a live mock exchange, log trades to a double-entry SQLite ledger, pass AST static audits, and face ruthless EOD evaluations. Score 100 or you don't advance.

---

## 🎯 What You Get

**One file. Zero dependencies. 90 days of rigorous training.**

| Spec | Detail |
|------|--------|
| File size | ~4,000 lines of Python |
| Dependencies | **None** — standard library only |
| Python | 3.8+ (any OS: Windows, macOS, Linux) |
| Setup | `python arbitrage_academy.py` — that's it |
| Interface | CLI (cmd.Cmd) + full Web Dashboard on `:8081` |
| Mock Exchange | HTTP server on `:8080` |

---

## 🧠 What You'll Master

### Phase 1 — Days 1–30: Data Ingestion & Risk Math
- Fetch order books from REST APIs with error handling
- Calculate SMA, EMA, Bollinger Bands, RSI
- Log all data to a double-entry SQLite ledger
- ASTM static code audits on every submission

### Phase 2 — Days 31–60: Arbitrage Logic
- Cross-exchange spread detection (PRIMARY vs SECONDARY)
- Real-time triangular arbitrage (BTC → ETH → USDT → BTC)
- Position sizing and Kelly Criterion
- Latency simulation and slippage models

### Phase 3 — Days 61–90: Slippage & SOCPA Compliance
- SOCPA-compliant audit trails and reconciliation
- IFRS 9 financial instrument reporting
- VaR, CVaR, and stress testing
- Full compliance report generation

---

## 🏗️ Architecture Overview

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

### 11 Interconnected Modules

| # | Module | Purpose |
|---|--------|---------|
| 1 | **Color/ANSI** | Terminal output formatting with 16-color palette |
| 2 | **Principal Strategist** | Clinical-tone persona with observations & consequences |
| 3 | **MockExchangeServer** | Threaded HTTP server simulating 5 symbols |
| 4 | **MockPriceGenerator** | Realistic bid/ask spread generation |
| 5 | **LedgerEngine** | Double-entry SQLite with 9 accounts |
| 6 | **CodeAuditor** | `ast`-based static analysis (9 check categories) |
| 7 | **StateManager** | JSON persistence for 90-day progression |
| 8 | **WorkspaceGenerator** | Per-day file generation (briefing + boilerplate + tests) |
| 9 | **EvaluationEngine** | Subprocess test runner + scoring |
| 10 | **ArbitrageAcademyCLI** | `cmd.Cmd` with 10 commands |
| 11 | **WebUIServer** | Threaded HTTP dashboard with live polling |

---

## 📸 Screenshots

### Web Dashboard — Live Market Feed & Controls
```
┌──────────────────────────────────────────────────────────────────┐
│  NovaCap Principal Strategist          ● Day 1      Phase 1     │
├──────────────────────────────────────────────────────────────────┤
│  BTC/USD $67,306.92  ETH/USDT $3,146.82  BTC/USDT $68,188.97   │
├──────────────────────────────────────────────────────────────────┤
│  ╔════════════╗ ╔════════════╗ ╔════════════╗ ╔══════════════╗  │
│  ║ Current Day║ ║   Phase   ║ ║Days Passed ║ ║Cum. Score    ║  │
│  ║   1 / 90   ║ ║Data Ingest║ ║     0      ║ ║   0.0%      ║  │
│  ╚════════════╝ ╚════════════╝ ╚════════════╝ ╚══════════════╝  │
│  [▶ Start Day] [⛔ EOD] [▶ Run] [→ Advance]                     │
└──────────────────────────────────────────────────────────────────┘
```

### Mock Exchange REST API — Live Order Book
```
GET /v1/ticker?symbol=BTC/USD
{
  "symbol": "BTC/USD",
  "price": 67306.92,
  "change_24h_pct": -4.07,
  "volume_24h": 5739.1,
  "timestamp": "2026-06-18T22:53:26"
}

GET /v1/orderbook?symbol=ETH/USDT
  ▲ Bids                  ▼ Asks
  3,142.89  40.45         3,151.16  40.45
  3,136.60  33.69         3,157.46  33.69
  3,130.32  22.72         3,163.76  22.72
  ─── Spread: 8.27 ───
```

### SQLite Ledger — Double-Entry Bookkeeping
```
Code    Name                  Type       Balance
1000    Cash - USD            asset    $100,000.00
1100    BTC Wallet            asset         0.50 BTC
4000    Revenue - Trading     revenue    $1,245.30
5000    Fees Paid             expense      $33.72
─────────────────────────────────────────────────
✓ Double-entry balanced  |  Trades logged: 1
```

### AST Static Code Audit
```
● CRITICAL  L5  Missing try-except on urllib.request.urlopen()
● WARNING   L11 O(n²) nested loop: for i in range(len(prices))
● INFO      L4  Missing type annotation for parameter 'url'
● CRITICAL  L3  Use of eval() detected — security risk
────────────────────────────────────────────────────────
Complexity Score: 14 | 4 critical, 1 warning, 2 info
```

---

## 🚀 Getting Started

```bash
# Download the script
python arbitrage_academy.py

# Output:
#   [✓] Web Dashboard: http://localhost:8081
#   ╔══════════════════════════════════════════╗
#   ║         PRINCIPAL STRATEGIST             ║
#   ╚══════════════════════════════════════════╝
#   WELCOME, TRAINEE.
#   Type "start" to begin Day 1.
```

### CLI Commands

| Command | Action |
|---------|--------|
| `start` | Begin current day (launches exchange + workspace) |
| `eod` | Trigger End-of-Day evaluation |
| `advance` | Move to next day (requires score 100) |
| `run` | Execute your solution file |
| `audit` | Run AST code audit on your solution |
| `ledger` | View account balances and trades |
| `exchange` | Check exchange server status |
| `status` | Show training progress summary |
| `reset` | Reset state back to Day 1 |
| `help` | Show command help |

---

## 📋 Requirements

- **Python 3.8 or later** (3.11+ recommended for best f-string support)
- **No pip packages** — uses `cmd`, `http.server`, `sqlite3`, `ast`, `threading`, `json`, `urllib`, `subprocess`, and other stdlib modules
- **Port 8080** (Mock Exchange) and **8081** (Web Dashboard) must be free

---

## 📜 License

This project is **MIT licensed** — see [`EULA.md`](EULA.md) for the full text.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software under the MIT terms.

---

## ❓ FAQ

**Q: Do I need to install anything?**
A: No. Python 3.8+ ships with everything required.

**Q: Is this a course or a tool?**
A: Both. It's a simulator that generates 90 days of progressive training exercises, evaluates your code, and won't let you advance unless you score 100.

**Q: Can I modify the curriculum?**
A: Days 1–3 are hand-crafted. Days 4–90 use procedural generation. You can modify the generator or add your own curricula.

**Q: Does it work on Windows/Mac/Linux?**
A: Yes. Tested on Python 3.8–3.13 on Windows, macOS, and Linux.

**Q: What if I find a bug?**
A: Open an issue on GitHub. The project is MIT licensed — community contributions and fixes are welcome.

---

## 🧑‍💻 About This Project

NovaCap is a **personal project** built at the intersection of Python engineering and quantitative finance. The "NovaCap Financial Technologies" name is part of the simulation's narrative — there's no company behind it, just a developer who wanted to build something challenging.

All trading data is synthetic. All standards referenced (CMA, SOCPA, IFRS) are real professional accounting frameworks used to structure realistic compliance scenarios.

---

*Built with Python standard library. No dependencies. No shortcuts.*
