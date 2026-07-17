#!/usr/bin/env python3
"""Render the markdown tables in a file as polished PNG images.

Substack/LinkedIn strip table formatting on paste — but they display images
exactly as designed. This extracts each table, renders it with real typography
in headless Chromium, and saves retina PNGs you drag into the editor.

Usage:
    python3 scripts/table-images.py path/to/lesson/README.md
    # -> path/to/lesson/visuals/README-table-01.png, ...

Requires: pip install playwright && python3 -m playwright install chromium
"""
import html
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #e9e9e9; font: 15px/1.55 -apple-system, "Segoe UI",
       Helvetica, Arial, sans-serif; color: #1a1a1a; }
#card { width: 720px; padding: 26px 30px; background: #ffffff; border-radius: 10px; }
table { border-collapse: collapse; width: 100%; }
th { text-align: left; font-weight: 650; padding: 9px 16px 9px 2px;
     border-bottom: 2px solid #1a1a1a; white-space: nowrap; }
td { padding: 9px 16px 9px 2px; border-bottom: 1px solid #e6e6e6; vertical-align: top; }
tr:last-child td { border-bottom: none; }
code { font: 12.5px Menlo, Consolas, monospace; background: #f2f2f2;
       padding: 1px 5px; border-radius: 4px; white-space: nowrap; }
strong { font-weight: 650; }
"""

INLINE_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
CODE = re.compile(r"`([^`]+)`")


def cell_html(cell: str) -> str:
    """Markdown inline formatting -> HTML for one table cell."""
    cell = html.escape(INLINE_LINK.sub(r"\1", cell.strip()))
    cell = BOLD.sub(r"<strong>\1</strong>", cell)
    cell = CODE.sub(r"<code>\1</code>", cell)
    return cell


def extract_tables(text: str) -> list[list[list[str]]]:
    """Return each GFM table as a list of rows (skipping fenced code blocks)."""
    tables, in_fence = [], False
    lines = text.splitlines()
    sep = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if (not in_fence and line.lstrip().startswith("|") and i + 1 < len(lines)
                and sep.match(lines[i + 1]) and "-" in lines[i + 1]):
            rows = [[c.strip() for c in line.strip().strip("|").split("|")]]
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            tables.append(rows)
            continue
        i += 1
    return tables


def table_page(rows: list[list[str]]) -> str:
    head = "".join(f"<th>{cell_html(c)}</th>" for c in rows[0])
    body = "".join(
        "<tr>" + "".join(f"<td>{cell_html(c)}</td>" for c in row) + "</tr>"
        for row in rows[1:]
    )
    return (f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>'
            f'<body><div id="card"><table><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div></body>")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip())
    src = Path(sys.argv[1])
    tables = extract_tables(src.read_text())
    if not tables:
        sys.exit(f"No markdown tables found in {src}")

    outdir = src.parent / "visuals"
    outdir.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2, viewport={"width": 800, "height": 600})
        for n, rows in enumerate(tables, 1):
            out = outdir / f"{src.stem}-table-{n:02d}.png"
            page.set_content(table_page(rows))
            page.locator("#card").screenshot(path=str(out))
            print(f"🖼  {out}")
        browser.close()
    print(f"\n{len(tables)} table(s) rendered — drag the PNGs into the editor.")


if __name__ == "__main__":
    main()
