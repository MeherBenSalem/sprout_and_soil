"""Bowl dishes: soups, stews, curries, salads, snacks (and the bowl ingredients).

Every dish uses the shared wooden bowl from :mod:`kitchen_kit`; dishes differ by their
*contents*: flat liquid vs. heap, chunk shapes, garnish and silhouette above the rim.
Bowl opening rows: 5 (x5-10), 6-8 (x3-12), 9 (x4-11). Front lip is row 10.
"""
from __future__ import annotations

from .core import Sprite
from .kitchen_kit import (BASIL, BOWL_SURFACE, BOWL_SURFACE_SET, C, LETTUCE, bowl_dish, dome, in_bowl,
                          put, puts, reg, rng_for, rp, stamp)


# --------------------------------------------------------------------------- content helpers


def liquid(s: Sprite, base, spread: float = 0.07) -> list:
    """Calm liquid surface: reflective band at the back-left, shadowed front-right."""
    r = rp(base, 5, spread)
    for x, y in BOWL_SURFACE:
        v = 2
        if y == 5 or (y == 6 and x <= 7):
            v = 3
        if y == 9 or (x >= 11 and y >= 7):
            v = 1
        s.set(x, y, r[v])
    put(s, 6, 5, r[4])
    put(s, 5, 6, r[4])
    return r


def heap(s: Sprite, top: int, base, rx: float = 5.6, spread: float = 0.09, cy: float = 9.5,
         bias: float = 0.0, cx: float = 8.0, flat: float = 1.0):
    """A mound rising out of the bowl to row ``top``; clipped to the opening below row 5."""
    r = rp(base, 5, spread)
    pts = dome(s, cx, cy, rx, cy - top, r, mask=in_bowl, bias=bias, flat=flat)
    return r, pts


def bumps(s: Sprite, pts, col, every: int = 2, phase: int = 0) -> None:
    """1 px bumps on the top silhouette of a heap (fluffy / leafy edges)."""
    tops: dict[int, int] = {}
    for x, y in pts:
        if x not in tops or y < tops[x]:
            tops[x] = y
    xs = sorted(tops)
    for i, x in enumerate(xs[1:-1], 1):
        if (i + phase) % every == 0 and tops[x] > 1:
            s.set(x, tops[x] - 1, C(col))


def grains(s: Sprite, pts, light, dark, step: int = 9) -> None:
    """Rice-like grain texture: a light fleck with a small cool shadow beneath."""
    ps = set(pts)
    for x, y in sorted(pts):
        k = (x * 7 + y * 3 + (y // 2) * 5) % step
        if k == 0:
            s.set(x, y, C(light))
            if (x, y + 1) in ps:
                s.set(x, y + 1, C(dark))


def basil_leaf(s: Sprite, x: int, y: int) -> None:
    stamp(s, [".ll", "lbd", "dd."], {"l": BASIL[3], "b": BASIL[2], "d": BASIL[1]}, x, y)


# palettes for repeated chunk types
CARROT = {"h": "#fbb870", "l": "#f69a48", "b": "#e8782a", "d": "#b8561a"}
POTATO = {"h": "#fbf0c4", "l": "#f2e0a0", "b": "#e0c47a", "d": "#b8984c"}
BEEF = {"h": "#b8784e", "l": "#9a5a34", "b": "#7e4224", "d": "#5a2a16"}
CHICKEN = {"h": "#fbe8cc", "l": "#f2d0a4", "b": "#dcac74", "d": "#b07a46"}
WHITE_FISH = {"h": "#fffbf4", "l": "#f4e8d8", "b": "#e0cdb6", "d": "#b49a84"}
TOFU = {"h": "#fffdf6", "l": "#f4efe0", "b": "#ddd6c0", "d": "#b8b09a"}
GREEN = {"h": "#9ad860", "l": "#6cba3e", "b": "#4a9a2e", "d": "#2e6a1e"}
RICE = rp("#efebe0", 5, 0.05)


# --------------------------------------------------------------------------- ingredients served in a bowl


@reg("tomato_sauce")
def tomato_sauce():
    def c(s):
        r, pts = heap(s, 4, "#b8241a", spread=0.085, flat=0.7)
        puts(s, [(5, 5), (6, 5), (4, 6)], r[4])          # wet gloss
        put(s, 5, 6, "#fcb8a8")
        puts(s, [(9, 7), (10, 7), (11, 8)], r[1])       # swirl groove
        puts(s, [(7, 8), (8, 8)], r[1])
        basil_leaf(s, 8, 3)
        put(s, 11, 4, BASIL[1])
    return bowl_dish(c)


@reg("cooked_rice")
def cooked_rice():
    def c(s):
        r, pts = heap(s, 3, "#e9e5da", spread=0.055)
        bumps(s, pts, r[3], every=2)
        grains(s, pts, "#fffefa", "#cdc8ba")
        for x, y in pts:
            if (x * 5 + y * 3) % 11 == 4 and y > 5:
                s.set(x, y, C("#d4cfc2"))
    return bowl_dish(c)


# --------------------------------------------------------------------------- soups


@reg("tomato_soup")
def tomato_soup():
    def c(s):
        r = liquid(s, "#d4381e", 0.065)
        cream, mid, low = C("#fbf0e2"), C("#efd6bc"), C("#d8b498")
        # open cream spiral in the middle of the bowl
        puts(s, [(6, 6), (7, 6), (8, 6)], cream)
        puts(s, [(5, 7), (9, 7)], mid)
        puts(s, [(7, 7)], cream)
        puts(s, [(6, 8), (7, 8), (8, 8)], low)
        put(s, 9, 8, mid)
        put(s, 10, 6, "#3f8a2e")
        put(s, 11, 6, "#62b453")
    return bowl_dish(c)


@reg("vegetable_soup")
def vegetable_soup():
    def c(s):
        liquid(s, "#c8902a", 0.07)
        stamp(s, ["hl", "bd"], CARROT, 3, 6)
        stamp(s, ["hl", "lb", "bd"], POTATO, 6, 4)       # potato poking up over the rim
        stamp(s, ["hl", "bd"], CARROT, 9, 5)
        stamp(s, ["lb"], POTATO, 10, 8)
        stamp(s, ["lb"], GREEN, 5, 8)                    # green bean
        puts(s, [(9, 7), (12, 7)], GREEN["l"])          # peas
        put(s, 8, 9, GREEN["b"])
    return bowl_dish(c)


@reg("pumpkin_soup")
def pumpkin_soup():
    def c(s):
        r = liquid(s, "#ea8a1c", 0.06)
        # cream drizzle ring
        puts(s, [(5, 6), (6, 6), (7, 6), (8, 6), (9, 6)], "#fce8c6")
        puts(s, [(4, 7), (10, 7)], "#f2d4a8")
        puts(s, [(5, 8), (6, 8), (8, 8), (9, 8)], "#f2d4a8")
        # toasted pumpkin seeds in the middle
        seed = {"l": "#eef0b8", "d": "#8a9a50"}
        stamp(s, ["ld"], seed, 6, 7)
        stamp(s, ["ld"], seed, 8, 7)
        stamp(s, ["l", "d"], seed, 7, 5)
        put(s, 11, 6, "#3f8a2e")
    return bowl_dish(c)


@reg("chicken_noodle_soup")
def chicken_noodle_soup():
    def c(s):
        liquid(s, "#e2b850", 0.07)
        n1, n2 = C("#fdf4d0"), C("#e2c886")
        puts(s, [(3, 7), (4, 6), (5, 6), (6, 7), (7, 7), (8, 6), (9, 6), (10, 7), (11, 7)], n1)
        puts(s, [(4, 9), (5, 8), (6, 8), (7, 9), (8, 9), (9, 8), (10, 8)], n2)
        stamp(s, ["hl", "lb"], CHICKEN, 6, 4)
        stamp(s, ["hl", "bd"], CHICKEN, 10, 5)
        stamp(s, ["hl"], CARROT, 3, 8)
        stamp(s, ["h", "b"], CARROT, 12, 7)
        puts(s, [(9, 4), (5, 5), (8, 8)], "#4f9a32")
        puts(s, [(9, 10), (9, 11)], n1)                  # noodle over the lip
    return bowl_dish(c)


@reg("beef_stew")
def beef_stew():
    def c(s):
        r, pts = heap(s, 5, "#5e2a10", spread=0.08, flat=0.7)
        beef = {"h": "#c8865a", "l": "#a8643c", "b": "#86482a", "d": "#5a2a16"}
        stamp(s, [".hl", "hlb", "lbd"], beef, 3, 4)
        stamp(s, ["hlb", "lbd"], beef, 8, 3)
        stamp(s, ["hl", "bd"], beef, 9, 7)
        stamp(s, ["hl", "bd"], CARROT, 6, 5)
        stamp(s, ["hl"], CARROT, 11, 5)
        stamp(s, ["h", "b"], CARROT, 4, 7)
        stamp(s, ["hl", "bd"], POTATO, 6, 8)
        puts(s, [(8, 6), (11, 7)], r[4])          # glossy gravy
        put(s, 12, 6, "#5aa832")
        put(s, 7, 4, "#5aa832")
    return bowl_dish(c)


@reg("fish_stew")
def fish_stew():
    def c(s):
        r = liquid(s, "#c84a2a", 0.07)
        stamp(s, [".hl.", "hllb", "lbbd"], WHITE_FISH, 3, 4)
        stamp(s, ["hlb", "lbd"], WHITE_FISH, 8, 4)
        stamp(s, ["lb"], WHITE_FISH, 9, 8)
        stamp(s, ["pP", "p."], {"p": "#ee7a5a", "P": "#fcb89c"}, 6, 7)   # shrimp curl
        put(s, 7, 8, "#ee7a5a")
        puts(s, [(11, 6), (5, 8)], "#4f9a32")
    return bowl_dish(c)


@reg("miso_soup")
def miso_soup():
    def c(s):
        r = liquid(s, "#c89a52", 0.06)
        puts(s, [(6, 7), (7, 7), (8, 8), (9, 8), (4, 8)], "#dcbc80")   # cloudy miso
        tofu = {"h": "#ffffff", "l": "#f8f4e8", "b": "#e2dcc8", "d": "#b8b09a"}
        stamp(s, ["hl", "bd"], tofu, 4, 5)
        stamp(s, ["hl", "bd"], tofu, 9, 5)
        stamp(s, ["hl", "bd"], tofu, 6, 7)
        puts(s, [(10, 8), (11, 8), (3, 7), (8, 6)], "#62c440")          # green onion
        stamp(s, ["kk", ".k"], {"k": "#1e3a22"}, 10, 7)                  # wakame
        put(s, 7, 9, "#1e3a22")
    return bowl_dish(c)


@reg("ramen")
def ramen():
    def c(s):
        liquid(s, "#c87c36", 0.07)
        n1, n2 = C("#f8de90"), C("#d8b45c")
        for x in range(3, 13):
            s.set(x, 8, n1 if x % 3 else n2)
        for x in range(4, 12):
            s.set(x, 9, n2 if x % 2 else n1)
        stamp(s, ["kn", "kn", "kn", "kn"], {"k": "#1c2e22", "n": "#2e4632"}, 10, 2)   # nori
        stamp(s, [".ww.", "wyyw", ".wwd"], {"w": "#faf4e6", "y": "#f29a1c", "d": "#d8ccb4"}, 3, 4)
        put(s, 4, 5, "#fbc860")
        stamp(s, [".pp", "pPp", "pp."], {"p": "#b8705a", "P": "#f2c8ac"}, 7, 5)       # chashu
        puts(s, [(6, 7), (11, 7), (8, 4)], "#5ab83e")
    return bowl_dish(c)


@reg("chili_con_carne")
def chili_con_carne():
    def c(s):
        r, pts = heap(s, 5, "#8a2a12", spread=0.085, flat=0.75)
        for x, y in pts:
            if (x * 5 + y * 3) % 7 == 0:
                s.set(x, y, r[1])
        bean = {"l": "#b04a3e", "b": "#6e1e1c", "d": "#4a1012"}
        for bx, by in ((3, 6), (9, 7), (11, 5), (6, 8)):
            stamp(s, ["lb", "bd"], bean, bx, by)
        stamp(s, [".hw", "hww", ".ws"], {"h": "#ffffff", "w": "#f6f2e8", "s": "#d8d0c0"}, 6, 3)  # sour cream
        puts(s, [(5, 6), (9, 5), (10, 4), (4, 5)], "#f4cc4a")                                  # cheese
        puts(s, [(5, 7), (10, 5)], "#d8a030")
        put(s, 8, 3, "#4f9a32")
    return bowl_dish(c)


@reg("vegetable_curry")
def vegetable_curry():
    def c(s):
        r = liquid(s, "#e0a020", 0.07)
        pts = dome(s, 5.6, 9.0, 3.7, 5.6, RICE, mask=in_bowl)
        grains(s, pts, "#fffefa", "#d6d0c0", step=6)
        stamp(s, ["hl", "bd"], CARROT, 9, 5)
        stamp(s, ["lb"], CARROT, 10, 8)
        puts(s, [(11, 6), (12, 7), (9, 8)], GREEN["l"])
        put(s, 11, 9, r[1])
        put(s, 5, 3, "#4f9a32")
    return bowl_dish(c)


@reg("chicken_curry")
def chicken_curry():
    def c(s):
        r, pts = heap(s, 6, "#d8741a", spread=0.07, flat=0.6)
        rpts = dome(s, 10.2, 8.0, 3.4, 5.0, RICE, mask=lambda x, y: in_bowl(x, y) and y <= 7)
        grains(s, rpts, "#fffefa", "#d6d0c0", step=6)
        stamp(s, [".hl", "hlb", "lbd"], CHICKEN, 3, 5)
        stamp(s, ["hl", "bd"], CHICKEN, 7, 7)
        puts(s, [(6, 6), (5, 8)], "#f8e6c8")             # cream
        puts(s, [(9, 3), (8, 4)], "#3f8a2e")             # coriander
        put(s, 10, 9, r[1])
    return bowl_dish(c)


@reg("fried_rice")
def fried_rice():
    rnd = rng_for("fried_rice")

    def c(s):
        r, pts = heap(s, 3, "#dcb86e", spread=0.07)
        bumps(s, pts, r[3], every=2)
        grains(s, pts, "#f8e6b4", r[1])
        egg = {"l": "#fcec80", "b": "#f2cc30"}
        for ex, ey in ((4, 5), (9, 3), (7, 7)):
            stamp(s, ["lb"], egg, ex, ey)
        for gx, gy in ((6, 4), (10, 6), (5, 8)):
            put(s, gx, gy, GREEN["l"])
        puts(s, [(8, 5), (11, 8)], CARROT["b"])
        put(s, 3, 7, GREEN["b"])
    return bowl_dish(c)


@reg("mushroom_risotto")
def mushroom_risotto():
    def c(s):
        r, pts = heap(s, 5, "#e6d8b4", spread=0.06, flat=0.6)
        grains(s, pts, r[4], r[1], step=5)
        mush = {"c": "#6a4428", "C": "#946a48", "s": "#ecdcbc", "d": "#45291a"}
        stamp(s, [".CC.", "Cccd", ".ss."], mush, 2, 4)
        stamp(s, [".CC.", "Cccd", ".ss."], mush, 8, 3)
        stamp(s, [".CC", "ccd", ".s."], mush, 6, 6)
        stamp(s, ["Cc", "s."], mush, 10, 7)
        puts(s, [(5, 8), (12, 7), (9, 6)], "#4f9a32")
        put(s, 4, 8, "#fbf6e2")                                    # parmesan
    return bowl_dish(c)


@reg("oatmeal")
def oatmeal():
    def c(s):
        r, pts = heap(s, 5, "#e6d4a8", spread=0.06, flat=0.6)
        for x, y in pts:
            k = (x * 3 + y * 7) % 5
            if k == 0:
                s.set(x, y, r[1])
            elif k == 2:
                s.set(x, y, r[4])
        blue = {"h": "#aab4f4", "b": "#4446a0", "d": "#2a2a6a"}
        for bx, by in ((6, 4), (8, 5), (4, 6), (10, 6)):
            stamp(s, ["hb", "bd"], blue, bx, by)
        put(s, 7, 7, blue["b"])
        puts(s, [(3, 8), (4, 8), (11, 8), (12, 8), (7, 8)], "#e8a83a")   # honey drizzle
    return bowl_dish(c)


@reg("corn_chowder")
def corn_chowder():
    def c(s):
        liquid(s, "#efe2bc", 0.05)
        corn = {"l": "#fde060", "b": "#f4b81c", "d": "#b87810"}
        for kx, ky in ((4, 6), (8, 5), (10, 7), (6, 8), (3, 8)):
            stamp(s, ["lb", "bd"] if kx != 3 else ["l", "b"], corn, kx, ky)
        puts(s, [(7, 6), (11, 6), (9, 9)], "#4f9a32")            # chives
        puts(s, [(9, 8), (5, 5)], "#a8401e")                     # bacon bits
    return bowl_dish(c)


@reg("mac_and_cheese")
def mac_and_cheese():
    def c(s):
        r, pts = heap(s, 4, "#f2b22a", spread=0.08, flat=0.8)
        ps = set(pts)
        for x, y in sorted(pts):
            k = (x + 2 * y) % 4
            if k == 0 and (x + 1, y) in ps:
                s.set(x, y, r[4])
                if (x + 1, y + 1) in ps:
                    s.set(x + 1, y + 1, r[0])
            elif k == 2 and y % 2 == 0:
                s.set(x, y, r[3])
        puts(s, [(6, 4), (9, 5), (4, 6)], "#c8781e")
    return bowl_dish(c)


@reg("baked_beans")
def baked_beans():
    def c(s):
        r, pts = heap(s, 5, "#b2401a", spread=0.08, flat=0.7)
        bean = {"h": "#fbb070", "l": "#e88a48", "b": "#cc6a30", "d": "#9a4220"}
        for bx, by in ((3, 6), (5, 5), (7, 4), (9, 5), (11, 6), (4, 8), (6, 7), (8, 6), (10, 8), (8, 8)):
            stamp(s, ["hl", "bd"], bean, bx, by)
        puts(s, [(5, 9), (10, 7), (9, 4)], r[1])
    return bowl_dish(c)


@reg("french_onion_soup")
def french_onion_soup():
    def c(s):
        liquid(s, "#8a5626", 0.07)
        cheese = rp("#f2cc60", 5, 0.08)
        dome(s, 7.6, 6.6, 4.4, 2.8, cheese, mask=lambda x, y: in_bowl(x, y) or y == 4)
        puts(s, [(5, 5), (8, 4), (10, 6), (7, 7)], "#c8862e")   # browned spots
        puts(s, [(6, 6), (9, 5)], "#a8641e")
        puts(s, [(3, 8), (12, 7), (11, 9)], "#d8b070")          # onions in the broth

    def drip(s):
        puts(s, [(4, 10), (4, 11)], "#f2cc60")
        put(s, 5, 10, "#e2b048")
    return bowl_dish(c, post=drip)


@reg("potato_leek_soup")
def potato_leek_soup():
    def c(s):
        liquid(s, "#ece4c2", 0.05)
        ring = {"g": "#5e9a34", "G": "#9cd068"}
        stamp(s, [".G.", "G.g", ".g."], ring, 4, 5)
        stamp(s, [".G.", "G.g", ".g."], ring, 8, 6)
        stamp(s, ["Gg"], ring, 10, 9)
        puts(s, [(7, 9), (11, 6)], "#4f8a2e")
        puts(s, [(6, 8), (3, 7), (10, 5)], "#6a6058")             # cracked pepper
    return bowl_dish(c)


@reg("broccoli_cheese_soup")
def broccoli_cheese_soup():
    def c(s):
        r = liquid(s, "#e8c056", 0.07)
        floret = {"h": "#7ab84a", "l": "#4f9a32", "b": "#3a7a26", "d": "#265a1a", "s": "#b0d880"}
        stamp(s, [".hl.", "hlbb", "lbbd", ".s.."], floret, 3, 4)
        stamp(s, [".hl", "lbd", ".s."], floret, 8, 3)
        stamp(s, ["lb", "bd"], floret, 9, 7)
        puts(s, [(7, 7), (6, 8)], r[4])
    return bowl_dish(c)


@reg("gazpacho")
def gazpacho():
    def c(s):
        liquid(s, "#e44a2a", 0.06)
        cuc = {"l": "#9ad06a", "d": "#4a8a2a", "w": "#e8f0c8"}
        for cx, cy in ((4, 6), (8, 5), (9, 8), (6, 8)):
            stamp(s, ["wl", "ld"], cuc, cx, cy)
        puts(s, [(7, 7), (11, 7)], "#f8f0e0")             # onion dice
        stamp(s, [".dd.", "dwwd", "dwwd", ".dd."], {"d": "#3a7a2a", "w": "#cce8a0"}, 10, 2)  # cucumber wheel
        put(s, 11, 3, "#eaf6cc")
    return bowl_dish(c)


@reg("vegetable_stir_fry")
def vegetable_stir_fry():
    def c(s):
        r, pts = heap(s, 4, "#7a4a1e", spread=0.09, flat=0.8)
        red = {"h": "#f88a70", "b": "#d02a1e", "d": "#8a1810"}
        yel = {"h": "#fcec90", "b": "#f2c63a", "d": "#b8861a"}
        grn = {"h": "#8ac850", "b": "#3f7a2c", "d": "#285a1c"}
        stamp(s, ["h..", "bb.", ".bd"], red, 3, 5)
        stamp(s, ["..h", ".bb", "bd."], yel, 6, 3)
        stamp(s, [".h.", "hbb", "bbd"], grn, 9, 3)
        stamp(s, ["hb", ".d"], red, 9, 6)
        stamp(s, ["hbbd"], grn, 5, 8)
        stamp(s, ["hb"], yel, 11, 7)
        puts(s, [(7, 6), (4, 4)], "#f6eedc")             # sesame
        put(s, 8, 5, r[4])
    return bowl_dish(c)


@reg("dumplings")
def dumplings():
    def c(s):
        liquid(s, "#c8a070", 0.06)
        dough = {"h": "#fffaf0", "l": "#f6eedc", "b": "#e2d4b8", "d": "#bca88a", "p": "#d2c2a0"}
        gold = {"h": "#fbe0a0", "l": "#f0c070", "b": "#d89a48", "d": "#a86a2a", "p": "#c88a40"}
        back = [".hlp.", "hlpbb", "lbbbd", ".ddd."]
        stamp(s, back, dough, 2, 3)
        stamp(s, back, gold, 8, 2)
        stamp(s, [".hlp.", "hllbb", "lbbbd", ".bdd."], dough, 5, 6)
        puts(s, [(4, 3), (10, 2)], "#ffffff")
        put(s, 11, 7, "#3f8a2e")
        put(s, 12, 6, "#5ab83e")
    return bowl_dish(c)


@reg("custard")
def custard():
    def c(s):
        liquid(s, "#f6dc80", 0.06)
        car = rp("#b8662a", 5, 0.09)
        dome(s, 7.6, 7.2, 3.8, 2.0, car, flat=0.3, mask=lambda x, y: (x, y) in BOWL_SURFACE_SET)
        puts(s, [(5, 6), (6, 6)], "#f2b86a")
        put(s, 6, 5, "#fff0c0")
        puts(s, [(11, 8), (11, 9)], car[2])
    return bowl_dish(c)


@reg("popcorn")
def popcorn():
    pop = {"h": "#ffffff", "l": "#fbf6e6", "b": "#efe2bc", "d": "#d8bc7a", "y": "#f2cc50"}

    def c(s):
        k3 = [".hl.", "hllb", "lbby", ".bd."]
        k2 = ["hl.", "lby", ".d."]
        for kx, ky, k in ((2, 5, k3), (9, 5, k3), (5, 4, k3), (4, 2, k2), (7, 1, k3), (10, 2, k2),
                          (7, 3, k3), (3, 3, k2), (11, 4, k2), (6, 6, k2)):
            stamp(s, k, pop, kx, ky)
        puts(s, [(8, 8), (5, 9), (10, 9), (11, 8), (3, 8), (9, 9), (4, 9), (7, 9), (6, 9)], pop["b"])
        puts(s, [(6, 8), (8, 9), (10, 8), (4, 8)], pop["y"])

    def spill(s):
        stamp(s, ["hl", "by"], pop, 13, 11)
    return bowl_dish(c, post=spill)


@reg("garden_salad")
def garden_salad():
    def c(s):
        r, pts = heap(s, 3, "#5aa236", spread=0.1)
        L = [C(x) for x in LETTUCE]
        bumps(s, pts, L[3], every=2)
        for x, y in pts:
            k = (x + 2 * y) % 5
            if k == 0:
                s.set(x, y, L[1])
            elif k == 2 and y < 8:
                s.set(x, y, L[4] if y < 5 else L[3])
        tom = {"h": "#fca08a", "l": "#ea4a3a", "b": "#c82a20", "s": "#f8d870"}
        stamp(s, ["hl", "bs"], tom, 4, 4)
        stamp(s, ["lb", "sb"], tom, 9, 5)
        cuc = {"d": "#2f6a22", "w": "#d4eca8", "s": "#a8cc78"}
        stamp(s, ["dd", "ws"], cuc, 6, 6)
        stamp(s, ["dd", "ws"], cuc, 10, 2)
        rad = {"r": "#d8325a", "w": "#fbeef0"}
        stamp(s, ["rw", "wr"], rad, 3, 7)
        stamp(s, ["rw"], rad, 8, 8)
    return bowl_dish(c)


@reg("fruit_salad")
def fruit_salad():
    def c(s):
        heap(s, 4, "#f0c050", spread=0.09)
        orange = {"h": "#fcc070", "l": "#f8a030", "b": "#e8801a", "d": "#b85a10"}
        straw = {"l": "#ec4a4a", "b": "#d02a30", "s": "#fce0a0"}
        yel = {"h": "#fff2a0", "l": "#f8e060", "b": "#e8c83a"}
        blue = {"h": "#8a9ae0", "b": "#3a4aa0", "d": "#232a6a"}
        kiwi = {"g": "#8ac040", "s": "#1a2010"}
        stamp(s, ["hl", "bd"], orange, 3, 5)
        stamp(s, [".l.", "lsb", ".b."], straw, 6, 2)
        stamp(s, ["hl", "lb"], yel, 9, 4)
        stamp(s, ["gg", "gs"], kiwi, 5, 5)
        stamp(s, ["hl", "lb"], yel, 4, 7)
        stamp(s, ["hb", "bd"], blue, 8, 6)
        stamp(s, ["hb"], blue, 11, 6)
        stamp(s, ["hl", "bd"], orange, 10, 7)
        stamp(s, ["ls", "bb"], straw, 6, 8)
        stamp(s, ["hb"], blue, 3, 4)
        stamp(s, [".l", "lb"], {"l": "#7cd06a", "b": "#3a9a3a"}, 9, 1)   # mint leaf
    return bowl_dish(c)


@reg("coleslaw")
def coleslaw():
    def c(s):
        r, pts = heap(s, 4, "#e2e6c6", spread=0.06)
        ps = set(pts)
        for x, y in pts:
            k = (x - y) % 3
            if k == 0:
                s.set(x, y, r[4] if y < 7 else r[3])
            elif k == 2 and (x + y) % 2:
                s.set(x, y, r[1])
        for x, y in ((4, 5), (5, 4), (8, 4), (9, 3), (10, 6), (11, 5), (6, 7), (7, 6)):
            if (x, y) in ps:
                s.set(x, y, C("#f08a2a"))
        puts(s, [(5, 5), (9, 4)], "#c8661a")
        puts(s, [(7, 4), (11, 7)], "#9a7ab0")
    return bowl_dish(c)


@reg("greek_salad")
def greek_salad():
    def c(s):
        heap(s, 4, "#6aa83e", spread=0.09)
        tom = {"h": "#fca08a", "l": "#ea4a3a", "b": "#c82a20", "d": "#8a1a12"}
        feta = {"h": "#ffffff", "l": "#f8f6ea", "b": "#e2decc", "d": "#bcb6a0"}
        cuc = {"d": "#2e6a22", "l": "#8ac060", "w": "#d4eca8"}
        olive = {"o": "#2a2a1a", "h": "#6a6a50", "k": "#141408"}
        stamp(s, ["hl", "bd"], tom, 3, 5)
        stamp(s, ["hl", "bd"], tom, 9, 3)
        stamp(s, ["hl", "lb"], feta, 6, 3)
        stamp(s, ["hl", "bd"], feta, 8, 6)
        stamp(s, ["hl", "bd"], feta, 3, 3)
        stamp(s, ["dw", "dl"], cuc, 5, 6)
        stamp(s, ["wd", "ld"], cuc, 11, 5)
        stamp(s, ["ho", "ok"], olive, 7, 2)
        stamp(s, ["ho", "ok"], olive, 10, 7)
        puts(s, [(5, 8), (4, 8)], "#b05a90")          # red onion
    return bowl_dish(c)


@reg("guacamole")
def guacamole():
    def c(s):
        r, pts = heap(s, 5, "#86b236", spread=0.09, flat=0.8)
        for x, y in pts:
            k = (x * 3 + y * 5) % 7
            if k == 0:
                s.set(x, y, r[0])
            elif k == 3:
                s.set(x, y, r[4])
        puts(s, [(4, 6), (8, 5), (10, 7), (6, 8)], "#d8322a")
        puts(s, [(5, 6), (9, 5)], "#f07060")
        puts(s, [(7, 7), (11, 6)], "#f4f0dc")
        chip = {"h": "#fbe08a", "l": "#f0c860", "b": "#d8a840", "d": "#b07a28"}
        stamp(s, ["...h", "..hl", ".hlb", "hlbd"], chip, 8, 1)
    return bowl_dish(c)
