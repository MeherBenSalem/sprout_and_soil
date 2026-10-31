#!/usr/bin/env bash
# Starts the development client of one workspace/loader on a virtual display, loads a world full of
# Sprout & Soil blocks, takes a screenshot and checks the log for model, texture and mod errors.
#
#   tools/qa/client_boot.sh <minecraft> <loader> [out-dir]
#
# Needs Xvfb, Mesa (software OpenGL) and ImageMagick's `import`. The world is the one written by
# tools/qa/prod_server.sh for the same target (run that first), staged with tools/showcase/make_showcase.py.
set -u
mc="${1:?minecraft version}"
loader="${2:?fabric, forge or neoforge}"
repo="$(cd "$(dirname "$0")/../.." && pwd)"
out="${3:-$repo/build/qa/screens}"
mkdir -p "$out"
ws="$repo/$mc"
world="$repo/build/qa/$mc-$loader/world"
[[ -d "$world" ]] || { echo "no server world at $world - run tools/qa/prod_server.sh $mc $loader first" >&2; exit 2; }
case "$(grep -E '^java_version=' "$ws/gradle.properties" | cut -d= -f2)" in
  17) export JAVA_HOME="${JAVA_HOME_17:-/usr/lib/jvm/java-17-openjdk-amd64}" ;;
  *) export JAVA_HOME="${JAVA_HOME_21:-/usr/lib/jvm/java-21-openjdk-amd64}" ;;
esac

client="$ws/$loader/runs/client"
mkdir -p "$client/saves"
rm -rf "$client/saves/qa"
cp -r "$world" "$client/saves/qa"
rm -f "$client/saves/qa/session.lock"
python3 "$repo/tools/showcase/make_showcase.py" "$client/saves/qa" --mc "$mc" > /dev/null
cat > "$client/options.txt" <<OPT
onboardAccessibility:false
tutorialStep:none
joinedFirstServer:true
skipMultiplayerWarning:true
renderDistance:6
simulationDistance:6
guiScale:2
graphicsMode:1
narrator:0
soundCategory_master:0.0
pauseOnLostFocus:false
OPT

display=":$((70 + RANDOM % 20))"
Xvfb "$display" -screen 0 1600x900x24 >/dev/null 2>&1 &
xvfb=$!
export DISPLAY="$display"
sleep 2
log="$out/client-$mc-$loader.log"
if [[ "$loader" == "fabric" ]]; then
  task=(":fabric:runClient" --args="--quickPlaySingleplayer qa --width 1600 --height 900")
else
  task=(":$loader:runQaClient")   # ModDevGradle runs take their arguments from build.gradle
fi
# own process group, so the game, Gradle and its workers can be stopped together
setsid bash -c 'cd "$1" && shift && exec ./gradlew "$@" --no-daemon --max-workers=2' _ "$ws" "${task[@]}" > "$log" 2>&1 &
gradle=$!
deadline=$((SECONDS + 1800))
status=1
while (( SECONDS < deadline )) && kill -0 "$gradle" 2>/dev/null; do
  if grep -qE 'joined the game' "$log"; then
    sleep 25
    import -display "$display" -window root "$out/client-$mc-$loader.png" && status=0
    break
  fi
  if grep -qE 'Crash report|Exception in thread "Render thread"|BUILD FAILED|---- Minecraft Crash Report' "$log"; then break; fi
  sleep 2
done
kill -TERM -- "-$gradle" 2>/dev/null
sleep 3
kill -KILL -- "-$gradle" 2>/dev/null
kill "$xvfb" 2>/dev/null
wait 2>/dev/null

errors=$(grep -E 'sprout_and_soil' "$log" | grep -iE 'missing|unable|exception|error|failed|unknown' | head -30)
errors+=$(grep -E '/(ERROR|FATAL)\]' "$log" | grep -viE 'realms|telemetry|narrator|sound|OpenAL|joystick|gamepad' | head -20)
if [[ -n "$errors" ]]; then
  echo "---- errors ----"; echo "$errors"; status=1
fi
grep -hE "Sprout & Soil: |joined the game" "$log" | head -2
echo "client_boot($mc $loader) status=$status screenshot=$out/client-$mc-$loader.png log=$log"
exit $status
