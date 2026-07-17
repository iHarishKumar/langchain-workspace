#!/usr/bin/env python3
"""Copy a markdown file to the macOS clipboard as rich text (HTML flavor).

WYSIWYG editors (Substack, LinkedIn, Gmail, Notion) can't ingest raw markdown —
they need rendered rich text on the clipboard. This renders the file and sets
the clipboard's HTML flavor, so pasting produces real headings, bold, lists,
links, and code blocks instead of literal `#` and `**`.

Usage:
    python3 scripts/copy-rich.py path/to/draft.md
    # then Cmd+V into the Substack/LinkedIn editor

Requires: pip install markdown   (pure-Python, no other dependencies)
"""
import subprocess
import sys
from pathlib import Path

import markdown

if len(sys.argv) != 2:
    sys.exit(__doc__.strip())

src = Path(sys.argv[1])
text = src.read_text()

# Strip HTML comments (draft notes like posting-time reminders) before rendering.
while "<!--" in text:
    start = text.index("<!--")
    end = text.index("-->", start) + 3
    text = text[:start] + text[end:]

html = markdown.markdown(
    text,
    extensions=["fenced_code", "tables", "sane_lists", "nl2br"],
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
print(f"✅ {src.name} rendered and copied as rich text — paste into the editor now.")
