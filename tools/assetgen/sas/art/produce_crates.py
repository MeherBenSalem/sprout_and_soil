"""Crate block textures (produce lane): shared side/bottom + one top per stored produce.

* ``crate_side``: sturdy slatted crate wall - dark corner posts, top/bottom rails,
  two slats with dark gaps (interior shadow), nail heads.
* ``crate_bottom``: four boards between corner post ends.
* ``<item>_crate_top``: 2 px wooden rim (lit top surface, darker outer bevel, post
  end-grain at the corners) around a heap of the produce, drawn as small 3-5 px
  shapes on a jittered grid with random variants, clipped by the rim and shadowed
  along the inner top/left walls.
"""
from __future__ import annotations

import random
from typing import Callable

from .core import Sprite, hexc
from .produce_kit import adj, mat, pal, render

CRATES: dict[str, Callable[[], Sprite]] = {}

WOOD = mat("#a8784a", 0.085)
POST = mat("#7a5232", 0.08)
NAIL = "#4c4a52"
INTERIOR = (0x3a, 0x26, 0x18, 255)     # shadowed crate interior showing between produce


def crate(name: str):
    def deco(fn):
        CRATES[name] = fn
        return fn
    return deco


# --------------------------------------------------------------------------- side & bottom


def _grain(rows: list[list[str]], y0: int, y1: int, x0: int, x1: int, rng: random.Random, p: float = 0.18):
    """Horizontal wood grain: short darker/lighter streaks inside a board."""
    for y in range(y0, y1 + 1):
        x = x0 + rng.randrange(0, 3)
        while x <= x1:
            run = rng.randrange(2, 5)
            if rng.random() < p * 2:
                d = -1 if rng.random() < 0.7 else 1
                for k in range(run):
                    if x + k <= x1:
                        rows[y][x + k] = adj(rows[y][x + k], d)
            x += run + rng.randrange(1, 4)


@crate("crate_side")
def crate_side() -> Sprite:
    rng = random.Random(41)
    g = [["." for _ in range(16)] for _ in range(16)]
    boards = [(0, 1), (3, 6), (8, 11), (13, 15)]
    for y in range(16):
        for x in range(2, 14):
            g[y][x] = "x"
    for y0, y1 in boards:
        for y in range(y0, y1 + 1):
            t = "4" if y == y0 else ("2" if y == y1 else "3")
            for x in range(2, 14):
                g[y][x] = t
        _grain(g, y0 + 1 if y1 - y0 > 1 else y0, y1 - 1 if y1 - y0 > 1 else y1, 2, 13, rng)
    for y in range(16):
        g[y][0], g[y][1] = "d", "c"
        g[y][14], g[y][15] = "c", "a"
        if rng.random() < 0.25:
            g[y][1] = "b"
        if rng.random() < 0.25:
            g[y][14] = "b"
    g[0][0] = g[0][1] = "e"
    g[0][14] = "d"
    g[15][0] = g[15][1] = g[15][14] = "b"
    g[15][15] = "a"
    for y in (4, 9, 14):
        g[y][2], g[y][13] = "n", "n"
    g[0][2] = g[0][13] = "n"
    rows = ["".join(r) for r in g]
    gap = POST.ramp[0]
    p = pal(WOOD, POST, x=(tuple(c - 18 if c > 18 else c for c in gap[:3]) + (255,), None, True), n=NAIL)
    return render(rows, p, outline=False)


@crate("crate_bottom")
def crate_bottom() -> Sprite:
    rng = random.Random(7)
    g = [["3"] * 16 for _ in range(16)]
    for b in range(4):
        y0 = b * 4
        for y in range(y0, y0 + 4):
            t = "4" if y == y0 else ("1" if y == y0 + 3 else "3")
            for x in range(16):
                g[y][x] = t
        _grain(g, y0 + 1, y0 + 2, 2, 13, rng)
    for (cx, cy) in ((0, 0), (14, 0), (0, 14), (14, 14)):
        g[cy][cx], g[cy][cx + 1] = "d", "c"
        g[cy + 1][cx], g[cy + 1][cx + 1] = "c", "b"
    for y in (1, 5, 9, 13):
        g[y][3], g[y][12] = "n", "n"
    rows = ["".join(r) for r in g]
    return render(rows, pal(WOOD, POST, n=NAIL), outline=False)


# --------------------------------------------------------------------------- tops

# mini shapes (bodies only): 1..5 main ramp, a..e accent ramp, z accent ink.  Each stamp also
# draws a 1 px dark ring ("o") around its body so overlapping produce stays readable.
MINI: dict[str, list[list[str]]] = {
    "apple": [[".4c4.", "45443", "45432", "34322", ".222."], [".44c.", "45543", "44432", "33322", ".222."]],
    "orange": [[".444.", "45c43", "45433", "34332", ".222."], [".444.", "4c543", "44533", "34322", ".222."]],
    "peach": [[".444.", "4544c", "454cb", "343b2", ".222."], [".44c.", "4543c", "4543b", "3432b", ".222."]],
    "tomato": [[".4b4.", "4bcb3", "45b32", "34322", ".222."], [".44b.", "45bcb", "443b2", "34322", ".222."]],
    "onion": [["..4..", ".454.", "45443", "34432", ".222."], ["..4..", ".445.", "44543", "34332", ".222."]],
    "garlic": [["..4..", ".454.", "45c54", "4c5c3", ".333."], ["..4..", ".544.", "45c43", "3c4c3", ".232."]],
    "beet": [[".444.", "45443", "45432", "34322", ".2c2.", "..c.."], [".444.", "45543", "44432", "33322", ".c22.", ".c..."]],
    "turnip": [[".ccd.", "cdddc", "45543", "34432", ".222.", "..2.."], [".dcc.", "cddcc", "44543", "34432", ".222.", ".2..."]],
    "radish": [[".444.", "45543", "44432", ".322.", "..c..", "..c.."], [".444.", "45443", "45432", ".322.", "..c..", ".c..."]],
    "pepper": [[".bc..", "45b54", "45443", "34432", "3.3.2"], ["..cb.", "45b54", "44543", "34432", "2.3.3"]],
    "eggplant": [["...bc", "..4cb", ".4543", "45432", "3432.", ".22.."], ["cb...", "bc4..", "3454.", "23454", ".2343", "..22."]],
    "cabbage": [[".4554.", "45dd54", "4dccd3", "4cd4c3", "34dc32", ".3222."],
                [".4554.", "4dd544", "4cdcd3", "3d4cd3", "33cd32", ".2222."]],
    "lettuce": [["4.45.4", "45dd54", "4dccd3", "34dd43", "334432", "3.3.2."],
                [".4.54.", "4dd545", "4cdd43", "34cd43", "33d332", ".3.2.3"]],
    "potato": [[".4444.", "45543c", "4c4433", "343c32", ".2222."], [".4444.", "4c5443", "445c32", "34433c", ".2222."]],
    "lemon": [["..44..", ".45543", "455432", ".3432.", "..2..."], ["..44..", "345543", "234554", ".2343.", "...2.."]],
    "mango": [[".4455.", "455443", "4544c2", ".34cc.", "..bc.."], [".4544.", "445543", "34544c", ".3cc2.", "..cb.."]],
    "pear": [["..c..", "..4..", ".454.", "45543", "45432", ".222."], ["..c..", "..4..", ".445.", "44543", "34432", ".222."]],
    # long produce, laid diagonally in parallel rows
    "carrot": [[".....bc", "....44b", "...443.", "..443..", ".443...", "432....", "3......"]],
    "cucumber": [["....45", "...453", "..4543", ".4543.", "4543..", "343...", "32...."]],
    "sweet_potato": [["....44", "...4543", "..45432", ".45432.", "4543...", "332...."]],
    "cob": [["....cd", "...545c", "..5454.", ".5454..", "5454...", "4543...", "b3....."]],
    "chili": [["....bc", "...44.", "..443.", ".443..", "443...", "32....", "2....."]],
}


def _flip(rows: list[str]) -> list[str]:
    w = max(len(r) for r in rows)
    return [r.ljust(w, ".")[::-1] for r in rows]


def heap(shapes: list[str], pitch: tuple[float, float], seed: int, jitter: int = 1,
         flip: bool = True, layers: int = 1) -> list[list[str]]:
    """Fill a 16x16 char grid with produce on jittered staggered grids (the rim clips it).

    A back layer (offset by half a pitch, one tone darker) fills the gaps so the heap
    reads as deep; every stamp writes a dark ring around its body first, so
    overlapping pieces stay distinct."""
    rng = random.Random(seed)
    g = [["_"] * 16 for _ in range(16)]
    sx, sy = pitch
    for layer in range(layers):
        back = layer < layers - 1
        y = -0.5 + (sy / 2 if back else 0)
        row = 0
        while y < 14:
            x = -1.0 + (sx / 2 if (row + layer) % 2 else 0) + rng.uniform(-0.5, 0.5)
            while x < 14:
                var = rng.choice(MINI[rng.choice(shapes)])
                if flip and rng.random() < 0.5:
                    var = _flip(var)
                ox = int(round(x + rng.randint(-jitter, jitter)))
                oy = int(round(y + rng.randint(-jitter, jitter)))
                body = {(ox + xx, oy + yy): ch for yy, r in enumerate(var) for xx, ch in enumerate(r) if ch != "."}
                for (px, py) in body:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        q = (px + dx, py + dy)
                        if q not in body and 0 <= q[0] < 16 and 0 <= q[1] < 16:
                            g[q[1]][q[0]] = "o"
                for (px, py), ch in body.items():
                    if 0 <= px < 16 and 0 <= py < 16:
                        g[py][px] = adj(ch, -1) if back else ch
                x += sx
            y += sy
            row += 1
    return g


def finish_top(g: list[list[str]], M, A, gap_c, seed: int) -> Sprite:
    """Inner-wall shadow + 2 px wooden rim around a filled 16x16 char grid, then render."""
    # inner rim shadow on the top/left walls (light from the top-left)
    for i in range(2, 14):
        for (x, y) in ((i, 2), (2, i)):
            g[y][x] = adj(g[y][x], -2) if g[y][x] in "12345abcde" else "o"
    for i in range(3, 14):
        for (x, y) in ((i, 3), (3, i)):
            if g[y][x] in "12345abcde" and (x + y) % 2 == 0:
                g[y][x] = adj(g[y][x], -1)
    for y in range(16):
        for x in range(16):
            ring = min(x, y, 15 - x, 15 - y)
            if ring >= 2:
                continue
            if (x < 2 or x > 13) and (y < 2 or y > 13):        # corner post end-grain
                if x > 13 and y > 13:
                    g[y][x] = "Q"
                elif x in (0, 15) and y in (0, 15):
                    g[y][x] = "S"
                else:
                    g[y][x] = "R" if (x < 2 and y < 2) else "T"
                continue
            if ring == 0:
                g[y][x] = "W" if (y == 0 or x == 0) else "U"
            else:
                g[y][x] = "X" if (y == 1 or x == 1) else "V"
    rng = random.Random(seed * 7 + 3)
    for _ in range(12):                                     # a little grain on the rim
        a, b = rng.randrange(2, 14), rng.choice([0, 1, 14, 15])
        x, y = (a, b) if rng.random() < 0.5 else (b, a)
        g[y][x] = {"X": "W", "W": "V", "V": "U", "U": "U"}[g[y][x]]
    rows = ["".join(r) for r in g]
    p = pal(M, A)
    wr, pr = WOOD.ramp, POST.ramp
    p.update({
        "_": (INTERIOR, None, True), "o": (gap_c, None, True),
        "W": (wr[3], None, True), "U": (wr[1], None, True), "X": (wr[4], None, True), "V": (wr[2], None, True),
        "R": (pr[3], None, True), "S": (pr[2], None, True), "T": (pr[1], None, True), "Q": (pr[0], None, True),
        "z": (A.ol[1], None, True),
    })
    return render(rows, p, outline=False)


def crate_top(main: str, accent: str, shapes: list[str], pitch=(4.0, 3.6), seed: int = 1,
              spread: float = 0.115, accent_spread: float = 0.09, gap: str | None = None,
              tweak: Callable[[list[list[str]], random.Random], None] | None = None,
              main_mat=None, accent_mat=None, flip: bool = True, jitter: int = 1) -> Sprite:
    M = main_mat or mat(main, spread)
    A = accent_mat or mat(accent, accent_spread)
    gap_c = hexc(gap) if gap else cap_lightness(M.ol[2], 0.20)
    g = heap(shapes, pitch, seed, flip=flip, jitter=jitter)
    if tweak:
        tweak(g, random.Random(seed + 100))
    return finish_top(g, M, A, gap_c, seed)


def cap_lightness(c, lmax: float):
    """Keep separation rings dark even for pale produce (garlic, turnip, lemon...)."""
    import colorsys
    h, l, sat = colorsys.rgb_to_hls(*(v / 255 for v in c[:3]))
    if l <= lmax:
        return c
    r, g, b = colorsys.hls_to_rgb(h, lmax, sat)
    return (round(r * 255), round(g * 255), round(b * 255), 255)


# ---- vanilla produce (approximate vanilla palettes, never copied pixels)


@crate("apple_crate_top")
def apple_crate_top():
    return crate_top("#dc1c28", "#6a3a14", ["apple"], pitch=(5.0, 4.4), seed=11, spread=0.12)


@crate("carrot_crate_top")
def carrot_crate_top():
    return crate_top("#f08a12", "#2f9a26", ["carrot"], pitch=(3.4, 6.0), seed=12, flip=False, jitter=0)


@crate("potato_crate_top")
def potato_crate_top():
    return crate_top("#d6a650", "#9a7a44", ["potato"], pitch=(5.6, 4.4), seed=13)


@crate("beetroot_crate_top")
def beetroot_crate_top():
    return crate_top("#a02a3e", "#5a1a2a", ["beet"], pitch=(5.0, 4.8), seed=14, spread=0.11)


# ---- mod produce (colours match the item sprites)


@crate("tomato_crate_top")
def tomato_crate_top():
    return crate_top("#d8322a", "#3f8a2a", ["tomato"], pitch=(5.0, 4.4), seed=21)


@crate("bell_pepper_crate_top")
def bell_pepper_crate_top():
    return crate_top("#c8281e", "#3c7a26", ["pepper"], pitch=(5.0, 4.6), seed=22)


@crate("chili_pepper_crate_top")
def chili_pepper_crate_top():
    return crate_top("#d7261e", "#3c7a26", ["chili"], pitch=(3.0, 5.4), seed=23, flip=False)


@crate("eggplant_crate_top")
def eggplant_crate_top():
    return crate_top("#4a2160", "#4a7a2a", ["eggplant"], pitch=(5.0, 5.0), seed=24,
                     main_mat=mat("#4a2160", 0.10, lift=0.05))


@crate("cucumber_crate_top")
def cucumber_crate_top():
    return crate_top("#3e7d2e", "#a7d06a", ["cucumber"], pitch=(3.4, 6.0), seed=25, flip=False, jitter=0)


@crate("cabbage_crate_top")
def cabbage_crate_top():
    return crate_top("#86b862", "#c8e0a2", ["cabbage"], pitch=(6.0, 5.4), seed=26)


@crate("lettuce_crate_top")
def lettuce_crate_top():
    return crate_top("#7cc04a", "#c9e88a", ["lettuce"], pitch=(6.0, 5.4), seed=27)


@crate("garlic_crate_top")
def garlic_crate_top():
    return crate_top("#efe6d6", "#b89ab0", ["garlic"], pitch=(5.0, 4.6), seed=28, spread=0.09)


@crate("onion_crate_top")
def onion_crate_top():
    return crate_top("#c88a3a", "#7a4a22", ["onion"], pitch=(5.0, 4.4), seed=29)


@crate("radish_crate_top")
def radish_crate_top():
    return crate_top("#d23a5a", "#f2ecea", ["radish"], pitch=(5.0, 5.0), seed=30)


@crate("turnip_crate_top")
def turnip_crate_top():
    return crate_top("#ece4d6", "#9a4a8a", ["turnip"], pitch=(5.0, 4.8), seed=31, spread=0.09)


@crate("sweet_potato_crate_top")
def sweet_potato_crate_top():
    return crate_top("#b8503a", "#e8964a", ["sweet_potato"], pitch=(3.8, 5.6), seed=32, flip=False)


@crate("corn_crate_top")
def corn_crate_top():
    return crate_top("#f2c63a", "#a8c86a", ["cob"], pitch=(3.6, 6.0), seed=33, flip=False, jitter=0)


@crate("rice_crate_top")
def rice_crate_top():
    M = mat("#f2ecd8", 0.07, lift=-0.04)
    rng = random.Random(34)
    g = [["3" if rng.random() < 0.5 else "2" for _ in range(16)] for _ in range(16)]
    for _ in range(64):
        x, y = rng.randrange(0, 15), rng.randrange(1, 15)
        dx, dy = rng.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
        g[y][x] = "5"
        g[y + dy][x + dx] = "4"
        if 0 <= x - 1 and 0 <= y + 1 < 16:
            g[y + 1][x - 1] = "1" if g[y + 1][x - 1] in "23" else g[y + 1][x - 1]
    return finish_top(g, M, mat("#c8b88a", 0.08), M.ol[2], 34)


@crate("lemon_crate_top")
def lemon_crate_top():
    return crate_top("#f2d83a", "#3f7a2a", ["lemon"], pitch=(5.4, 4.2), seed=35)


@crate("orange_crate_top")
def orange_crate_top():
    return crate_top("#f08a1a", "#3f7a2a", ["orange"], pitch=(5.0, 4.4), seed=36)


@crate("peach_crate_top")
def peach_crate_top():
    return crate_top("#f2ae6a", "#e0604a", ["peach"], pitch=(5.0, 4.4), seed=37)


@crate("pear_crate_top")
def pear_crate_top():
    return crate_top("#c8d050", "#6a4a2a", ["pear"], pitch=(4.8, 5.0), seed=38)


@crate("mango_crate_top")
def mango_crate_top():
    return crate_top("#f2b02a", "#e05a2a", ["mango"], pitch=(5.4, 4.6), seed=39)
