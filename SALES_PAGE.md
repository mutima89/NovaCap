# Principal Strategist — 90-Day FinTech Arbitrage Simulator

> **A ruthless Python training simulation. Write code. Execute trades. Survive the audit.**

---

## The Pitch

You're a FinTech Arbitrage Specialist at NovaCap Financial. The year is 2026. You have
90 days to prove you can build, execute, and audit algorithmic trading systems — or
you're out.

This is not a video course. This is not a tutorial. This is a **simulation** that
generates daily trading challenges, evaluates your code with AST static analysis, runs
hidden test suites, and **will not let you advance until you score 100**.

## What Makes This Different

| Other Training | Principal Strategist |
|----------------|---------------------|
| Watch videos | Write code under pressure |
| Drag-and-drop UI | Real Python against a live exchange |
| Multiple-choice quizzes | AST code audits + hidden test suites |
| Self-paced, no standards | CMA/SOCPA/IFRS compliance enforced |
| "Good enough" to pass | Must score 100/100 to advance |
| Requires pip install | **Zero dependencies** — run it |

## What You Get

- **1 file** (`arbitrage_academy.py`) — ~4,000 lines of pure Python
- **90 days** of progressive training (Data Ingestion → Arbitrage Logic → SOCPA Compliance)
- **Live mock exchange** on `localhost:8080` with BTC, ETH, USDT, EUR/USD
- **Double-entry SQLite ledger** with full P&L tracking
- **AST static code auditor** — 9 check categories
- **EOD evaluation engine** — subprocess tests + ledger verification
- **Dark-themed web dashboard** on `localhost:8081`
- **CLI interface** with clinical Principal Strategist persona
- **Hand-crafted Days 1–3** + procedural generator for Days 4–90
- **Zero external dependencies** — Python 3.8+ stdlib only

## How It Works

```
START → Briefing → Write Code → Run → EOD → Score 100? → ADVANCE
                                ↑                          ↓
                           Fix violations ←── NO ←── Score < 100
```

Each day:
1. Type `start` — exchange launches, workspace generates, briefing appears
2. Write your solution in the generated boilerplate
3. Run it against the live exchange — fetch data, calculate, log to ledger
4. Type `eod` — AST audit → hidden tests → ledger verify → **score**
5. Score 100? Type `advance`. Score less? Fix your violations.

## Tech Specs

| Requirement | Detail |
|-------------|--------|
| Python | 3.8 – 3.13 |
| Dependencies | **Zero.** Zip file = `python arbitrage_academy.py` |
| Ports | 8080 (exchange) + 8081 (dashboard) |
| OS | Windows, macOS, Linux |
| Lines of code | ~4,000 in a single file |
| Total curriculum days | 90 with procedural fallback |

---

## License

This project is **MIT licensed** — free to use, modify, and distribute.
See [`EULA.md`](EULA.md) for the full license text.

---

## FAQ

**"Do I need to install anything?"**
No. Python 3.8+ ships with everything you need.

**"I'm a beginner. Is this for me?"**
It's challenging. Days 1–3 are accessible to intermediate Python devs. The difficulty
ramps significantly. If you can write functions with type annotations and handle
exceptions, you're ready.

**"Can I see it running?"**
Absolutely. Clone the repo and run `python arbitrage_academy.py` — the dashboard
appears on `http://localhost:8081` with a live exchange, ticker feed, and ledger.

**"Is this financial advice?"**
Absolutely not. All market data is synthetic. This is a code training simulator.

---

Get started: **[github.com/mutima89/NovaCap](https://github.com/mutima89/NovaCap)**
