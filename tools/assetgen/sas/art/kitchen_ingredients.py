"""Ingredients: staples, pantry jars & bottles, meat and fish cuts, eggs, containers."""
from __future__ import annotations

import math

from .core import Sprite
from .kitchen_kit import (CORK, GLASS, JAR_FILL, JAR_GLASS, C, capsule, dome, ell, finish, jar_base, lit,
                          mug_base, plate_base, put, puts, reg, rng_for, rp, scatter, shade_pts, stamp, strip)
from .kitchen_parts import EGG


# ============================================================================ containers


@reg("plate")
def plate():
    """The empty plate item is centred vertically (dishes keep it at the bottom under the food)."""
    s = Sprite()
    plate_base(s)
    puts(s, [(4, 11), (5, 11)], "#ffffff")              # glaze glint
    puts(s, [(9, 12), (10, 12), (11, 12)], "#dcd8cc")   # faint shadow in the well
    return s.shift(0, -3)


@reg("mug")
def mug():
    s = Sprite()
    mug_base(s)
    put(s, 4, 9, "#f6b884")
    put(s, 4, 10, "#f6b884")
    return s


# ============================================================================ sacks & staples

SACK = [
    #0123456789abcdef
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "...F.FFFFFF.F...",  # 3   flared fabric opening (folded edge)
    "..FfppppppppfF..",  # 4   contents visible in the mouth
    "...fFppppppFf...",  # 5
    "....fFFFFFFf....",  # 6
    ".....tttttt.....",  # 7   twine at the cinched neck
    "....bbbbbbbd....",  # 8
    "...bbbbbbbbbd...",  # 9
    "..bbbbbbbbbbbd..",  # 10
    "..bbbbbbbbbbbd..",  # 11
    "..bbbbbbbbbbbd..",  # 12
    "...bbbbbbbbbd...",  # 13
    "....ddddddddd...",  # 14
]


def sack(burlap, contents, key) -> Sprite:
    s = Sprite()
    b = rp(burlap, 5, 0.09)
    c = rp(contents, 4, 0.07)
    stamp(s, SACK, {"F": b[3], "f": b[2], "t": "#6a4a24", "b": b[2], "d": b[1], "p": c[2]})
    body = [(x, y) for y in range(8, 15) for x in range(16) if SACK[y][x] in "bd"]
    dome(s, 7.6, 11.2, 5.9, 4.4, b, mask=lambda x, y: (x, y) in set(body), flat=0.9)
    # coarse burlap weave + seam/fold creases
    for x, y in body:
        if (x + y) % 4 == 0 and (x * 3 + y) % 2 == 0:
            s.set(x, y, b[1])
    puts(s, [(6, 9), (6, 10), (9, 11), (9, 12)], b[1])
    puts(s, [(5, 9), (8, 11)], b[3])
    puts(s, [(5, 7), (8, 7)], "#8a6a3a")
    # heaped contents in the mouth + a small spill down the side
    stamp(s, ["..hh..", ".hhll.", "hlllcc"], {"h": c[3], "l": c[2], "c": c[1]}, 5, 2)
    puts(s, [(12, 13), (13, 13), (12, 12), (2, 14)], c[2])
    put(s, 13, 12, c[3])
    return finish(s)


@reg("flour")
def flour():
    return sack("#c8a878", "#f4efe2", "flour")


@reg("cornmeal")
def cornmeal():
    return sack("#b89060", "#f2c84a", "cornmeal")


@reg("dough")
def dough():
    s = Sprite()
    d = rp("#efd9a8", 5, 0.07)
    pts = dome(s, 7.8, 10.2, 6.2, 4.6, d, flat=0.85)
    # fold crease and flour dusting
    puts(s, [(5, 9), (6, 10), (7, 10), (8, 10)], d[1])
    puts(s, [(5, 8), (6, 9)], d[3])
    puts(s, [(4, 7), (6, 6), (9, 7), (10, 9), (7, 8), (11, 11), (3, 10)], "#fffcf2")
    puts(s, [(12, 13), (13, 13), (2, 13)], "#f8f4ea")      # flour on the surface
    return finish(s)


@reg("tortilla")
def tortilla():
    s = Sprite()
    t = rp("#ecd08a", 5, 0.07)
    dome(s, 7.6, 9.0, 6.7, 4.6, t, flat=0.25)
    # thickness edge along the front
    for x in range(2, 14):
        y = 13 if 3 < x < 12 else 12
        s.set(x, y, t[1])
    for x, y in ((4, 7), (5, 7), (9, 6), (10, 9), (11, 9), (6, 10), (3, 10), (8, 8), (12, 7)):
        put(s, x, y, "#b88a4a")
    puts(s, [(5, 8), (10, 10), (9, 7)], "#c8a060")
    return finish(s)


@reg("raw_pasta")
def raw_pasta():
    """A nest of flat ribbons wound around a dark hollow centre."""
    s = Sprite()
    p = rp("#f2d88a", 5, 0.08)
    cx, cy = 7.8, 9.0
    for y in range(16):
        for x in range(16):
            r = math.hypot((x + 0.5 - cx) / 6.6, (y + 0.5 - cy) / 4.8)
            if r > 1.0:
                continue
            if r < 0.42:
                s.set(x, y, C("#8a6024") if y < cy else C("#b08a40"))
                continue
            band = int(r * 7.5)
            lightv = -((x + 0.5 - cx) / 6.6 + (y + 0.5 - cy) / 4.8) * 0.9
            v = 2 + (1 if band % 2 == 0 else -1) + round(lightv)
            if r < 0.55 and y > cy:          # inner wall of the nest catches light
                v = 4
            s.set(x, y, p[max(0, min(4, v))])
    puts(s, [(13, 12), (14, 11), (14, 10)], p[3])     # loose ribbon end
    return finish(s)


def powder_pile(r, grains, key, peak=5, extra=None) -> Sprite:
    """Rounded heap of fine powder sitting on the ground."""
    s = Sprite()
    r = [C(c) for c in r]
    pts = []
    for y in range(peak, 14):
        half = math.sqrt((y - peak + 0.6) * 5.2) + 0.2
        for x in range(16):
            dx = x + 0.5 - 7.8
            if abs(dx) <= half:
                v = 2.6 - dx / max(half, 1) * 1.5 - (0.7 if y >= 12 else 0.0) + (0.6 if y <= peak + 1 else 0)
                s.set(x, y, r[max(0, min(4, round(v)))])
                pts.append((x, y))
    rnd = rng_for(key)
    scatter(s, [p for p in pts if p[1] < 13], grains, len(pts) // 6, rnd, spacing=2)
    if extra:
        extra(s)
    return finish(s)


@reg("salt")
def salt():
    def extra(s):
        puts(s, [(7, 6), (6, 8), (5, 10)], "#ffffff")
        puts(s, [(13, 13), (14, 13)], "#e6ebf0")
    return powder_pile(["#a9b6c6", "#c9d4e0", "#e6ebf0", "#f8f8f4", "#ffffff"], ["#ffffff", "#d8e8f8", "#b8c6d6"],
                       "salt", extra=extra)


@reg("black_pepper")
def black_pepper():
    def extra(s):
        stamp(s, [".h.", "hbd", ".d."], {"h": "#7a6a5a", "b": "#3a302a", "d": "#1e1814"}, 12, 11)
    return powder_pile(["#1e1a18", "#2c2624", "#3e3632", "#564c44", "#706458"], ["#8a7a6a", "#151210", "#7a6a5a"],
                       "black_pepper", extra=extra)


@reg("butter")
def butter():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",  # 0
        "................",
        "................",
        "................",
        "......hTTwWwWw..",  # 4  top face: butter (left) + paper (right)
        "....hTTTTwwwWwe.",  # 5
        "..hTTTTTTwwwwWe.",  # 6
        ".FFFFFFFFPpppPe.",  # 7  front face
        ".FffFFFFFPpPppe.",  # 8
        ".FFFFFFFFPpppPe.",  # 9
        ".ffffffffPpppe..",  # 10
        "..ddddddddeee...",  # 11
    ]
    pal = {"h": "#fff6c0", "T": "#fbe890", "F": "#f6e07a", "f": "#e8c860", "d": "#c8a840",
           "w": "#fbfaf2", "W": "#e8e4d4", "P": "#efebde", "p": "#f8f6ee", "e": "#c8c2ae"}
    stamp(s, rows, pal)
    put(s, 2, 8, "#fff2b0")
    puts(s, [(10, 6), (11, 9)], "#d8d2c0")     # paper creases
    return finish(s)


@reg("cheese")
def cheese():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",  # 0
        "................",
        "............r...",  # 2
        "..........rTR...",  # 3
        "........rTTTR...",  # 4
        "......rTTTTTR...",  # 5
        "....rTTTTTTTR...",  # 6
        "..rhTTTTTTTTR...",  # 7
        "..FFFFFFFFFFRR..",  # 8  front face
        "..FFFFFFFFFFRR..",  # 9
        "..FFFFFFFFFFRR..",  # 10
        "..FFFFFFFFFFRR..",  # 11
        "..ffffffffffRR..",  # 12
    ]
    pal = {"r": "#f8d868", "h": "#fff0a0", "T": "#f6d050", "R": "#d89a28", "F": "#f2c03a", "f": "#e0a830"}
    stamp(s, rows, pal)
    hole = {"d": "#c88a1a", "k": "#a86a12", "l": "#f8d870"}
    for hx, hy in ((3, 9), (8, 10), (5, 11)):
        stamp(s, ["dk", "kl"], hole, hx, hy)
    stamp(s, ["dk"], hole, 9, 5)
    stamp(s, ["k"], hole, 7, 7)
    puts(s, [(10, 8), (6, 9)], "#c88a1a")
    return finish(s)


@reg("tofu")
def tofu():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",
        "................",
        "................",
        "......hhhhhh....",  # 3   top face
        ".....hTTTTTTr...",  # 4
        "....hTTTTTTrR...",  # 5
        "...hTTTTTTrRR...",  # 6
        "...FFFFFFFRRR...",  # 7   front + right faces
        "...FFFFFFFRRR...",  # 8
        "...FFFFFFFRRR...",  # 9
        "...FFFFFFFRRd...",  # 10
        "...ffffffffd....",  # 11
        "................",
    ]
    stamp(s, rows, {"h": "#fffef8", "T": "#f8f5ea", "r": "#e8e4d6", "F": "#ece8da", "f": "#d6d0c0",
                    "R": "#d2ccba", "d": "#bdb6a2"})
    puts(s, [(5, 8), (8, 10), (11, 8)], "#e0dbcc")   # soft pores
    return finish(s)


# ============================================================================ pastry bits


PIE_CRUST_ROWS = [
    #0123456789abcdef
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "................",  # 3
    "....HhHhHhHh....",  # 4   crimped rim (back)
    "..HhkkkkkkkkhH..",  # 5   back inner wall, in shadow
    ".HhkffffffffkhH.",  # 6   pale pastry floor
    ".hffFfffffFfffd.",  # 7
    ".HfffffFfffffdD.",  # 8
    "..hHffffffffdD..",  # 9
    "...HhHhHhHhdDd..",  # 10  crimped rim (front)
    "....sSssssss....",  # 11  side wall
    "................",
]


@reg("pie_crust")
def pie_crust():
    s = Sprite()
    stamp(s, PIE_CRUST_ROWS, {"H": "#f6d48c", "h": "#d8984a", "d": "#b47634", "D": "#8a5420",
                              "k": "#d8ae6c", "f": "#f6e4b4", "F": "#dcc08a", "s": "#b47634", "S": "#c88a44"})
    return finish(s)


WAFFLE = rp("#d89a4a", 5, 0.1)


def cone(s: Sprite, top: int = 6) -> None:
    """Waffle cone body (criss-cross) from row ``top`` down to the tip at row 15."""
    for y in range(top, 16):
        half = max(0, round((15 - y) * 0.42 + 0.5))
        for x in range(8 - half, 8 + half):
            k = ((x + y) % 3 == 0) or ((x - y) % 3 == 0)
            light = x < 8
            s.set(x, y, WAFFLE[1] if k else (WAFFLE[3] if light else WAFFLE[2]))
    for y in range(top, 15):
        half = max(0, round((15 - y) * 0.42 + 0.5))
        if half:
            s.set(8 - half, y, WAFFLE[3])


@reg("waffle_cone")
def waffle_cone():
    s = Sprite()
    cone(s, 5)
    rim = [
        "...rrrrrrrrrr...",
        "..rkkkkkkkkkkr..",
        "..RkkkkkkkkkkR..",
        "...RRRRRRRRRR...",
    ]
    stamp(s, rim, {"r": WAFFLE[4], "R": WAFFLE[3], "k": "#7a4a1e"}, 0, 2)
    puts(s, [(4, 4), (5, 4), (6, 4)], "#5e3614")
    put(s, 2, 4, WAFFLE[4])
    return finish(s)


@reg("chocolate_bar")
def chocolate_bar():
    s = Sprite()
    choc = rp("#5a2e1a", 5, 0.09)
    x0, y0, x1, y1, hw = 3.0, 13.0, 12.5, 3.5, 2.9
    ax, ay = x1 - x0, y1 - y0
    L = math.hypot(ax, ay)
    ux, uy = ax / L, ay / L
    nx, ny = -uy, ux
    if nx + ny > 0:
        nx, ny = -nx, -ny
    for y in range(16):
        for x in range(16):
            px, py = x + 0.5 - x0, y + 0.5 - y0
            t = px * ux + py * uy
            w = px * nx + py * ny
            if -0.6 <= t <= L + 0.6 and abs(w) <= hw:
                if t < L * 0.45:          # paper wrapper (lower-left)
                    col = "#e8dcc4" if w > 0 else "#cfc0a4"
                    if L * 0.36 < t:
                        col = "#c8282e" if w > 0 else "#a01e24"     # red band
                    if L * 0.43 < t:
                        col = "#d8dce4"   # foil edge
                    s.set(x, y, C(col))
                else:                      # chocolate with a segment grid
                    seg_t = (t - L * 0.45) % 3.0
                    v = 2
                    if seg_t < 1.0:
                        v = 1 if w < 0 else 3
                    if abs(w) < 0.6:
                        v = 1
                    if w > hw - 1.0:
                        v = 4 if seg_t >= 1.0 else 3
                    s.set(x, y, choc[v])
    return finish(s)


# ============================================================================ piles


def heap_of(items) -> Sprite:
    s = Sprite()
    for x, y, rows, pal in items:
        stamp(s, rows, pal, x, y)
    return finish(s)


@reg("raisins")
def raisins():
    r = {"h": "#9a6a62", "l": "#6e3c38", "b": "#4e2628", "d": "#30161a"}
    a = ["hl.", "lbd", ".dd"]
    b = ["hl", "bd"]
    c = [".h", "lb", "bd"]
    spots = [(6, 3, a), (4, 6, b), (8, 5, c), (10, 7, a), (2, 9, a), (6, 8, b), (8, 9, a), (11, 10, b),
             (4, 11, c), (7, 11, b), (12, 8, c)]
    return heap_of([(x, y, k, r) for x, y, k in spots])


@reg("roasted_coffee_beans")
def roasted_coffee_beans():
    s = Sprite()
    bean = {"h": "#c08a5c", "l": "#7e4c26", "b": "#563016", "d": "#38200c", "c": "#170a02"}
    a = [".hl.", "hlcb", "lcbd", ".bd."]
    b = [".hl.", "lcbb", "hlcd", ".bd."]
    for x, y, r in ((6, 2, a), (3, 5, b), (8, 5, a), (1, 8, a), (6, 8, b), (11, 8, a), (3, 11, b),
                    (8, 11, a)):
        stamp(s, r, bean, x, y)
    return finish(s)


# ============================================================================ jars


def jar(fill, lid, extra=None, cloth=None) -> Sprite:
    s = Sprite()
    jar_base(s, lid=lid)
    r = rp(fill, 5, 0.09)
    shade_pts(s, JAR_FILL, r)
    if extra:
        extra(s, r)
    # glass glints
    puts(s, [(3, 8), (3, 9), (4, 11)], GLASS["h"])
    if cloth:
        cloth(s)
    return finish(s, exclude=set(JAR_GLASS))


def cloth_cover(a, b, tie="#c8a868"):
    def draw(s):
        rows = [
            #0123456789abcdef
            "................",  # 0
            "................",
            "................",
            ".....abababa....",  # 3
            "....abababab....",  # 4
            "...abababababa..",  # 5
            "..ababababababa.",  # 6
            "..tttttttttttt..",  # 7  twine
            "..b.a.b..a.b.a..",  # 8  ruffled hem
        ]
        stamp(s, rows, {"a": a, "b": b, "t": tie})
        put(s, 13, 8, tie)
        put(s, 14, 9, tie)
    return draw


@reg("peanut_butter")
def peanut_butter():
    def extra(s, r):
        puts(s, [(5, 8), (6, 8), (7, 9), (9, 8), (10, 9)], r[3])     # swirl at the top
        puts(s, [(6, 11), (9, 12)], r[1])
    return jar("#b8783a", "#c8281e", extra)


@reg("berry_jam")
def berry_jam():
    def extra(s, r):
        puts(s, [(5, 10), (9, 9), (7, 12), (11, 11)], "#c8304e")      # fruit bits
        puts(s, [(6, 9), (10, 12)], "#5a0a24")
    return jar("#8a1a3a", "#c8281e", extra, cloth=cloth_cover("#d0283a", "#f8f0e6"))


@reg("orange_marmalade")
def orange_marmalade():
    def extra(s, r):
        for x, y in ((4, 9), (5, 9), (8, 10), (9, 10), (6, 12), (7, 12), (10, 8), (11, 12)):
            put(s, x, y, "#c85a0a")                                     # peel strips
        puts(s, [(5, 11), (9, 9)], "#fbb850")
    return jar("#e8801a", "#c8281e", extra, cloth=cloth_cover("#3a6ab0", "#f4f0e6"))


# ============================================================================ bottles (pantry)


@reg("cooking_oil")
def cooking_oil():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",  # 0
        "......kkK.......",  # 1  cork
        ".....lmmmo......",  # 2  lip
        "......l#o.......",  # 3  neck
        "......l#o.......",  # 4
        ".....lh##o......",  # 5
        "....lh####o.....",  # 6  shoulder
        "....lh####o.....",  # 7
        "....lLLLLLo.....",  # 8  label
        "....lLGGLLo.....",  # 9
        "....lLLLLLo.....",  # 10
        "....lh####o.....",  # 11
        "....lh###do.....",  # 12
        "....ol###do.....",  # 13
    ]
    oil = rp("#e8c84a", 5, 0.08)
    pal = dict(GLASS)
    pal.update({"k": CORK[2], "K": CORK[1], "#": oil[2], "L": "#f4ecd2", "G": "#5a8a2a"})
    stamp(s, rows, pal)
    for x, y in ((7, 4), (7, 5), (7, 6), (8, 6)):
        put(s, x, y, oil[3])
    for y in (7, 8, 12, 13, 14):
        put(s, 6, y, oil[4] if y < 9 else oil[3])
        put(s, 9, y, oil[1])
    puts(s, [(7, 14), (8, 14)], oil[1])
    put(s, 8, 10, "#8ab84a")
    glass = {(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch in "lhmdo"}
    return finish(s, exclude=glass)


@reg("soy_sauce")
def soy_sauce():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",  # 0
        "................",
        "......cCc.......",  # 2  red spout cap
        ".....cCCcd......",  # 3
        ".....RRRRd......",  # 4
        "......l#o.......",  # 5
        ".....lh##o......",  # 6
        "....lh####o.....",  # 7
        "....lh####o.....",  # 8
        "...lh######o....",  # 9
        "...lh######o....",  # 10
        "...lWWWWWWWo....",  # 11 label
        "...l#######o....",  # 12
        "....o######o....",  # 13
        ".....oooooo.....",  # 14
    ]
    soy = rp("#3a1a0a", 5, 0.07)
    pal = dict(GLASS)
    pal.update({"c": "#e83a2a", "C": "#c8201a", "R": "#9a1610", "d": "#6a0e0a", "#": soy[2],
                "W": "#f4ecd8"})
    stamp(s, rows, pal)
    puts(s, [(6, 7), (5, 9), (5, 10)], soy[4])
    puts(s, [(9, 9), (10, 10), (9, 12), (10, 12)], soy[1])
    puts(s, [(6, 11), (8, 11)], "#c8201a")
    glass = {(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch in "lhmo"}
    return finish(s, exclude=glass)


# ============================================================================ produce cut


@reg("pumpkin_slice")
def pumpkin_slice():
    """Ring-segment wedge running diagonally: ribbed rind outside, pulp and seeds inside."""
    s = Sprite()
    rind = rp("#c8661a", 4, 0.09)
    flesh = rp("#f0a040", 5, 0.07)
    ox, oy, R, r = 0.0, 0.0, 14.6, 8.4
    a0, a1 = math.radians(10), math.radians(80)
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - ox, y + 0.5 - oy
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            if not (r <= d <= R and a0 <= ang <= a1):
                continue
            k = (d - r) / (R - r)
            if k > 0.80:
                ridge = int(math.degrees(ang) / 9) % 2
                s.set(x, y, rind[1 + ridge] if k < 0.93 else rind[0 + ridge])
            elif k > 0.7:
                s.set(x, y, flesh[1])
            elif k < 0.16:
                s.set(x, y, C("#e07a18"))               # stringy pulp
            else:
                s.set(x, y, flesh[3] if (ang > 0.9) else flesh[2])
    for x, y in ((9, 3), (6, 6), (3, 9)):              # seeds on the pulp edge
        stamp(s, ["w", "c"] if x != 6 else ["wc"], {"w": "#fbf2d0", "c": "#d8c890"}, x, y)
    puts(s, [(5, 10), (10, 5)], flesh[4])
    return finish(s)


# ============================================================================ meat


def bacon_strips(m, M, f, F, crisp=None) -> Sprite:
    """Two wavy strips; raw and cooked share this exact silhouette."""
    s = Sprite()
    a = strip(s, 2.0, 10.4, 10.6, 1.8, [M, f, m], wave=0.7, freq=1.25)
    b = strip(s, 5.4, 13.8, 13.8, 5.4, [M, f, m], wave=0.7, freq=1.25, phase=1.9)
    if crisp:
        for i, (x, y) in enumerate(sorted(set(a + b))):
            if i % 7 == 0 and s.get(x, y) == C(m):
                s.set(x, y, C(crisp))
    return finish(s)


@reg("bacon")
def bacon():
    return bacon_strips("#ea948c", "#cc6a66", "#fae8dc", "#ecc8b8")


@reg("cooked_bacon")
def cooked_bacon():
    return bacon_strips("#b04a20", "#7a2e12", "#eeaa5a", "#c87a3a", crisp="#5e2210")


@reg("minced_beef")
def minced_beef():
    s = Sprite()
    r = rp("#c83a3a", 5, 0.09)
    pts = dome(s, 7.8, 11.4, 6.4, 6.6, r, mask=lambda x, y: y <= 12, flat=0.8)
    for x in range(3, 13):
        s.set(x, 13, r[1])
    # wormy mince texture
    for x, y in pts:
        k = (x * 2 + y * 3 + (x * y) % 3) % 5
        if k == 0:
            s.set(x, y, C("#ee8a86"))
        elif k == 2:
            s.set(x, y, r[1] if y > 7 else r[2])
    puts(s, [(6, 6), (9, 8), (5, 10)], "#f8c8c0")   # fat flecks
    return finish(s)


@reg("beef_patty")
def beef_patty():
    s = Sprite()
    side = rp("#5a2c16", 4, 0.08)
    for y in range(16):
        for x in range(16):
            if ell(7.8, 10.4, 6.8, 3.7)(x, y):
                s.set(x, y, side[1] if x > 9 else side[2])
    top = rp("#8a4c2a", 5, 0.08)
    pts = set(dome(s, 7.8, 8.4, 6.8, 3.7, top, flat=0.35))
    # crusty texture then three parallel grill bars
    for x, y in pts:
        if (x * 3 + y * 5) % 7 == 0:
            s.set(x, y, top[1])
    for k in (-3, 0, 3):
        for i in range(-6, 7):
            x, y = 7 + k + i, 8 + (-i) // 2
            if (x, y) in pts:
                s.set(x, y, C("#2a1208"))
    puts(s, [(4, 7), (5, 7), (9, 6)], top[4])
    return finish(s)


def chunks(pal_list) -> Sprite:
    s = Sprite()
    a = ["..hhh.", ".hhhll", "lllllb", "llllbd", ".lbbd."]
    b = [".hhh", "hhll", "lllb", "lbbd", ".dd."]
    for (x, y), rows, pal in zip(((1, 4), (8, 3), (5, 9)), (a, b, a), pal_list):
        stamp(s, rows, pal, x, y)
    return s


@reg("chicken_cuts")
def chicken_cuts():
    raw = {"h": "#fdeee4", "l": "#f6d4c4", "b": "#eab8a6", "d": "#c88e80"}
    s = chunks([raw, raw, raw])
    puts(s, [(4, 6), (10, 5), (7, 10)], "#fff6f0")   # fibres
    puts(s, [(3, 7), (8, 11)], "#f0c6b8")
    return finish(s)


@reg("cooked_chicken_cuts")
def cooked_chicken_cuts():
    ck = {"h": "#f6cc8a", "l": "#e2a862", "b": "#c8884a", "d": "#985a28"}
    s = chunks([ck, ck, ck])
    puts(s, [(4, 6), (10, 5), (7, 10)], "#fbe0ac")
    puts(s, [(5, 7), (9, 11), (11, 6)], "#a8642c")   # sear
    return finish(s)


# ============================================================================ fish


def fillet(flesh, skin, line_col, crust=None) -> Sprite:
    """Flat fillet lying diagonally: rounded head end, tapering tail, skin along the lower edge.

    Shaded as a slab (flat top, lit rim top-left, shadowed rim bottom-right), not a cylinder.
    """
    s = Sprite()
    r = rp(flesh, 5, 0.07)
    pts = capsule(s, 4.8, 10.9, 12.2, 4.6, 3.9, r, r_end=1.9)
    ps = set(pts)
    for (x, y), (t, side) in pts.items():
        v = 2
        if side > 0.55:
            v = 3
        if (x - 1, y) not in ps or (x, y - 1) not in ps:
            v = 4
        if side < -0.7:
            s.set(x, y, C(skin[0] if (x + y) % 3 else skin[1]))
            continue
        if crust and side > 0.2:
            s.set(x, y, C(crust) if side < 0.7 else lit(crust, 0.08))
            continue
        s.set(x, y, r[v])
    # muscle lines: gentle arcs across the fillet
    for (x, y), (t, side) in pts.items():
        if -0.7 <= side <= 0.75 and 0.12 < t < 0.9:
            k = t * 5.0 + abs(side) * 0.6
            if abs(k - round(k)) < 0.13:
                s.set(x, y, C(line_col))
    return finish(s)


@reg("cod_fillet")
def cod_fillet():
    return fillet("#ecdcca", ["#9a9aa2", "#d4d8dc"], "#fbf4ea")


@reg("cooked_cod_fillet")
def cooked_cod_fillet():
    return fillet("#f0d4a0", ["#a87a40", "#c89a60"], "#fbe8c4", crust="#e0b46a")


@reg("salmon_fillet")
def salmon_fillet():
    return fillet("#f07858", ["#8a8a96", "#c8ccd4"], "#fcc8b0")


@reg("cooked_salmon_fillet")
def cooked_salmon_fillet():
    return fillet("#e8905a", ["#8a4a22", "#a8642e"], "#f8c8a0", crust="#c87838")


@reg("fried_egg")
def fried_egg():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",  # 0
        "................",
        "................",
        "......ewwwe.....",  # 3
        "....ewhwwwwwe...",  # 4
        "...ewwwwwwwwwe..",  # 5
        "..ewwwwYYywwwwe.",  # 6
        ".ewwwwYYyyywwws.",  # 7
        ".ewwwwYyyyowwws.",  # 8
        "..ewwwwyoowwwse.",  # 9
        "..eewwwwwwwwsse.",  # 10
        "...eewwwwwssee..",  # 11
        ".....eeeseee....",  # 12
    ]
    stamp(s, rows, {**EGG, "e": "#d8a868", "Y": "#fcd860", "y": "#f6b21c", "o": "#d8840e"})
    put(s, 7, 6, "#fff6c8")
    puts(s, [(2, 6), (13, 7), (4, 11)], "#b8803e")    # crispy browned lace
    return finish(s)
