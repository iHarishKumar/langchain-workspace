#!/usr/bin/env python3
"""Copy a markdown file to the macOS clipboard as rich text (HTML flavor).

WYSIWYG editors (Substack, LinkedIn, Gmail, Notion) can't ingest raw markdown —
they need rendered rich text on the clipboard. This renders the file and sets
the clipboard's HTML flavor, so pasting produces real headings, bold, lists,
links, and code blocks instead of literal `#` and `**`.

Markdown tables are converted before rendering, because Substack (and LinkedIn)
have no table support and flatten pasted <table> HTML into mush:
  - 2-column tables  -> a bullet list ("**term** — description")
  - wider tables     -> an aligned monospace grid inside a code block

Usage:
    python3 scripts/copy-rich.py path/to/draft.md
    python3 scripts/copy-rich.py --tables grid path/to/draft.md   # force grid
    python3 scripts/copy-rich.py --tables list path/to/draft.md   # force bullets
    # then Cmd+V into the Substack/LinkedIn editor

Requires: pip install markdown   (pure-Python, no other dependencies)
"""
import argparse
import re
import subprocess
from pathlib import Path

import markdown

INLINE_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def plain(cell: str) -> str:
    """Strip inline markdown from a cell destined for a monospace grid."""
    cell = INLINE_LINK.sub(r"\1", cell)
    return cell.replace("**", "").replace("`", "").strip()


def parse_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table_to_list(rows: list[list[str]]) -> list[str]:
    """2-column table -> bullet list: '**term** — description'."""
    out = []
    for term, desc in rows[1:]:
        term = plain(term)
        out.append(f"- **{term}** — {desc.strip()}" if desc.strip() else f"- **{term}**")
    return out


def table_to_grid(rows: list[list[str]]) -> list[str]:
    """Any table -> aligned monospace grid in a fenced code block."""
    cells = [[plain(c) for c in row] for row in rows]
    ncols = max(len(r) for r in cells)
    cells = [r + [""] * (ncols - len(r)) for r in cells]
    widths = [max(len(r[i]) for r in cells) for i in range(ncols)]
    fmt = lambda r: "  ".join(r[i].ljust(widths[i]) for i in range(ncols)).rstrip()
    out = ["```", fmt(cells[0]), "  ".join("-" * w for w in widths)]
    out += [fmt(r) for r in cells[1:]]
    out.append("```")
    return out


def convert_tables(text: str, mode: str) -> str:
    """Replace GFM tables with paste-safe equivalents; skip fenced code blocks."""
    lines = text.splitlines()
    out, i, in_fence = [], 0, False
    sep = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        is_table_start = (
            not in_fence
            and line.lstrip().startswith("|")
            and i + 1 < len(lines)
            and sep.match(lines[i + 1])
            and "-" in lines[i + 1]
        )
        if not is_table_start:
            out.append(line)
            i += 1
            continue
        rows = [parse_row(line)]
        i += 2  # skip the |---| separator row
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            rows.append(parse_row(lines[i]))
            i += 1
        two_col = all(len(r) <= 2 for r in rows)
        use_list = mode == "list" or (mode == "auto" and two_col)
        out.extend(table_to_list(rows) if use_list and two_col else table_to_grid(rows))
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", type=Path)
    ap.add_argument("--tables", choices=["auto", "list", "grid"], default="auto",
                    help="table conversion: auto (2-col->bullets, wider->grid), list, or grid")
    args = ap.parse_args()

    text = args.file.read_text()

    # Strip HTML comments (draft notes like posting-time reminders) before rendering.
    while "<!--" in text:
        start = text.index("<!--")
        end = text.index("-->", start) + 3
        text = text[:start] + text[end:]

    text = convert_tables(text, args.tables)

    html = markdown.markdown(
        text,
        extensions=["fenced_code", "sane_lists", "nl2br"],
    )

    # Editors keep <pre> blocks as code on paste; give them a hint of styling for
    # targets that honor inline styles (Substack strips them harmlessly).
    html = html.replace(
        "<pre>", '<pre style="font-family: Menlo, monospace; font-size: 13px;">'
    )

    # Set the clipboard's HTML flavor via AppleScript's raw-data form.
    hex_html = html.encode("utf-8").hex()
    subprocess.run(
        ["osascript", "-e", f'set the clipboard to «data HTML{hex_html}»'],
        check=True,
    )
    print(f"✅ {args.file.name} rendered and copied as rich text — paste into the editor now.")


if __name__ == "__main__":
    main()
