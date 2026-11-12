#!/usr/bin/env python3
"""Points the download buttons to a published release: writes js/release.js with each installer's
link and SHA-256, read from the release's SHA256SUMS.txt.

    python3 tools/release.py 1.0.0                      # reads SHA256SUMS.txt from the GitHub release
    python3 tools/release.py 1.0.0 --sums SHA256SUMS.txt   # or from a downloaded copy
    python3 tools/release.py 1.0.0 --clear              # no installers yet: "Aviat disponible"

Options: --repo owner/name (default aocdev/pessic). The files are expected with the names the app's
Installers workflow gives them: *.msi, *-arm64.dmg, *-x64.dmg, *.deb, *.rpm. Standard library only.
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
TARGET = SITE / "js" / "release.js"
TYPES = {  # file type -> how to recognise its file name
    "msi": re.compile(r"\.msi$"),
    "dmgArm": re.compile(r"-arm64\.dmg$"),
    "dmgIntel": re.compile(r"-x64\.dmg$"),
    "deb": re.compile(r"\.deb$"),
    "rpm": re.compile(r"\.rpm$"),
}
HEADER = """/* The published release: written by tools/release.py from the release's SHA256SUMS.txt. Do not edit by hand.
   Empty links show "Aviat disponible"; empty checksums are not shown. */
window.PESSIC_RELEASE = """


def read(source):
    if re.match(r"^https?://", source):
        try:
            with urllib.request.urlopen(source, timeout=30) as response:
                return response.read().decode("utf-8")
        except Exception as e:
            sys.exit(f"Cannot download {source}: {e}\n"
                     "Is the release published? You can also pass a downloaded copy with --sums FILE.")
    return Path(source).read_text(encoding="utf-8")


def parse(text):
    """sha256sum output: '<64 hex>  <name>' (or '*<name>' in binary mode)."""
    sums = {}
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        m = re.match(r"^([0-9a-fA-F]{64}) [ *](.+)$", line.strip())
        if not m:
            sys.exit(f"SHA256SUMS line {n} is not '<sha256>  <file>': {line!r}")
        sums[m.group(2).strip()] = m.group(1).lower()
    return sums


def write(version, checksums_url, files):
    data = {"version": version, "checksums": checksums_url, "files": files}
    TARGET.write_text(HEADER + json.dumps(data, indent=2) + ";\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", help="the released version, e.g. 1.0.0 (the tag is v<version>)")
    ap.add_argument("--repo", default="aocdev/pessic")
    ap.add_argument("--sums", help="SHA256SUMS.txt: a file or a URL (default: the one in the release)")
    ap.add_argument("--clear", action="store_true", help="no links: every button says 'Aviat disponible'")
    args = ap.parse_args()

    version = args.version.removeprefix("v")
    if args.clear:
        write(version, "", {t: {"href": "", "sha256": ""} for t in TYPES})
        print(f"{TARGET.relative_to(SITE)}: version {version}, no installers")
        return

    base = f"https://github.com/{args.repo}/releases/download/v{version}/"
    sums_source = args.sums or base + "SHA256SUMS.txt"
    sums = parse(read(sums_source))

    files, missing = {}, []
    for type_, pattern in TYPES.items():
        names = [name for name in sums if pattern.search(name)]
        if len(names) > 1:
            sys.exit(f"More than one file for {type_}: {names}")
        if names:
            files[type_] = {"href": base + names[0], "sha256": sums[names[0]]}
        else:
            files[type_] = {"href": "", "sha256": ""}
            missing.append(type_)
    unknown = [n for n in sums if not any(p.search(n) for p in TYPES.values())]

    write(version, base + "SHA256SUMS.txt", files)
    print(f"{TARGET.relative_to(SITE)}: version {version}")
    for type_, f in files.items():
        print(f"  {type_:9} {f['href'].rsplit('/', 1)[-1] or '(none: Aviat disponible)'}")
    if missing:
        print(f"warning: no file for {', '.join(missing)}")
    if unknown:
        print(f"note: ignored {', '.join(unknown)}")


if __name__ == "__main__":
    main()
