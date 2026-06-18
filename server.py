#!/usr/bin/env python3
"""
NovaCap Financial Simulation — Web Server
Serves a browser-based GUI for the corporate finance daily simulation.

Usage:
    python server.py [port]

Then open http://localhost:8080 in your browser.
Requires: Python 3.8+ (standard library only)
"""

import json
import os
import sys
import urllib.parse
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional

# ── Import core simulation engine ──────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finance_sim import (
    SimulationState, TaskGenerator, EvaluationEngine,
    MarketDataGenerator, CompanyConfig, RoleConfig,
    TASK_DATABASE, BoxChars, Color, _USE_UNICODE,
)

# ==============================================================================
# GLOBAL SIMULATION STATE (persistent across requests)
# ==============================================================================
sim = SimulationState()
task_gen = TaskGenerator()
evaluator = EvaluationEngine()


# ==============================================================================
# HELPER: Clean ANSI / Unicode from text for JSON-serialisable output
# ==============================================================================
def clean_text(text: str) -> str:
    """Strip ANSI colour codes; replace common Unicode with ASCII."""
    text = Color.strip(text)
    if not _USE_UNICODE:
        replacements = {
            "\u2500": "-", "\u2502": "|", "\u250c": "+", "\u2510": "+",
            "\u2514": "+", "\u2518": "+", "\u251c": "+", "\u2524": "+",
            "\u2550": "=", "\u2551": "|", "\u2554": "+", "\u2557": "+",
            "\u255a": "+", "\u255d": "+", "\u25b8": ">", "\u2713": "v",
            "\u2717": "x", "\u2726": "*", "\u2600": "O",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
    return text


def json_state() -> Dict[str, Any]:
    """Return serialisable simulation state for the frontend."""
    return {
        "phase": sim.phase,
        "time": sim.current_time_str,
        "date": sim.simulation_date,
        "timeRemaining": sim.time_remaining_str(),
        "company": CompanyConfig.NAME,
        "role": RoleConfig.TITLE,
        "tasks": [
            {
                "id": t["id"],
                "title": t["title"],
                "category": t["category"],
                "categoryLabel": t["category_label"],
                "difficulty": t["difficulty"],
                "briefing": clean_text(t["briefing"]),
                "completed": t["id"] in sim.completed_task_ids,
            }
            for t in sim.tasks
        ],
        "completedIds": sim.completed_task_ids,
        "currentTaskId": sim.current_task_id,
        "allCompleted": sim.all_tasks_completed() if sim.tasks else False,
    }


# ==============================================================================
# HTTP REQUEST HANDLER
# ==============================================================================

class FinanceAPIHandler(BaseHTTPRequestHandler):

    # ── CORS helpers ────────────────────────────────────────────────────────
    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, msg: str, status: int = 400) -> None:
        self._send_json({"error": msg}, status)

    def _read_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    # ── Route dispatch ──────────────────────────────────────────────────────
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "" or path == "/":
            self._send_html(HTML_TEMPLATE)
        elif path == "/api/state":
            self._handle_get_state()
        elif path.startswith("/api/task/"):
            try:
                tid = int(path.split("/")[-1])
                self._handle_get_task(tid)
            except (ValueError, IndexError):
                self._send_error("Invalid task ID")
        else:
            self._send_error("Not found", 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        handlers = {
            "/api/start": self._handle_start,
            "/api/reset": self._handle_reset,
            "/api/eod": self._handle_eod,
        }

        if path in handlers:
            handlers[path]()
        elif path.startswith("/api/submit/"):
            try:
                tid = int(path.split("/")[-1])
                self._handle_submit(tid)
            except (ValueError, IndexError):
                self._send_error("Invalid task ID")
        elif path.startswith("/api/workon/"):
            try:
                tid = int(path.split("/")[-1])
                self._handle_workon(tid)
            except (ValueError, IndexError):
                self._send_error("Invalid task ID")
        else:
            self._send_error("Not found", 404)

    def do_OPTIONS(self):
        """CORS preflight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── API handlers ────────────────────────────────────────────────────────

    def _handle_get_state(self):
        data = json_state()
        if sim.market_briefing:
            data["briefing"] = sim.market_briefing
        if sim.phase == "complete" and evaluator.results:
            data["evaluationResults"] = [
                {
                    "taskId": r["task_id"],
                    "title": r["title"],
                    "score": r["score"],
                    "maxScore": r["max_score"],
                    "percentage": r["percentage"],
                    "grade": r["grade"],
                    "feedback": clean_text(r["feedback"]),
                    "criticalErrors": r.get("critical_errors", []),
                }
                for r in evaluator.results.values()
            ]
            data["overallScore"] = sum(r["score"] for r in evaluator.results.values())
            data["overallMax"] = sum(r["max_score"] for r in evaluator.results.values())
        self._send_json(data)

    def _handle_start(self):
        if sim.phase not in ("initialized", "complete"):
            self._send_error("Simulation already in progress. Use reset first.")
            return
        sim.reset()
        evaluator.reset()
        sim.market_briefing = MarketDataGenerator.generate_briefing()
        sim.tasks = task_gen.generate_daily_tasks()
        sim.phase = "working"
        self._send_json({
            "success": True,
            "state": json_state(),
            "briefing": sim.market_briefing,
        })

    def _handle_reset(self):
        sim.reset()
        evaluator.reset()
        self._send_json({"success": True, "state": json_state()})

    def _handle_workon(self, task_id: int):
        if sim.phase not in ("working", "briefing"):
            self._send_error("Simulation not started.")
            return
        task = next((t for t in sim.tasks if t["id"] == task_id), None)
        if not task:
            self._send_error(f"Task #{task_id} not found.")
            return
        if task_id in sim.completed_task_ids:
            self._send_error(f"Task #{task_id} already completed.")
            return
        sim.current_task_id = task_id
        sim.advance_time(10)
        self._send_json({
            "success": True,
            "task": {
                "id": task["id"],
                "title": task["title"],
                "category": task["category"],
                "categoryLabel": task["category_label"],
                "difficulty": task["difficulty"],
                "briefing": clean_text(task["briefing"]),
                "description": clean_text(task["description"]),
                "dataProvided": task["data_provided"],
                "keyConcepts": task["key_concepts"],
            },
            "state": json_state(),
        })

    def _handle_submit(self, task_id: int):
        if sim.current_task_id != task_id:
            self._send_error("Not the active task. Use workon first.")
            return
        body = self._read_body()
        answer = body.get("answer", "").strip()
        if not answer:
            self._send_error("Answer cannot be empty.")
            return
        sim.submit_answer(task_id, answer)
        sim.advance_time(20)
        sim.current_task_id = None

        resp = {"success": True, "state": json_state()}

        # If all done, suggest EOD
        if sim.all_tasks_completed():
            resp["message"] = "All tasks completed! Click 'End of Day' for evaluation."

        self._send_json(resp)

    def _handle_eod(self):
        if sim.phase not in ("working", "briefing"):
            self._send_error("Simulation not in progress.")
            return
        if not sim.tasks:
            self._send_error("No tasks assigned.")
            return

        # Auto-submit empty for pending tasks
        for task in sim.get_pending_tasks():
            if task["id"] not in sim.answers:
                sim.answers[task["id"]] = "[NO ANSWER SUBMITTED]"
            if task["id"] not in sim.completed_task_ids:
                sim.completed_task_ids.append(task["id"])

        sim.phase = "eod"
        sim.current_time_minutes = SimulationState.DAY_END_HOUR * 60

        # Run evaluation
        results = []
        for task in sim.tasks:
            user_answer = sim.answers.get(task["id"], "[NO ANSWER]")
            result = evaluator.evaluate(task, user_answer)
            results.append(result)

        sim.phase = "complete"
        sim.evaluation_results = results

        # Build report
        report = evaluator.generate_variance_report(results)
        report_clean = clean_text(report)

        self._send_json({
            "success": True,
            "results": [
                {
                    "taskId": r["task_id"],
                    "title": r["title"],
                    "score": r["score"],
                    "maxScore": r["max_score"],
                    "percentage": r["percentage"],
                    "grade": r["grade"],
                    "feedback": clean_text(r["feedback"]),
                    "criticalErrors": r.get("critical_errors", []),
                    "expected": clean_text(r["expected"]),
                    "userAnswer": clean_text(r["user_answer"]),
                    "checks": [
                        {
                            "desc": c["description"],
                            "earned": c["points_earned"],
                            "possible": c["points_possible"],
                            "passed": c["passed"],
                            "partial": c["partial"],
                        }
                        for c in r["checks"]
                    ],
                }
                for r in results
            ],
            "report": report_clean,
            "overallScore": sum(r["score"] for r in results),
            "overallMax": sum(r["max_score"] for r in results),
            "overallGrade": (
                "A" if (sum(r["score"] for r in results) / max(1, sum(r["max_score"] for r in results)) * 100) >= 90 else
                "B" if (sum(r["score"] for r in results) / max(1, sum(r["max_score"] for r in results)) * 100) >= 80 else
                "C" if (sum(r["score"] for r in results) / max(1, sum(r["max_score"] for r in results)) * 100) >= 70 else
                "D" if (sum(r["score"] for r in results) / max(1, sum(r["max_score"] for r in results)) * 100) >= 60 else
                "F"
            ),
            "state": json_state(),
        })


# ==============================================================================
# HTML / CSS / JS FRONTEND (single-page application, embedded)
# ==============================================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NovaCap Financial Simulation</title>
<style>
  /* ── Reset & Base ──────────────────────────────────────────── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; overflow: hidden; }
  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    background: #0a0e17;
    color: #c8d6e5;
    font-size: 14px;
    line-height: 1.5;
    display: flex;
    flex-direction: column;
  }
  a { color: #54a0ff; text-decoration: none; }
  a:hover { text-decoration: underline; }

  /* ── Scrollbar ─────────────────────────────────────────────── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #0d1520; }
  ::-webkit-scrollbar-thumb { background: #2d3a4a; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #3d4a5a; }

  /* ── Header ────────────────────────────────────────────────── */
  .header {
    background: linear-gradient(135deg, #0f1a2e 0%, #162032 100%);
    border-bottom: 1px solid #1e3a5f;
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
    z-index: 10;
  }
  .header-left { display: flex; align-items: center; gap: 16px; }
  .header-logo {
    font-size: 18px; font-weight: 700;
    background: linear-gradient(135deg, #48dbfb, #0abde3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .header-role { color: #8395a7; font-size: 12px; }
  .header-right { display: flex; align-items: center; gap: 20px; }
  .header-time {
    font-size: 20px; font-weight: 600; color: #48dbfb;
    font-variant-numeric: tabular-nums;
  }
  .header-status {
    padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .status-ready { background: #1a3a2a; color: #2ecc71; border: 1px solid #2ecc7144; }
  .status-working { background: #1a2a3a; color: #48dbfb; border: 1px solid #48dbfb44; }
  .status-complete { background: #2a1a1a; color: #ff6b6b; border: 1px solid #ff6b6b44; }

  /* ── Main Layout ───────────────────────────────────────────── */
  .main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  /* ── Sidebar ───────────────────────────────────────────────── */
  .sidebar {
    width: 280px;
    min-width: 280px;
    background: #0d1520;
    border-right: 1px solid #1a2a3a;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .sidebar-title {
    padding: 16px 16px 8px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #576574;
    font-weight: 600;
  }
  .sidebar-tasks {
    flex: 1;
    overflow-y: auto;
    padding: 4px 8px;
  }
  .task-card {
    padding: 12px 14px;
    margin: 4px 0;
    border-radius: 8px;
    cursor: pointer;
    background: #111e2f;
    border: 1px solid #1a2a3a;
    transition: all 0.2s;
    position: relative;
  }
  .task-card:hover { background: #162438; border-color: #2d4a6a; }
  .task-card.active { border-color: #48dbfb; box-shadow: 0 0 12px #48dbfb22; }
  .task-card.completed { opacity: 0.6; }
  .task-card.completed::after {
    content: '';
    position: absolute; top: 8px; right: 8px;
    width: 8px; height: 8px; border-radius: 50%;
    background: #2ecc71;
  }
  .task-card-cat {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;
    font-weight: 600; margin-bottom: 4px;
  }
  .cat-quantitative { color: #54a0ff; }
  .cat-corporate_finance { color: #2ecc71; }
  .cat-risk_compliance { color: #feca57; }
  .task-card-title { font-size: 13px; font-weight: 500; color: #dfe6e9; }
  .task-card-diff {
    font-size: 10px; color: #576574; margin-top: 4px;
  }
  .diff-easy { color: #2ecc71; }
  .diff-medium { color: #feca57; }
  .diff-hard { color: #ff6b6b; }

  .sidebar-footer {
    padding: 12px 16px;
    border-top: 1px solid #1a2a3a;
    font-size: 11px;
    color: #576574;
  }

  /* ── Content Area ──────────────────────────────────────────── */
  .content {
    flex: 1;
    overflow-y: auto;
    padding: 24px 32px;
    background: #0a0e17;
  }

  /* ── Panels / Cards ────────────────────────────────────────── */
  .panel {
    background: #111e2f;
    border: 1px solid #1a2a3a;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
  }
  .panel-title {
    font-size: 16px; font-weight: 600; color: #dfe6e9;
    margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
  }
  .panel-title .accent { color: #48dbfb; }
  .panel-subtitle {
    font-size: 12px; color: #576574; margin-bottom: 12px;
  }
  .data-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
  }
  .data-item {
    background: #0a1525; padding: 12px 16px; border-radius: 8px;
    border: 1px solid #152535;
  }
  .data-item .label { font-size: 11px; color: #576574; text-transform: uppercase; letter-spacing: 0.5px; }
  .data-item .value { font-size: 18px; font-weight: 600; color: #dfe6e9; margin-top: 4px; }
  .data-item .value.positive { color: #2ecc71; }
  .data-item .value.negative { color: #ff6b6b; }
  .data-item .value.crypto { color: #feca57; }

  .event-list { list-style: none; margin-top: 8px; }
  .event-list li {
    padding: 8px 12px; margin: 4px 0;
    background: #0a1525; border-radius: 6px;
    border-left: 3px solid #48dbfb;
    font-size: 13px; color: #c8d6e5;
  }

  /* ── Buttons ───────────────────────────────────────────────── */
  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 24px; border-radius: 8px; border: none;
    font-size: 14px; font-weight: 600; cursor: pointer;
    transition: all 0.2s;
  }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-primary {
    background: linear-gradient(135deg, #0abde3, #48dbfb);
    color: #0a0e17;
  }
  .btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px #0abde344; }
  .btn-danger {
    background: linear-gradient(135deg, #ee5a24, #ff6b6b);
    color: #fff;
  }
  .btn-danger:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px #ee5a2444; }
  .btn-secondary {
    background: #1a2a3a; color: #c8d6e5; border: 1px solid #2d3a4a;
  }
  .btn-secondary:hover:not(:disabled) { background: #243548; }
  .btn-success {
    background: linear-gradient(135deg, #00b894, #2ecc71);
    color: #fff;
  }
  .btn-sm { padding: 6px 14px; font-size: 12px; }
  .btn-group { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px; }

  /* ── Task Detail ───────────────────────────────────────────── */
  .task-detail-section { margin-bottom: 20px; }
  .task-detail-section h3 {
    font-size: 13px; color: #48dbfb; text-transform: uppercase;
    letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;
  }
  .task-detail-section p, .task-detail-section div { color: #c8d6e5; font-size: 13px; line-height: 1.7; }
  .data-block {
    background: #0a1525; padding: 16px; border-radius: 8px;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 12px; color: #8395a7; white-space: pre-wrap;
    max-height: 400px; overflow: auto; border: 1px solid #152535;
  }

  textarea.answer-input {
    width: 100%; min-height: 160px;
    background: #0a1525; color: #dfe6e9; border: 1px solid #2d3a4a;
    border-radius: 8px; padding: 14px; font-family: inherit;
    font-size: 13px; line-height: 1.6; resize: vertical;
    transition: border-color 0.2s;
  }
  textarea.answer-input:focus { outline: none; border-color: #48dbfb; }

  /* ── Welcome Screen ────────────────────────────────────────── */
  .welcome {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; min-height: 60vh; text-align: center;
  }
  .welcome h1 {
    font-size: 28px; font-weight: 700; margin-bottom: 8px;
    background: linear-gradient(135deg, #48dbfb, #0abde3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .welcome .subtitle { color: #576574; font-size: 15px; margin-bottom: 32px; max-width: 480px; }
  .welcome .details {
    color: #8395a7; font-size: 13px; margin-bottom: 32px; max-width: 500px;
    line-height: 1.8;
  }

  /* ── EOD Report ────────────────────────────────────────────── */
  .result-card {
    background: #0a1525; border: 1px solid #152535; border-radius: 10px;
    padding: 20px; margin-bottom: 16px;
  }
  .result-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 12px;
  }
  .result-title { font-size: 15px; font-weight: 600; color: #dfe6e9; }
  .result-grade {
    font-size: 24px; font-weight: 700; padding: 4px 12px;
    border-radius: 8px;
  }
  .grade-A { color: #2ecc71; background: #2ecc7122; }
  .grade-B { color: #48dbfb; background: #48dbfb22; }
  .grade-C { color: #feca57; background: #feca5722; }
  .grade-D { color: #feca57; background: #feca5722; }
  .grade-F { color: #ff6b6b; background: #ff6b6b22; }

  .result-score { font-size: 14px; color: #8395a7; }
  .result-score strong { color: #dfe6e9; }
  .result-feedback { font-size: 13px; color: #c8d6e5; line-height: 1.7; white-space: pre-wrap; margin-top: 8px; }
  .result-expected, .result-user {
    margin-top: 12px; padding: 12px; border-radius: 8px; font-size: 12px;
    white-space: pre-wrap; max-height: 200px; overflow: auto;
  }
  .result-expected { background: #0a1a1a; border: 1px solid #2ecc7122; color: #55efc4; }
  .result-user { background: #1a0a0a; border: 1px solid #ff6b6b22; color: #fab1a0; }

  .result-critical {
    margin-top: 8px; padding: 8px 12px; background: #2a1a1a;
    border-left: 3px solid #ff6b6b; border-radius: 4px;
    color: #ff6b6b; font-size: 12px; font-weight: 600;
  }

  .checks-list { margin-top: 8px; }
  .check-item {
    display: flex; align-items: center; gap: 8px;
    padding: 4px 0; font-size: 12px; color: #8395a7;
  }
  .check-pass { color: #2ecc71; }
  .check-partial { color: #feca57; }
  .check-fail { color: #ff6b6b; }

  .overall-score {
    text-align: center; padding: 32px; margin-bottom: 20px;
  }
  .overall-score .big-number {
    font-size: 56px; font-weight: 700;
    background: linear-gradient(135deg, #48dbfb, #0abde3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .overall-score .big-label { font-size: 16px; color: #576574; margin-top: 4px; }

  .competency-map {
    background: #0a1525; border: 1px solid #152535; border-radius: 10px;
    padding: 20px; margin-top: 20px;
  }
  .competency-map h3 { color: #48dbfb; font-size: 13px; text-transform: uppercase; margin-bottom: 12px; }
  .competency-map li { padding: 4px 0; font-size: 13px; color: #8395a7; }

  .report-raw {
    margin-top: 16px; padding: 16px; background: #0a1525;
    border: 1px solid #152535; border-radius: 8px;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 12px; color: #8395a7; white-space: pre-wrap;
    max-height: 500px; overflow: auto;
  }

  /* ── Loading / States ──────────────────────────────────────── */
  .loading { text-align: center; padding: 60px; color: #576574; }
  .loading .spinner {
    display: inline-block; width: 32px; height: 32px;
    border: 3px solid #1a2a3a; border-top-color: #48dbfb;
    border-radius: 50%; animation: spin 0.8s linear infinite;
    margin-bottom: 12px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .empty-state { text-align: center; padding: 40px; color: #576574; }
  .error-state { text-align: center; padding: 40px; color: #ff6b6b; }

  /* ── Notification Toast ────────────────────────────────────── */
  .toast {
    position: fixed; bottom: 24px; right: 24px;
    padding: 12px 20px; border-radius: 8px; font-size: 13px; font-weight: 500;
    z-index: 1000; transform: translateY(80px); opacity: 0;
    transition: all 0.3s ease;
    max-width: 400px;
  }
  .toast.show { transform: translateY(0); opacity: 1; }
  .toast-success { background: #00b894; color: #fff; }
  .toast-error { background: #d63031; color: #fff; }
  .toast-info { background: #1a2a3a; color: #c8d6e5; border: 1px solid #2d3a4a; }

  /* ── Responsive ────────────────────────────────────────────── */
  @media (max-width: 768px) {
    .sidebar { display: none; }
    .content { padding: 16px; }
    .data-grid { grid-template-columns: 1fr; }
    .header { padding: 10px 16px; flex-wrap: wrap; gap: 8px; }
    .header-role { display: none; }
  }

  /* ── Misc ──────────────────────────────────────────────────── */
  .flex { display: flex; }
  .flex-col { flex-direction: column; }
  .gap-8 { gap: 8px; }
  .gap-16 { gap: 16px; }
  .mt-8 { margin-top: 8px; }
  .mt-16 { margin-top: 16px; }
  .mb-16 { margin-bottom: 16px; }
  .text-center { text-align: center; }
  .text-muted { color: #576574; }
  .text-accent { color: #48dbfb; }
  .tag {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
  }
  .tag-easy { background: #2ecc7122; color: #2ecc71; }
  .tag-medium { background: #feca5722; color: #feca57; }
  .tag-hard { background: #ff6b6b22; color: #ff6b6b; }

  .concept-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
  .concept-chip {
    padding: 3px 10px; border-radius: 12px; font-size: 11px;
    background: #1a2a3a; color: #8395a7; border: 1px solid #2d3a4a;
  }
</style>
</head>
<body>

<!-- ── Header ────────────────────────────────────────────────── -->
<header class="header">
  <div class="header-left">
    <div class="header-logo">NovaCap Financial</div>
    <span class="header-role">Financial Analyst — FinTech Arbitrage</span>
  </div>
  <div class="header-right">
    <span id="headerStatus" class="header-status status-ready">Ready</span>
    <span id="headerTime" class="header-time">09:00</span>
  </div>
</header>

<!-- ── Main ──────────────────────────────────────────────────── -->
<div class="main">

  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-title">Today's Tasks</div>
    <div id="taskList" class="sidebar-tasks">
      <div class="empty-state">No tasks yet.<br>Click "Start Day" to begin.</div>
    </div>
    <div class="sidebar-footer" id="sidebarFooter">
      <div id="timeRemaining" style="margin-bottom:8px; color:#576574; font-size:12px;"></div>
      <button id="btnStart" class="btn btn-primary btn-sm" style="width:100%" onclick="startDay()">Start Day</button>
      <button id="btnEOD" class="btn btn-danger btn-sm" style="width:100%;margin-top:6px;display:none" onclick="endDay()">End of Day (EOD)</button>
      <button id="btnReset" class="btn btn-secondary btn-sm" style="width:100%;margin-top:6px;display:none" onclick="resetSim()">New Day</button>
    </div>
  </aside>

  <!-- Content -->
  <main class="content" id="mainContent">
    <div class="welcome" id="welcomeScreen">
      <h1>NovaCap Financial Technologies</h1>
      <p class="subtitle">Corporate Finance Daily Simulation Environment</p>
      <div class="details">
        <strong>Role:</strong> Financial Analyst — FinTech Arbitrage Specialist<br>
        <strong>Standards:</strong> CMA Framework | SOCPA Compliance | IFRS Reporting<br>
        <strong>Location:</strong> Dubai International Financial Centre (DIFC)
      </div>
      <button class="btn btn-primary" onclick="startDay()">Start Your Day</button>
      <div style="margin-top:12px;font-size:12px;color:#576574;">
        Tasks will be randomly selected from 10 pre-defined scenarios across 3 categories.
      </div>
    </div>

    <div id="appContent" style="display:none;">
      <!-- Dynamic content rendered by JS -->
    </div>
  </main>

</div>

<!-- ── Toast ──────────────────────────────────────────────────── -->
<div id="toast" class="toast"></div>

<!-- ── JavaScript ─────────────────────────────────────────────── -->
<script>
// ═══════════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════════
let appState = { phase: 'initialized', tasks: [], briefing: null };
let currentTaskId = null;

// ═══════════════════════════════════════════════════════════════════
// API HELPER
// ═══════════════════════════════════════════════════════════════════
async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const resp = await fetch(path, opts);
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || 'Request failed');
  return data;
}

// ═══════════════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════════
let toastTimer = null;
function showToast(msg, type = 'info') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast toast-' + type + ' show';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 4000);
}

// ═══════════════════════════════════════════════════════════════════
// FORMAT HELPERS
// ═══════════════════════════════════════════════════════════════════
function catLabel(cat) {
  return { quantitative: 'QUANT', corporate_finance: 'CORP FIN', risk_compliance: 'RISK/COMP' }[cat] || cat;
}
function catColor(cat) {
  return { quantitative: '#54a0ff', corporate_finance: '#2ecc71', risk_compliance: '#feca57' }[cat] || '#8395a7';
}
function diffLabel(d) { return d ? d.toUpperCase() : ''; }
function pctColor(val) { return val >= 0 ? '#2ecc71' : '#ff6b6b'; }
function pctStr(val) { return (val >= 0 ? '+' : '') + val.toFixed(2) + '%'; }

// ═══════════════════════════════════════════════════════════════════
// RENDER: HEADER
// ═══════════════════════════════════════════════════════════════════
function updateHeader(state) {
  document.getElementById('headerTime').textContent = state.time || '09:00';
  const statusEl = document.getElementById('headerStatus');
  if (state.phase === 'initialized') {
    statusEl.textContent = 'Ready';
    statusEl.className = 'header-status status-ready';
  } else if (state.phase === 'working' || state.phase === 'briefing') {
    statusEl.textContent = 'In Progress';
    statusEl.className = 'header-status status-working';
  } else if (state.phase === 'complete') {
    statusEl.textContent = 'Complete';
    statusEl.className = 'header-status status-complete';
  }
}

// ═══════════════════════════════════════════════════════════════════
// RENDER: SIDEBAR
// ═══════════════════════════════════════════════════════════════════
function renderSidebar(state) {
  const list = document.getElementById('taskList');
  const footer = document.getElementById('sidebarFooter');
  const timeRem = document.getElementById('timeRemaining');

  if (state.phase === 'initialized') {
    list.innerHTML = '<div class="empty-state">No tasks yet.<br>Click "Start Day" to begin.</div>';
    document.getElementById('btnStart').style.display = 'block';
    document.getElementById('btnEOD').style.display = 'none';
    document.getElementById('btnReset').style.display = 'none';
    timeRem.textContent = '';
    return;
  }

  timeRem.textContent = state.timeRemaining || '';

  document.getElementById('btnStart').style.display = 'none';
  document.getElementById('btnEOD').style.display = (state.phase === 'working' || state.phase === 'briefing') ? 'block' : 'none';
  document.getElementById('btnReset').style.display = (state.phase !== 'initialized') ? 'block' : 'none';

  if (!state.tasks || state.tasks.length === 0) {
    list.innerHTML = '<div class="empty-state">No tasks assigned.</div>';
    return;
  }

  let html = '';
  state.tasks.forEach(t => {
    const active = (t.id === currentTaskId) ? ' active' : '';
    const done = t.completed ? ' completed' : '';
    html += `
      <div class="task-card${active}${done}" onclick="workOn(${t.id})">
        <div class="task-card-cat cat-${t.category}">${catLabel(t.category)}</div>
        <div class="task-card-title">${escHtml(t.title)}</div>
        <div class="task-card-diff"><span class="diff-${t.difficulty}">${diffLabel(t.difficulty)}</span></div>
      </div>`;
  });
  list.innerHTML = html;
}

// ═══════════════════════════════════════════════════════════════════
// RENDER: BRIEFING
// ═══════════════════════════════════════════════════════════════════
function renderBriefing(briefing) {
  const container = document.getElementById('appContent');
  if (!briefing) {
    container.innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading briefing...</div></div>';
    return;
  }

  const sp = briefing.indices['S&P 500'];
  const nas = briefing.indices['NASDAQ 100'];
  const btc = briefing.crypto['BTC/USD'];
  const eth = briefing.crypto['ETH/USD'];

  let eventsHtml = '';
  (briefing.key_events || []).forEach(e => {
    eventsHtml += `<li>${escHtml(e)}</li>`;
  });

  container.innerHTML = `
    <div class="panel">
      <div class="panel-title"><span class="accent">&#9728;</span> Morning Briefing &mdash; ${escHtml(briefing.date)}</div>
      <div class="panel-subtitle">${escHtml(briefing.session)}</div>

      <div class="data-grid">
        <div class="data-item">
          <div class="label">S&P 500</div>
          <div class="value ${sp.change_pct >= 0 ? 'positive' : 'negative'}">${sp.level.toLocaleString()}</div>
          <div style="font-size:12px;color:#576574">${pctStr(sp.change_pct)}</div>
        </div>
        <div class="data-item">
          <div class="label">NASDAQ 100</div>
          <div class="value ${nas.change_pct >= 0 ? 'positive' : 'negative'}">${nas.level.toLocaleString()}</div>
          <div style="font-size:12px;color:#576574">${pctStr(nas.change_pct)}</div>
        </div>
        <div class="data-item">
          <div class="label">BTC/USD</div>
          <div class="value crypto">$${btc.level.toLocaleString()}</div>
          <div style="font-size:12px;color:#576574">${pctStr(btc.change_pct)}</div>
        </div>
        <div class="data-item">
          <div class="label">ETH/USD</div>
          <div class="value crypto">$${eth.level.toLocaleString()}</div>
          <div style="font-size:12px;color:#576574">${pctStr(eth.change_pct)}</div>
        </div>
        <div class="data-item">
          <div class="label">EUR/USD</div>
          <div class="value">${briefing.fx['EUR/USD']}</div>
        </div>
        <div class="data-item">
          <div class="label">VIX</div>
          <div class="value" style="color:#feca57">${briefing.volatility.VIX}</div>
        </div>
        <div class="data-item">
          <div class="label">10Y Treasury</div>
          <div class="value" style="color:#feca57">${briefing.volatility['10Y Treasury Yield']}</div>
        </div>
      </div>

      <div style="margin-top:20px">
        <div class="panel-subtitle" style="margin-bottom:6px">Key Macro Events</div>
        <ul class="event-list">${eventsHtml}</ul>
      </div>
    </div>

    <div class="panel">
      <div class="panel-title"><span class="accent">&#128232;</span> Inbox &mdash; ${appState.tasks.length} New Tasks</div>
      <div class="panel-subtitle">Select a task from the sidebar to begin working.</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;margin-top:8px">
        ${appState.tasks.map(t => `
          <div style="background:#0a1525;border:1px solid #152535;border-radius:8px;padding:14px;cursor:pointer" onclick="workOn(${t.id})">
            <div style="font-size:10px;text-transform:uppercase;color:${catColor(t.category)};font-weight:600;letter-spacing:0.5px">${catLabel(t.category)}</div>
            <div style="font-size:13px;font-weight:500;color:#dfe6e9;margin:4px 0">${escHtml(t.title)}</div>
            <div style="font-size:11px;color:#576574;display:flex;justify-content:space-between">
              <span>#${t.id}</span>
              <span style="color:${t.difficulty === 'easy' ? '#2ecc71' : t.difficulty === 'medium' ? '#feca57' : '#ff6b6b'}">${diffLabel(t.difficulty)}</span>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════════════
// RENDER: TASK DETAIL
// ═══════════════════════════════════════════════════════════════════
function renderTaskDetail(task) {
  currentTaskId = task.id;
  const container = document.getElementById('appContent');

  let conceptsHtml = '';
  (task.keyConcepts || []).forEach(c => {
    conceptsHtml += `<span class="concept-chip">${escHtml(c)}</span>`;
  });

  container.innerHTML = `
    <div class="panel">
      <div class="panel-title" style="justify-content:space-between;flex-wrap:wrap">
        <span><span style="color:${catColor(task.category)}">[${catLabel(task.category)}]</span> Task #${task.id}: ${escHtml(task.title)}</span>
        <span><span class="tag tag-${task.difficulty}">${diffLabel(task.difficulty)}</span></span>
      </div>
      <div class="panel-subtitle">${escHtml(task.categoryLabel)}</div>

      <div class="task-detail-section">
        <h3>Context</h3>
        <p>${escHtml(task.briefing)}</p>
      </div>

      <div class="task-detail-section">
        <h3>Task</h3>
        <div>${escHtml(task.description).replace(/\\n/g, '<br>')}</div>
      </div>

      <div class="task-detail-section">
        <h3>Data</h3>
        <div class="data-block">${escHtml(task.dataProvided)}</div>
      </div>

      ${conceptsHtml ? `<div class="task-detail-section"><h3>Key Concepts</h3><div class="concept-chips">${conceptsHtml}</div></div>` : ''}
    </div>

    <div class="panel">
      <div class="panel-title"><span class="accent">&#9997;</span> Your Analysis</div>
      <div class="panel-subtitle">Submit your detailed analysis. Include calculations, reasoning, and conclusions.</div>
      <textarea id="answerInput" class="answer-input" placeholder="Enter your analysis here... Include key numbers, methodology, and conclusions."></textarea>
      <div class="btn-group">
        <button class="btn btn-success" onclick="submitAnswer(${task.id})">Submit Answer</button>
        <button class="btn btn-secondary" onclick="backToBriefing()">Back to Tasks</button>
      </div>
    </div>
  `;

  // Update sidebar active state
  renderSidebar(appState);
}

// ═══════════════════════════════════════════════════════════════════
// RENDER: EOD REPORT
// ═══════════════════════════════════════════════════════════════════
function renderEODReport(data) {
  const container = document.getElementById('appContent');
  const results = data.results || [];
  const overall = data.overallScore || 0;
  const overallMax = data.overallMax || 1;
  const pct = (overall / overallMax * 100);

  let resultsHtml = '';
  results.forEach(r => {
    const gradeClass = 'grade-' + r.grade;
    let checksHtml = '';
    (r.checks || []).forEach(c => {
      const cls = c.passed ? 'check-pass' : (c.partial ? 'check-partial' : 'check-fail');
      const icon = c.passed ? '\u2713' : (c.partial ? '~' : '\u2717');
      checksHtml += `<div class="check-item ${cls}"><span>${icon}</span> ${escHtml(c.desc)}: ${c.earned}/${c.possible}</div>`;
    });

    let criticalHtml = '';
    if (r.criticalErrors && r.criticalErrors.length > 0) {
      criticalHtml = r.criticalErrors.map(e => `<div class="result-critical">!! ${escHtml(e)}</div>`).join('');
    }

    resultsHtml += `
      <div class="result-card">
        <div class="result-header">
          <div>
            <div class="result-title">${escHtml(r.title)}</div>
            <div class="result-score">Score: <strong>${r.score}</strong>/${r.maxScore} (${r.percentage.toFixed(0)}%)</div>
          </div>
          <div class="result-grade ${gradeClass}">${r.grade}</div>
        </div>
        ${criticalHtml}
        <div class="result-feedback">${escHtml(r.feedback)}</div>
        ${checksHtml ? `<div class="checks-list" style="margin-top:10px">${checksHtml}</div>` : ''}
        <div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div>
            <div style="font-size:11px;color:#576574;margin-bottom:4px;text-transform:uppercase">Expected Answer</div>
            <div class="result-expected">${escHtml(r.expected)}</div>
          </div>
          <div>
            <div style="font-size:11px;color:#576574;margin-bottom:4px;text-transform:uppercase">Your Answer</div>
            <div class="result-user">${escHtml(r.userAnswer)}</div>
          </div>
        </div>
      </div>`;
  });

  container.innerHTML = `
    <div class="panel overall-score">
      <div class="big-number">${pct.toFixed(1)}%</div>
      <div class="big-label">Overall Score: ${overall}/${overallMax} &mdash; Grade: ${data.overallGrade}</div>
      <div style="margin-top:16px;font-size:13px;color:#576574">
        Evaluation complete. Review each task below for detailed feedback.
      </div>
    </div>

    ${resultsHtml}

    <div class="competency-map">
      <h3>CMA / SOCPA Competency Mapping</h3>
      <ul>
        <li>Financial Statement Analysis (CMA Part 1 - Section C)</li>
        <li>Risk Management &amp; Internal Controls (CMA Part 1 - Section E)</li>
        <li>Quantitative Methods &amp; Decision Analysis (CMA Part 2 - Section A)</li>
        <li>Investment Decision Analysis (CMA Part 2 - Section D)</li>
        <li>SOCPA Audit &amp; Assurance Standards Compliance</li>
      </ul>
    </div>

    <div class="btn-group" style="margin-top:20px">
      <button class="btn btn-primary" onclick="resetSim()">Start New Day</button>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════════════
// ESCAPE HTML
// ═══════════════════════════════════════════════════════════════════
function escHtml(str) {
  if (!str) return '';
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

// ═══════════════════════════════════════════════════════════════════
// ACTIONS
// ═══════════════════════════════════════════════════════════════════
async function startDay() {
  try {
    document.getElementById('appContent').style.display = 'block';
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('appContent').innerHTML = '<div class="loading"><div class="spinner"></div><div>Generating market data and tasks...</div></div>';

    const data = await api('POST', '/api/start');
    appState = data.state;
    appState.briefing = data.briefing;
    appState.phase = 'working';
    currentTaskId = null;

    updateHeader(appState);
    renderSidebar(appState);
    renderBriefing(data.briefing);
    showToast('Day started! 3 tasks assigned. Select one from the sidebar.', 'success');
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
    document.getElementById('appContent').innerHTML = '<div class="error-state">Failed to start: ' + escHtml(e.message) + '</div>';
  }
}

async function workOn(taskId) {
  try {
    document.getElementById('appContent').innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading task...</div></div>';

    const data = await api('POST', '/api/workon/' + taskId);
    appState = data.state;
    appState.phase = 'working';
    currentTaskId = taskId;

    updateHeader(appState);
    renderSidebar(appState);
    renderTaskDetail(data.task);
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
    document.getElementById('appContent').innerHTML = '<div class="error-state">' + escHtml(e.message) + '</div>';
  }
}

async function submitAnswer(taskId) {
  const input = document.getElementById('answerInput');
  const answer = input ? input.value.trim() : '';
  if (!answer) {
    showToast('Please enter your analysis before submitting.', 'error');
    return;
  }

  try {
    document.getElementById('appContent').innerHTML = '<div class="loading"><div class="spinner"></div><div>Submitting answer...</div></div>';

    const data = await api('POST', '/api/submit/' + taskId, { answer });
    appState = data.state;

    if (data.message) {
      showToast(data.message, 'info');
    } else {
      showToast('Answer submitted successfully!', 'success');
    }

    currentTaskId = null;
    updateHeader(appState);
    renderSidebar(appState);

    // Refresh briefing view
    const stateData = await api('GET', '/api/state');
    appState = stateData;
    appState.phase = 'working';
    if (stateData.briefing) appState.briefing = stateData.briefing;
    renderBriefing(appState.briefing);

  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  }
}

async function endDay() {
  try {
    document.getElementById('appContent').innerHTML = '<div class="loading"><div class="spinner"></div><div>Running evaluation...</div></div>';

    const data = await api('POST', '/api/eod');
    appState.phase = 'complete';

    updateHeader(appState);
    renderSidebar(appState);
    renderEODReport(data);
    showToast('Evaluation complete! Review your results.', 'success');
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  }
}

async function resetSim() {
  try {
    document.getElementById('appContent').innerHTML = '<div class="loading"><div class="spinner"></div><div>Resetting...</div></div>';

    const data = await api('POST', '/api/reset');
    appState = data.state;
    appState.phase = 'initialized';
    currentTaskId = null;

    document.getElementById('appContent').style.display = 'none';
    document.getElementById('welcomeScreen').style.display = 'block';

    updateHeader(appState);
    renderSidebar(appState);
    showToast('Simulation reset. Ready for a new day.', 'info');
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  }
}

function backToBriefing() {
  currentTaskId = null;
  renderBriefing(appState.briefing);
  // Update sidebar active state
  const cards = document.querySelectorAll('.task-card');
  cards.forEach(c => c.classList.remove('active'));
}

// ═══════════════════════════════════════════════════════════════════
// INIT: auto-fetch state on load
// ═══════════════════════════════════════════════════════════════════
(async function init() {
  try {
    const data = await api('GET', '/api/state');
    appState = data;
    if (data.briefing) appState.briefing = data.briefing;
    updateHeader(appState);
    renderSidebar(appState);

    if (data.phase === 'working' || data.phase === 'briefing') {
      document.getElementById('appContent').style.display = 'block';
      document.getElementById('welcomeScreen').style.display = 'none';
      renderBriefing(data.briefing);
    } else if (data.phase === 'complete') {
      document.getElementById('appContent').style.display = 'block';
      document.getElementById('welcomeScreen').style.display = 'none';
      if (data.evaluationResults) {
        renderEODReport(data);
      }
    }
  } catch (e) {
    // Server just started, that's fine
  }
})();
</script>
</body>
</html>"""

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    server = HTTPServer(("", port), FinanceAPIHandler)
    print(f" " + "=" * 58)
    print(f"  NovaCap Financial Simulation — Web Server")
    print(f"  Open:  http://localhost:{port}")
    print(f"  Quit:  Ctrl+C")
    print(f" " + "=" * 58)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
