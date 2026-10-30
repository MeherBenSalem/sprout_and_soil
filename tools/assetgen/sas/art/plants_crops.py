"""Crop growth-stage textures (40 crops x 4 stages + corn tops): registry.

Every crop is a small hand-placed composition built from the ``plants_kit`` primitives
(split-shaded leaves, 1px stems, ASCII produce stamps) and the ``plants_lib`` helpers.  Crops are
grouped in habit families (staked vine, bush, rosette, root row, grain, allium, reed, sprawl,
shrub, herb, corn, trellis, pineapple), one module per family; each crop adds its own leaf shape,
palette and produce so no two crops are simple recolours.

Canvas conventions: 16x16, ground row y=15, plants grow upwards.  Stage heights follow
STYLE.md: ~5, ~8, ~12, ~15-16 px.
"""
from __future__ import annotations

from typing import Callable

from .core import Sprite
from .plants_kit import Plant
from . import plants_berries as B, plants_corn as K, plants_fruiting as F, plants_grains as G
from . import plants_herbs as E, plants_leafy as L, plants_roots as R

# =========================================================================== registry

CROP_FNS: dict[str, Callable[[int], Plant]] = {
    "tomato": F.tomato, "bell_pepper": F.bell_pepper, "chili_pepper": F.chili_pepper, "eggplant": F.eggplant,
    "cucumber": F.cucumber, "zucchini": F.zucchini, "green_bean": F.green_bean,
    "lettuce": L.lettuce, "cabbage": L.cabbage, "spinach": L.spinach, "broccoli": L.broccoli, "cauliflower": L.cauliflower,
    "celery": L.celery, "asparagus": L.asparagus,
    "garlic": R.garlic, "onion": R.onion, "leek": R.leek, "radish": R.radish, "turnip": R.turnip,
    "sweet_potato": R.sweet_potato, "ginger": R.ginger, "peanut": R.peanut,
    "rice": G.rice, "barley": G.barley, "oat": G.oat, "soybean": G.soybean,
    "strawberry": B.strawberry, "blueberry": B.blueberry, "raspberry": B.raspberry, "blackberry": B.blackberry,
    "cranberry": B.cranberry, "grape": B.grape, "pineapple": B.pineapple,
    "coffee": E.coffee, "tea": E.tea, "cotton": E.cotton, "basil": E.basil, "mint": E.mint, "peppercorn": E.peppercorn,
}


def crop_textures() -> dict[str, "Sprite"]:
    """All crop textures keyed by file stem (e.g. ``tomato_stage3``, ``corn_stage2_top``)."""
    out: dict[str, Sprite] = {}
    for name, fn in CROP_FNS.items():
        for st in range(4):
            out[f"{name}_stage{st}"] = fn(st).render()
    for st in range(4):
        full = K.corn_full(st).render()
        if full.h == 16:
            out[f"corn_stage{st}"] = full
        else:
            top, bot = Sprite(), Sprite()
            for y in range(16):
                top.px[y] = full.px[y][:]
                bot.px[y] = full.px[y + 16][:]
            out[f"corn_stage{st}"] = bot
            out[f"corn_stage{st}_top"] = top
    return out
