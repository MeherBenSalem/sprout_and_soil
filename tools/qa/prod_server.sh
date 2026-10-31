#!/usr/bin/env bash
# Boots a built release JAR on a real (non-development) dedicated server and checks that it starts
# cleanly. Unlike the Gradle dev runs, this catches remapping problems (Forge reobf, Fabric
# intermediary and mixin refmaps) and missing runtime dependencies.
#
#   tools/qa/prod_server.sh <minecraft> <loader> [work-dir]
#   tools/qa/prod_server.sh 1.20.1 forge
#
# Build the workspace first (./gradlew build in <minecraft>/). The server, its installer and Fabric
# API are downloaded into the work dir (default build/qa/<minecraft>-<loader>, git-ignored).
# Exit code 0 only if the server reached "Done", the mod loaded its content and nothing in the log
# looks like a Sprout & Soil, mixin or data-loading error.
set -u
mc="${1:?minecraft version, e.g. 1.20.1}"
loader="${2:?fabric, forge or neoforge}"
repo="$(cd "$(dirname "$0")/../.." && pwd)"
work="${3:-$repo/build/qa/$mc-$loader}"
props="$repo/$mc/gradle.properties"
prop() { grep -E "^$1=" "$props" | head -1 | cut -d= -f2-; }

jar="$repo/$mc/$loader/build/libs/sprout_and_soil-$loader-$mc-$(prop version).jar"
[[ -f "$jar" ]] || { echo "no $loader jar for $mc - build $mc first" >&2; exit 2; }

case "$(prop java_version)" in
  17) java_home="${JAVA_HOME_17:-/usr/lib/jvm/java-17-openjdk-amd64}" ;;
  *) java_home="${JAVA_HOME_21:-/usr/lib/jvm/java-21-openjdk-amd64}" ;;
esac
export JAVA_HOME="$java_home" PATH="$java_home/bin:$PATH"

mkdir -p "$work/mods"
cd "$work"
rm -rf world logs crash-reports mods/sprout_and_soil-*.jar
fetch() { [[ -s "$2" ]] || curl -fsSL --retry 3 -o "$2" "$1"; }

case "$loader" in
  fabric)
    installer=$(curl -fsSL https://meta.fabricmc.net/v2/versions/installer | python3 -c 'import json,sys; print(next(v["version"] for v in json.load(sys.stdin) if v["stable"]))')
    fetch "https://meta.fabricmc.net/v2/versions/loader/$mc/$(prop fabric_loader_version)/$installer/server/jar" server.jar
    api="$(prop fabric_version)"
    fetch "https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api/$api/fabric-api-$api.jar" "mods/fabric-api-$api.jar"
    launch=(java -Xmx2G -jar server.jar nogui)
    ;;
  forge)
    version="$mc-$(prop forge_version)"
    fetch "https://maven.minecraftforge.net/net/minecraftforge/forge/$version/forge-$version-installer.jar" installer.jar
    [[ -f run.sh ]] || java -jar installer.jar --installServer . > installer.log 2>&1 || { tail -20 installer.log; exit 1; }
    launch=(bash run.sh nogui)
    ;;
  neoforge)
    version="$(prop neoforge_version)"
    fetch "https://maven.neoforged.net/releases/net/neoforged/neoforge/$version/neoforge-$version-installer.jar" installer.jar
    [[ -f run.sh ]] || java -jar installer.jar --install-server . > installer.log 2>&1 || { tail -20 installer.log; exit 1; }
    launch=(bash run.sh nogui)
    ;;
  *) echo "unknown loader $loader" >&2; exit 2 ;;
esac

cp "$jar" mods/
echo "eula=true" > eula.txt
cat > server.properties <<PROPS
server-port=$((25600 + RANDOM % 2000))
online-mode=false
spawn-protection=0
view-distance=6
simulation-distance=6
PROPS

log="$work/server.log"
rm -f console && mkfifo console
"${launch[@]}" < console > "$log" 2>&1 &
pid=$!
exec 3> console
deadline=$((SECONDS + 900))
status=1
while kill -0 "$pid" 2>/dev/null; do
  if grep -qE 'Done \([0-9.]+s\)!' "$log"; then status=0; break; fi
  if grep -qE 'Crash report|Exception in server tick loop|Failed to start the minecraft server' "$log"; then break; fi
  if (( SECONDS > deadline )); then echo "timeout" >> "$log"; break; fi
  sleep 2
done
echo "stop" >&3
for _ in $(seq 60); do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
kill "$pid" 2>/dev/null
exec 3>&-
wait "$pid" 2>/dev/null
rm -f console

if ! grep -q "Sprout & Soil: .* crops" "$log"; then
  echo "Sprout & Soil did not initialise"; status=1
fi
errors=$(grep -E '/(ERROR|FATAL)\]|Mixin apply failed|InvalidInjectionException|Couldn.t parse|Failed to (load|parse)|Unknown (item|block|tag)|Parsing error|validation problem' "$log" \
  | grep -viE 'realms|server\.properties|eula\.txt' | head -40)
if [[ -n "$errors" ]]; then
  echo "---- errors ----"; echo "$errors"; status=1
fi
grep -hE "Sprout & Soil: |Done \(" "$log" | head -3
echo "prod_server($mc $loader) status=$status jar=$(basename "$jar") log=$log"
exit $status
