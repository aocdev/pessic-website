#!/usr/bin/env python3
"""Counts the downloads of Pessic's installers, from every release on GitHub, and writes them for the site.

    python3 tools/downloads.py                         # writes js/downloads.js
    python3 tools/downloads.py --out _site/js/downloads.js
    python3 tools/downloads.py --zero                  # the placeholder kept in the repository

The Pages workflow runs it on every deploy (and daily), so visitors' browsers never contact GitHub.
Counts only installers (.msi, .dmg, .deb, .rpm), not SHA256SUMS.txt. Set GH_TOKEN for a higher API rate
limit. Options: --repo owner/name (default aocdev/pessic). Standard library only.
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
SYSTEMS = {"windows": re.compile(r"\.msi$"), "mac": re.compile(r"\.dmg$"), "linux": re.compile(r"\.(deb|rpm)$")}
HEADER = """/* Downloads of Pessic's installers, from every GitHub release: written by tools/downloads.py when the site
   is deployed. The copy in the repository is a placeholder with zeros (nothing is shown). */
window.PESSIC_DOWNLOADS = """


def releases(repo):
    """All releases (paginated), via the public API."""
    out, page = [], 1
    while True:
        request = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "pessic-website"})
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(request, timeout=30) as response:
            batch = json.load(response)
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def count(all_releases):
    totals = {system: 0 for system in SYSTEMS}
    for release in all_releases:
        if release.get("draft"):
            continue
        for asset in release.get("assets", []):
            for system, pattern in SYSTEMS.items():
                if pattern.search(asset["name"]):
                    totals[system] += asset.get("download_count", 0)
    return {"total": sum(totals.values()), **totals}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + json.dumps(data, indent=2) + ";\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default="aocdev/pessic")
    ap.add_argument("--out", default=str(SITE / "js" / "downloads.js"))
    ap.add_argument("--zero", action="store_true", help="write the placeholder: zeros, nothing is shown")
    args = ap.parse_args()
    out = Path(args.out)

    if args.zero:
        write(out, {"total": 0, "windows": 0, "mac": 0, "linux": 0, "updated": ""})
        print(f"{out}: placeholder")
        return
    try:
        data = count(releases(args.repo))
    except Exception as e:
        sys.exit(f"Cannot read the releases of {args.repo}: {e}")
    data["updated"] = datetime.date.today().isoformat()
    write(out, data)
    print(f"{out}: {data['total']} downloads (Windows {data['windows']}, macOS {data['mac']}, Linux {data['linux']})")


if __name__ == "__main__":
    main()
