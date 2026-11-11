#!/usr/bin/env bash
# Retakes the website screenshots from the real app, with the invented demo profile "Marta".
# Needs JDK 21, Maven, Python 3 with Pillow, and the app built once (mvn install in ../pessic).
# Never touches your own Pessic data: it uses a temporary database (PESSIC_DB) and a fixed date.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SITE="$(cd "$HERE/../.." && pwd)"
APP="${PESSIC_SRC:-$SITE/../pessic}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

mvn -q -f "$APP/pessic-app/pom.xml" dependency:build-classpath -Dmdep.outputFile="$WORK/cp.txt" >/dev/null
CP="$APP/pessic-app/target/classes:$APP/pessic-core/target/classes:$APP/pessic-db/target/classes:$(cat "$WORK/cp.txt")"
javac -d "$WORK/classes" -cp "$CP" "$HERE"/*.java
java -cp "$WORK/classes:$CP" MakeDemo "$APP/pessic-db/src/test/resources/backup-sample.json" "$WORK/demo.db"

mkdir -p "$WORK/shots"
for day in 2026-11-09 2026-11-28; do   # the 28th shows the month-close dialog
  rm -rf "$WORK/run.db"* "$WORK/backups" && cp "$WORK/demo.db" "$WORK/run.db"
  (cd "$WORK" && PESSIC_DB="$WORK/run.db" PESSIC_TODAY=$day java -Ddir="$WORK/shots" -cp "$WORK/classes:$CP" WebShotsMain)
done

python3 - "$WORK/shots" "$SITE/assets/screens" <<'PY'
import sys
from pathlib import Path
from PIL import Image
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
for png in sorted(src.glob("*.png")):
    Image.open(png).convert("RGB").save(dst / (png.stem + ".webp"), "WEBP", quality=88, method=6)
    print("updated", png.stem + ".webp")
PY
