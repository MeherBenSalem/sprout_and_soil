"""Seed item sprites (produce lane).

Vanilla seeds are small scattered clusters with no outline: each seed is a
2-4 px shape with a light top-left pixel and a dark bottom-right pixel.  Here
every crop gets its own seed *shape* (flat disc, kidney bean, slender grain,
tooth-shaped kernel, glossy bead...), colour ramp, count and scatter layout so
no two seed items read the same.
"""
from __future__ import annotations

from typing import Callable

from .core import Sprite
from .produce_kit import Grid, mat, pal, render

SEEDS: dict[str, Callable[[], Sprite]] = {}

# ---------------------------------------------------------------- seed shapes (tone rows 1..5, a..e)
# 5/4 light, 3 base, 2/1 shadow.  Secondary letters (a..e) use an accent ramp.
SH = {
    "flat":    ["54.", "4321"],                 # flat oval (tomato)
    "flat_b":  [".54", "4321"],
    "disc":    [".54.", "5432", ".321"],        # flat round disc (pepper)
    "disc_b":  [".45.", "4532", ".221"],
    "chip":    ["54", "21"],                    # 2x2 small flat
    "chip_b":  ["45", "21"],
    "kidney":  ["54.", "4321", ".21"],          # eggplant-ish kidney
    "lens":    ["5..", "43.", ".31"],           # pointed oval, diagonal (cucumber)
    "lens_b":  ["..5", ".43", "21."],
    "slab":    [".55.", "5443", ".321"],        # big flat oval (zucchini)
    "slab_b":  ["554.", "4432", ".21."],
    "bean":    [".554.", "54432", ".2a21"],     # kidney bean with hilum (green bean)
    "bean_b":  [".455.", "4433a", ".2221"],
    "streak":  ["5", "3", "1"],                 # slender ribbed (lettuce)
    "streak_b": ["5.", "3.", ".1"],
    "bead":    ["53", "21"],                    # tiny round (brassicas)
    "bead_b":  ["43", "21"],
    "dot":     ["4", "1"],                      # very tiny (celery, mint, basil)
    "dot_b":   ["41"],
    "prickle": [".4.", "532", "2.."],           # spiny (spinach)
    "prickle_b": ["4.", "53", ".21"],
    "glossy":  [".5.", "e32", ".21"],           # glossy bead with glint (asparagus)
    "glossy_b": ["e3", "21"],
    "angle":   ["54.", "321"],                  # angular black (leek)
    "angle_b": ["4..", "53.", "221"],
    "round3":  [".4.", "532", ".2."],           # small round (radish/turnip)
    "kernel":  ["d554", "5443", "4332", ".32."],  # corn kernel (tooth) with pale crown
    "kernel_b": [".d5.", "d554", "5433", ".22."],
    "grain":   ["45..", ".543", "..21"],        # barley: plump pointed grain
    "grain_b": ["..54", "543.", "21.."],
    "oat":     ["5...", ".4..", "..3.", "...1"],  # slender husk grain
    "oat_b":   ["...5", "..4.", ".3..", "1..."],
    "achene":  ["5", "1"],                      # strawberry: tiny yellow drops
    "pip":     ["4", "1"],
    "dkid":    ["54", "3.", "21"],              # raspberry D-shape
    "tri":     [".5", "43", "21"],              # blackberry wrinkled triangle
    "ovl":     ["5.", "43", ".1"],              # cranberry slender oval
    "pear":    [".5.", "543", "432", ".2."],    # grape seed: pear shape with beak
    "pear_b":  [".4.", "542", "321", ".1."],
    "nut":     [".55.", "5443", "4332", ".21."],  # tea seed: round nut
    "nut_b":   [".54.", "5433", "4322", ".21."],
    "fuzz":    ["e.", "52", "21"],              # cotton: dark seed with lint fleck
    "fuzz_b":  [".e", "53", "21"],
}


def scatter(shapes: list[str], spots: list[tuple[int, int]]) -> Grid:
    g = Grid()
    for i, (x, y) in enumerate(spots):
        g.rows(SH[shapes[i % len(shapes)]], x, y)
    return g


SEED_STEPS = (-0.40, -0.22, 0.0, 0.08, 0.15)


def seeds_sprite(color: str, shapes: list[str], spots: list[tuple[int, int]], spread: float = 0.12,
                 lift: float = 0.0, accent: str | None = None, accent_spread: float = 0.08) -> Sprite:
    """``spread`` scales the default seed ramp (deep shadows, modest highlights for contrast on slots)."""
    k = spread / 0.12
    P = mat(color, steps=tuple(v * k + lift for v in SEED_STEPS))
    S_ = mat(accent, accent_spread) if accent else None
    return render(scatter(shapes, spots).out(), pal(P, S_), outline=False)


def seed(name: str):
    def deco(fn):
        SEEDS[name] = fn
        return fn
    return deco


# ---------------------------------------------------------------- layouts (top-left of each seed)
L_MED6 = [(3, 3), (9, 2), (6, 7), (12, 7), (2, 11), (9, 12)]
L_MED5 = [(4, 3), (10, 4), (3, 9), (8, 8), (11, 12)]
L_BIG4 = [(2, 3), (9, 2), (4, 9), (10, 10)]
L_BIG3 = [(2, 4), (9, 2), (6, 10)]
L_SMALL8 = [(4, 3), (10, 2), (7, 5), (2, 8), (12, 7), (6, 10), (10, 11), (3, 13)]
L_SMALL9 = [(3, 2), (8, 3), (12, 4), (5, 6), (10, 8), (2, 9), (7, 10), (12, 12), (4, 13)]
L_TINY11 = [(3, 3), (7, 2), (11, 3), (5, 6), (9, 6), (13, 7), (2, 9), (7, 9), (11, 11), (4, 12), (8, 13)]


@seed("tomato_seeds")
def tomato_seeds():
    return seeds_sprite("#e7d39a", ["flat", "flat_b", "flat", "flat_b", "flat", "flat_b", "flat"],
                        [(3, 3), (9, 2), (6, 6), (11, 7), (2, 10), (8, 11), (12, 12)], lift=-0.02)


@seed("bell_pepper_seeds")
def bell_pepper_seeds():
    return seeds_sprite("#efe0a8", ["disc", "disc_b"], [(2, 2), (9, 3), (5, 7), (11, 9), (3, 12)], lift=-0.04)


@seed("chili_pepper_seeds")
def chili_pepper_seeds():
    return seeds_sprite("#f0c870", ["chip", "chip_b"], L_SMALL9, lift=-0.02)


@seed("eggplant_seeds")
def eggplant_seeds():
    return seeds_sprite("#d9c48c", ["kidney"], [(3, 3), (10, 3), (6, 8), (2, 12), (11, 11)], lift=-0.06)


@seed("cucumber_seeds")
def cucumber_seeds():
    return seeds_sprite("#f2ecc8", ["lens", "lens_b"], [(3, 2), (9, 3), (5, 7), (12, 7), (2, 11), (8, 11)],
                        lift=-0.06)


@seed("zucchini_seeds")
def zucchini_seeds():
    return seeds_sprite("#efe6c0", ["slab", "slab_b"], [(2, 3), (9, 2), (6, 8), (11, 11), (2, 12)], lift=-0.06)


@seed("green_bean_seeds")
def green_bean_seeds():
    return seeds_sprite("#f1ead2", ["bean", "bean_b"], [(2, 3), (9, 4), (4, 9), (10, 11)], lift=-0.06,
                        accent="#5a3a2a")


@seed("lettuce_seeds")
def lettuce_seeds():
    return seeds_sprite("#c9c2a0", ["streak", "streak_b"], L_SMALL9, lift=-0.04)


@seed("cabbage_seeds")
def cabbage_seeds():
    return seeds_sprite("#5b3f2a", ["bead", "bead_b"], L_SMALL9, lift=0.06)


@seed("spinach_seeds")
def spinach_seeds():
    return seeds_sprite("#8a7a52", ["prickle", "prickle_b"], L_MED6, lift=0.02)


@seed("broccoli_seeds")
def broccoli_seeds():
    # brassica seeds: tiny beads; broccoli's lean olive-brown and come in a looser scatter
    return seeds_sprite("#5b4a2a", ["bead_b", "dot"], L_TINY11, lift=0.08)


@seed("cauliflower_seeds")
def cauliflower_seeds():
    return seeds_sprite("#6e4e34", ["round3", "bead"], L_MED6, lift=0.06)


@seed("celery_seeds")
def celery_seeds():
    return seeds_sprite("#a8956a", ["dot", "dot_b"], L_TINY11, lift=-0.02)


@seed("asparagus_seeds")
def asparagus_seeds():
    return seeds_sprite("#2a2420", ["glossy", "glossy_b"], L_MED6, lift=0.12, accent="#9a9aa8")


@seed("leek_seeds")
def leek_seeds():
    return seeds_sprite("#2a2420", ["angle", "angle_b"], L_MED6[::-1], lift=0.14)


@seed("radish_seeds")
def radish_seeds():
    return seeds_sprite("#8a5a3a", ["round3"], [(3, 3), (9, 2), (6, 7), (12, 8), (2, 11), (8, 12)], lift=0.02)


@seed("turnip_seeds")
def turnip_seeds():
    return seeds_sprite("#6a3a30", ["bead", "bead_b"], L_SMALL8, lift=0.06)


@seed("corn_seeds")
def corn_seeds():
    return seeds_sprite("#f0c03a", ["kernel", "kernel_b"], [(2, 2), (9, 3), (4, 9), (10, 10)], lift=-0.02,
                        accent="#f8eab0")


@seed("barley_seeds")
def barley_seeds():
    return seeds_sprite("#d8b868", ["grain", "grain_b"], [(2, 2), (9, 3), (5, 7), (11, 9), (2, 12)], lift=-0.02)


@seed("oat_seeds")
def oat_seeds():
    return seeds_sprite("#e0d098", ["oat", "oat_b"], [(2, 2), (9, 2), (6, 7), (11, 9), (2, 11)], lift=-0.04)


@seed("strawberry_seeds")
def strawberry_seeds():
    return seeds_sprite("#e8c04a", ["achene"], L_TINY11, lift=-0.02)


@seed("blueberry_seeds")
def blueberry_seeds():
    return seeds_sprite("#6a5a7a", ["pip", "bead_b"], L_SMALL9, lift=0.06)


@seed("raspberry_seeds")
def raspberry_seeds():
    return seeds_sprite("#c89a6a", ["dkid"], L_SMALL8, lift=-0.02)


@seed("blackberry_seeds")
def blackberry_seeds():
    return seeds_sprite("#7a5a4a", ["tri"], L_SMALL8[::-1], lift=0.04)


@seed("cranberry_seeds")
def cranberry_seeds():
    return seeds_sprite("#c8a07a", ["ovl"], L_SMALL8, lift=-0.02)


@seed("grape_seeds")
def grape_seeds():
    return seeds_sprite("#8a6a3a", ["pear", "pear_b"], [(3, 2), (10, 3), (6, 7), (12, 10), (2, 11)], lift=0.02)


@seed("tea_seeds")
def tea_seeds():
    return seeds_sprite("#6a4a2a", ["nut", "nut_b"], L_BIG3 + [(11, 11)], lift=0.04)


@seed("cotton_seeds")
def cotton_seeds():
    return seeds_sprite("#4a3a2a", ["fuzz", "fuzz_b"], L_MED6, lift=0.08, accent="#f4f0e8")


@seed("basil_seeds")
def basil_seeds():
    return seeds_sprite("#2a2420", ["dot", "dot_b"], L_TINY11, lift=0.10)


@seed("mint_seeds")
def mint_seeds():
    return seeds_sprite("#5a4a3a", ["bead_b", "dot"], L_SMALL9[::-1], lift=0.04)


@seed("pineapple_seeds")
def pineapple_seeds():
    """'Pineapple Crown': a spiky leaf rosette twisted off the fruit, with a fibrous golden stub."""
    from .produce_items import build
    G = mat("#3a7a3a", 0.10)
    P = mat("#e8c050", 0.09)
    g = Grid()
    base = (5.6, 11.0)
    tips = [("h", (1.4, 7.6)), ("M", (13.6, 9.6)), ("g", (2.6, 2.6)), ("H", (12.6, 3.4)), ("G", (7.4, 1.5)),
            ("m", (10.4, 6.6))]
    for ch, (tx, ty) in tips:
        g.capsule(base[0], base[1], tx, ty, 1.15, 0.4, ch)
    g.ellipse(4.6, 12.6, 2.2, 1.5, "P", angle=-35)
    d = Grid()
    for ch, (tx, ty) in tips:
        mx, my = base[0] + (tx - base[0]) * 0.55, base[1] + (ty - base[1]) * 0.55
        if g.get(int(mx), int(my)) == ch:
            d.put(int(mx), int(my), "+")
    d.pts([(4, 12), (5, 13)], "-")
    return build(g, pal(P, G), d)
