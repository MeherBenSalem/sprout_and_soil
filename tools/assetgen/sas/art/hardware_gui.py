"""Hardware lane: cooking pot GUI sheet, mob effect icons and the mod logo."""
from __future__ import annotations

import math

from PIL import Image

from .core import CLEAR, Sprite, hexc, sphere_shade
from .hardware_tools import Pal, outline_material

# =========================================================================== GUI
# Layout (see STYLE.md "Cooking pot GUI")

PANEL = hexc("#c6c6c6")
WHITE = hexc("#ffffff")
BLACK = hexc("#000000")
BEVEL_DARK = hexc("#555555")
SLOT_DARK = hexc("#373737")
SLOT_BG = hexc("#8b8b8b")

INPUT_SLOTS = [(x, y) for y in (17, 35) for x in (30, 48, 66)]
CONTAINER_SLOT = (92, 54)
OUTPUT_SLOT = (124, 30)
FLAME_POS = (49, 56)
ARROW_POS = (89, 26)
LIT_FLAME_UV = (176, 0)
FULL_ARROW_UV = (176, 14)
PANEL_W, PANEL_H = 176, 166


def player_slots():
    out = [(8 + 18 * i, 84 + 18 * r) for r in range(3) for i in range(9)]
    out += [(8 + 18 * i, 142) for i in range(9)]
    return out


def _panel(s: Sprite, w: int, h: int) -> None:
    """Vanilla-style container panel: 1px black border with cut corners, 2px white bevel on the
    top/left, 2px dark bevel on the bottom/right, #c6c6c6 face."""
    for y in range(h):
        for x in range(w):
            s.set(x, y, PANEL)
    for x in range(2, w - 3):
        s.set(x, 1, WHITE)
    for x in range(1, w - 3):
        s.set(x, 2, WHITE)
    for y in range(2, h - 3):
        s.set(1, y, WHITE)
    for y in range(1, h - 3):
        s.set(2, y, WHITE)
    s.set(3, 3, WHITE)
    for x in range(3, w - 1):
        s.set(x, h - 3, BEVEL_DARK)
    for x in range(3, w - 2):
        s.set(x, h - 2, BEVEL_DARK)
    for y in range(3, h - 1):
        s.set(w - 3, y, BEVEL_DARK)
    for y in range(3, h - 2):
        s.set(w - 2, y, BEVEL_DARK)
    s.set(w - 4, h - 4, BEVEL_DARK)
    s.set(w - 3, 2, PANEL)
    s.set(2, h - 3, PANEL)
    for x in range(2, w - 3):
        s.set(x, 0, BLACK)
    for x in range(3, w - 2):
        s.set(x, h - 1, BLACK)
    for y in range(2, h - 3):
        s.set(0, y, BLACK)
    for y in range(3, h - 2):
        s.set(w - 1, y, BLACK)
    for (x, y) in ((1, 1), (w - 3, 1), (w - 2, 2), (1, h - 3), (2, h - 2), (w - 2, h - 2)):
        s.set(x, y, BLACK)
    for (x, y) in ((0, 0), (1, 0), (0, 1), (w - 3, 0), (w - 2, 0), (w - 1, 0), (w - 2, 1), (w - 1, 1),
                   (w - 1, 2), (0, h - 3), (0, h - 2), (1, h - 2), (0, h - 1), (1, h - 1), (2, h - 1),
                   (w - 1, h - 2), (w - 2, h - 1), (w - 1, h - 1)):
        s.px[y][x] = CLEAR


def _slot(s: Sprite, ix: int, iy: int, size: int = 18) -> None:
    """Slot frame whose interior starts at the item position (ix, iy); ``size`` is the frame."""
    pad = (size - 16) // 2
    x0, y0 = ix - pad, iy - pad
    x1, y1 = x0 + size - 1, y0 + size - 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            s.set(x, y, SLOT_BG)
    for x in range(x0, x1):
        s.set(x, y0, SLOT_DARK)
    for y in range(y0, y1):
        s.set(x0, y, SLOT_DARK)
    for x in range(x0 + 1, x1 + 1):
        s.set(x, y1, WHITE)
    for y in range(y0 + 1, y1 + 1):
        s.set(x1, y, WHITE)
    s.set(x1, y0, SLOT_BG)
    s.set(x0, y1, SLOT_BG)


FLAME = [
    "......#.......",
    "......##......",
    ".....###......",
    ".....####.....",
    "....#####..#..",
    "..#.#####..#..",
    "..#.######.##.",
    ".##.######.##.",
    ".############.",
    ".############.",
    "..##########..",
    "..##########..",
    "...########...",
    "....######....",
]


def _flame_mask():
    return {(x, y) for y, row in enumerate(FLAME) for x, ch in enumerate(row) if ch == "#"}


def _depth(mask: set, x: int, y: int) -> int:
    d = 0
    while all((x + dx, y + dy) in mask for dx in range(-d - 1, d + 2) for dy in range(-d - 1, d + 2)
              if abs(dx) + abs(dy) <= d + 1):
        d += 1
        if d > 6:
            break
    return d


def draw_flame(s: Sprite, ox: int, oy: int, lit: bool) -> None:
    mask = _flame_mask()
    if not lit:
        dark, mid = hexc("#8b8b8b"), hexc("#7c7c7c")
        for (x, y) in mask:
            s.set(ox + x, oy + y, dark)
        for (x, y) in mask:      # faint inner tongue keeps the shape legible
            if _depth(mask, x, y) >= 2 and y >= 6:
                s.set(ox + x, oy + y, mid)
        return
    cols = [hexc(c) for c in ("#a8200e", "#e0461a", "#f6861e", "#fcc838", "#fff2a8")]
    for (x, y) in mask:
        d = _depth(mask, x, y)
        heat = min(d, 3) + (1 if (y >= 10 and 5 <= x <= 8) else 0)
        s.set(ox + x, oy + y, cols[min(4, heat)])


# progress arrow 24x17: 3px shaft (rows 7..9) and a 9-column head
def _arrow_mask():
    m = set()
    for x in range(0, 15):
        for y in (7, 8, 9):
            m.add((x, y))
    for i, x in enumerate(range(15, 24)):
        for y in range(i, 17 - i):
            m.add((x, y))
    return m


def draw_arrow(s: Sprite, ox: int, oy: int, full: bool) -> None:
    m = _arrow_mask()
    for (x, y) in m:
        if not full:
            s.set(ox + x, oy + y, SLOT_BG)
            continue
        below = (x, y + 1) not in m
        right = (x + 1, y) not in m and y > 8
        s.set(ox + x, oy + y, hexc("#b8b8b8") if (below or right) else WHITE)


BOWL_GHOST = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "..LLLLLLLLLLLL..",
    ".LDDDDDDDDDDDDL.",
    ".BBBBBBBBBBBBBB.",
    "..BBBBBBBBBBBB..",
    "..BBBBBBBBBBBB..",
    "...BBBBBBBBBB...",
    "....BBBBBBBB....",
    ".....BBBBBB.....",
    "................",
    "................",
]


def draw_bowl_ghost(s: Sprite, ix: int, iy: int) -> None:
    pal = {"L": hexc("#9c9c9c"), "D": hexc("#767676"), "B": hexc("#7f7f7f")}
    for y, row in enumerate(BOWL_GHOST):
        for x, ch in enumerate(row):
            if ch in pal:
                s.set(ix + x, iy + y, pal[ch])


def cooking_pot_gui() -> Sprite:
    s = Sprite(256, 256)
    _panel(s, PANEL_W, PANEL_H)
    for (x, y) in INPUT_SLOTS:
        _slot(s, x, y)
    _slot(s, *CONTAINER_SLOT)
    draw_bowl_ghost(s, *CONTAINER_SLOT)
    _slot(s, *OUTPUT_SLOT, size=26)
    for (x, y) in player_slots():
        _slot(s, x, y)
    draw_flame(s, *FLAME_POS, lit=False)
    draw_arrow(s, *ARROW_POS, full=False)
    # sprites
    draw_flame(s, *LIT_FLAME_UV, lit=True)
    draw_arrow(s, *FULL_ARROW_UV, full=True)
    return s


# =========================================================================== mob effects


def _draw18(rows: list[str], pal: Pal) -> Sprite:
    s = Sprite(18, 18)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal.chars:
                s.set(x, y, pal.chars[ch])
    return s


WELL_FED = [
    "..................",
    "..........aaa.....",
    "........aABBba....",
    ".......aBBBBBba...",
    "......aBBbBBBbba..",
    "......ABBBBBBbba..",
    "......aBBBBBbbba..",
    "......abBBbbbbba..",
    ".......abbbbbba...",
    "......wWabbbbba...",
    ".....wWW.aaaaa....",
    "....wWw...........",
    "...wWw............",
    ".wWWw.............",
    "wWWWW.............",
    ".wWw..............",
    "..w...............",
    "..................",
]


def well_fed() -> Sprite:
    p = Pal()
    meat = [hexc(c) for c in ("#5a2a0a", "#8a4210", "#c06a1e", "#e0962e", "#f6c45a", "#fff0a0")]
    p.put("a", meat[1], meat[0]).put("b", meat[2], meat[0]).put("B", meat[3], meat[0]).put("A", meat[4], meat[0])
    bone = [hexc(c) for c in ("#6a6250", "#c8bea0", "#f2ecd8", "#ffffff")]
    p.put("w", bone[1], bone[0]).put("W", bone[2], bone[0])
    s = _draw18(WELL_FED, p)
    # golden glaze glints
    for (x, y) in ((9, 3), (8, 4), (10, 2)):
        s.set(x, y, meat[5])
    return outline_material(s, p)


COZY = [
    "..................",
    "..................",
    "..................",
    "..................",
    "..................",
    "..................",
    "...RRRRRRRRR......",
    "...rCCCCCCCrR.....",
    "...rLMMMMMMrRRR...",
    "...rLMMMMMMrr.R...",
    "...rLMMMMMMrr.R...",
    "...rLMMMMMMrRRR...",
    "...rLMMMMMmrR.....",
    "...rrmmmmmmr......",
    "..f.rrrrrrr.......",
    ".fFf..............",
    ".fYf..............",
    "..................",
]


def cozy() -> Sprite:
    p = Pal()
    mug = [hexc(c) for c in ("#4a1a10", "#8a3220", "#b44a2e", "#d06a44", "#e88a5e", "#f6b08a")]
    p.put("R", mug[2], mug[0]).put("r", mug[2], mug[0]).put("M", mug[3], mug[0]).put("m", mug[2], mug[0])
    p.put("L", mug[5], mug[0]).put("C", hexc("#5a3018"), mug[0])
    p.put("s", hexc("#f2f2f2"), hexc("#8a8a98"))
    p.put("f", hexc("#e0461a"), hexc("#6a1a08")).put("F", hexc("#f6a020"), hexc("#6a1a08"))
    p.put("Y", hexc("#fff0a0"), hexc("#6a1a08"))
    s = _draw18(COZY, p)
    s.set(4, 7, hexc("#7a4224"))      # cocoa highlight
    s.set(5, 7, hexc("#7a4224"))
    s = outline_material(s, p)
    # two soft steam wisps rising from the drink (no hard outline so they stay airy)
    hi, lo = hexc("#ffffff"), hexc("#b8bcc8")
    for (x, y, c) in ((5, 5, lo), (6, 4, hi), (6, 3, hi), (5, 2, lo), (5, 1, hi),
                      (9, 5, lo), (9, 4, hi), (10, 3, hi), (10, 2, lo), (9, 1, hi), (9, 0, lo)):
        s.set(x, y, c)
    return s


CAFFEINATED = [
    "..................",
    "...........yy.....",
    "..........yYy.....",
    ".........yYy......",
    "........yYyyyy....",
    ".......yYYYYy.....",
    "......yyyyYy......",
    "....bbbb.yY.......",
    "...bBBBbbyy.......",
    "..bBBBBbcb........",
    "..bBBBbcBb........",
    ".bBBBbcBBb........",
    ".bBBbcBBBb........",
    ".bBbcBBBbb........",
    "..bcBBBbb.........",
    "..bbBbbb..........",
    "...bbb............",
    "..................",
]


def caffeinated() -> Sprite:
    p = Pal()
    bean = [hexc(c) for c in ("#1e0e06", "#4a2412", "#7a3e1e", "#a0582e", "#c27a48")]
    p.put("b", bean[2], bean[0]).put("B", bean[3], bean[0]).put("c", bean[1], bean[0])
    bolt = [hexc(c) for c in ("#6a4a00", "#f2c418", "#fff27a")]
    p.put("y", bolt[1], bolt[0]).put("Y", bolt[2], bolt[0])
    s = _draw18(CAFFEINATED, p)
    for (x, y) in ((4, 8), (3, 9), (5, 8)):
        s.set(x, y, bean[4])
    return outline_material(s, p)


def effect_icons() -> dict[str, Sprite]:
    return {"well_fed": well_fed(), "cozy": cozy(), "caffeinated": caffeinated()}


# =========================================================================== logo


def logo_small() -> Sprite:
    """64x64 emblem (upscaled 2x to 128): round badge, sprout from a soil mound,
    a tomato on the left and wheat on the right, warm farmhouse palette."""
    N = 64
    s = Sprite(N, N)
    cx, cy, R = 31.5, 31.5, 30.5

    def inside(x, y, r=R):
        return (x + 0.5 - cx - 0.5) ** 2 + (y + 0.5 - cy - 0.5) ** 2 <= r * r

    sky = [hexc(c) for c in ("#fbe6a8", "#f8d890", "#f4c47a", "#eeb06a")]
    for y in range(N):
        for x in range(N):
            if inside(x, y):
                band = min(3, max(0, (y - 6) // 9))
                s.set(x, y, sky[band])
    # sun
    sun = [hexc("#fff4c8"), hexc("#fde59a")]
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - 31.5, y - 27.5)
            if d <= 11.5 and inside(x, y):
                s.set(x, y, sun[0] if d <= 9.5 else sun[1])
    # distant field strip
    for x in range(N):
        for y in range(38, 41):
            if inside(x, y):
                s.set(x, y, hexc("#9aa848") if y == 38 else hexc("#7e9038"))
    # soil mound (dome) with tilled furrows that follow its curve
    soil = [hexc(c) for c in ("#2a170c", "#3e2414", "#55321c", "#6e4426", "#8a5a34", "#a8744a")]

    def soil_top(x):
        return 41 - 9 * math.exp(-((x - 31.5) / 15.0) ** 2)

    for y in range(N):
        for x in range(N):
            if not inside(x, y):
                continue
            top = soil_top(x)
            if y < top:
                continue
            depth = y - top
            if depth < 1.0:
                c = soil[5] if x < 30 else soil[4]          # sunlit crest
            else:
                band = int((depth - 1.0) / 3.0)
                within = (depth - 1.0) - band * 3.0
                c = soil[3 - min(2, band // 2)] if within < 1.0 else soil[2 - min(1, band // 3)]
                if within >= 2.0:
                    c = soil[1]                            # furrow shadow
            s.set(x, y, c)
    for (x, y) in ((22, 40), (37, 37), (44, 44), (28, 47), (50, 41), (12, 50), (40, 52), (33, 43)):
        if inside(x, y) and y >= soil_top(x) + 1:
            s.set(x, y, soil[5])                            # clods / pebbles
            s.set(x + 1, y, soil[4])
    # sprout: 2px stem with a gentle S-curve and two leaves
    leaf = [hexc(c) for c in ("#1c4a12", "#2f7020", "#46952c", "#66b83c", "#96d860")]
    for y in range(20, 34):
        x = 31 + (1 if y < 25 else 0) - (1 if y > 30 else 0)
        s.set(x, y, leaf[3])
        s.set(x + 1, y, leaf[2])

    def ellipse_leaf(cx_, cy_, rx, ry, ang):
        ca, sa = math.cos(ang), math.sin(ang)
        for y in range(N):
            for x in range(N):
                dx, dy = x + 0.5 - cx_, y + 0.5 - cy_
                u = (dx * ca + dy * sa) / rx
                v = (-dx * sa + dy * ca) / ry
                if u * u + v * v <= 1.0:
                    if abs(v) < 0.2 and -0.7 < u < 0.75:
                        c = leaf[4]                     # midrib
                    elif v < 0:
                        c = leaf[3] if u * u + v * v < 0.7 else leaf[2]
                    else:
                        c = leaf[2] if u * u + v * v < 0.7 else leaf[1]
                    s.set(x, y, c)

    ellipse_leaf(25.0, 17.5, 7.5, 4.0, math.radians(-28))
    ellipse_leaf(39.5, 15.0, 9.5, 4.8, math.radians(25))
    # tomato (left, nestled in the soil)
    tom = [hexc(c) for c in ("#6a0e0a", "#9a1a12", "#c82a1e", "#e04430", "#f4785a")]
    sphere_shade(s, 15.5, 40.5, 8.2, tom)
    for (x, y) in ((11, 36), (12, 36), (11, 37)):
        s.set(x, y, hexc("#fff0e0"))
    calyx = [(15, 32), (16, 32), (14, 33), (15, 33), (16, 33), (17, 33), (13, 33), (18, 33), (15, 31), (16, 31),
             (16, 30), (12, 34), (19, 34)]
    for (x, y) in calyx:
        s.set(x, y, leaf[2])
    s.set(16, 30, leaf[3])
    s.set(15, 33, leaf[3])
    # wheat (right): two leaning stalks with braided ears and awns
    gold = [hexc(c) for c in ("#7a5414", "#a8781e", "#d0a032", "#e8c050", "#f8e08a")]
    for (bx, by, top, lean) in ((46, 38, 14, 0), (52, 39, 18, 1)):
        # stalk
        for y in range(top + 10, by + 1):
            x = bx + (lean if y < by - 8 else 0)
            s.set(x, y, gold[2])
        # leaf blade off the stalk
        for i in range(4):
            s.set(bx - 1 - i, by - 6 - i // 2, leaf[2] if i < 3 else leaf[3])
        # braided ear: kernels alternating left/right of the axis
        ex = bx + lean
        for k in range(5):
            y = top + 2 * k + 1
            s.set(ex - 1, y, gold[3])
            s.set(ex - 1, y + 1, gold[2])
            s.set(ex, y, gold[4] if k < 3 else gold[3])
            s.set(ex, y + 1, gold[3])
            s.set(ex + 1, y + 1, gold[2])
            s.set(ex + 1, y + 2, gold[1])
        s.set(ex, top, gold[4])
        for i in range(1, 4):           # awns
            s.set(ex - i, top - i + 1, gold[3])
            s.set(ex + i, top - i + 1, gold[3])
        s.set(ex, top - 2, gold[3])
    # outline all foreground subjects (sprout, tomato, wheat) against the sky/sun
    fg = Sprite(N, N)
    # (re-detect foreground by colour family: leaf/tomato/gold)
    fg_cols = set(leaf) | set(tom) | set(gold) | {hexc("#fff0e0")}
    for y in range(N):
        for x in range(N):
            if s.px[y][x] in fg_cols:
                fg.px[y][x] = s.px[y][x]
    ink = hexc("#3a1e10")
    for y in range(N):
        for x in range(N):
            if fg.opaque(x, y) or not inside(x, y):
                continue
            if any(fg.opaque(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                bg = s.px[y][x]
                if bg not in soil:
                    s.px[y][x] = ink
                else:
                    s.px[y][x] = soil[0]
    # badge rim: wood ring with a highlight, transparent outside
    wood = [hexc(c) for c in ("#3a2210", "#5a3618", "#7a4c22", "#9a6430", "#b88048")]
    for y in range(N):
        for x in range(N):
            d = math.hypot(x + 0.5 - 32, y + 0.5 - 32)
            if d > 31.6:
                s.px[y][x] = CLEAR
            elif d > 30.6:
                s.px[y][x] = wood[0]
            elif d > 28.4:
                ang = math.atan2(y + 0.5 - 32, x + 0.5 - 32)
                lit = math.cos(ang + math.radians(135))
                s.px[y][x] = wood[4] if lit > 0.55 else wood[3] if lit > -0.2 else wood[2]
            elif d > 27.6:
                s.px[y][x] = wood[1]
    return s


def logo() -> Image.Image:
    return logo_small().image().resize((128, 128), Image.NEAREST)
