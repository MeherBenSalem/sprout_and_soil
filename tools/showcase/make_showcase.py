#!/usr/bin/env python3
"""Builds a datapack that stages an in-game showcase of Sprout & Soil content and flies a spectator
camera through it. Used with tools/showcase/capture.sh to take real client screenshots.

    python3 tools/showcase/make_showcase.py <world-dir>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assetgen"))
from sas import spec  # noqa: E402

M = "sprout_and_soil"
Y = 160  # build platform height (above terrain)
SCENE_TICKS = 300


def build_commands() -> list[str]:
    c = [
        "gamerule doDaylightCycle false", "gamerule doWeatherCycle false", "gamerule doMobSpawning false",
        "gamerule randomTickSpeed 0", "time set 6000", "weather clear",
        f"fill -6 {Y - 1} -6 60 {Y - 1} 46 minecraft:grass_block",
        f"fill -6 {Y} -6 60 {Y + 12} 46 minecraft:air",
    ]
    # ---- scene 1: crop field, every crop ripe, 4 rows of 10 with water channels
    for i, crop in enumerate(spec.CROPS):
        row, col = divmod(i, 10)
        x, z = col * 2, row * 3
        c.append(f"setblock {x} {Y - 1} {z} minecraft:farmland[moisture=7]")
        c.append(f"setblock {x} {Y} {z} {M}:{crop.block}[age=7]")
        c.append(f"setblock {x} {Y - 1} {z + 1} minecraft:farmland[moisture=7]")
        c.append(f"setblock {x} {Y} {z + 1} {M}:{crop.block}[age=4]")
    # ---- scene 2: orchard, a small tree per fruit, saplings and wild gardens in front
    for i, tree in enumerate(spec.TREES):
        x, z = 26 + (i % 6) * 6, 2 + (i // 6) * 8
        log = tree.log
        for dy in range(4):
            c.append(f"setblock {x} {Y + dy} {z} {log}[axis=y]")
        c.append(f"fill {x - 2} {Y + 3} {z - 2} {x + 2} {Y + 4} {z + 2} {M}:{tree.leaves}[age=3,persistent=true] keep")
        c.append(f"fill {x - 1} {Y + 5} {z - 1} {x + 1} {Y + 5} {z + 1} {M}:{tree.leaves}[age=1,persistent=true] keep")
        c.append(f"setblock {x} {Y + 6} {z} {M}:{tree.leaves}[age=2,persistent=true]")
        c.append(f"setblock {x + 2} {Y} {z + 3} {M}:{tree.sapling}")
    for i, g in enumerate(spec.GARDENS):
        c.append(f"setblock {26 + i * 3} {Y} 20 {M}:{g.id}")
    # ---- scene 3: kitchen & farm hardware
    kx, kz = 2, 28
    c += [
        f"fill {kx - 2} {Y - 1} {kz - 2} {kx + 22} {Y - 1} {kz + 10} minecraft:spruce_planks",
        f"setblock {kx} {Y} {kz} minecraft:campfire[lit=true]",
        f"setblock {kx} {Y + 1} {kz} {M}:cooking_pot[facing=south]",
        f"setblock {kx + 2} {Y} {kz} minecraft:oak_planks",
        f"setblock {kx + 2} {Y + 1} {kz} {M}:cutting_board[facing=south]",
        f'data merge block {kx + 2} {Y + 1} {kz} {{Item:{{id:"minecraft:beef",count:1}}}}',
        f"setblock {kx + 4} {Y} {kz} minecraft:oak_planks",
        f"setblock {kx + 4} {Y + 1} {kz} {M}:cutting_board[facing=south]",
        f'data merge block {kx + 4} {Y + 1} {kz} {{Item:{{id:"{M}:tomato",count:1}}}}',
        f"setblock {kx + 7} {Y} {kz} {M}:scarecrow[facing=south]",
        f"setblock {kx + 9} {Y} {kz} {M}:sprinkler",
        f"setblock {kx + 10} {Y} {kz} minecraft:water_cauldron[level=3]",
    ]
    feasts = [f.id for f in spec.FEASTS]
    for i, f in enumerate(feasts):
        c.append(f"setblock {kx + i * 2} {Y} {kz + 3} minecraft:oak_planks")
        state = "[servings_taken=1]" if f in ("apple_pie", "pizza") else ""
        if f == "chocolate_cake":
            state = "[bites=2]"
        c.append(f"setblock {kx + i * 2} {Y + 1} {kz + 3} {M}:{f}{state}")
    for i, crate in enumerate(spec.crate_sources()):
        x = kx + (i % 12)
        y = Y + (i // 12)
        c.append(f"setblock {x} {y} {kz + 7} {M}:{crate}")
    c.append(f"forceload remove all")
    return c


SCENES = [
    # (x, y, z, yaw, pitch) camera positions, SCENE_TICKS each
    (9.5, Y + 6.5, -6.5, 0, 30),        # crop field overview
    (3.5, Y + 2.2, -2.0, 0, 18),        # crop close-up, first rows
    (12.5, Y + 2.2, 5.0, 0, 18),        # crop close-up, later rows
    (41.0, Y + 8.0, -9.0, 0, 22),       # orchard overview
    (27.5, Y + 3.5, -3.0, 0, 8),        # orchard close-up
    (38.0, Y + 1.8, 15.0, 0, 15),       # gardens
    (7.0, Y + 3.2, 22.0, 0, 28),        # kitchen workstations
    (6.5, Y + 2.8, 27.0, 0, 35),        # pot, boards close
    (8.0, Y + 3.5, 30.5, 0, 25),        # feasts and crates
]


def main() -> None:
    world = Path(sys.argv[1])
    pack = world / "datapacks" / "showcase"
    fn = pack / "data" / "showcase" / "function"
    tags = pack / "data" / "minecraft" / "tags" / "function"
    fn.mkdir(parents=True, exist_ok=True)
    tags.mkdir(parents=True, exist_ok=True)
    (pack / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 48, "description": "Sprout & Soil showcase"}}))
    (tags / "load.json").write_text(json.dumps({"values": ["showcase:load"]}))
    (tags / "tick.json").write_text(json.dumps({"values": ["showcase:tick"]}))
    (fn / "load.mcfunction").write_text("\n".join([
        "scoreboard objectives add showcase dummy",
        "scoreboard players set #t showcase 0",
        "forceload add -16 -16 64 48",
    ]) + "\n")
    (fn / "build.mcfunction").write_text("\n".join(build_commands()) + "\n")
    tick = ["scoreboard players add #t showcase 1",
            "execute if score #t showcase matches 60 run function showcase:build",
            "gamemode spectator @a"]
    start = 120
    for i, (x, y, z, yaw, pitch) in enumerate(SCENES):
        lo, hi = start + i * SCENE_TICKS, start + (i + 1) * SCENE_TICKS - 1
        tick.append(f"execute if score #t showcase matches {lo}..{hi} as @a run tp @s {x} {y} {z} {yaw} {pitch}")
        tick.append(f'execute if score #t showcase matches {lo} run say SCENE {i}')
    (fn / "tick.mcfunction").write_text("\n".join(tick) + "\n")
    print(f"showcase datapack written to {pack} ({len(build_commands())} build commands, {len(SCENES)} scenes)")


if __name__ == "__main__":
    main()
