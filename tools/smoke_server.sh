#!/usr/bin/env bash
# Boots a dedicated server for one loader, waits until the world is ready (or fails), then stops it.
# Usage: tools/smoke_server.sh <fabric|neoforge> [log-file]
# Exit code 0 only if the server reached "Done" without errors from Sprout & Soil or data loading.
set -u
loader="${1:?fabric or neoforge}"
log="${2:-/tmp/sprout_smoke_${loader}.log}"
root="$(cd "$(dirname "$0")/../1.21.1" && pwd)"
cd "$root"

case "$loader" in
  fabric) rundir="fabric/runs/server" ;;
  neoforge) rundir="neoforge/runs/server" ;;
  *) echo "unknown loader $loader" >&2; exit 2 ;;
esac
mkdir -p "$rundir"
echo "eula=true" > "$rundir/eula.txt"
rm -rf "$rundir/world"

./gradlew ":${loader}:runServer" --no-daemon --max-workers=2 > "$log" 2>&1 &
pid=$!
deadline=$((SECONDS + 1500))
status=1
while kill -0 "$pid" 2>/dev/null; do
  if grep -qE 'Done \([0-9.]+s\)!' "$log"; then status=0; break; fi
  if grep -qE 'Crash report|Exception in server tick loop|Failed to start the minecraft server|BUILD FAILED' "$log"; then break; fi
  if (( SECONDS > deadline )); then echo "timeout" >> "$log"; break; fi
  sleep 3
done
sleep 2
pkill -f "runServer" 2>/dev/null; pkill -f "net.fabricmc.devlaunchinjector\|cpw.mods\|neoforge.*server\|KnotServer" 2>/dev/null
kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null

errors=$(grep -E '\[(main|Server thread|Worker-Main-[0-9]+)/(ERROR|FATAL)\]|Couldn.t parse|Failed to (load|parse)|Unknown (item|block|tag)|Parsing error|validation problem' "$log" | grep -v "Realms\|realms" | head -60)
if [[ -n "$errors" ]]; then
  echo "---- errors ----"; echo "$errors"; status=1
fi
grep -E 'Sprout & Soil:|Done \(' "$log" | head -5
echo "smoke($loader) status=$status log=$log"
exit $status
