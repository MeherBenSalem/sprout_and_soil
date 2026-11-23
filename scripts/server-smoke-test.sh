#!/usr/bin/env bash
# Boots a dev server for one Minecraft version and loader and proves Sprout & Soil works at runtime, not only
# compiles (NightBeam convention; same pattern as NoMore63AE2's scripts/server-smoke-test.sh). A datapack, with no
# player online:
#   places every Sprout & Soil configured feature (12 fruit trees, 6 wild gardens) with /place feature on prepared pads,
#   places every structure template with /place template,
#   plants every fruit sapling on its own pad, bone-meals it from a dispenser and checks that each grew into its tree
#   (the sapling's tree grower finds its feature),
#   sets every Sprout & Soil block (crops, crates, feasts, cooking pot, cutting board, scarecrow, sprinkler...) on
#   farmland,
#   summons every Sprout & Soil item as an item entity and checks each one is still there a few ticks later
#   (an unknown or broken item is dropped as air),
#   then runs /save-all and a guarded /reload and stops.
# The mod has no commands and no entities of its own. Every class a mixin of this target applies to is loaded at
# startup (sprout_and_soil.qa.load_classes), so a broken injection fails here instead of when the first player joins.
# Fails on a crash report, a mixin error, an ERROR/WARN/exception line mentioning the mod, a failed command, a mixin
# target that did not load, or when the RAN/OK markers never show up.
#   usage: scripts/server-smoke-test.sh <1.20.1|1.21.1|26.2|26.3> <fabric|forge|neoforge>
set -u
VERSION="$1"; LOADER="$2"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/$VERSION"
MOD=sprout_and_soil
NS=sas_smoke
RUN="$LOADER/runs/server"
rm -rf "$RUN/world" "$RUN/crash-reports" "$RUN/logs"
PACK="$RUN/world/datapacks/$NS"
mkdir -p "$PACK"
echo "eula=true" > "$RUN/eula.txt"
cat > "$RUN/server.properties" <<PROPS
online-mode=false
function-permission-level=4
spawn-protection=0
view-distance=6
simulation-distance=6
level-seed=20261123
initial-enabled-packs=vanilla,file/$NS
PROPS
if [ "$LOADER" = forge ]; then
  # In the dev environment Forge's LAN advertiser loads a client-only class and can stop the server.
  mkdir -p "$RUN/defaultconfigs"
  printf '[server]\n\tadvertiseDedicatedServerToLan = false\n' > "$RUN/defaultconfigs/forge-server.toml"
fi

# pack.mcmeta as valid JSON, with the same format (range) as the mod's own pack (26.x uses min_format/max_format).
python3 - common/src/main/resources/pack.mcmeta "$PACK/pack.mcmeta" <<'PY'
import json, sys
src = json.load(open(sys.argv[1]))["pack"]
pack = {"description": "Sprout & Soil smoke test"}
for key in ("pack_format", "min_format", "max_format", "supported_formats"):
    if key in src:
        pack[key] = src[key]
json.dump({"pack": pack}, open(sys.argv[2], "w"))
PY
cat "$PACK/pack.mcmeta"; echo

# Every class a mixin of this target applies to (common and loader mixin configs), fully qualified from the mixin's
# imports. Client-only mixins are left out: a dedicated server never loads those classes.
TARGETS="$(python3 - "$MOD" "$LOADER" <<'PY'
import json, re, sys
from pathlib import Path
mod, loader = sys.argv[1], sys.argv[2]
out = []
for module in ("common", loader):
    res, src = Path(module, "src/main/resources"), Path(module, "src/main/java")
    for cfg_file in sorted(res.glob("*.mixins.json")):
        cfg = json.load(open(cfg_file))
        pkg = Path(*cfg["package"].split("."))
        for n in cfg.get("mixins", []) + cfg.get("server", []):
            text = (src / pkg / (n.replace(".", "/") + ".java")).read_text()
            imports = {m.group(2): m.group(1) + m.group(2) for m in re.finditer(r"^import ([\w.]+\.)(\w+);", text, re.M)}
            m = re.search(r"@Mixin\(\s*(?:value\s*=\s*)?\{?([^)}]*)\}?", text)
            for ref in re.findall(r"([\w.]+)\.class", m.group(1)):
                head, *rest = ref.split(".")
                fqn = imports.get(head, head) + "".join("$" + r for r in rest)
                if fqn not in out:
                    out.append(fqn)
print(",".join(out))
PY
)"
TARGET_COUNT=$(echo "$TARGETS" | tr ',' '\n' | grep -c .)
echo "Mixin targets ($TARGET_COUNT): $TARGETS"
export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -D$MOD.qa.load_classes=$TARGETS"

# What the mod adds, read from its own resources (datagen output and hand-written files).
ASSETS=common/src/generated/resources/assets/$MOD
DATA=common/src/generated/resources/data/$MOD
# Configured features live in worldgen/configured_feature up to 26.2 and in worldgen/feature from 26.3.
if [ -d "$DATA/worldgen/configured_feature" ]; then FEATURE_DIR="$DATA/worldgen/configured_feature"; else FEATURE_DIR="$DATA/worldgen/feature"; fi
FEATURES="$(cd "$FEATURE_DIR" && find . -name '*.json' | sed 's|^\./||; s|\.json$||' | sort)"
# Structure templates: structures/ up to 1.20.1, structure/ from 1.21.
TEMPLATES="$(for d in "$DATA/structures" "$DATA/structure"; do [ -d "$d" ] && (cd "$d" && find . -name '*.nbt' | sed 's|^\./||; s|\.nbt$||'); done | sort)"
BLOCKS="$(ls "$ASSETS/blockstates" | sed 's/\.json$//' | sort)"
# 26.x has an item model definition (assets/<mod>/items) for every item; earlier versions an item model for every item.
if [ -d "$ASSETS/items" ]; then ITEM_DIR="$ASSETS/items"; else ITEM_DIR="$ASSETS/models/item"; fi
ITEMS="$(ls "$ITEM_DIR" | sed 's/\.json$//' | sort)"
SAPLINGS="$(echo "$BLOCKS" | grep '_sapling$')"
FEATURE_COUNT=$(echo "$FEATURES" | grep -c .); TEMPLATE_COUNT=$(echo "$TEMPLATES" | grep -c .)
BLOCK_COUNT=$(echo "$BLOCKS" | grep -c .); ITEM_COUNT=$(echo "$ITEMS" | grep -c .); SAPLING_COUNT=$(echo "$SAPLINGS" | grep -c .)
echo "Features ($FEATURE_COUNT): $(echo $FEATURES)"
echo "Templates ($TEMPLATE_COUNT): $(echo $TEMPLATES)"
echo "Saplings ($SAPLING_COUNT), blocks ($BLOCK_COUNT), items ($ITEM_COUNT)"
[ "$FEATURE_COUNT" -gt 0 ] && [ "$BLOCK_COUNT" -gt 0 ] && [ "$ITEM_COUNT" -gt 0 ] && [ "$SAPLING_COUNT" -gt 0 ] \
  || { echo "::error::could not read the mod's features, blocks, items or saplings"; exit 1; }

if [ "$VERSION" = 1.20.1 ]; then COUNT='Count:1b'; else COUNT='count:1'; fi
case "$VERSION" in
  26.*) DAYLIGHT=advance_time; WEATHER=advance_weather; MOBS=spawn_mobs ;;
  *) DAYLIGHT=doDaylightCycle; WEATHER=doWeatherCycle; MOBS=doMobSpawning ;;
esac

# Pads for the features and saplings: 13x13, 16 blocks apart, four rows north of spawn, high above the terrain
# (dirt, grass on top, air above). The block garden is a 26x26 farmland field south-west of spawn.
SLOTS=()
for gz in -64 -48 -32 -16; do for gx in -64 -48 -32 -16 0 16 32 48 64; do SLOTS+=("$gx $gz"); done; done
[ $((FEATURE_COUNT + SAPLING_COUNT + TEMPLATE_COUNT)) -le ${#SLOTS[@]} ] || { echo "::error::not enough pads"; exit 1; }
pad() { # x z
  echo "fill $(($1-6)) 97 $(($2-6)) $(($1+6)) 98 $(($2+6)) minecraft:dirt"
  echo "fill $(($1-6)) 99 $(($2-6)) $(($1+6)) 99 $(($2+6)) minecraft:grass_block"
  echo "fill $(($1-6)) 100 $(($2-6)) $(($1+6)) 125 $(($2+6)) minecraft:air"
}

FN="$PACK/data/$NS"
for dir in function functions; do
  mkdir -p "$FN/$dir" "$PACK/data/minecraft/tags/$dir"
  echo "{\"values\":[\"$NS:start\"]}" > "$PACK/data/minecraft/tags/$dir/load.json"
  check() { # marker command...
    local marker="$1"; shift
    echo "scoreboard players set #r sas 0"
    echo "execute store success score #r sas run $*"
    echo "execute if score #r sas matches 1 run say SAS_OK $marker"
    echo "execute unless score #r sas matches 1 run say SAS_FAILED $marker"
  }
  {
    echo 'scoreboard objectives add sas dummy'
    # /reload in finish.mcfunction runs this load function again; only the first load starts the test.
    echo 'execute if score #started sas matches 1 run say SAS_SMOKE_RELOADED'
    echo "execute unless score #started sas matches 1 run function $NS:begin"
  } > "$FN/$dir/start.mcfunction"
  {
    echo 'scoreboard players set #started sas 1'
    echo 'forceload add -80 -80 80 80'
    echo "gamerule $DAYLIGHT false"
    echo "gamerule $WEATHER false"
    echo "gamerule $MOBS false"
    echo 'time set noon'
    echo 'weather clear'
    echo 'say SAS_SMOKE_LOADED'
    echo "schedule function $NS:build 300t"
  } > "$FN/$dir/begin.mcfunction"

  # Build every pad and the farmland field, then place a tick later.
  {
    i=0
    for _ in $FEATURES $SAPLINGS $TEMPLATES; do
      set -- ${SLOTS[$i]}; pad "$1" "$2"; i=$((i + 1))
    done
    echo "fill -66 97 14 -40 98 40 minecraft:dirt"
    echo "fill -66 99 14 -40 99 40 minecraft:farmland"
    echo "fill -66 100 14 -40 125 40 minecraft:air"
    echo 'say SAS_SMOKE_BUILT'
    echo "schedule function $NS:run 20t"
  } > "$FN/$dir/build.mcfunction"

  {
    i=0
    # Up to 1.21.1 a wild garden is a random patch whose 8 tries can all miss the pad; any of 5 placements counts.
    for f in $FEATURES; do
      set -- ${SLOTS[$i]}; i=$((i + 1))
      echo "scoreboard players set #g sas 0"
      for _ in 1 2 3 4 5; do
        echo "execute if score #g sas matches 0 store success score #g sas run place feature $MOD:$f $1 100 $2"
      done
      echo "execute if score #g sas matches 1 run say SAS_OK place_feature_$f"
      echo "execute unless score #g sas matches 1 run say SAS_FAILED place_feature_$f"
    done
    # Each sapling with a dispenser of bone meal east of it (pulsed by pulse.mcfunction).
    for s in $SAPLINGS; do
      set -- ${SLOTS[$i]}; i=$((i + 1))
      check "plant_$s" setblock "$1" 100 "$2" "$MOD:$s"
      echo "setblock $(($1+1)) 100 $2 minecraft:dispenser[facing=west]"
      echo "item replace block $(($1+1)) 100 $2 container.0 with minecraft:bone_meal 64"
    done
    for t in $TEMPLATES; do
      set -- ${SLOTS[$i]}; i=$((i + 1))
      check "place_template_$t" place template "$MOD:$t" "$(($1-4))" 100 "$(($2-4))"
    done
    # Every block on the farmland field, two blocks apart.
    j=0
    for b in $BLOCKS; do
      x=$((-64 + (j % 12) * 2)); z=$((16 + (j / 12) * 2)); j=$((j + 1))
      check "setblock_$b" setblock "$x" 100 "$z" "$MOD:$b"
    done
    # Every item as a floating item entity above the field east of it.
    j=0
    for it in $ITEMS; do
      x=$((-30 + (j % 20))); z=$((16 + (j / 20))); j=$((j + 1))
      check "summon_$it" summon minecraft:item "$x" 120 "$z" "{Item:{id:\"$MOD:$it\",$COUNT},Tags:[\"sas_smoke\",\"sas_i_$it\"],NoGravity:1b,PickupDelay:32767,Age:-32768}"
    done
    echo 'scoreboard players set #p sas 0'
    echo "schedule function $NS:pulse 10t"
    echo 'say SAS_SMOKE_RAN'
    echo "schedule function $NS:items 10t"
  } > "$FN/$dir/run.mcfunction"

  # Bone meal: 25 redstone pulses into every sapling's dispenser, 10 ticks apart (each has a 45% chance to advance it).
  {
    echo 'scoreboard players add #p sas 1'
    i=$FEATURE_COUNT
    for _ in $SAPLINGS; do set -- ${SLOTS[$i]}; i=$((i + 1)); echo "setblock $(($1+2)) 100 $2 minecraft:redstone_block"; done
    echo "schedule function $NS:unpulse 4t"
    echo "execute if score #p sas matches ..24 run schedule function $NS:pulse 10t"
  } > "$FN/$dir/pulse.mcfunction"
  {
    i=$FEATURE_COUNT
    for _ in $SAPLINGS; do set -- ${SLOTS[$i]}; i=$((i + 1)); echo "setblock $(($1+2)) 100 $2 minecraft:air"; done
  } > "$FN/$dir/unpulse.mcfunction"

  # An item that does not exist, or whose stack fails to load, leaves an empty item entity that is removed at once.
  {
    for it in $ITEMS; do
      check "item_$it" execute if entity "@e[type=minecraft:item,tag=sas_i_$it]"
    done
    echo "schedule function $NS:finish 600t"
  } > "$FN/$dir/items.mcfunction"

  {
    i=$FEATURE_COUNT
    for s in $SAPLINGS; do
      set -- ${SLOTS[$i]}; i=$((i + 1))
      # The sapling is gone and a trunk stands where it was: its tree grower found the fruit tree feature.
      check "grew_$s" execute unless block "$1" 100 "$2" "$MOD:$s" unless block "$1" 100 "$2" minecraft:air
    done
    check save save-all flush
    echo 'reload'
    echo "schedule function $NS:end 100t"
  } > "$FN/$dir/finish.mcfunction"

  {
    echo 'kill @e[tag=sas_smoke]'
    echo 'say SAS_SMOKE_OK'
    echo 'stop'
  } > "$FN/$dir/end.mcfunction"
done
EXPECTED_OK=$(cat "$FN/function/"*.mcfunction | grep -c "say SAS_OK")

LOG="$ROOT/server-smoke-$VERSION-$LOADER.log"
./gradlew ":$LOADER:runServer" --stacktrace -Porg.gradle.java.installations.fromEnv=JAVA_HOME_17_X64,JAVA_HOME_21_X64,JAVA_HOME_25_X64 < /dev/null > "$LOG" 2>&1 &
PID=$!
CRASH='This crash report has been saved|Encountered an unexpected exception|Failed to start the minecraft server|Mixin apply.*failed|InvalidInjectionException|MixinApplyError|MixinTransformerError|Mixin.*(error|failed)'
result=timeout
for _ in $(seq 1 240); do
  sleep 5
  if grep -q "SAS_SMOKE_OK" "$LOG"; then result=ok; break; fi
  if grep -q -E "$CRASH" "$LOG"; then result=crash; break; fi
  if ! kill -0 $PID 2>/dev/null; then result=exited; break; fi
done
sleep 10
pkill -P $PID 2>/dev/null; kill $PID 2>/dev/null; wait $PID 2>/dev/null

echo "===== markers"
grep -n -E "SAS_SMOKE|SAS_FAILED|QA: |Sprout & Soil:|Found new data pack" "$LOG" | head -80
for f in "$RUN"/crash-reports/*.txt; do [ -f "$f" ] && { echo "=== $f"; head -100 "$f"; }; done
echo "===== errors and warnings"
grep -n -E "ERROR|WARN|Exception|Caused by|[Mm]ixin.*(fail|error)|Failed to|Couldn't|Unknown" "$LOG" | grep -v -E "Download|Task :" | head -80
echo "Result: $result"

fail=0
[ "$result" = ok ] || { echo "::error::server did not reach SAS_SMOKE_OK ($result)"; fail=1; }
grep -q -E "$CRASH" "$LOG" && { echo "::error::crash or mixin error"; fail=1; }
grep -q "SAS_SMOKE_RAN" "$LOG" || { echo "::error::the smoke function never ran"; fail=1; }
grep -q "SAS_SMOKE_RELOADED" "$LOG" || { echo "::error::/reload never finished"; fail=1; }
if grep -n "SAS_FAILED" "$LOG"; then echo "::error::a command failed"; fail=1; fi
oks=$(grep -c "SAS_OK " "$LOG"); loaded=$(grep -c "QA: loaded " "$LOG")
echo "Commands OK: $oks of $EXPECTED_OK; mixin targets loaded: $loaded of $TARGET_COUNT"
[ "$oks" -ge "$EXPECTED_OK" ] || { echo "::error::not every command check passed"; fail=1; }
[ "$loaded" -ge "$TARGET_COUNT" ] || { echo "::error::not every mixin target class loaded"; fail=1; }
# (The checkout path is left out: it holds the repository name.)
# Errors, warnings and exceptions that mention the mod (its id, its logger name, its package or the smoke pack).
# (Mixin's "refmap could not be read" warning is expected in a dev environment, where names are not remapped.)
if grep -n -E "(ERROR|WARN|Exception|Caused by|Failed|Couldn't|Unknown|Errors in)" "$LOG" | sed "s|$ROOT|<checkout>|g" \
    | grep -v -E "JAVA_TOOL_OPTIONS|Reference map '$MOD.refmap.json' .* could not be read" \
    | grep -i -E "$MOD|Sprout & Soil|tn\.nightbeam\.sproutandsoil|$NS"; then
  echo "::error::error or warning mentioning the mod"; fail=1
fi
exit $fail
