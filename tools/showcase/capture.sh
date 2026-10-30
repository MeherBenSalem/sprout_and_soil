#!/usr/bin/env bash
# Runs the real Fabric client on a virtual display, loads a showcase world and screenshots each scene.
# Usage: tools/showcase/capture.sh <out-dir>     (needs Xvfb, Mesa and ImageMagick's `import`)
set -u
out="${1:?output dir}"; mkdir -p "$out"
root="$(cd "$(dirname "$0")/../.." && pwd)"
ws="$root/1.21.1"
client="$ws/fabric/runs/client"
mkdir -p "$client/saves"
rm -rf "$client/saves/showcase"
cp -r "$ws/fabric/runs/server/world" "$client/saves/showcase"
python3 "$root/tools/showcase/make_showcase.py" "$client/saves/showcase"
cat > "$client/options.txt" <<OPT
onboardAccessibility:false
tutorialStep:none
joinedFirstServer:true
skipMultiplayerWarning:true
renderDistance:5
simulationDistance:5
guiScale:2
fov:0.25
graphicsMode:1
narrator:0
soundCategory_master:0.0
pauseOnLostFocus:false
OPT
export DISPLAY=:77
Xvfb :77 -screen 0 1600x900x24 >/dev/null 2>&1 &
xvfb=$!
sleep 2
log="$out/client.log"
(cd "$ws" && ./gradlew :fabric:runClient --no-daemon --max-workers=2 --args="--quickPlaySingleplayer showcase --width 1600 --height 900" > "$log" 2>&1) &
gradle=$!
deadline=$((SECONDS + 2400))
next=0
while (( SECONDS < deadline )) && kill -0 "$gradle" 2>/dev/null; do
  if grep -q "SCENE $next\b" "$log"; then
    sleep 11
    import -display :77 -window root "$out/scene_$next.png" && echo "captured scene $next"
    next=$((next + 1))
    [[ $next -ge 9 ]] && break
  fi
  if grep -qE "Crash report|Exception in thread \"Render thread\"|BUILD FAILED" "$log"; then echo "client failed"; break; fi
  sleep 1
done
pkill -f "fabric.*runClient\|KnotClient\|devlaunchinjector" 2>/dev/null
kill "$gradle" 2>/dev/null; kill "$xvfb" 2>/dev/null
wait 2>/dev/null
echo "captured $next scenes into $out"
