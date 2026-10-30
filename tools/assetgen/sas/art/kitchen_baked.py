"""Baked goods, ice creams, pie/pizza slices and whole-feast item icons."""
from __future__ import annotations

import math

from .core import Sprite
from .kitchen_kit import C, dome, ell, finish, put, puts, reg, rp, stamp
from .kitchen_ingredients import WAFFLE, cone
from .kitchen_parts import basil

# ============================================================================ baked


@reg("blueberry_muffin")
def blueberry_muffin():
    s = Sprite()
    # pleated paper cup
    cup = [
        #0123456789abcdef
        "...hpPpPpPpPd...",  # 9
        "...hpPpPpPpPd...",  # 10
        "....pPpPpPpd....",  # 11
        "....pPpPpPpd....",  # 12
        ".....dddddd.....",  # 13
    ]
    stamp(s, cup, {"h": "#fbf2e6", "p": "#f2e2cc", "P": "#d8c4a8", "d": "#b8a284"}, 0, 9)
    top = rp("#d8a050", 5, 0.09)
    dome(s, 7.8, 8.8, 6.6, 6.2, top, mask=lambda x, y: y <= 8)
    for x in range(2, 14):
        s.set(x, 8, top[1] if x > 4 else top[2])     # overhang lip
    blue = {"h": "#8a94e0", "b": "#3a3a98", "d": "#22225a"}
    for bx, by in ((4, 4), (8, 3), (10, 6), (6, 6), (11, 4)):
        stamp(s, ["hb", "bd"] if bx % 2 == 0 else ["b", "d"], blue, bx, by)
    puts(s, [(5, 3), (6, 4), (9, 5)], top[4])          # sugar crust glints
    return finish(s)


@reg("banana_bread")
def banana_bread():
    s = Sprite()
    slice_rows = [
        ".cccc.",
        "cCbbbC",
        "cbbBbc",
        "cbbbbc",
        "cbBbbc",
        "cbbbbc",
        "cbbbBc",
        "cccccc",
    ]
    pal = {"c": "#8a521e", "C": "#a8682a", "b": "#dcac5e", "B": "#8a5a2a"}
    stamp(s, slice_rows, pal, 2, 6)                    # back slice, leaning
    stamp(s, slice_rows, {**pal, "b": "#e8c070"}, 7, 4)
    puts(s, [(9, 6), (11, 9), (8, 10)], "#6a3e1a")             # banana flecks / walnut
    puts(s, [(8, 6), (9, 5)], "#f4d896")
    puts(s, [(3, 8)], "#f2d088")
    return finish(s)


@reg("cornbread")
def cornbread():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",
        "................",
        "................",
        "................",
        ".....hTTTTTTc...",  # 4  top face (golden crust)
        "....hTTTTTTTcd..",  # 5
        "...hTTTTTTTcdd..",  # 6
        "..hTTTTTTTcddd..",  # 7
        "..FFFFFFFFFRRd..",  # 8  front & side (crumb)
        "..FFfFFFFfFRRd..",  # 9
        "..FFFFFfFFFRRd..",  # 10
        "..FfFFFFFFFRd...",  # 11
        "..ddddddddddd...",  # 12
    ]
    stamp(s, rows, {"h": "#eab452", "T": "#d29630", "c": "#b07a22", "d": "#8a5a18", "F": "#f4d05a",
                    "f": "#fbe286", "R": "#dcae3e"})
    puts(s, [(6, 6), (9, 5), (4, 7), (10, 7)], "#b88024")      # baked crust speckle
    stamp(s, ["bB", "BB"], {"b": "#fff6c0", "B": "#f6e08a"}, 6, 4)    # butter pat
    put(s, 8, 6, "#f6e08a")
    return finish(s)


@reg("oatmeal_cookie")
def oatmeal_cookie():
    s = Sprite()
    c = rp("#c8904a", 5, 0.09)
    pts = dome(s, 7.8, 8.4, 6.6, 6.0, c, flat=0.45)
    for x, y in pts:
        if (x * 5 + y * 3) % 7 == 0:
            s.set(x, y, c[4])          # oat flakes
        elif (x * 3 + y * 7) % 11 == 0:
            s.set(x, y, c[1])
    rais = {"l": "#7a4a42", "b": "#4a2a2a", "d": "#2e1416"}
    for rx_, ry_ in ((5, 5), (9, 6), (6, 9), (10, 10), (4, 11)):
        stamp(s, ["lb", "bd"] if rx_ % 2 else ["bd"], rais, rx_, ry_)
    return finish(s)


# ============================================================================ ice cream


def ice_cream(base, spread, bits=None, drips=((5, 8), (9, 9))) -> Sprite:
    s = Sprite()
    cone(s, 8)
    for x in range(3, 13):
        s.set(x, 8, WAFFLE[4] if x < 7 else WAFFLE[3])
    r = rp(base, 5, spread)
    dome(s, 7.8, 5.2, 5.4, 4.6, r, mask=lambda x, y: y <= 8)
    # scoop's frilly lower edge resting on the rim + drips
    for x in range(2, 14):
        if (x % 3) != 1:
            s.set(x, 8, r[1] if x > 8 else r[2])
    for x, y in drips:
        s.set(x, y, r[2])
        s.set(x, y + 1, r[1])
    if bits:
        for (x, y), col in bits:
            s.set(x, y, C(col))
    put(s, 5, 3, r[4])
    put(s, 6, 2, r[4])
    return finish(s)


@reg("strawberry_ice_cream")
def strawberry_ice_cream():
    return ice_cream("#f4a0b0", 0.08, bits=[((8, 4), "#e0303a"), ((5, 6), "#d02a3a"), ((10, 6), "#e0303a"),
                                            ((9, 3), "#fcd8e0")])


@reg("chocolate_ice_cream")
def chocolate_ice_cream():
    return ice_cream("#7a4224", 0.09, bits=[((8, 4), "#3a1a0a"), ((5, 6), "#3a1a0a"), ((10, 6), "#3a1a0a"),
                                            ((6, 4), "#a8704a")])


@reg("mint_ice_cream")
def mint_ice_cream():
    return ice_cream("#a8e8c8", 0.07, bits=[((8, 4), "#3a1a0a"), ((5, 6), "#3a1a0a"), ((10, 6), "#3a1a0a"),
                                            ((7, 7), "#3a1a0a"), ((11, 4), "#3a1a0a")])


# ============================================================================ pies

PIE_FILL = {"apple": ("#d8b050", "#f6e6a8"), "cherry": ("#a01a2a", "#e8485a"), "berry": ("#4a2a7a", "#8a6ac8")}
CRUST = rp("#e8b868", 5, 0.09)


def pie_slice(kind) -> Sprite:
    """Wedge in 3/4 view: lattice top, crimped crust at the back, filling on the cut face."""
    fill, fill_hi = PIE_FILL[kind]
    fr = rp(fill, 4, 0.1)
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",  # 0
        "................",
        "................",
        "..........RRR...",  # 3   crimped back crust
        "........RRLLRR..",  # 4
        "......RRLffLLR..",  # 5
        ".....LfLLfLffR..",  # 6   lattice over filling
        "...LLffLffLLfR..",  # 7
        "..LfLLfLLffLLR..",  # 8
        ".LLffLffLfLfRR..",  # 9
        ".XXXXXXXXXXXXRd.",  # 10  cut face: filling
        ".xXXxXXXxXXXxRd.",  # 11
        ".BBBBBBBBBBBBdd.",  # 12  bottom crust
        ".dddddddddddd...",  # 13
    ]
    pal = {"R": CRUST[3], "L": CRUST[4], "f": fr[1], "X": fr[2], "x": fill_hi, "B": CRUST[2], "d": CRUST[1]}
    stamp(s, rows, pal)
    puts(s, [(12, 5), (11, 4)], CRUST[2])
    if kind == "apple":
        puts(s, [(3, 11), (8, 10), (11, 11)], "#fcf0c0")
    else:
        puts(s, [(3, 10), (9, 11)], fill_hi)
    return finish(s)


@reg("apple_pie_slice")
def apple_pie_slice():
    return pie_slice("apple")


@reg("cherry_pie_slice")
def cherry_pie_slice():
    return pie_slice("cherry")


@reg("berry_pie_slice")
def berry_pie_slice():
    return pie_slice("berry")


def whole_pie(kind) -> Sprite:
    fill, fill_hi = PIE_FILL[kind]
    fr = rp(fill, 4, 0.1)
    s = Sprite()
    cx, cy = 7.8, 8.0
    outer, inner = ell(cx, cy, 7.2, 4.6), ell(cx, cy - 0.2, 5.6, 3.2)
    for y in range(16):
        for x in range(16):
            if ell(cx, cy + 2.2, 7.0, 4.2)(x, y) and not outer(x, y):
                s.set(x, y, CRUST[1] if x > 9 else CRUST[2])          # pie side / dish
    for y in range(16):
        for x in range(16):
            if outer(x, y) and not inner(x, y):
                ang = math.atan2(y + 0.5 - cy, (x + 0.5 - cx) * 0.64)
                lobe = int((ang + math.pi) / (2 * math.pi) * 18) % 2
                lightside = (x + 0.5 - cx) * -0.6 + (y + 0.5 - cy) * -1.0 > -1.5
                s.set(x, y, CRUST[4 if lightside else 3] if lobe else CRUST[2 if lightside else 1])
            elif inner(x, y):
                s.set(x, y, fr[1] if (x + y) % 2 else fr[2])
                # lattice strips: two diagonal families
                if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                    s.set(x, y, CRUST[4] if y < cy else CRUST[3])
    puts(s, [(5, 7), (9, 8)], fill_hi)
    return finish(s)


@reg("apple_pie")
def apple_pie():
    return whole_pie("apple")


@reg("cherry_pie")
def cherry_pie():
    return whole_pie("cherry")


@reg("berry_pie")
def berry_pie():
    return whole_pie("berry")


# ============================================================================ pizza

DOUGH = rp("#e8b060", 5, 0.09)
SAUCE = "#c8281e"
MOZZ = rp("#f2d060", 4, 0.08)


@reg("pizza_slice")
def pizza_slice():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",  # 0
        "..CCCCCCCCCCC...",  # 1   crust
        "..ccccccccccccC.",  # 2
        "..srmmmMmmmmmsc.",  # 3   sauce rim + melted cheese
        "...smmmmmmMmmsc.",  # 4
        "...smMmmmmmmsc..",  # 5
        "....smmmmMmms...",  # 6
        "....smmmmmmsc...",  # 7
        ".....smMmmmsc...",  # 8
        ".....smmmmsc....",  # 9
        "......smmms.....",  # 10
        "......smmsc.....",  # 11
        ".......sms......",  # 12
        ".......ss.......",  # 13
    ]
    stamp(s, rows, {"C": DOUGH[4], "c": DOUGH[2], "s": SAUCE, "r": "#e8483a", "m": MOZZ[2], "M": MOZZ[3]})
    puts(s, [(3, 1), (4, 1)], "#fbe0a0")
    puts(s, [(5, 3), (9, 6), (8, 9)], "#f8e8a8")
    puts(s, [(6, 6), (10, 4)], "#e8a830")               # browned cheese
    basil(s, 4, 3)
    basil(s, 8, 6, flip=True)
    return finish(s)


@reg("pizza")
def pizza():
    s = Sprite()
    cx, cy = 7.8, 8.2
    for y in range(16):
        for x in range(16):
            if ell(cx, cy + 1.4, 7.2, 4.4)(x, y):
                s.set(x, y, DOUGH[1] if x > 9 else DOUGH[2])         # crust side
    dome(s, cx, cy, 7.2, 4.8, DOUGH, flat=0.4)
    sauce = rp(SAUCE, 4, 0.08)
    inner = ell(cx, cy, 5.8, 3.6)
    for y in range(16):
        for x in range(16):
            if inner(x, y):
                s.set(x, y, sauce[2] if (x + y) % 3 else sauce[1])
    # mozzarella pools and basil leaves
    for mx, my in ((3, 7), (7, 5), (10, 7), (6, 9), (10, 10), (4, 10)):
        stamp(s, [".M.", "MMm", ".m."], {"M": MOZZ[3], "m": MOZZ[2]}, mx, my)
    basil(s, 6, 6)
    basil(s, 9, 8, flip=True)
    put(s, 4, 9, "#2c7028")
    return finish(s)


# ============================================================================ cakes


CAKE_ROWS = [
    #0123456789abcdef
    "................",  # 1
    "................",  # 2
    ".....hhTTTT.....",  # 3   frosted top (flat ellipse)
    "...hhTTTTTTTT...",  # 4
    "..hTTTTTTTTTTt..",  # 5
    ".hTTTTTTTTTTTtt.",  # 6
    ".TTTTTTTTTTTTtt.",  # 7
    "..tTTTTTTTTTtt..",  # 8
    ".FfFffFfffFfffD.",  # 9   frosting lip
    ".sFsssFsssssFsd.",  # 10  sponge with drips
    ".sFssssssssssdd.",  # 11
    ".LLLLLLLLLLLLLd.",  # 12  filling layer
    ".ssssssssssssdd.",  # 13
    "..ssssssssssdd..",  # 14
    "....dddddddd....",  # 15
    "................",
]


def cake(frost, body, filling, top_deco) -> Sprite:
    """Frosted round cake: flat elliptical top, straight sides, drips and a filling layer."""
    s = Sprite()
    f = rp(frost, 5, 0.07)
    b = rp(body, 4, 0.09)
    fl = rp(filling, 3, 0.06)
    stamp(s, CAKE_ROWS, {"h": f[4], "T": f[3], "t": f[2], "F": f[2], "f": f[1], "D": f[0],
                         "s": b[2], "d": b[1], "L": fl[1]})
    puts(s, [(1, 9), (1, 10), (1, 12), (2, 13)], b[3])       # rim light on the left of the sponge
    put(s, 1, 11, fl[2])
    top_deco(s, f)
    return finish(s)


@reg("chocolate_cake")
def chocolate_cake():
    def deco(s, f):
        # white drizzle: two loose diagonal lines across the glossy top
        puts(s, [(3, 5), (4, 4), (5, 4), (6, 3), (7, 3)], "#f8f0e8")
        puts(s, [(6, 7), (7, 6), (8, 6), (9, 5), (10, 5), (11, 4)], "#f8f0e8")
        puts(s, [(10, 8), (10, 9), (4, 8)], "#f8f0e8")           # drizzle running over the edge
        puts(s, [(3, 3), (4, 3)], "#9a6a4a")                     # gloss
        stamp(s, [".g", "rR", "RR"], {"r": "#e83048", "R": "#a81428", "g": "#3f6a1a"}, 8, 0)   # cherry
    return cake("#4e2614", "#7a4426", "#f4e8dc", deco)


@reg("carrot_cake")
def carrot_cake():
    def deco(s, f):
        for x, y in ((3, 5), (7, 3), (11, 5), (8, 6)):
            stamp(s, ["G.", "oo"], {"o": "#ec7a2a", "G": "#4fa02e"}, x, y)
        puts(s, [(5, 4), (10, 3), (6, 6)], "#b88a5a")            # walnut crumbs
    return cake("#f6efe2", "#c8803a", "#f6efe2", deco)
