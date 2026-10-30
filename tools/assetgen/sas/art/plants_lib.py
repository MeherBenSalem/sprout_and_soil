"""Shared palettes, helpers and produce stamps for the crop textures (plants lane).

See ``plants_kit`` for the renderer; family modules (``plants_fruiting``, ``plants_leafy``,
``plants_roots``, ``plants_grains``, ``plants_berries``, ``plants_herbs``, ``plants_corn``) build
the actual crops from these helpers.
"""
from __future__ import annotations

import math

from .core import Color, hexc, shade
from .plants_kit import C, Plant, green, line, tones, wood

# --------------------------------------------------------------------------- palettes

G_STD = green("#4e8a2e")                 # default crop green (spec leaf hint)
G_BLUE = green("#4f8a62", sat=-0.06)     # brassicas, alliums
G_GLOSS = green("#2f7030")               # glossy dark shrubs
G_LIGHT = green("#79b844")
STEM = tones("#6b9a34", (-0.17, -0.08, 0.0, 0.07, 0.13), hue=0.04)
STEM_DK = tones("#4f7a2a", (-0.15, -0.07, 0.0, 0.07, 0.13), hue=0.04)
WOOD = wood("#a07a46")
TWINE = hexc("#d8c08a")
CALYX = green("#4a8a2a")
GLINT = hexc("#fff6ee")

H = (5, 8, 12, 15)          # target plant heights per stage
TOP = tuple(16 - x for x in H)


# --------------------------------------------------------------------------- helpers


def stem(p: Plant, ctrl, rmp=STEM, base=2, **kw) -> int:
    return p.add(line(ctrl), rmp, base=base, **kw)


def leaf(p: Plant, a, b, w: float, rmp=G_STD, prof="ovate", bend: float = 0.0, depth: int = 0, **kw) -> int:
    """Leaf from ``a`` (base) to ``b`` (tip); ``bend`` pushes the middle sideways."""
    if bend:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        ctrl = [a, (mx - dy / L * bend, my + dx / L * bend), b]
    else:
        ctrl = [a, b]
    return p.leaf(ctrl, w, rmp, prof, depth=depth, **kw)


def curve_leaf(p: Plant, ctrl, w: float, rmp=G_STD, prof="blade", depth: int = 0, **kw) -> int:
    return p.leaf(list(ctrl), w, rmp, prof, depth=depth, **kw)


def stake(p: Plant, x: int, top: int, bottom: int = 15, ties=()) -> None:
    """Two-pixel wooden stake with a lit left face, a cut top and twine ties."""
    t = {}
    for y in range(top, bottom + 1):
        t[(x, y)] = 3 if y > top else 4
        t[(x + 1, y)] = 1 if y > top else 3
    for y in range(top + 3, bottom + 1, 5):
        t[(x, y)] = 2
    p.fixed(t, WOOD, cast=False)
    for y in ties:
        p.px(x, y, TWINE)
        p.px(x + 1, y, shade(TWINE, -0.2))


def flower(p: Plant, x: int, y: int, petal, centre=None, big: bool = False) -> None:
    """Tiny flower: 3x3 plus with a centre (big) or a 2px petal pair."""
    pc = C(petal)
    dk = shade(pc, -0.17)
    if big:
        p.px(x, y - 1, pc)
        p.px(x - 1, y, pc)
        p.px(x + 1, y, dk)
        p.px(x, y + 1, dk)
        p.px(x, y, C(centre) if centre else pc)
    else:
        p.px(x, y, pc)
        p.px(x + 1, y, dk if centre is None else C(centre))


def stamp(p: Plant, rows, x: int, y: int, rmp: list[Color], extra: dict | None = None, flip=False, **kw):
    """Stamp produce. Digits 0-4 index ``rmp``; g/G calyx greens, w glint, s dark stem."""
    key: dict = {str(i): (rmp, i) for i in range(len(rmp))}
    key.update({"g": (CALYX, 1), "G": (CALYX, 3), "w": GLINT, "s": (STEM_DK, 1), "S": (STEM_DK, 3)})
    if extra:
        key.update(extra)
    return p.stamp(rows, x, y, key, flip=flip, **kw)


# Hand-drawn seedlings (digits = leaf ramp tone, s = stem). Anchor: bottom row, column of the 's'.
SPROUTS = {
    # two narrow cotyledons in a V
    "v": ["4.....3",
          "43...32",
          ".32.32.",
          "..3s2..",
          "...s..."],
    # two round cotyledons
    "round": [".43.34.",
              "4332332",
              ".21s21.",
              "...s..."],
    # V cotyledons + first true leaf unfolding in the middle
    "true": ["...4...",
             "4..3..3",
             "43.s.32",
             ".32s22.",
             "...s..."],
    # broad heart cotyledons (beans, squash)
    "broad": ["34.....43",
              "4332.2332",
              ".2221s1221."[:9],
              "....s....",
              "....s...."],
    # small: two tiny leaves
    "tiny": ["43.32",
             ".3s2.",
             "..s.."],
    # spoon/rosette sprout: three short spoon leaves
    "spoon": ["..4..",
              "3.3.3",
              "43s32",
              ".2s1."],
}


def sprout(p: Plant, x: int, rmp=G_STD, kind: str = "v", stem_h: int = 1, stem_r=STEM, flip=False) -> None:
    """Stamp a seedling whose stem foot sits at (x, 15); ``stem_h`` extra stem pixels lift it."""
    rows = SPROUTS[kind]
    sx = rows[-1].index("s")
    w = max(len(r) for r in rows)
    if flip:
        rows = [r.ljust(w, ".")[::-1] for r in rows]
        sx = w - 1 - sx
    oy = 15 - stem_h - (len(rows) - 1)
    if stem_h:
        stem(p, [(x, 15), (x, 16 - stem_h)], stem_r)
    key = {str(i): (rmp, i) for i in range(len(rmp))}
    key["s"] = (stem_r, 2)
    p.stamp(rows, x - sx, oy, key)


def compound(p: Plant, a, b, rmp, n: int = 1, size: float = 2.0, depth: int = 0, stem_r=STEM) -> None:
    """Pinnate leaf: petiole a->b with ``n`` leaflet pairs and a terminal leaflet."""
    stem(p, [a, b], stem_r)
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    for i in range(n):
        t = (i + 1) / (n + 1)
        bx, by = a[0] + dx * t, a[1] + dy * t
        for sgn in (-1, 1):
            ox, oy = ux * 0.7 - uy * sgn * 1.2, uy * 0.7 + ux * sgn * 1.2
            tip = (round(bx + ox * size), round(by + oy * size))
            leaf(p, (round(bx), round(by)), tip, size, rmp, "ovate", depth=depth)
    leaf(p, b, (round(b[0] + ux * size * 1.4), round(b[1] + uy * size * 1.4)), size + 0.5, rmp, "ovate", depth=depth)


def trifoliate(p: Plant, base, tip, rmp, size: float = 2.6, depth: int = 0, stem_r=STEM, prof="ovate") -> None:
    """Three leaflets at the end of a petiole (bean, soy, strawberry, peanut-ish)."""
    stem(p, [base, tip], stem_r)
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    s = size
    leaf(p, tip, (round(tip[0] + ux * s * 1.2), round(tip[1] + uy * s * 1.2)), s, rmp, prof, depth=depth)
    for sgn in (-1, 1):
        ox, oy = ux * 0.35 - uy * sgn, uy * 0.35 + ux * sgn
        leaf(p, tip, (round(tip[0] + ox * s), round(tip[1] + oy * s)), s * 0.85, rmp, prof, depth=depth - 1)


def tendril(p: Plant, x: int, y: int, d: int = 1, rmp=STEM) -> None:
    pts = [(x, y), (x + d, y - 1), (x + 2 * d, y - 1), (x + 2 * d, y)]
    p.add(pts, rmp, base=3, cast=False)


def dots(p: Plant, pts, light, dark) -> None:
    for i, (x, y) in enumerate(pts):
        p.px(x, y, light if (x + y) % 2 == 0 else dark)


# --------------------------------------------------------------------------- produce stamps



