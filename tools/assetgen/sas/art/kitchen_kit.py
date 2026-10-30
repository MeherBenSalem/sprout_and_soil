"""Drawing kit for the kitchen lane (ingredients, dishes, drinks, feasts).

Builds on :mod:`sas.art.core` (which is shared and never edited from here). Deterministic.

Conventions
-----------
* Food is drawn *without* its outer outline; :func:`finish` adds a directional, hue-shifted
  outline (lighter top-left, darker bottom-right) derived from the neighbouring pixels.
* Containers are fixed templates so every dish in the same container shares one silhouette:
  bowl (wood, auto outline), plate/mug/bottle/jar (hand-placed outlines baked into the rows).
* Light comes from the top-left. Shadows drift cool, highlights warm (``core.shade``).
"""
from __future__ import annotations

import colorsys
import math
import random
import zlib
from typing import Callable, Iterable

from .core import CLEAR, Color, Sprite, hexc, mix, ramp, shade

Pt = tuple[int, int]

# --------------------------------------------------------------------------- colour helpers


def C(c) -> Color:
    return hexc(c) if isinstance(c, str) else c


def rp(base, n: int = 5, spread: float = 0.10) -> list[Color]:
    """Hue-shifted ramp, darkest -> lightest, centred on ``base``."""
    return ramp(C(base), n, spread)


def lit(c, amt: float) -> Color:
    return shade(C(c), amt)


def lightness(c: Color) -> float:
    return colorsys.rgb_to_hls(c[0] / 255, c[1] / 255, c[2] / 255)[1]


def set_lightness(c: Color, l: float) -> Color:
    h, _, s = colorsys.rgb_to_hls(c[0] / 255, c[1] / 255, c[2] / 255)
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), s)
    return (round(r * 255), round(g * 255), round(b * 255), 255)


def saturate(c, ds: float) -> Color:
    c = C(c)
    h, l, s = colorsys.rgb_to_hls(c[0] / 255, c[1] / 255, c[2] / 255)
    r, g, b = colorsys.hls_to_rgb(h, l, max(0.0, min(1.0, s + ds)))
    return (round(r * 255), round(g * 255), round(b * 255), 255)


def blend(a, b, t: float) -> Color:
    return mix(C(a), C(b), t)


def rng_for(key: str) -> random.Random:
    return random.Random(zlib.crc32(key.encode()))


# --------------------------------------------------------------------------- sprite helpers


def stamp(s: Sprite, rows: Iterable[str], pal: dict, ox: int = 0, oy: int = 0) -> list[Pt]:
    """Paint ASCII ``rows`` at an offset; characters missing from ``pal`` are skipped."""
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            col = pal.get(ch)
            if col is None:
                continue
            s.set(x + ox, y + oy, C(col))
            out.append((x + ox, y + oy))
    return out


def where(rows: Iterable[str], chars: str, ox: int = 0, oy: int = 0) -> list[Pt]:
    return [(x + ox, y + oy) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch in chars]


def mask_of(s: Sprite) -> set[Pt]:
    return {(x, y) for y in range(s.h) for x in range(s.w) if s.px[y][x][3]}


def put(s: Sprite, x: int, y: int, c) -> None:
    s.set(x, y, C(c))


def puts(s: Sprite, pts, c) -> None:
    for x, y in pts:
        s.set(x, y, C(c))


def ell(cx: float, cy: float, rx: float, ry: float) -> Callable[[int, int], bool]:
    return lambda x, y: ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0


def pts_where(pred: Callable[[int, int], bool], w: int = 16, h: int = 16) -> list[Pt]:
    return [(x, y) for y in range(h) for x in range(w) if pred(x, y)]


def dome(s: Sprite, cx: float, cy: float, rx: float, ry: float, rmp: list[Color],
         mask: Callable[[int, int], bool] | None = None, light=(-0.55, -0.75, 0.5),
         bias: float = 0.0, flat: float = 1.0) -> list[Pt]:
    """Cel-shade an ellipsoid lit from the top-left; returns the painted points.

    ``flat`` > 1 flattens the bulge (cushions, liquids), ``bias`` shifts toward light.
    """
    lx, ly, lz = light
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / ln, ly / ln, lz / ln
    out = []
    for y in range(s.h):
        for x in range(s.w):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d2 = dx * dx + dy * dy
            if d2 > 1.0 or (mask and not mask(x, y)):
                continue
            dz = math.sqrt(max(0.0, 1 - d2)) * flat
            n = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
            v = (dx * lx + dy * ly + dz * lz) / n
            v = (v + 1) / 2 + bias
            idx = max(0, min(len(rmp) - 1, int(v * len(rmp) - 0.35)))
            s.set(x, y, rmp[idx])
            out.append((x, y))
    return out


def shade_pts(s: Sprite, pts, rmp: list[Color], light=(-0.6, -0.8), bias: float = 0.0,
              edge: float = 0.16) -> None:
    """Form-shade an arbitrary point set using its bounding box plus a rim term."""
    pts = list(pts)
    if not pts:
        return
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs) + 1) / 2, (min(ys) + max(ys) + 1) / 2
    rx, ry = max(1.0, (max(xs) - min(xs) + 1) / 2), max(1.0, (max(ys) - min(ys) + 1) / 2)
    ps = set(pts)
    for x, y in pts:
        dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
        v = (dx * light[0] + dy * light[1]) * 0.45 + 0.5 + bias
        if (x + 1, y) not in ps or (x, y + 1) not in ps:
            v -= edge
        if (x - 1, y) not in ps or (x, y - 1) not in ps:
            v += edge * 0.7
        idx = max(0, min(len(rmp) - 1, int(v * len(rmp))))
        s.set(x, y, rmp[idx])


def outline_color(c: Color, bottom_right: bool, k_tl: float = 0.50, k_br: float = 0.36,
                  lo: float = 0.08, hi: float = 0.34) -> Color:
    """Dark, saturated, hue-shifted outline colour derived from an edge pixel."""
    l = lightness(c)
    target = max(lo, min(hi - (0.05 if bottom_right else 0.0), l * (k_br if bottom_right else k_tl)))
    col = shade(c, target - l, sat=0.08 * max(0.0, 1.0 - l) ** 2)
    col = set_lightness(col, target)
    if l > 0.78:                       # very light materials: keep a soft neutral outline
        col = saturate(col, -0.6) if colorsys.rgb_to_hls(*(v / 255 for v in col[:3]))[2] > 0.22 else col
    return col


def finish(s: Sprite, k_tl: float = 0.50, k_br: float = 0.36, hi: float = 0.34,
           keep: Callable[[int, int], bool] | None = None, exclude: set | None = None) -> Sprite:
    """Directional selective outline (4-connected) around the opaque silhouette.

    ``exclude``: opaque pixels that never spawn an outline (glass, steam, pre-outlined parts).
    """
    out = s.copy()
    for y in range(s.h):
        for x in range(s.w):
            if s.opaque(x, y) or (keep and not keep(x, y)):
                continue
            ns = []
            br = False
            for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                if s.opaque(x + dx, y + dy) and not (exclude and (x + dx, y + dy) in exclude):
                    ns.append(s.get(x + dx, y + dy))
                    if dx == -1 or dy == -1:
                        br = True  # neighbour is up/left -> we sit on the bottom/right edge
            if not ns:
                continue
            base = tuple(round(sum(c[i] for c in ns) / len(ns)) for i in range(3)) + (255,)
            out.px[y][x] = outline_color(base, br, k_tl, k_br, hi=hi)
    return out


def binarize(s: Sprite) -> Sprite:
    """Force alpha to 0/255 (cutout rendering)."""
    for y in range(s.h):
        for x in range(s.w):
            c = s.px[y][x]
            s.px[y][x] = CLEAR if c[3] < 128 else (c[0], c[1], c[2], 255)
    return s


def scatter(s: Sprite, pts, cols, n: int, rnd: random.Random, spacing: int = 2) -> list[Pt]:
    """Place ``n`` single pixels from ``cols`` on candidate ``pts`` keeping some spacing."""
    pts = sorted(pts)
    rnd.shuffle(pts)
    placed: list[Pt] = []
    for p in pts:
        if len(placed) >= n:
            break
        if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= spacing for q in placed):
            placed.append(p)
    for i, (x, y) in enumerate(placed):
        s.set(x, y, C(cols[i % len(cols)]))
    return placed


# Tiny shaded pieces. 'h' highlight, 'l' light, 'b' base, 'd' dark, 'k' darkest.
PIECES = {
    "1": ["b"],
    "2h": ["lb"],
    "2v": ["l", "d"],
    "2x2": ["lb", "bd"],
    "cube": ["hl", "bd"],
    "3x2": ["llb", "bdd"],
    "2x3": ["lb", "bb", "bd"],
    "3x3": [".l.", "lbb", ".bd"],
    "lump": [".lb.", "lbbd", ".dd."],
    "coin": ["lb.", "bbd"],
}


def piece(s: Sprite, x: int, y: int, base, shape: str = "2x2", spread: float = 0.12,
          rows: list[str] | None = None) -> list[Pt]:
    r = rp(base, 5, spread)
    pal = {"k": r[0], "d": r[1], "b": r[2], "l": r[3], "h": r[4]}
    return stamp(s, rows or PIECES[shape], pal, x, y)


def capsule(s: Sprite, x0: float, y0: float, x1: float, y1: float, r: float, rmp: list[Color],
            mask: Callable[[int, int], bool] | None = None, round_ends: bool = True,
            r_end: float | None = None) -> dict[Pt, tuple[float, float]]:
    """Diagonal cylinder from (x0,y0) to (x1,y1), shaded across its width (lit side up-left).

    Returns {point: (t along axis 0..1, side -1..1)} so callers can pattern along the axis.
    """
    ax, ay = x1 - x0, y1 - y0
    L = math.hypot(ax, ay) or 1.0
    ux, uy = ax / L, ay / L
    nx, ny = -uy, ux
    if nx + ny > 0:
        nx, ny = -nx, -ny          # normal pointing toward the light (up-left)
    out = {}
    for y in range(s.h):
        for x in range(s.w):
            px, py = x + 0.5 - x0, y + 0.5 - y0
            t = (px * ux + py * uy) / L
            tc = max(0.0, min(1.0, t))
            if not round_ends and (t < 0 or t > 1):
                continue
            cx, cy = tc * ax, tc * ay
            d = math.hypot(px - cx, py - cy)
            rr = r if r_end is None else r + (r_end - r) * tc
            if d > rr or (mask and not mask(x, y)):
                continue
            side = ((px - cx) * nx + (py - cy) * ny) / rr
            v = 0.5 + side * 0.42 - (0.12 if d > rr - 0.9 and side < 0 else 0.0)
            idx = max(0, min(len(rmp) - 1, int(v * len(rmp))))
            s.set(x, y, rmp[idx])
            out[(x, y)] = (t, side)
    return out


def strip(s: Sprite, x0: float, y0: float, x1: float, y1: float, bands: list, wave: float = 1.0,
          freq: float = 0.9, phase: float = 0.0) -> list[Pt]:
    """Wavy ribbon (bacon, noodles) along a line; ``bands`` are colours across its width."""
    ax, ay = x1 - x0, y1 - y0
    L = math.hypot(ax, ay) or 1.0
    ux, uy = ax / L, ay / L
    nx, ny = -uy, ux
    half = len(bands) / 2
    out = []
    steps = int(L * 3) + 1
    for i in range(steps):
        tt = i / 3
        off = math.sin(tt * freq + phase) * wave
        for j, col in enumerate(bands):
            w = j - half + 0.5 + off
            x, y = x0 + ux * tt + nx * w, y0 + uy * tt + ny * w
            p = (int(math.floor(x)), int(math.floor(y)))
            s.set(p[0], p[1], C(col))
            out.append(p)
    return out


# --------------------------------------------------------------------------- materials

WOOD = ["#33200c", "#4b3114", "#64431b", "#7e5824", "#9a6f30", "#b38842"]
TERRACOTTA = ["#6e2a1a", "#8f3a22", "#ad4c2c", "#c8643a", "#dc8150", "#eda26c"]
MUG_OUTLINE = "#561c12"
GLASS = {"h": "#f2f8fd", "l": "#cfe2f3", "m": "#a9c8e6", "d": "#6e9ccc", "o": "#4d7db2"}
CORK = ["#7d3d1f", "#a2582e", "#c27a45", "#d99a63"]
STEAM = ["#dfe4ea", "#f4f6f8"]
LETTUCE = ["#2f6a1f", "#468a2a", "#62a836", "#84c64e", "#aee07a"]
BASIL = ["#1d521c", "#2c7028", "#41913a", "#62b453"]
HERB = "#3f8a2e"
CHEESE = ["#b8761a", "#d8981e", "#f0b82a", "#f8d050", "#fbe68a"]
BREAD = ["#7a4515", "#a0621f", "#c4842e", "#dda44a", "#efc677"]
CRUMB = ["#c8a46a", "#dcbc82", "#ead29e", "#f5e4bc"]
TOMATO = ["#7a1410", "#a8201a", "#d0322a", "#e85a40", "#f89070"]
EGG_WHITE = ["#c8c2b0", "#e2ddcf", "#f4f1e8", "#fdfcf8"]
YOLK = ["#c86a08", "#e8900e", "#f6b21c", "#fbd560"]
BACON = ["#5e1e10", "#8a3218", "#b04a22", "#d07038", "#eaa060"]
FAT = ["#d8b49a", "#f0d8c4", "#fbeee0"]
STEAK = ["#3a180c", "#5a2814", "#7a3c1e", "#9a5630", "#b87448"]
CHOC = ["#2a1208", "#3e1c0c", "#5a2e16", "#7a4424", "#9a6038"]


# --------------------------------------------------------------------------- bowl
# Wooden bowl, 12 px wide (14 incl. outline), rows 4-13. Digits index WOOD.
# 's' marks the opening (contents surface), painted by the dish.
BOWL_BACK = [
    #0123456789abcdef
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "................",  # 3
    ".....233332.....",  # 4   far rim
    "...23ssssss32...",  # 5
    "..3ssssssssss2..",  # 6
    "..3ssssssssss1..",  # 7
    "..3ssssssssss1..",  # 8
    "..34ssssssss21..",  # 9
]
BOWL_FRONT = [
    #0123456789abcdef
    "..455444444321..",  # 10  front lip
    "...4333333221...",  # 11
    "....22222211....",  # 12
    "......1100......",  # 13  foot
]
BOWL_LIP = 10
_WOOD_PAL = {str(i): WOOD[i] for i in range(len(WOOD))}
BOWL_SURFACE: list[Pt] = where(BOWL_BACK, "s")
BOWL_SURFACE_SET = set(BOWL_SURFACE)


def bowl_back(s: Sprite) -> None:
    stamp(s, BOWL_BACK, _WOOD_PAL)


def bowl_front(s: Sprite) -> None:
    stamp(s, BOWL_FRONT, _WOOD_PAL, 0, BOWL_LIP)


def in_bowl(x: int, y: int) -> bool:
    """Clip for contents heaped in the bowl: free above row 5, inside the opening below."""
    return y <= 5 or (x, y) in BOWL_SURFACE_SET


def bowl_dish(contents: Callable[[Sprite], None], post: Callable[[Sprite], None] | None = None,
              steam: list[Pt] | None = None) -> Sprite:
    s = Sprite()
    bowl_back(s)
    contents(s)
    bowl_front(s)
    if post:
        post(s)
    ex = None
    if steam:
        ex = set(steam)
        for i, (x, y) in enumerate(steam):
            s.set(x, y, C(STEAM[i % 2]))
    return finish(s, exclude=ex)


# --------------------------------------------------------------------------- plate
# 16 x 7 ellipse at rows 8-15 with a baked-in cool grey-blue outline.
PLATE_ROWS = [
    #0123456789abcdef
    "................",  # 0
    "................",
    "................",
    "................",
    "................",
    "................",  # 5
    "................",
    "................",
    "....oooooooo....",  # 8
    "..oobbbbbbbboo..",  # 9   rim (pale blue band) at the back
    ".obbhhhhhhhhbbo.",  # 10  rim top surface
    "obhhwwwwwwwwhhbo",  # 11  well
    "obhwwwwwwwwwwhbO",  # 12
    "oBbhhwwwwwwhhbBO",  # 13
    ".OBBbbbbbbbbBBO.",  # 14  front rim
    "..OOOOOOOOOOOO..",  # 15
]
PLATE_PAL = {"h": "#fbfaf4", "w": "#e9e6db", "b": "#a9c2d2", "B": "#88a5b9", "o": "#6a7e8c", "O": "#4b5d6b"}
PLATE_MASK = set(where(PLATE_ROWS, "hwbBoO"))


def plate_base(s: Sprite) -> None:
    stamp(s, PLATE_ROWS, PLATE_PAL)


def plate_dish(food: Callable[[Sprite], None]) -> Sprite:
    """Plate + food layer. The food is outlined on its own so it casts a dark edge on the plate."""
    s = Sprite()
    plate_base(s)
    f = Sprite()
    food(f)
    s.paste(finish(f))
    return s


# --------------------------------------------------------------------------- mug
MUG_ROWS = [
    #0123456789abcdef
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "....oooooo......",  # 3
    "...o555555o.....",  # 4   rim back
    "..o5iiiiii4o....",  # 5   inside back wall / drink
    "..o4cccccc3o....",  # 6   drink surface
    "..o4cccccc3o....",  # 7
    "..o55444443ooo..",  # 8   front lip
    "..o54443322333o.",  # 9   handle top bar
    "..o5444332o.o3o.",  # 10
    "..o5444332o.o2o.",  # 11
    "..o54443322222o.",  # 12  handle bottom bar
    "..o4433322oooo..",  # 13
    "...o333221o.....",  # 14
    "....oooooo......",  # 15
]
MUG_INSIDE = where(MUG_ROWS, "ic")
MUG_MASK = set(where(MUG_ROWS, "0123456789oic"))


def mug_base(s: Sprite, glaze="#ebdfc6") -> None:
    pal = {str(i): TERRACOTTA[i] for i in range(len(TERRACOTTA))}
    g = rp(glaze, 4, 0.07)
    pal.update({"c": g[2], "i": g[1], "o": MUG_OUTLINE})
    stamp(s, MUG_ROWS, pal)
    put(s, 4, 6, g[3])


def mug_drink(s: Sprite, base, spread: float = 0.07) -> list[Color]:
    """Fill the mug opening with a drink surface (lighter at the back-left)."""
    r = rp(base, 5, spread)
    for x, y in MUG_INSIDE:
        v = {5: 1, 6: 2, 7: 2}[y]
        if y == 7 and x >= 8:
            v = 1
        if y == 6 and x <= 5:
            v = 3
        s.set(x, y, r[v])
    return r


# --------------------------------------------------------------------------- bottle (vanilla glass-bottle silhouette)
BOTTLE_ROWS = [
    #0123456789abcdef
    "................",  # 0
    "................",  # 1
    ".......kkK......",  # 2   cork top
    "......lkkkd.....",  # 3
    "......lmmmo.....",  # 4   lip
    ".......l#o......",  # 5   neck
    ".......l#o......",  # 6
    "......l###o.....",  # 7
    ".....lh####o....",  # 8
    "....lh######o...",  # 9
    "....lh######o...",  # 10
    "....l######do...",  # 11
    "....o######do...",  # 12
    ".....o####do....",  # 13
    "......ooooo.....",  # 14
]
BOTTLE_LIQUID = where(BOTTLE_ROWS, "#")
BOTTLE_GLASS = set(where(BOTTLE_ROWS, "lhmdo"))
BOTTLE_MASK = set(where(BOTTLE_ROWS, "kKlhmdo#"))


def bottle_base(s: Sprite, cork=True) -> None:
    pal = dict(GLASS)
    pal.update({"k": CORK[2], "K": CORK[3]})
    if not cork:
        pal.update({"k": None, "K": None})
    stamp(s, BOTTLE_ROWS, pal)


# --------------------------------------------------------------------------- jar
JAR_ROWS = [
    #0123456789abcdef
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "................",  # 3
    ".....kkkkkk.....",  # 4   lid outline
    "....kHLLLLMk....",  # 5   lid top
    "....kDDDDDDk....",  # 6   lid band
    "...lmmmmmmmmo...",  # 7   glass shoulder
    "..lh########do..",  # 8
    "..lh#########o..",  # 9
    "..l##########o..",  # 10
    "..l##########o..",  # 11
    "..l#########do..",  # 12
    "..ol########do..",  # 13
    "...oooooooooo...",  # 14
]
JAR_FILL = where(JAR_ROWS, "#")
JAR_GLASS = set(where(JAR_ROWS, "lhmdo"))
JAR_LID = where(JAR_ROWS, "HLMDk")


def jar_base(s: Sprite, lid="#c8281e") -> None:
    lr = rp(lid, 5, 0.1)
    pal = dict(GLASS)
    pal.update({"H": lr[4], "L": lr[3], "M": lr[2], "D": lr[1], "k": outline_color(lr[1], True)})
    stamp(s, JAR_ROWS, pal)


# --------------------------------------------------------------------------- misc

def steam_wisps(xs: Iterable[int], top: int = 0, h: int = 3) -> list[Pt]:
    """Short S-shaped wisps starting at ``top`` (each wisp 1 px wide, ``h`` rows)."""
    out = []
    for i, x in enumerate(xs):
        for j in range(h):
            out.append((x + (1 if (j + i) % 2 else 0), top + j))
    return out


# --------------------------------------------------------------------------- registry
# id -> zero-arg function returning the finished 16x16 Sprite. Filled by kitchen_* modules.
REG: dict[str, Callable[[], Sprite]] = {}


def reg(*ids: str):
    """Decorator: register a drawer for one or more item ids.

    A drawer taking one positional argument receives the item id (for parametrised families).
    """
    import inspect

    def deco(fn):
        takes_id = len(inspect.signature(fn).parameters) >= 1
        for i in ids:
            REG[i] = (lambda i=i: fn(i)) if takes_id else fn
        return fn
    return deco
