#!/usr/bin/env python3
"""Captures the listing screenshots in marketing/images/screenshots/ from the real game.

1. world  - a fresh Minecraft 1.21.1 world from the Fabric production server that
            ``tools/qa/prod_server.sh 1.21.1 fabric`` sets up (seed SEED). ``locate biome minecraft:plains``
            picks the build site.
2. stage  - a datapack flattens the site and builds a farm (all 40 crops, sprinklers, a scarecrow), an
            orchard (the 12 fruit trees), an open-air kitchen (cooking pots on campfires, cutting boards,
            pies, pizza, cakes, crates) and a meadow of wild gardens. Everything is placed with commands;
            everything that moves (steam, sprinkler spray, watering, the cooking pot screen) is the mod running.
3. shoot  - the 1.21.1 Fabric dev client opens the world in a 1920x1080 window on a virtual display (Xvfb).
            The script steps through the scenes with ``/trigger sas_next`` and takes each picture with
            ImageMagick ``import``: every screenshot is one unedited frame.

    python3 marketing/source/capture.py              # every scene
    python3 marketing/source/capture.py farm kitchen # some scenes (the others are skipped quickly)

Needs Python 3, Xvfb, Mesa, xdotool and ImageMagick.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "assetgen"))
from sas import spec  # noqa: E402

M = "sprout_and_soil"
SEED = 7201193855
WS = ROOT / "1.21.1"
SERVER_TEMPLATE = ROOT / "build" / "qa" / "1.21.1-fabric"
WORK = ROOT / "build" / "marketing"
CLIENT = WS / "fabric" / "runs" / "client"
OUT = ROOT / "marketing" / "images" / "screenshots"
JAVA = Path(os.environ.get("JAVA_HOME_21", "/usr/lib/jvm/java-21-openjdk-amd64"))
DISPLAY = ":61"
W, H = 1920, 1080
ORIGIN = "@e[type=marker,tag=sas_origin,limit=1]"


# =========================================================================== layout (relative to the site)

def rel(x, y, z, cmd: str) -> str:
    """A command run at the site origin (ground level y=0) with ~x ~y ~z substituted."""
    return f"execute at {ORIGIN} run " + cmd.replace("{p}", f"~{x} ~{y} ~{z}")


def setblock(x, y, z, block: str) -> str:
    return rel(x, y, z, "setblock {p} " + block)


def fill(x1, y1, z1, x2, y2, z2, block: str) -> list[str]:
    """fill, split into pieces under the 32768-block limit."""
    out = []
    step = 16
    for bx in range(min(x1, x2), max(x1, x2) + 1, step):
        for bz in range(min(z1, z2), max(z1, z2) + 1, step):
            ex, ez = min(bx + step - 1, max(x1, x2)), min(bz + step - 1, max(z1, z2))
            out.append(f"execute at {ORIGIN} run fill ~{bx} ~{y1} ~{bz} ~{ex} ~{y2} ~{ez} {block}")
    return out


def noise(*args) -> float:
    """Deterministic 0..1 'random' value."""
    h = 2166136261
    for a in args:
        for ch in str(a):
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h / 0xFFFFFFFF


BANDS = [  # back (north) to front (south): tall bushy crops at the back, low leafy ones in front
    ["corn", "grape", "raspberry", "blackberry", "coffee", "tea", "cotton", "peppercorn"],
    ["tomato", "bell_pepper", "chili_pepper", "eggplant", "cucumber", "zucchini", "green_bean", "asparagus"],
    ["rice", "barley", "oat", "soybean", "peanut", "sweet_potato", "ginger", "basil"],
    ["lettuce", "cabbage", "spinach", "broccoli", "cauliflower", "celery", "leek", "mint"],
    ["strawberry", "blueberry", "cranberry", "pineapple", "garlic", "onion", "radish", "turnip"],
]
FIELD_X0 = -12          # 8 crops x 3 blocks: x -12..11
FIELD_Z0 = -9           # band b: rows z0+3b, z0+3b+1, water z0+3b+2
TREES_AT = [(x, z) for z in (-31, -21) for x in (-25, -15, -5, 5, 15, 25)]
BLOSSOMING = {"sweet_cherry", "peach", "plum"}
POTS = [(22, -4), (25, -4)]
TABLE_Z = 1


def build() -> list[str]:
    crops = {c.id: c for c in spec.CROPS}
    assert sorted(sum(BANDS, [])) == sorted(crops), "every crop appears exactly once in BANDS"
    c: list[str] = []
    # ---- the site: flatten 73x73, grass on top
    c += fill(-36, 0, -36, 36, 26, 36, "minecraft:air")
    c += fill(-36, -5, -36, 36, -2, 36, "minecraft:dirt")
    c += fill(-36, -1, -36, 36, -1, 36, "minecraft:grass_block")
    for d in range(1, 13):  # terrace the surroundings down to the site instead of leaving a cliff
        r = 36 + d
        for x1, z1, x2, z2 in ((-r, -r, r, -r), (-r, r, r, r), (-r, -r, -r, r), (r, -r, r, r)):
            c += fill(x1, d, z1, x2, 30, z2, "minecraft:air")
            c += fill(x1, d - 1, z1, x2, d - 1, z2, "minecraft:grass_block replace minecraft:dirt")
            c += fill(x1, d - 1, z1, x2, d - 1, z2, "minecraft:grass_block replace minecraft:stone")
    for x in range(-36, 37, 1):
        for z in range(-36, 37, 1):
            n = noise("deco", x, z)
            if abs(x) <= 16 and -12 <= z <= 9 or (17 <= x <= 31 and -9 <= z <= 7):
                continue  # field and kitchen stay clear
            if n < 0.16:
                c.append(setblock(x, 0, z, "minecraft:short_grass"))
            elif n < 0.18:
                c.append(setblock(x, 0, z, ["minecraft:poppy", "minecraft:dandelion", "minecraft:oxeye_daisy",
                                            "minecraft:cornflower"][int(n * 1000) % 4]))
    # ---- the field: 5 bands of 8 crops, water channels between, a path all around
    c += fill(-14, -1, -11, 13, -1, 8, "minecraft:dirt_path")
    for b, band in enumerate(BANDS):
        z0 = FIELD_Z0 + b * 3
        c += fill(FIELD_X0, -1, z0, FIELD_X0 + 23, -1, z0 + 1, "minecraft:farmland[moisture=7]")
        if b < len(BANDS) - 1:
            c += fill(FIELD_X0, -1, z0 + 2, FIELD_X0 + 23, -1, z0 + 2, "minecraft:water")
        for i, crop_id in enumerate(band):
            crop = crops[crop_id]
            for dx in range(3):
                for dz in range(2):
                    x, z = FIELD_X0 + i * 3 + dx, z0 + dz
                    age = 7 if crop.perennial or noise(crop_id, dx, dz) < 0.75 else 6
                    c.append(setblock(x, 0, z, f"{M}:{crop.block}[age={age}]"))
    for x in (-6, 6):
        c.append(setblock(x, 0, FIELD_Z0 + 5, f"{M}:sprinkler"))
        c.append(setblock(x, 0, FIELD_Z0 + 11, f"{M}:sprinkler"))
    c.append(setblock(-14, 0, -2, f"{M}:scarecrow[facing=east]"))
    c.append(setblock(13, 0, 4, f"{M}:scarecrow[facing=west]"))
    for x in (-14, 13):
        for z in (-11, 8):
            c.append(setblock(x, 0, z, "minecraft:oak_fence"))
            c.append(setblock(x, 1, z, "minecraft:lantern"))
    c.append(setblock(-15, 0, 4, "minecraft:composter[level=5]"))
    c.append(setblock(-15, 0, 5, "minecraft:hay_block"))
    c.append(setblock(-15, 1, 5, "minecraft:hay_block"))
    c.append(setblock(-16, 0, 5, "minecraft:hay_block"))
    # ---- the orchard: 12 fruit trees in two rows, saplings between them
    for i, tree in enumerate(spec.TREES):
        x, z = TREES_AT[i]
        trunk = 4 if tree.id not in ("mango", "avocado", "banana") else 5
        for dy in range(trunk):
            c.append(setblock(x, dy, z, f"{tree.log}[axis=y]"))
        top = trunk
        layers = [(top - 2, 2, True), (top - 1, 2, True), (top, 1, False), (top + 1, 0, False)]
        for y, r, cut_corners in layers:
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if cut_corners and abs(dx) == r and abs(dz) == r:
                        continue
                    if (dx, dz) == (0, 0) and y < top:
                        continue
                    n = noise(tree.id, dx, y, dz)
                    if tree.id in BLOSSOMING:
                        age = 1 if n < 0.85 else 0
                    else:
                        age = 3 if n < 0.62 else (2 if n < 0.82 else 0)
                    c.append(setblock(x + dx, y, z + dz,
                                      f"{M}:{tree.leaves}[age={age},persistent=true,distance=1]"))
        c.append(setblock(x + 3, 0, z + 4, f"{M}:{tree.sapling}"))
    # ---- the kitchen: an open spruce pavilion
    c += fill(18, -1, -8, 30, -1, 6, "minecraft:spruce_planks")
    for x in (18, 24, 30):
        for z in (-8, 6):
            c += fill(x, 0, z, x, 3, z, "minecraft:stripped_spruce_log")
    c += fill(18, 4, -8, 30, 4, 6, "minecraft:spruce_slab[type=bottom]")
    c += fill(19, 4, -7, 29, 4, 5, "minecraft:spruce_slab[type=top]")
    for x in (20, 23, 26, 29):
        c.append(setblock(x, 3, -1, "minecraft:lantern[hanging=true]"))
    # back counter with cutting boards
    c += fill(19, 0, -7, 29, 0, -7, "minecraft:spruce_planks")
    boards = [(20, "minecraft:beef"), (21, f"{M}:tomato"), (27, "minecraft:pumpkin"), (28, f"{M}:eggplant")]
    for x, item in boards:
        c.append(setblock(x, 1, -7, f"{M}:cutting_board[facing=south]"))
        c.append(rel(x, 1, -7, "data merge block {p} {Item:{id:\"" + item + "\",count:1}}"))
    c.append(setblock(23, 1, -7, f"{M}:{'apple'}_crate"))
    c.append(setblock(24, 1, -7, "minecraft:flower_pot"))
    c.append(setblock(19, 1, -7, "minecraft:barrel[facing=up]"))
    c.append(setblock(29, 1, -7, "minecraft:barrel[facing=up]"))
    # two pots over campfires
    for x, z in POTS:
        c.append(setblock(x, 0, z, "minecraft:campfire[lit=true,signal_fire=false]"))
        c.append(setblock(x, 1, z, f"{M}:cooking_pot[facing=south]"))
    # the feast table
    c += fill(20, 0, TABLE_Z, 28, 0, TABLE_Z, "minecraft:stripped_oak_log[axis=x]")
    feasts = {"apple_pie": 20, "chocolate_cake": 22, "pizza": 24, "berry_pie": 26, "carrot_cake": 28}
    for f, x in feasts.items():
        state = "[servings_taken=1]" if f == "pizza" else ("[bites=1]" if f == "carrot_cake" else "")
        c.append(setblock(x, 1, TABLE_Z, f"{M}:{f}{state}"))
    c.append(setblock(21, 1, TABLE_Z, f"{M}:cherry_pie"))
    # crate wall on the east side, 3 high
    crates = list(spec.crate_sources())
    for i, crate in enumerate(crates[:21]):
        c.append(setblock(31, i // 7, -5 + i % 7, f"{M}:{crate}"))
    for i, crate in enumerate(crates[21:]):
        c.append(setblock(28 - i, 0, 4, f"{M}:{crate}"))
    # ---- wild gardens in the meadow to the west
    for i, g in enumerate(spec.GARDENS):
        for k in range(3):
            if noise(g.id, k) < 0.8:
                c.append(setblock(-27 + i, 0, -1 + k, f"{M}:{g.id}"))
    return c


# =========================================================================== scenes


def look(cam, target) -> tuple[float, float]:
    dx, dy, dz = target[0] - cam[0], target[1] - cam[1], target[2] - cam[2]
    yaw = math.degrees(math.atan2(-dx, dz))
    pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return round(yaw, 1), round(pitch, 1)


@dataclass
class Scene:
    name: str
    cam: tuple                       # eye position, relative to the site
    target: tuple                    # what the camera looks at
    mode: str = "spectator"          # spectator, creative or survival
    hand: str | None = None          # item for the main hand (creative/survival scenes)
    hud: bool = False                # False: F1 (no hotbar, hand or chat)
    action: str | None = None        # None, "use" (one right-click) or "hold" (keep right button down)
    setup: list = field(default_factory=list)
    settle: float = 12.0             # seconds before the picture (chunks, particles, chat fade)
    frames: int = 1                  # pictures taken 0.6 s apart (spray, steam); the busiest one is kept


def pot_items() -> list[str]:
    x, z = POTS[0]
    items = ",".join([f'{{Slot:{i}b,id:"{M}:{item}",count:{n}}}' for i, (item, n) in enumerate(
        [("tomato", 6), ("tomato", 5), ("onion", 4), ("salt", 8)])]
        + [f'{{Slot:6b,id:"minecraft:bowl",count:7}}', f'{{Slot:7b,id:"{M}:tomato_soup",count:3}}'])
    return [rel(x, 1, z, "data merge block {p} {Items:[" + items + "]}")]


SCENES = [
    Scene("farm", (-3, 9, 19), (4, 0, -10)),
    Scene("field", (-15.5, 4.2, 7.5), (2, 0.2, -5)),
    Scene("crops", (-7.5, 3.3, -2.6), (-4.5, 0.2, -5.6)),
    Scene("corn", (-4, 4.0, -5.4), (-11, 1.2, -9)),
    Scene("orchard", (2, 4.5, -8), (0, 2.5, -28)),
    Scene("blossom", (-19, 3.0, -14.5), (-18, 3.6, -21.5)),
    Scene("fruit", (-17.5, 4.2, -24), (-15, 3.0, -31)),
    Scene("kitchen", (21, 2.6, 12), (25, 0.8, -4), frames=3),
    Scene("pots", (23.5, 4.2, -1.0), (23.5, 1.0, -4.2), frames=3),
    Scene("boards", (19.8, 2.4, -4.9), (20.8, 1.05, -7.0)),
    Scene("feast", (24.0, 4.0, 3.6), (24, 1.0, 1.0)),
    Scene("crates", (26.5, 2.6, -1.0), (31, 1.2, -2)),
    Scene("gardens", (-24, 1.9, 4.4), (-24, 0.3, 0.3)),
    Scene("scarecrow", (-17.5, 3.5, 1.5), (-14, 1.0, -2)),
    Scene("sprinkler", (-3.6, 2.7, -2.4), (-5.5, 0.3, -3.6), frames=6, settle=8.0),
    Scene("pot_gui", (22.5, 1.62, -1.5), (22.5, 1.45, -3.6), mode="creative", action="use", hud=True,
          setup=pot_items(), settle=6.0),
    Scene("watering", (3.5, 1.62, 5.6), (3.5, 0.2, 3.0), mode="creative", hand=f"{M}:watering_can", hud=True,
          action="hold", settle=12.0, frames=3),
]


# =========================================================================== datapack


def datapack(world: Path, origin: tuple[int, int]) -> None:
    ox, oz = origin
    pack = world / "datapacks" / "showcase"
    if pack.exists():
        shutil.rmtree(pack)
    fn = pack / "data" / "showcase" / "function"
    tags = pack / "data" / "minecraft" / "tags" / "function"
    fn.mkdir(parents=True)
    tags.mkdir(parents=True)
    (pack / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 48, "description": "Sprout & Soil showcase"}}))
    (tags / "load.json").write_text(json.dumps({"values": ["showcase:load"]}))
    (tags / "tick.json").write_text(json.dumps({"values": ["showcase:tick"]}))
    (fn / "load.mcfunction").write_text("\n".join([
        "scoreboard objectives add sas dummy",
        "scoreboard objectives add sas_next trigger",
        "execute unless score #built sas matches 1 run scoreboard players set #built sas 0",
        "scoreboard players set #scene sas -1",
        f"forceload add {ox - 48} {oz - 48} {ox + 48} {oz + 48}",
        "gamerule doDaylightCycle false", "gamerule doWeatherCycle false", "gamerule doMobSpawning false",
        "gamerule randomTickSpeed 0", "gamerule doFireTick false", "gamerule sendCommandFeedback false",
        "gamerule announceAdvancements false", "gamerule doInsomnia false", "gamerule doPatrolSpawning false",
        "gamerule doTraderSpawning false", "gamerule showDeathMessages false",
        "time set 3000", "weather clear 1000000",
    ]) + "\n")
    origin_cmd = (f"execute unless entity {ORIGIN} positioned {ox} 0 {oz} positioned over motion_blocking_no_leaves "
                  "run summon marker ~ ~ ~ {Tags:[\"sas_origin\"]}")
    (fn / "build.mcfunction").write_text("\n".join(build() + [
        "kill @e[type=item]", "scoreboard players set #built sas 1", "say READY"]) + "\n")
    tick = [
        "execute if score #scene sas matches ..-1 run gamemode spectator @a",
        f"execute if score #built sas matches 0 run tp @a {ox} 120 {oz}",
        f"execute if score #built sas matches 1 if score #scene sas matches ..-1 at {ORIGIN} run tp @a ~20 ~14 ~22 140 25",
        f"execute if score #built sas matches 0 run {origin_cmd}",
        f"execute if score #built sas matches 0 if entity {ORIGIN} run scoreboard players add #wait sas 1",
        "execute if score #built sas matches 0 if score #wait sas matches 100.. run function showcase:build",
        "scoreboard players enable @a sas_next",
        "execute if entity @a[scores={sas_next=1..}] run function showcase:next",
    ]
    nxt = ["scoreboard players set @a sas_next 0", "scoreboard players add #scene sas 1"]
    for i, s in enumerate(SCENES):
        yaw, pitch = look(s.cam, s.target)
        x, y, z = s.cam
        # the origin marker stands on a block centre (integer command coordinates are centred), cameras use corners
        tick.append(f"execute if score #scene sas matches {i} at {ORIGIN} run "
                    f"tp @a ~{x - 0.5} ~{round(y - 1.62, 2)} ~{z - 0.5} {yaw} {pitch}")
        body = [f"gamemode {s.mode} @a", "clear @a", "kill @e[type=item]"]
        if s.hand:
            body.append(f"item replace entity @a weapon.mainhand with {s.hand}")
        body += s.setup
        body.append(f"say SCENE {s.name}")
        (fn / f"scene_{i}.mcfunction").write_text("\n".join(body) + "\n")
        nxt.append(f"execute if score #scene sas matches {i} run function showcase:scene_{i}")
    (fn / "tick.mcfunction").write_text("\n".join(tick) + "\n")
    (fn / "next.mcfunction").write_text("\n".join(nxt) + "\n")


# =========================================================================== world


def make_world() -> tuple[Path, tuple[int, int]]:
    """Generates the world on the production server and finds a plains build site."""
    if not (SERVER_TEMPLATE / "server.jar").exists():
        sys.exit("run tools/qa/prod_server.sh 1.21.1 fabric first (it sets up the server this script uses)")
    server = WORK / "server"
    if server.exists():
        shutil.rmtree(server)
    shutil.copytree(SERVER_TEMPLATE, server, ignore=shutil.ignore_patterns("world", "logs", "*.log", "console"))
    (server / "server.properties").write_text(f"level-name=showcase\nlevel-seed={SEED}\nonline-mode=false\n"
                                              "server-port=25890\nview-distance=4\nspawn-protection=0\n")
    log = (server / "showcase.log").open("w")
    proc = subprocess.Popen([str(JAVA / "bin" / "java"), "-Xmx2G", "-jar", "server.jar", "nogui"], cwd=server,
                            stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT, text=True)
    text = wait_for(server / "showcase.log", r"Done \(", 600)
    proc.stdin.write("locate biome minecraft:plains\n")
    proc.stdin.flush()
    text = wait_for(server / "showcase.log", r"nearest minecraft:plains is at \[(-?\d+), (?:~|-?\d+), (-?\d+)\]", 300)
    x, z = map(int, re.search(r"nearest minecraft:plains is at \[(-?\d+), (?:~|-?\d+), (-?\d+)\]", text).groups())
    proc.stdin.write("stop\n")
    proc.stdin.flush()
    proc.wait(120)
    # step 40 blocks further in the direction away from spawn, into the biome
    d = math.hypot(x, z) or 1
    site = (int(x + 40 * x / d), int(z + 40 * z / d))
    print(f"plains at {x},{z} -> site {site}")
    return server / "showcase", site


def wait_for(path: Path, pattern: str, timeout: float) -> str:
    end = time.time() + timeout
    while time.time() < end:
        text = path.read_text(errors="replace") if path.exists() else ""
        if re.search(pattern, text):
            return text
        if "Crash report" in text or "BUILD FAILED" in text:
            raise RuntimeError(f"failure in {path}")
        time.sleep(1)
    raise TimeoutError(f"{pattern!r} not seen in {path}")


# =========================================================================== shooting


def xdo(*args) -> None:
    subprocess.run(["xdotool", *args], env={**os.environ, "DISPLAY": DISPLAY}, check=False)


def grab(path: Path) -> None:
    subprocess.run(["import", "-display", DISPLAY, "-window", "root", str(path)], check=True)


def busiest(frames: list[Path]) -> Path:
    """Frame with the most changed pixels against the median (most spray, steam or splash)."""
    from PIL import Image, ImageChops, ImageStat
    if len(frames) == 1:
        return frames[0]
    imgs = [Image.open(f).convert("L").resize((480, 270)) for f in frames]
    scores = []
    for i, img in enumerate(imgs):
        others = [o for j, o in enumerate(imgs) if j != i]
        scores.append(sum(ImageStat.Stat(ImageChops.difference(img, o)).mean[0] for o in others))
    return frames[scores.index(max(scores))]


def shoot(world: Path, wanted: set[str]) -> None:
    saves = CLIENT / "saves"
    saves.mkdir(parents=True, exist_ok=True)
    target = saves / "showcase"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(world, target)
    (target / "session.lock").unlink(missing_ok=True)
    (CLIENT / "options.txt").write_text("\n".join([
        "onboardAccessibility:false", "tutorialStep:none", "joinedFirstServer:true", "skipMultiplayerWarning:true",
        "renderDistance:12", "simulationDistance:8", "guiScale:3", "graphicsMode:1", "ao:true", "fov:0.0",
        "renderClouds:\"true\"", "particles:0", "narrator:0", "soundCategory_master:0.0", "pauseOnLostFocus:false",
        "chatOpacity:1.0", "entityShadows:true", "biomeBlendRadius:5", "maxFps:60", "enableVsync:false",
    ]) + "\n")
    xvfb = subprocess.Popen(["Xvfb", DISPLAY, "-screen", "0", f"{W}x{H}x24"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    time.sleep(2)
    log_path = WORK / "client.log"
    env = {**os.environ, "DISPLAY": DISPLAY, "JAVA_HOME": str(JAVA)}
    client = subprocess.Popen(["./gradlew", ":fabric:runClient", "--no-daemon", "--max-workers=2",
                               f"--args=--quickPlaySingleplayer showcase --width {W} --height {H}"],
                              cwd=WS, env=env, stdout=log_path.open("w"), stderr=subprocess.STDOUT,
                              start_new_session=True)
    try:
        wait_for(log_path, r"\[Server\] READY", 1800)
        time.sleep(20)
        win = subprocess.run(["xdotool", "search", "--name", "Minecraft"], env=env, capture_output=True,
                             text=True).stdout.split()
        if win:
            xdo("windowfocus", win[-1])
        OUT.mkdir(parents=True, exist_ok=True)
        hud = True
        for i, s in enumerate(SCENES):
            xdo("key", "slash")
            time.sleep(0.8)
            xdo("type", "--delay", "40", "trigger sas_next")
            xdo("key", "Return")
            wait_for(log_path, rf"\[CHAT\] \[Server\] SCENE {s.name}\b", 120)
            if s.name not in wanted:
                continue
            if s.hud != hud:
                xdo("key", "F1")
                hud = s.hud
            time.sleep(s.settle)
            xdo("mousemove", str(W // 2), str(H // 2))
            if s.action == "use":
                xdo("mousedown", "3")
                time.sleep(0.25)
                xdo("mouseup", "3")
                time.sleep(4)
            elif s.action == "hold":
                xdo("mousedown", "3")
                time.sleep(2.5)
            frames = []
            for k in range(s.frames):
                frame = WORK / f"{s.name}_{k}.png"
                grab(frame)
                frames.append(frame)
                time.sleep(0.6)
            if s.action == "hold":
                xdo("mouseup", "3")
            if s.action == "use":
                xdo("key", "Escape")
                time.sleep(1)
            best = busiest(frames)
            subprocess.run(["convert", str(best), "-quality", "92", str(OUT / f"{s.name}.jpg")], check=True)
            print(f"captured {s.name}", flush=True)
    finally:
        os.killpg(client.pid, 15)
        time.sleep(3)
        try:
            os.killpg(client.pid, 9)
        except ProcessLookupError:
            pass
        xvfb.terminate()


def main() -> None:
    wanted = set(sys.argv[1:]) or {s.name for s in SCENES}
    unknown = wanted - {s.name for s in SCENES}
    if unknown:
        sys.exit(f"unknown scenes {sorted(unknown)}; known: {[s.name for s in SCENES]}")
    WORK.mkdir(parents=True, exist_ok=True)
    world, site = make_world()
    datapack(world, site)
    shoot(world, wanted)


if __name__ == "__main__":
    main()
