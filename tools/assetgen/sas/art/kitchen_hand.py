"""Handhelds & snacks: sandwiches, burgers, tacos, wraps, skewers, sushi, fries, sides."""
from __future__ import annotations

from .core import Sprite
from .kitchen_kit import (C, GLASS, capsule, dome, finish, jar_base, JAR_FILL, JAR_GLASS, put, puts, reg,
                          rp, shade_pts, stamp)
from .kitchen_parts import EGG, basil, lettuce_frill

# ============================================================================ sandwiches
SANDWICH = [
    #0123456789abcdef
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "...cccccccccc...",  # 3   top slice seen from above: crust ring + soft face
    "..cTTTTtTTTTTc..",  # 4
    "..cTTTTTTTTtTd..",  # 5
    "..cTtTTTTTTTTd..",  # 6
    "..cccccccccccd..",  # 7   crust edge of the top slice
    "..bbbbbbbbbbbb..",  # 8   white crumb (cut side of the top slice)
    "..111111111111..",  # 9   fillings
    "..222222222222..",  # 10
    "..333333333333..",  # 11
    "..bbbbbbbbbbbb..",  # 12  bottom slice crumb
    "..CCCCCCCCCCCd..",  # 13  bottom crust
]
BREAD_PAL = {"c": "#c88a40", "C": "#a86a2a", "d": "#7e4a1a", "T": "#f2d49a", "t": "#e0b470", "b": "#f6e6c4"}
TOAST_PAL = {"c": "#b8762e", "C": "#9a5a1e", "d": "#6e3c12", "T": "#e8b868", "t": "#c88a40", "b": "#f2d8a4"}


def sandwich(fills: dict[str, list], toasted: bool = False, extra=None) -> Sprite:
    """``fills`` maps '1'/'2'/'3' to a list of colours cycled along the row."""
    s = Sprite()
    pal = dict(TOAST_PAL if toasted else BREAD_PAL)
    for k in "123":
        pal[k] = fills[k][0]
    stamp(s, SANDWICH, pal)
    for k, row in zip("123", (9, 10, 11)):
        cols = fills[k]
        for i, x in enumerate(range(2, 14)):
            s.set(x, row, C(cols[i % len(cols)]))
    # light top-left of the top face
    puts(s, [(3, 4), (4, 4), (5, 4), (3, 5)], "#fbecc4" if not toasted else "#f6d48c")
    put(s, 13, 8, pal["t"])
    if extra:
        extra(s)
    return finish(s)


def _frill(s: Sprite, y: int) -> None:
    lettuce_frill(s, 1, 14, y)


@reg("blt_sandwich")
def blt_sandwich():
    def extra(s):
        _frill(s, 9)
        for x in range(2, 14):
            s.set(x, 10, C("#d8322a" if x % 4 else "#f07050"))
        for x in range(2, 14):
            s.set(x, 11, C(("#b04a22", "#e8a868", "#8a3218")[x % 3]))
    return sandwich({"1": ["#7cc04a"], "2": ["#d8322a"], "3": ["#b04a22"]}, toasted=True, extra=extra)


@reg("chicken_sandwich")
def chicken_sandwich():
    def extra(s):
        _frill(s, 9)
        for x in range(2, 14):
            s.set(x, 10, C(("#e8b878", "#d0904a", "#f2cc90")[x % 3]))
            s.set(x, 11, C(("#c8884a", "#a86a34")[x % 2]))
        puts(s, [(1, 10), (14, 11)], "#c8884a")
    return sandwich({"1": ["#7cc04a"], "2": ["#e8b878"], "3": ["#c8884a"]}, extra=extra)


@reg("egg_sandwich")
def egg_sandwich():
    def extra(s):
        _frill(s, 9)
        for x in range(2, 14):
            s.set(x, 10, C(EGG["w"]))
            s.set(x, 11, C(EGG["s"]))
        puts(s, [(5, 10), (6, 10), (7, 10), (8, 10)], EGG["Y"])
        puts(s, [(5, 11), (6, 11), (7, 11), (8, 11)], EGG["y"])
        puts(s, [(1, 10), (14, 10)], EGG["w"])
    return sandwich({"1": ["#7cc04a"], "2": ["#f8f6f0"], "3": ["#f8f6f0"]}, extra=extra)


@reg("pbj_sandwich")
def pbj_sandwich():
    def extra(s):
        for x in range(2, 14):
            s.set(x, 9, C(("#c8884a", "#b8783a")[x % 2]))
            s.set(x, 10, C("#a06030" if x % 3 == 0 else "#b8783a"))
            s.set(x, 11, C(("#9a1a3a", "#7a1430", "#b8304e")[x % 3]))
        # jam oozing out and dripping
        puts(s, [(1, 11), (4, 12), (4, 13), (9, 12), (10, 12), (10, 13), (10, 14), (14, 11)], "#8a1a3a")
        puts(s, [(4, 12), (9, 12)], "#c03656")
        put(s, 1, 9, "#c8884a")
    return sandwich({"1": ["#b8783a"], "2": ["#b8783a"], "3": ["#8a1a3a"]}, extra=extra)


# ============================================================================ burgers
BUN = rp("#d8903a", 5, 0.09)


def burger(layers) -> Sprite:
    s = Sprite()
    dome(s, 7.6, 8.3, 6.1, 6.0, BUN, mask=lambda x, y: y <= 7)
    puts(s, [(2, 7), (13, 7), (13, 6)], BUN[1])
    for x in range(3, 13):
        s.set(x, 7, BUN[1] if x > 9 else BUN[2])
    # sesame seeds
    puts(s, [(5, 4), (8, 3), (10, 5), (6, 6), (11, 3), (3, 6)], "#fbf2d6")
    puts(s, [(5, 5), (8, 4), (10, 6)], "#d8b884")
    y = 8
    for draw in layers:
        y = draw(s, y)
    # bottom bun
    for x in range(2, 14):
        s.set(x, y, BUN[3] if x < 6 else BUN[2])
    for x in range(3, 13):
        s.set(x, y + 1, BUN[1] if x > 9 else BUN[2])
    return finish(s)


def l_lettuce(s, y):
    lettuce_frill(s, 1, 14, y)
    return y + 1


def l_tomato(s, y):
    for x in range(2, 14):
        s.set(x, y + 1, C("#d8322a" if x % 4 else "#f27a5a"))
    return y + 2


def l_patty(color="#6a3a1e", flecks=None):
    r = rp(color, 4, 0.1)

    def d(s, y):
        for x in range(1, 15):
            s.set(x, y, r[3] if x % 3 == 0 else r[2])
            if 1 < x:
                s.set(x, y + 1, r[1] if x % 2 else r[0])
        if flecks:
            for i, x in enumerate(range(2, 14, 3)):
                s.set(x, y + (i % 2), C(flecks[i % len(flecks)]))
        return y + 2
    return d


def l_cheese(s, y):
    ch = rp("#f2b82a", 4, 0.09)
    for x in range(1, 15):
        s.set(x, y, ch[2])
    puts(s, [(2, y), (3, y)], ch[3])
    for x in (3, 8, 12):
        s.set(x, y + 1, ch[2])
    s.set(8, y + 2, ch[1])
    return y + 1


@reg("hamburger")
def hamburger():
    return burger([l_lettuce, l_tomato, l_patty()])


@reg("cheeseburger")
def cheeseburger():
    def patty_with_cheese(s, y):
        y2 = l_patty()(s, y + 1)
        l_cheese(s, y)
        return y2
    return burger([l_lettuce, patty_with_cheese])


@reg("veggie_burger")
def veggie_burger():
    return burger([l_lettuce, l_tomato, l_patty("#c8a060", flecks=["#5a9a32", "#e8702a", "#5a9a32"])])


# ============================================================================ taco / wraps / skewer


@reg("taco")
def taco():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",  # 0
        "................",
        "................",
        "....g.Y..g......",  # 3
        "...gGYgGtgYg....",  # 4  lettuce / cheese / tomato on top
        "..gmmGmYmmGmg...",  # 5  beef
        ".SmmmmmmmmmmmS..",  # 6  shell rim
        ".sShhhhhhhhhsS..",  # 7
        ".sShhhhhhhhhss..",  # 8
        "..sShhhhhhhss...",  # 9
        "...ssShhhhss....",  # 10
        ".....ssssss.....",  # 11
    ]
    pal = {"g": "#7cc04a", "G": "#4f9a2e", "Y": "#f6d04a", "t": "#d8322a", "m": "#7a4220",
           "S": "#f6d488", "h": "#ecc070", "s": "#c8943e"}
    stamp(s, rows, pal)
    puts(s, [(5, 8), (9, 9), (11, 7), (7, 10)], "#b07a30")     # toasted spots
    puts(s, [(3, 5), (8, 5)], "#a05a2a")
    puts(s, [(9, 4), (4, 6)], "#d8322a")
    return finish(s)


@reg("burrito")
def burrito():
    s = Sprite()
    tort = rp("#ecd08a", 5, 0.09)
    pts = capsule(s, 4.6, 11.4, 11.0, 5.0, 3.6, tort)
    # foil wrap on the lower-left half
    foil = rp("#c8ccd4", 5, 0.12)
    for (x, y), (t, side) in pts.items():
        if t < 0.42:
            v = 0.5 + side * 0.45
            s.set(x, y, foil[max(0, min(4, int(v * 5)))])
            if (x * 3 + y) % 5 == 0:
                s.set(x, y, foil[4])
    # open top end showing the filling
    end = [
        ".fff.",
        "fwrbf",
        "frwbf",
        ".fff.",
    ]
    stamp(s, end, {"f": tort[3], "w": "#f6f2e8", "r": "#c8281e", "b": "#5a2a1a"}, 10, 2)
    puts(s, [(8, 7), (6, 9)], tort[1])    # toasted spots
    return finish(s)


@reg("chicken_wrap")
def chicken_wrap():
    s = Sprite()
    tort = rp("#ecd08a", 5, 0.09)
    # two halves: back one leaning, front one standing, both showing the cut face
    capsule(s, 3.5, 11.5, 7.5, 7.5, 2.9, tort)
    capsule(s, 8.0, 12.0, 11.5, 9.0, 2.9, tort)
    face = [
        ".fff.",
        "fgcgf",
        "fcglf",
        "fgcgf",
        ".fff.",
    ]
    pal = {"f": tort[3], "g": "#5aa836", "l": "#8ad05a", "c": "#d8984e"}
    stamp(s, face, pal, 6, 3)
    stamp(s, face, pal, 10, 6)
    puts(s, [(4, 10), (9, 11)], tort[1])
    return finish(s)


@reg("kebab")
def kebab():
    s = Sprite()
    stick = rp("#c09060", 3, 0.12)
    for i in range(1, 15):
        x, y = i, 15 - i
        if 1 < i < 15:
            s.set(x, y, stick[1] if i % 2 else stick[2])
    chunk = [".hl.", "hlbd", "lbbd", ".dd."]
    meat = {"h": "#c88050", "l": "#9a5530", "b": "#7a3c1e", "d": "#4e2210"}
    pep = {"h": "#fc8a6a", "l": "#e8402a", "b": "#c8281e", "d": "#7e140e"}
    oni = {"h": "#ffffff", "l": "#f6eedc", "b": "#e2d0b8", "d": "#a8889a"}
    for (x, y), pal in zip(((1, 10), (4, 7), (7, 4), (10, 1)), (meat, pep, oni, meat)):
        stamp(s, chunk, pal, x, y)
    puts(s, [(2, 12), (11, 3), (3, 11)], "#2e1408")      # char marks
    return finish(s)


# ============================================================================ sushi
NORI = {"n": "#22301f", "N": "#3a4a32"}


def maki(fill_hi, fill) -> Sprite:
    s = Sprite()
    roll = [
        ".rrrr.",
        "rRffRr",
        "rRFfRr",
        "nrrrrn",
        "nNnnnn",
        "nNnnnn",
        ".nnnn.",
    ]
    pal = {"r": "#f6f4ee", "R": "#e0ddd2", "f": fill, "F": fill_hi, **NORI}
    stamp(s, roll, pal, 5, 1)    # back roll
    stamp(s, roll, pal, 1, 6)
    stamp(s, roll, pal, 9, 7)
    return finish(s)


@reg("salmon_maki")
def salmon_maki():
    return maki("#fbb098", "#f07858")


@reg("cucumber_maki")
def cucumber_maki():
    return maki("#a8e07a", "#4fa83a")


@reg("onigiri")
def onigiri():
    s = Sprite()
    rows = [
        #0123456789abcdef
        "................",
        "................",
        ".......hh.......",  # 2
        "......hwwr......",  # 3
        ".....hwwwwr.....",  # 4
        ".....wwwwwrs....",  # 5
        "....hwwwwwwrs...",  # 6
        "....wwwwwwwrs...",  # 7
        "...hwwwwwwwwrs..",  # 8
        "...wwwnnnnwwrs..",  # 9
        "..hwwnNnnnnwrss.",  # 10
        "..wwwnNnnnnwwrs.",  # 11
        "..wwwnNnnnnwrss.",  # 12
        "...sswnnnnwsss..",  # 13
    ]
    stamp(s, rows, {"h": "#ffffff", "w": "#f6f4ee", "r": "#e2ded2", "s": "#c8c4b6", **NORI})
    puts(s, [(7, 5), (9, 7), (6, 8), (10, 10), (4, 11)], "#e2ded2")   # rice grains
    puts(s, [(7, 4), (8, 4)], "#c8304a")                              # umeboshi peek
    return finish(s)


# ============================================================================ breads


def toast_slice(s: Sprite, x: int, y: int, top_pal: dict, rows=None) -> None:
    rows = rows or [
        "..cccc..",
        ".cTTTTcc",
        "cTTTTTTc",
        "cTTTTTdc",
        ".cddddc.",
        "..CCCC..",
    ]
    stamp(s, rows, top_pal, x, y)


@reg("garlic_bread")
def garlic_bread():
    s = Sprite()
    pal = {"c": "#b86e24", "C": "#8a4a14", "T": "#f2d474", "d": "#e0b048"}
    toast_slice(s, 1, 7, pal)
    toast_slice(s, 7, 3, pal)
    for x, y in ((3, 9), (5, 10), (4, 11), (9, 5), (11, 6), (10, 7), (6, 9)):
        put(s, x, y, "#3f8a2e")
    puts(s, [(4, 9), (10, 5), (12, 7)], "#fffbe0")    # garlic / butter shine
    return finish(s)


@reg("bruschetta")
def bruschetta():
    s = Sprite()
    pal = {"c": "#b06a24", "C": "#7e4214", "T": "#e6b462", "d": "#c88a3e"}
    rows = [
        "....cccccc....",
        "..ccTTTTTTcc..",
        ".cTTTTTTTTTTc.",
        "cTTTTTTTTTTTdc",
        ".cTTTTTTTTddc.",
        "..ccddddddcc..",
        "....CCCCCC....",
    ]
    stamp(s, rows, pal, 1, 7)
    tom = {"h": "#fca08a", "l": "#ea4a3a", "b": "#c82a20", "d": "#8a1a12"}
    for tx, ty in ((3, 7), (5, 6), (8, 6), (10, 7), (6, 8), (9, 8), (4, 9), (11, 9)):
        stamp(s, ["hl", "bd"], tom, tx, ty)
    basil(s, 6, 3)
    basil(s, 10, 4, flip=True)
    return finish(s)


# ============================================================================ fries & rings


@reg("fries")
def fries():
    s = Sprite()
    fry = {"h": "#fdf0a8", "l": "#f8d860", "b": "#e8b83a", "d": "#c08a24"}
    heights = [3, 1, 2, 0, 2, 1, 3, 2]
    for i, h in enumerate(heights):
        x = 4 + i
        for y in range(1 + h, 8):
            s.set(x, y, C(fry["l"] if i % 2 == 0 else fry["b"]))
        s.set(x, 1 + h, C(fry["h"] if i % 2 == 0 else fry["l"]))
        if i % 2:
            s.set(x, 6, C(fry["d"]))
    carton = [
        #0123456789abcdef
        "..hrrrrrrrrrrd..",  # 7
        "..hrrrrrrrrrrd..",  # 8
        "...hrrwwwwrrd...",  # 9
        "...hrwyyyywrd...",  # 10
        "...hrrwwwwrrd...",  # 11
        "....hrrrrrrd....",  # 12
        "....hrrrrrdd....",  # 13
    ]
    stamp(s, carton, {"h": "#f05a46", "r": "#d0281e", "d": "#8a1610", "w": "#f6f0e0", "y": "#f2c63a"}, 0, 7)
    puts(s, [(2, 7), (13, 7)], "#e8402e")
    return finish(s)


@reg("onion_rings")
def onion_rings():
    """Three battered rings standing on edge, fanned diagonally; each hole shows through."""
    import math
    s = Sprite()
    ring = rp("#e0a040", 5, 0.1)
    holes = []
    for cx, cy in ((11.2, 4.6), (7.9, 7.9), (4.6, 11.2)):
        for y in range(16):
            for x in range(16):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                d = math.hypot(dx, dy)
                if 1.75 < d <= 3.75:
                    # torus-ish light: outer edge lit top-left, inner edge lit bottom-right
                    n = (dx * -0.7 + dy * -0.7) / max(d, 0.01)
                    v = 0.5 + (n * 0.4 if d > 2.75 else -n * 0.3)
                    s.set(x, y, ring[max(0, min(4, int(v * 5)))])
                elif d <= 1.75:
                    s.set(x, y, (0, 0, 0, 0))
                    holes.append((x, y))
        # batter crumbs
        for bx, by in ((-2, -3), (2, -2), (-3, 1), (3, 2)):
            px, py = int(cx + bx), int(cy + by)
            if s.opaque(px, py):
                s.set(px, py, ring[4] if by < 0 else ring[3])
    return finish(s)


# ============================================================================ snacks (piles)


def pile(items):
    """Draw a small heap from a list of (x, y, rows, pal) sprites, back to front."""
    s = Sprite()
    for x, y, rows, pal in items:
        stamp(s, rows, pal, x, y)
    return finish(s)


PEANUT = {"h": "#f2d29a", "l": "#dcac68", "b": "#b8783a", "d": "#8a5426"}
RAISIN = {"h": "#8a5a52", "l": "#6a3a34", "b": "#4a2424", "d": "#2e1416"}
CHIP = {"h": "#8a5a3a", "l": "#5a2e1a", "b": "#3e1e10", "d": "#26100a"}
NUT = ["hl", "lb", "bd"]
NUT2 = ["hlb", "lbd"]
RAI = ["lb", "bd"]
CHP = [".l.", "lbd"]


@reg("trail_mix")
def trail_mix():
    items = [
        (6, 3, NUT2, PEANUT), (4, 5, RAI, RAISIN), (9, 4, CHP, CHIP), (7, 6, NUT, PEANUT),
        (2, 8, NUT2, PEANUT), (10, 6, NUT2, PEANUT), (5, 8, CHP, CHIP), (8, 9, RAI, RAISIN),
        (11, 9, NUT, PEANUT), (3, 10, RAI, RAISIN), (6, 10, NUT2, PEANUT), (9, 11, CHP, CHIP),
        (12, 8, RAI, RAISIN), (4, 12, CHP, CHIP),
    ]
    return pile(items)


@reg("roasted_peanuts")
def roasted_peanuts():
    items = [
        (6, 3, NUT2, PEANUT), (4, 5, NUT, PEANUT), (9, 4, NUT2, PEANUT), (7, 6, NUT, PEANUT),
        (2, 8, NUT2, PEANUT), (10, 6, NUT2, PEANUT), (5, 8, NUT2, PEANUT), (8, 9, NUT, PEANUT),
        (11, 9, NUT, PEANUT), (3, 10, NUT2, PEANUT), (6, 11, NUT2, PEANUT), (9, 11, NUT2, PEANUT),
        (12, 8, NUT, PEANUT),
    ]
    s = pile(items)
    puts(s, [(7, 4), (5, 6), (9, 10)], "#fbe6b8")   # salt glints
    return s


@reg("pickles")
def pickles():
    s = Sprite()
    jar_base(s, lid="#8a8a92")
    brine = rp("#c8d080", 5, 0.06)
    shade_pts(s, JAR_FILL, brine)
    pick = {"h": "#9ac04a", "l": "#6a8a2a", "b": "#4e6a1e", "d": "#34481a"}
    for x, y in ((4, 8), (7, 9), (10, 8)):
        stamp(s, ["hl", "lb", "lb", "bd", "bd"], pick, x, y)
    puts(s, [(5, 10), (8, 11), (11, 10)], pick["h"])
    puts(s, [(6, 8), (9, 12), (12, 11)], "#3a6a2a")    # dill
    puts(s, [(3, 8), (3, 9)], GLASS["h"])
    return finish(s, exclude=set(JAR_GLASS))


@reg("baked_sweet_potato")
def baked_sweet_potato():
    s = Sprite()
    skin = rp("#8e3a24", 5, 0.1)
    pts = capsule(s, 4.0, 11.4, 12.4, 4.6, 3.5, skin)
    flesh = rp("#f2862a", 5, 0.08)
    # the split: a wide orange slit along the upper side of the tuber
    for (x, y), (t_, side) in pts.items():
        if side > -0.15 and 0.12 < t_ < 0.92:
            s.set(x, y, flesh[3] if side > 0.45 else flesh[2])
        if -0.35 < side <= -0.15 and 0.12 < t_ < 0.92:
            s.set(x, y, flesh[1])
    puts(s, [(5, 9), (7, 8), (9, 6), (10, 5)], flesh[4])
    stamp(s, ["bB", "BB"], {"b": "#fcf4b0", "B": "#f2d870"}, 7, 6)     # butter pat
    puts(s, [(2, 11), (13, 5)], skin[3])
    return finish(s)


@reg("grilled_corn")
def grilled_corn():
    s = Sprite()
    corn = rp("#e8b030", 5, 0.1)
    pts = capsule(s, 5.0, 11.0, 12.0, 4.0, 2.9, corn)
    for (x, y), (t, side) in pts.items():
        if (x + y) % 2 == 0 and side > -0.6:
            s.set(x, y, corn[min(4, int((0.5 + side * 0.45) * 5) + 1)])
        if 0.15 < t < 0.95 and int(t * 10) % 3 == 0:
            s.set(x, y, C("#6a3a14") if (x + y) % 2 else C("#8a5a1a"))   # char stripes
    # butter melting on top
    puts(s, [(8, 5), (9, 5), (7, 6)], "#fcf0a8")
    # husk at the bottom end
    husk = {"g": "#b8c070", "G": "#dce4a0", "d": "#7a8a3a"}
    stamp(s, ["G...", "gG..", "dgG.", ".dgg", "..dd"], husk, 1, 9)
    stamp(s, ["..G", ".Gg", "Ggd"], husk, 5, 11)
    return finish(s)
