#!/usr/bin/env python3
"""Generate PDF versions of all documentation files using Microsoft Edge headless.

For .html files: converts directly via Edge print-to-pdf.
For .md files: wraps in dark-themed HTML template, then converts via Edge.
Outputs to docs/ directory and creates docs/index.html.
"""

import subprocess
import os
import sys
import markdown
import tempfile
import shutil
import glob

# ─── Configuration ───────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Verify Edge exists
if not os.path.isfile(EDGE_PATH):
    print(f"ERROR: Edge not found at {EDGE_PATH}")
    sys.exit(1)

# Map of source file → output PDF name
CONVERSIONS = [
    # (source_path_relative, type, output_pdf_name)
    ("promo.html",              "html", "promo.pdf"),
    ("PRODUCT.md",              "md",   "product.pdf"),
    ("SALES_PAGE.md",           "md",   "sales-page.pdf"),
    ("EULA.md",                 "md",   "eula.pdf"),
    ("TRAINING_PROGRAM.html",   "html", "training-program.pdf"),
    ("TRAINING_PROGRAM.md",     "md",   "training-program-md.pdf"),
    ("BEFORE_YOU_BEGIN.html",   "html", "before-you-begin.pdf"),
]

# ─── Dark Theme HTML Wrapper for Markdown Files ──────────────────────

DARK_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg-primary: #060a12;
    --bg-secondary: #0a0e17;
    --bg-card: #0f1525;
    --bg-code: #060a12;
    --border: #152030;
    --text-primary: #dfe6e9;
    --text-secondary: #8395a7;
    --text-muted: #4a5a6a;
    --accent-cyan: #48dbfb;
    --accent-blue: #0abde3;
    --accent-green: #2ecc71;
    --accent-red: #ff6b6b;
    --accent-gold: #feca57;
    --accent-purple: #a29bfe;
  }}
  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.7;
    padding: 40px 48px;
    max-width: 1000px;
    margin: 0 auto;
  }}
  h1 {{ font-size: 28px; font-weight: 800; color: var(--accent-cyan); margin: 32px 0 12px; letter-spacing: -0.5px; }}
  h2 {{ font-size: 22px; font-weight: 700; color: var(--accent-cyan); margin: 28px 0 10px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }}
  h3 {{ font-size: 18px; font-weight: 600; color: var(--text-primary); margin: 22px 0 8px; }}
  h4 {{ font-size: 15px; font-weight: 600; color: var(--text-secondary); margin: 18px 0 6px; }}
  p  {{ margin: 8px 0; color: var(--text-secondary); font-size: 14px; }}
  strong {{ color: var(--text-primary); }}
  em {{ color: var(--accent-cyan); }}
  a {{ color: var(--accent-cyan); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  blockquote {{
    border-left: 3px solid var(--accent-cyan);
    padding: 10px 16px;
    margin: 12px 0;
    background: var(--bg-card);
    border-radius: 0 6px 6px 0;
    color: var(--text-secondary);
    font-style: italic;
  }}
  blockquote strong {{ color: var(--accent-cyan); }}

  code {{
    font-family: 'JetBrains Mono', 'Consolas', 'Cascadia Code', monospace;
    background: var(--bg-code);
    color: var(--accent-green);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    border: 1px solid var(--border);
  }}
  pre {{
    background: var(--bg-code);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
    overflow-x: auto;
  }}
  pre code {{
    background: none;
    border: none;
    padding: 0;
    font-size: 12px;
    line-height: 1.6;
    color: var(--accent-green);
  }}

  hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 28px 0;
  }}

  ul, ol {{ margin: 8px 0; padding-left: 24px; }}
  li {{ color: var(--text-secondary); font-size: 14px; margin: 4px 0; }}
  li strong {{ color: var(--text-primary); }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 13px;
  }}
  th {{
    background: var(--bg-card);
    color: var(--accent-cyan);
    text-align: left;
    padding: 10px 12px;
    border: 1px solid var(--border);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 11px;
  }}
  td {{
    padding: 8px 12px;
    border: 1px solid var(--border);
    color: var(--text-secondary);
  }}
  tr:nth-child(even) {{ background: rgba(15, 21, 37, 0.4); }}

  img {{ max-width: 100%; border-radius: 6px; margin: 12px 0; }}

  .header-bar {{
    text-align: center;
    padding: 24px 0 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
  }}
  .header-bar .logo {{
    font-size: 18px;
    font-weight: 800;
    color: var(--accent-cyan);
    letter-spacing: 2px;
    text-transform: uppercase;
  }}
  .header-bar .sub {{
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 4px;
  }}
  .footer-bar {{
    text-align: center;
    padding: 20px 0;
    margin-top: 32px;
    border-top: 1px solid var(--border);
    font-size: 11px;
    color: var(--text-muted);
  }}
</style>
</head>
<body>
<div class="header-bar">
  <div class="logo">NovaCap Financial Technologies</div>
  <div class="sub">Principal Strategist — 90-Day FinTech Arbitrage Academy</div>
</div>
{content}
<div class="footer-bar">
  Generated by NovaCap Principal Strategist &mdash; Python Standard Library Only
</div>
</body>
</html>
"""


def md_to_html(md_content, title="Documentation"):
    """Convert Markdown content to dark-themed HTML."""
    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'tables', 'fenced_code']
    )
    # Wrap in dark template
    return DARK_TEMPLATE.format(title=title, content=html_body)


def convert_to_pdf(source_path, output_path):
    """Convert an HTML file to PDF using Microsoft Edge headless."""
    abs_source = os.path.abspath(source_path)
    abs_output = os.path.abspath(output_path)
    file_url = f"file:///{abs_source.replace(os.sep, '/')}"

    os.makedirs(os.path.dirname(abs_output), exist_ok=True)

    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"--print-to-pdf={abs_output}",
        "--disable-print-preview",
        file_url
    ]

    print(f"  Converting: {os.path.basename(source_path)} -> {os.path.basename(output_path)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if os.path.isfile(abs_output):
        size = os.path.getsize(abs_output)
        print(f"    [OK] PDF created: {size:,} bytes")
        return True
    else:
        print(f"    [FAIL] PDF not created")
        if result.stderr:
            # Show only relevant errors (ignore non-critical Chrome messages)
            for line in result.stderr.split('\n'):
                if 'ERROR' in line and 'FATAL' not in line:
                    if 'fallback_task_provider' not in line and 'GetUpdates' not in line:
                        print(f"      {line.strip()}")
        return False


def build_index_html():
    """Create docs/index.html with links to all PDFs."""
    pdfs = sorted(glob.glob(os.path.join(DOCS_DIR, "*.pdf")))

    rows = ""
    icons = {
        "promo": "🎯",
        "product": "📋",
        "sales-page": "💰",
        "eula": "⚖️",
        "training-program": "📚",
        "training-program-md": "📖",
        "before-you-begin": "🚀",
    }

    for pdf_path in pdfs:
        name = os.path.basename(pdf_path)
        stem = name.replace(".pdf", "")
        size = os.path.getsize(pdf_path)
        size_str = f"{size/1024:.0f} KB" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
        icon = icons.get(stem, "📄")
        display_name = {
            "promo": "Product Landing Page",
            "product": "Product Documentation (README)",
            "sales-page": "Sales Page / Listing Copy",
            "eula": "MIT License",
            "training-program": "Training Program Syllabus (HTML)",
            "training-program-md": "Training Program Syllabus (Markdown)",
            "before-you-begin": "Before You Begin — Prep Guide",
        }.get(stem, stem.replace("-", " ").title())

        rows += f"""
    <a href="{name}" class="pdf-card">
      <span class="pdf-icon">{icon}</span>
      <div class="pdf-info">
        <div class="pdf-name">{display_name}</div>
        <div class="pdf-meta">{name} &middot; {size_str}</div>
      </div>
      <span class="pdf-arrow">&rarr;</span>
    </a>"""

    index_html = rf"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NovaCap — Documentation PDFs</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg-primary: #060a12;
    --bg-secondary: #0a0e17;
    --bg-card: #0f1525;
    --border: #152030;
    --border-light: #1a3050;
    --text-primary: #dfe6e9;
    --text-secondary: #8395a7;
    --text-muted: #4a5a6a;
    --accent-cyan: #48dbfb;
    --accent-blue: #0abde3;
    --accent-green: #2ecc71;
  }}
  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 20px;
  }}
  .bg-grid {{
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image:
      linear-gradient(rgba(72, 219, 251, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(72, 219, 251, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
  }}
  .container {{ max-width: 720px; width: 100%; position: relative; z-index: 1; }}
  .header {{
    text-align: center;
    margin-bottom: 40px;
  }}
  .logo {{
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent-cyan);
    margin-bottom: 8px;
  }}
  .header h1 {{
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 8px;
  }}
  .header p {{
    color: var(--text-muted);
    font-size: 14px;
  }}
  .header p a {{ color: var(--accent-cyan); text-decoration: none; }}
  .header p a:hover {{ text-decoration: underline; }}
  .pdf-grid {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .pdf-card {{
    display: flex;
    align-items: center;
    gap: 16px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 20px;
    text-decoration: none;
    transition: all 0.2s;
  }}
  .pdf-card:hover {{
    border-color: var(--accent-cyan);
    background: rgba(15, 21, 37, 0.8);
    transform: translateX(3px);
  }}
  .pdf-icon {{ font-size: 28px; flex-shrink: 0; }}
  .pdf-info {{ flex: 1; min-width: 0; }}
  .pdf-name {{
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 2px;
  }}
  .pdf-meta {{
    font-size: 12px;
    color: var(--text-muted);
  }}
  .pdf-arrow {{
    color: var(--text-muted);
    font-size: 20px;
    transition: transform 0.2s, color 0.2s;
  }}
  .pdf-card:hover .pdf-arrow {{
    color: var(--accent-cyan);
    transform: translateX(4px);
  }}
  .footer {{
    text-align: center;
    margin-top: 48px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 12px;
    width: 100%;
  }}
  .footer a {{ color: var(--accent-cyan); text-decoration: none; }}
  .footer a:hover {{ text-decoration: underline; }}
  @media (max-width: 500px) {{
    .header h1 {{ font-size: 24px; }}
    .pdf-card {{ padding: 14px 16px; }}
    .pdf-icon {{ font-size: 22px; }}
    .pdf-name {{ font-size: 13px; }}
  }}
</style>
</head>
<body>
<div class="bg-grid"></div>
<div class="container">
  <div class="header">
    <div class="logo">NovaCap Financial Technologies</div>
    <h1>Documentation &amp; Resources</h1>
    <p>
      Principal Strategist &mdash; 90-Day FinTech Arbitrage Academy<br>
      <a href="http://localhost:8081">Launch Web Dashboard</a>
      &middot;
      <a href="http://localhost:8080">Mock Exchange</a>
    </p>
  </div>
  <div class="pdf-grid">
    {rows}
  </div>
  <div class="footer">
    Generated on 2026-06-19 &middot;
    <a href="generate_pdfs.py">Re-generate script</a> &middot;
    Python standard library only
  </div>
</div>
</body>
</html>
"""
    index_path = os.path.join(DOCS_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"\n  ✓ docs/index.html created")
    return index_path


def main():
    print("=" * 60)
    print("  NovaCap PDF Generator")
    print("  Converting 7 documentation files to PDF")
    print("=" * 60)

    # Create docs directory
    os.makedirs(DOCS_DIR, exist_ok=True)

    success_count = 0
    fail_count = 0

    for source_rel, file_type, output_name in CONVERSIONS:
        source_path = os.path.join(BASE_DIR, source_rel)
        output_path = os.path.join(DOCS_DIR, output_name)

        if not os.path.isfile(source_path):
            print(f"  ! SKIP: {source_rel} not found")
            continue

        if file_type == "html":
            # Direct HTML → PDF conversion
            if convert_to_pdf(source_path, output_path):
                success_count += 1
            else:
                fail_count += 1

        elif file_type == "md":
            # Markdown → HTML → PDF conversion
            with open(source_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Create title from filename
            title = output_name.replace(".pdf", "").replace("-", " ").title()
            if title == "Eula":
                title = "MIT License"

            # Convert to dark-themed HTML
            html_content = md_to_html(md_content, title)

            # Write temp HTML file
            temp_html = os.path.join(tempfile.gettempdir(), f"novacap_{output_name.replace('.pdf', '.html')}")
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Convert to PDF
            if convert_to_pdf(temp_html, output_path):
                success_count += 1
            else:
                fail_count += 1

            # Clean up temp file
            try:
                os.remove(temp_html)
            except OSError:
                pass

    # Build index.html
    print("\n" + "=" * 60)
    print("  Creating docs/index.html...")
    print("=" * 60)
    build_index_html()

    # Summary
    total = success_count + fail_count
    print("\n" + "=" * 60)
    print(f"  Complete: {success_count}/{total} PDFs generated")
    if fail_count > 0:
        print(f"  Failures: {fail_count}")
    print(f"  Output: {DOCS_DIR}")
    print("=" * 60)
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
