"""The texture/model contract: every file the data generator will reference.

``python3 -m sas.contract`` prints a summary and writes build/texture_contract.json.
Paths are relative to ``assets/sprout_and_soil/`` (e.g. ``textures/item/tomato.png``).
Each entry belongs to one art *lane* so generators can be developed in parallel:

* plants   - crop growth stages, saplings, fruit leaves, wild gardens
* produce  - crop produce, seeds, fruits, crate textures
* kitchen  - ingredients, dishes, drinks, slices, containers, feast item icons
* hardware - tools, 3D workstation models, feast block textures & templates, GUI, effects, logo
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from . import spec
from .paths import BUILD


@dataclass
class Tex:
    path: str
    lane: str
    subject: str
    archetype: str = ""
    colors: list[str] = field(default_factory=list)
    desc: str = ""
    size: str = "16x16"


def _art(i):
    return (i.art.archetype, i.art.colors, i.art.desc) if i.art else ("", [], "")


def build() -> list[Tex]:
    out: list[Tex] = []

    # ---------------------------------------------------------------- plants
    for c in spec.CROPS:
        for n in range(4):
            out.append(Tex(f"textures/block/{c.id}_stage{n}.png", "plants", c.id, f"crop:{c.model}",
                           [c.leaf] + (c.produce.art.colors if c.produce.art else []),
                           f"growth stage {n}/3 ({['sprout', 'young', 'flowering/maturing', 'ripe'][n]}); {c.stage_art}"))
        if c.model == "tall":
            for n in (2, 3):
                out.append(Tex(f"textures/block/{c.id}_stage{n}_top.png", "plants", c.id, "crop:tall_top",
                               [c.leaf] + c.produce.art.colors, f"upper block of stage {n}; {c.stage_art}"))
    for t in spec.TREES:
        out.append(Tex(f"textures/block/{t.sapling}.png", "plants", t.id, "sapling", t.leaf_colors,
                       f"{t.display} sapling (trunk like {t.log}); show a tiny fruit or blossom hint"))
        fruit_colors = [] if isinstance(t.fruit, str) else t.fruit.art.colors
        if isinstance(t.fruit, str):
            fruit_colors = ["#d0302a"]
        for n, what in enumerate(["plain leaves", f"leaves with {t.blossom} blossoms",
                                  "leaves with small unripe (green-ish) fruit", "leaves with ripe fruit"]):
            out.append(Tex(f"textures/block/{t.leaves}_{n}.png", "plants", t.id, "fruit_leaves",
                           t.leaf_colors + [t.blossom] + fruit_colors,
                           f"tileable leaves block texture, {what}; cutout (transparent gaps like vanilla leaves)"))
    for g in spec.GARDENS:
        out.append(Tex(f"textures/block/{g.id}.png", "plants", g.id, "garden", g.art.colors, g.art.desc))

    # ---------------------------------------------------------------- produce
    for c in spec.CROPS:
        a, col, d = _art(c.produce)
        out.append(Tex(f"textures/item/{c.produce.id}.png", "produce", c.produce.id, a, col, d))
        if c.seed:
            a, col, d = _art(c.seed)
            out.append(Tex(f"textures/item/{c.seed.id}.png", "produce", c.seed.id, a, col, d))
    for i in spec.fruit_items():
        a, col, d = _art(i)
        out.append(Tex(f"textures/item/{i.id}.png", "produce", i.id, a, col, d))
    for crate, item in spec.crate_sources().items():
        out.append(Tex(f"textures/block/{crate}_top.png", "produce", crate, "crate_top", [],
                       f"top of a wooden crate filled with {item}"))
    out.append(Tex("textures/block/crate_side.png", "produce", "crate", "crate_side", ["#a8784a"],
                   "side of a slatted wooden produce crate with dark corner posts"))
    out.append(Tex("textures/block/crate_bottom.png", "produce", "crate", "crate_bottom", ["#a8784a"],
                   "bottom of the crate: planks"))

    # ---------------------------------------------------------------- kitchen
    for i in spec.FOOD_ITEMS + spec.slice_items():
        a, col, d = _art(i)
        out.append(Tex(f"textures/item/{i.id}.png", "kitchen", i.id, a, col, d))
    for f in spec.FEASTS:
        out.append(Tex(f"textures/item/{f.id}.png", "kitchen", f.id, f"{f.kind}_item", f.art.colors,
                       f"inventory icon of a whole {f.display}: {f.art.desc}"))

    # ---------------------------------------------------------------- hardware
    for i in spec.TOOLS:
        a, col, d = _art(i)
        out.append(Tex(f"textures/item/{i.id}.png", "hardware", i.id, a, col, d))
    for w in spec.WORKSTATIONS:
        a, col, d = _art(w)
        out.append(Tex(f"models/block/{w.id}.json", "hardware", w.id, "block_model", col,
                       d + " (textures under textures/block/<id>/ or textures/block/<id>_*.png)", size="model"))
    for f in spec.FEASTS:
        if f.kind == "cake":
            for part in ("top", "side", "inner", "bottom"):
                out.append(Tex(f"textures/block/{f.id}_{part}.png", "hardware", f.id, f"cake_{part}", f.art.colors,
                               f"{part} texture for vanilla cake model layout: {f.art.desc}"))
        else:
            for part in ("top", "inner"):
                out.append(Tex(f"textures/block/{f.id}_{part}.png", "hardware", f.id, f"{f.kind}_{part}", f.art.colors,
                               f"{part} texture for the {f.kind} template model: {f.art.desc}"))
    for kind in ("pie", "pizza"):
        for part in ("side", "bottom"):
            out.append(Tex(f"textures/block/{kind}_{part}.png", "hardware", kind, f"{kind}_{part}", [],
                           f"shared {part} texture for all {kind}s"))
        for n in range(4):
            out.append(Tex(f"models/block/template_{kind}_{n}.json", "hardware", kind, "block_model", [],
                           f"{kind} with {n} quarter(s) removed; texture vars #top #side #inner #bottom #particle",
                           size="model"))
    out.append(Tex("textures/gui/container/cooking_pot.png", "hardware", "cooking_pot_gui", "gui", [],
                   "256x256 container GUI, see STYLE.md cooking pot layout", size="256x256"))
    for e in ("well_fed", "cozy", "caffeinated"):
        out.append(Tex(f"textures/mob_effect/{e}.png", "hardware", e, "effect_icon", [],
                       {"well_fed": "golden drumstick/bowl icon", "cozy": "steaming mug with tiny flame",
                        "caffeinated": "coffee bean with lightning spark"}[e], size="18x18"))
    out.append(Tex("logo.png", "hardware", "logo", "logo", [],
                   "mod icon: sprout growing from rich soil with a tomato & wheat, warm farmhouse palette",
                   size="128x128 (placed at common/src/main/resources/logo.png)"))
    return out


def by_lane(lane: str) -> list[Tex]:
    return [t for t in build() if t.lane == lane]


def main() -> None:
    entries = build()
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "texture_contract.json").write_text(json.dumps([asdict(t) for t in entries], indent=1))
    from collections import Counter
    print(Counter(t.lane for t in entries))
    print(len(entries), "entries ->", BUILD / "texture_contract.json")


if __name__ == "__main__":
    main()
