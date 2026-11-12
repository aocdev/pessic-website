#!/usr/bin/env python3
"""Checks the built pages: balanced HTML tags, files that exist, and links to anchors that exist.

    python3 tools/check.py

Covers index.html, manual.html and every <language>/ folder. Exits with an error listing the problems.
Standard library only.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "path", "rect", "circle", "area", "base", "col", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.ids, self.refs = [], [], set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for name in ("href", "src"):
            if attrs.get(name):
                self.refs.append(attrs[name])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")


def main():
    pages = sorted(p for p in SITE.rglob("*.html")
                   if not p.relative_to(SITE).parts[0] in {"src", "tools", ".git", ".idea", ".app", "node_modules"})
    parsed = {}
    for page in pages:
        p = Page()
        p.feed(page.read_text(encoding="utf-8"))
        parsed[page] = p

    problems = []
    for page, p in parsed.items():
        name = page.relative_to(SITE)
        if p.stack:
            problems.append(f"{name}: unclosed tags {p.stack}")
        problems += [f"{name}: {e}" for e in p.errors]
        if "‼" in page.read_text(encoding="utf-8"):
            problems.append(f"{name}: a text key is missing (‼)")
        for ref in p.refs:
            if re.match(r"^(https?:|mailto:|data:)", ref):
                continue
            path, _, anchor = ref.partition("#")
            target = (page.parent / path).resolve() if path else page.resolve()
            if not target.exists():
                problems.append(f"{name}: missing file {ref}")
            elif anchor and target.suffix == ".html":
                ids = parsed[target].ids if target in parsed else set()
                if anchor not in ids:
                    problems.append(f"{name}: missing anchor {ref}")

    if problems:
        sys.exit("\n".join(problems))
    print(f"{len(pages)} pages ok: tags balanced, files and anchors found")


if __name__ == "__main__":
    main()
