#!/usr/bin/env python3
"""Builds the website pages from the templates in src/ and the texts in i18n/<language>.json.

    python3 tools/build.py [path/to/pessic]      (default: ../pessic next to this website)

Catalan (i18n/ca.json) is the default language and is written at the root: index.html, manual.html.
Every other i18n/<code>.json is written to <code>/index.html; its manual comes from the app's
MANUAL.<code>.md if it exists, otherwise its pages link to the Catalan manual. Keys missing from a
translation fall back to Catalan, with a warning.

Templates:  {{key}}    text (may contain inline HTML)
            {{@key}}   text inside an attribute (escaped)
            {{=name}}  a value from this script: lang, root, generated, alternates, languages,
                       jsStrings, toc, body

Fails if a template or js/main.js uses a key that ca.json does not have, or ca.json has a key
nothing uses. Standard library only.
"""
import html
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
APP = Path(sys.argv[1]) if len(sys.argv) > 1 else SITE.parent / "pessic"
DEFAULT = "ca"
PLACEHOLDER = re.compile(r"\{\{([@=]?)([\w.]+)\}\}")
JS_KEY = re.compile(r"""["'](js\.[\w.]+)["']""")


# ------------------------------------------------------------------ texts

def flatten(tree, prefix=""):
    out = {}
    for k, v in tree.items():
        if k.startswith("_"):
            continue
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, key + "."))
        else:
            out[key] = v
    return out


def load_languages():
    langs = {}
    for f in sorted((SITE / "i18n").glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        langs[f.stem] = {"name": data.get("_language", {}).get("name", f.stem), "texts": flatten(data)}
    if DEFAULT not in langs:
        sys.exit(f"i18n/{DEFAULT}.json is missing")
    return langs


# ------------------------------------------------------------------ manual (Markdown subset used by MANUAL.md)

def slug(text):
    """GitHub-style anchor: lower case, punctuation removed, spaces to hyphens (accents kept)."""
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def inline(text):
    codes = []

    def keep_code(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def markdown(md, index_title):
    """Returns (body html, [(anchor, title)] of the level-2 headings). Drops the manual's own index."""
    lines = md.splitlines()
    out, toc, para, lists = [], [], [], []  # lists: stack of [indent, tag]
    i = 0

    def close_para():
        if para:
            # a line that is all bold (an FAQ question) ends with a line break
            parts = [inline(l) + ("<br>" if re.fullmatch(r"\*\*.+\*\*", l) else "") for l in para]
            out.append("<p>" + " ".join(parts).replace("<br> ", "<br>\n") + "</p>")
            para.clear()

    def close_lists(to_indent=-1):
        while lists and lists[-1][0] > to_indent:
            out.append(f"</li></{lists.pop()[1]}>")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        item = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if not stripped:
            close_para()
            i += 1
        elif stripped == "---":
            close_para(); close_lists()
            out.append("<hr>")
            i += 1
        elif heading:
            close_para(); close_lists()
            level, text = len(heading.group(1)), heading.group(2).strip()
            if level == 2 and text == index_title:  # the page has its own index: skip it and its rule
                i += 1
                while i < len(lines) and lines[i].strip() != "---":
                    i += 1
                i += 1
                continue
            anchor = slug(text)
            if level == 2:
                toc.append((anchor, text))
            out.append(f'<h{level} id="{anchor}">{inline(text)}</h{level}>')
            i += 1
        elif stripped.startswith(">"):
            close_para(); close_lists()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(quote))}</p></blockquote>")
        elif stripped.startswith("|"):
            close_para(); close_lists()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>")
            out += ["<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[2:]]
            out.append("</tbody></table>")
        elif item:
            close_para()
            indent, marker, text = len(item.group(1)), item.group(2), item.group(3)
            tag = "ol" if marker[0].isdigit() else "ul"
            if lists and indent > lists[-1][0]:
                out.append(f"<{tag}>")
                lists.append([indent, tag])
            else:
                close_lists(indent)
                if lists and lists[-1][0] == indent:
                    out.append("</li>")
                else:
                    out.append(f"<{tag}>")
                    lists.append([indent, tag])
            out.append(f"<li>{inline(text)}")
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]) \
                    and len(lines[i]) - len(lines[i].lstrip()) > indent:
                out[-1] += " " + inline(lines[i].strip())
                i += 1
        elif lists and line.startswith(" "):
            out[-1] += " " + inline(stripped)
            i += 1
        else:
            close_lists()
            para.append(stripped)
            i += 1
    close_para(); close_lists()
    return "\n".join(out), toc


# ------------------------------------------------------------------ pages

def render(template, texts, values, used, missing):
    def sub(m):
        kind, name = m.group(1), m.group(2)
        if kind == "=":
            return values[name]
        used.add(name)
        if name not in texts:
            missing.add(name)
            return f"‼{name}"
        return html.escape(texts[name], quote=True) if kind == "@" else texts[name]
    return PLACEHOLDER.sub(sub, template)


def main():
    langs = load_languages()
    base = langs[DEFAULT]["texts"]
    templates = {name: (SITE / "src" / name).read_text(encoding="utf-8") for name in ("index.html", "manual.html")}
    js_source = (SITE / "js" / "main.js").read_text(encoding="utf-8")
    js_keys = set(JS_KEY.findall(js_source))
    errors, written = [], []
    manuals = {c: (APP / ("MANUAL.md" if c == DEFAULT else f"MANUAL.{c}.md")).exists() for c in langs}

    for code, lang in langs.items():
        texts = dict(base)
        extra = set(lang["texts"]) - set(base)
        gaps = set(base) - set(lang["texts"])
        texts.update({k: v for k, v in lang["texts"].items() if k in base})
        if code != DEFAULT and gaps:
            print(f"warning: {code}.json lacks {len(gaps)} keys (Catalan used): {', '.join(sorted(gaps)[:8])}…")
        if extra:
            print(f"warning: {code}.json has keys that ca.json does not: {', '.join(sorted(extra))}")

        out_dir = SITE if code == DEFAULT else SITE / code
        root = "" if code == DEFAULT else "../"
        manual_md = APP / ("MANUAL.md" if code == DEFAULT else f"MANUAL.{code}.md")
        has_manual = manual_md.exists()
        if code == DEFAULT and not has_manual:
            sys.exit(f"{manual_md} not found (pass the app's folder as an argument)")

        def page_url(c, page):
            if page == "manual.html" and not manuals[c]:
                c = DEFAULT  # no manual in that language: the Catalan one
            return page if c == DEFAULT else f"{c}/{page}"

        used, missing = set(), set()

        def values_for(page):
            alternates = "\n".join(
                f'  <link rel="alternate" hreflang="{c}" href="{root}{page_url(c, page)}">' for c in langs) if len(langs) > 1 else ""
            switch = "\n".join(
                f'        <a class="lang-link" href="{root}{page_url(c, page)}" hreflang="{c}" lang="{c}"'
                + (' aria-current="true"' if c == code else "") + f'>{html.escape(l["name"])}</a>'
                for c, l in langs.items() if page != "manual.html" or manuals[c] or c == DEFAULT) if len(langs) > 1 else ""
            if switch:
                switch = (f'        <span class="lang-switch" role="group" aria-label="{html.escape(texts["a11y.language"])}">\n'
                          + switch + "\n        </span>")
            used.add("a11y.language")
            js = {k: v for k, v in texts.items() if k.startswith("js.")}
            return {
                "lang": code,
                "root": root,
                "generated": f"Generated by tools/build.py from src/{page} and i18n/{code}.json. Do not edit by hand.",
                "alternates": alternates,
                "languages": switch,
                "jsStrings": '  <script id="i18n-strings" type="application/json">'
                             + json.dumps(js, ensure_ascii=False).replace("</", "<\\/") + "</script>",
            }

        out_dir.mkdir(exist_ok=True)

        page = render(templates["index.html"], texts, values_for("index.html"), used, missing)
        if code != DEFAULT and not has_manual:
            page = page.replace('href="manual.html', f'href="{root}manual.html')
        (out_dir / "index.html").write_text(page, encoding="utf-8")
        written.append(out_dir / "index.html")

        if has_manual:
            body, toc = markdown(manual_md.read_text(encoding="utf-8"), texts["manual.toc"])
            values = values_for("manual.html")
            values["body"] = body
            values["toc"] = "\n".join(
                f'          <li><a href="#{a}">{inline(re.sub(r"^\d+\.\s*", "", t))}</a></li>' for a, t in toc)
            (out_dir / "manual.html").write_text(render(templates["manual.html"], texts, values, used, missing), encoding="utf-8")
            written.append(out_dir / "manual.html")

        if code == DEFAULT:
            if missing:
                errors.append(f"templates use keys missing from ca.json: {sorted(missing)}")
            unused = set(base) - used - {k for k in base if k.startswith("js.")}
            if unused:
                errors.append(f"ca.json has keys no template uses: {sorted(unused)}")
            js_missing = js_keys - set(base)
            js_unused = {k for k in base if k.startswith("js.")} - js_keys
            if js_missing:
                errors.append(f"js/main.js uses keys missing from ca.json: {sorted(js_missing)}")
            if js_unused:
                errors.append(f"ca.json has js.* keys that js/main.js does not use: {sorted(js_unused)}")

    if errors:
        sys.exit("\n".join(errors))
    for f in written:
        print("wrote", f.relative_to(SITE))


if __name__ == "__main__":
    main()
