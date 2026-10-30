"""Drinks: bottled juices & smoothies (vanilla glass-bottle silhouette) and hot mug drinks."""
from __future__ import annotations

from .core import Sprite
from .kitchen_kit import (BOTTLE_GLASS, BOTTLE_LIQUID, GLASS, MUG_MASK, STEAM, C, bottle_base, dome, finish,
                          mug_base, mug_drink, put, puts, reg, rp, stamp)

LIQ = set(BOTTLE_LIQUID)


def bottle_drink(base, spread=0.09, fill_top=5, cork=True, extra=None, top=None, pulp=None) -> Sprite:
    """Glass bottle filled with ``base``; ``fill_top`` leaves empty glass above (clear drinks)."""
    s = Sprite()
    bottle_base(s, cork=cork)
    r = rp(base, 5, spread)
    puts(s, BOTTLE_LIQUID, r[2])
    dome(s, 8.0, 10.4, 4.6, 4.6, r, mask=lambda x, y: (x, y) in LIQ, bias=-0.06)
    for x, y in BOTTLE_LIQUID:
        if y < fill_top:
            s.set(x, y, C(GLASS["l"]) if y < fill_top - 1 or x != 8 else C(GLASS["m"]))
        elif y in (5, 6) and fill_top <= 5:
            s.set(x, y, r[3])
    # meniscus / top colour band
    if top:
        for x, y in BOTTLE_LIQUID:
            if y == fill_top or (y == fill_top + 1 and x in (7, 8, 9)):
                s.set(x, y, C(top))
    if pulp:
        for x, y in ((6, 10), (9, 9), (7, 12), (10, 11), (8, 11)):
            if (x, y) in LIQ:
                s.set(x, y, C(pulp))
    # specular glints on the bulb
    put(s, 6, 9, r[4])
    put(s, 6, 10, "#ffffff")
    if extra:
        extra(s, r)
    return finish(s, exclude=set(BOTTLE_GLASS) | LIQ)


def straw(s: Sprite, a="#e8483a", b="#fbf6f0") -> None:
    for i, (x, y) in enumerate(((8, 4), (8, 3), (9, 2), (9, 1), (10, 1))):
        s.set(x, y, C(a if i % 2 else b))


@reg("orange_juice")
def orange_juice():
    return bottle_drink("#f89a1c", 0.09, pulp="#fcc860", top="#fcb848")


@reg("apple_juice")
def apple_juice():
    def extra(s, r):
        puts(s, [(9, 11), (7, 9), (10, 12)], "#fff4c8")       # bubbles
        puts(s, [(5, 10), (5, 11)], "#fcecb0")               # clear-glass shine through the juice
    return bottle_drink("#e8b040", 0.07, fill_top=8, extra=extra)


@reg("grape_juice")
def grape_juice():
    def extra(s, r):
        put(s, 7, 9, r[3])
    return bottle_drink("#6a1a5a", 0.10, extra=extra)


@reg("lemonade")
def lemonade():
    def extra(s, r):
        wheel = [".yy.", "ypwy", "ywpy", ".yy."]
        stamp(s, wheel, {"y": "#f2d020", "p": "#fcf4b0", "w": "#ffffff"}, 7, 9)
        puts(s, [(6, 12), (10, 10)], "#ffffff")              # ice / bubbles
    return bottle_drink("#f6ec9c", 0.05, fill_top=6, extra=extra)


@reg("pineapple_juice")
def pineapple_juice():
    def extra(s, r):
        puts(s, [(7, 7), (8, 7), (9, 7), (8, 6), (8, 5)], "#fffbe0")    # froth
        puts(s, [(6, 8), (10, 8)], "#fcf2b0")
    return bottle_drink("#f8cc2a", 0.08, pulp="#fce880")


@reg("tomato_juice")
def tomato_juice():
    def extra(s, r):
        # celery stick standing in the neck
        cel = {"g": "#9ac860", "G": "#c8e890", "d": "#5e8a2e", "l": "#4fa02e"}
        puts(s, [(8, 4), (8, 3), (9, 2)], cel["g"])
        puts(s, [(9, 3)], cel["d"])
        puts(s, [(9, 1), (10, 1), (10, 2), (11, 1)], cel["l"])
        put(s, 8, 2, cel["G"])
    return bottle_drink("#d02a1a", 0.09, cork=False, extra=extra)


@reg("carrot_juice")
def carrot_juice():
    def extra(s, r):
        # carrot-top sprig tucked by the cork
        puts(s, [(10, 2), (11, 1), (11, 3), (12, 2)], "#4fa02e")
        puts(s, [(12, 1), (10, 1)], "#7cc84a")
    return bottle_drink("#f0701a", 0.08, top="#f8a050")


@reg("berry_smoothie")
def berry_smoothie():
    def extra(s, r):
        straw(s, "#e8483a", "#fbf6f0")
        puts(s, [(6, 11), (9, 10), (8, 12), (10, 12), (7, 9)], "#4a0e30")    # seeds
    return bottle_drink("#a83a7a", 0.08, cork=False, top="#f0c0d8", extra=extra)


@reg("tropical_smoothie")
def tropical_smoothie():
    def extra(s, r):
        straw(s, "#2aa8a0", "#fbf6f0")
        y = rp("#f8e070", 4, 0.06)
        for x, yy in BOTTLE_LIQUID:
            if 8 <= yy <= 9:
                s.set(x, yy, y[2] if x > 6 else y[3])     # sunrise layers: yellow over orange
        put(s, 6, 9, "#ffffff")
    return bottle_drink("#f8a030", 0.08, cork=False, top="#fff2c0", extra=extra)


# ============================================================================ mugs


def mug_hot(base, features=None, steam=True, spread=0.07) -> Sprite:
    s = Sprite()
    mug_base(s)
    r = mug_drink(s, base, spread)
    if features:
        features(s, r)
    ex = set(MUG_MASK)
    if steam:
        wisps = [(6, 2), (6, 1), (7, 0)] if steam is True else steam
        for i, (x, y) in enumerate(wisps):
            s.set(x, y, C(STEAM[0] if y >= 2 else STEAM[1]))
        ex |= set(wisps)
    return finish(s, exclude=ex)


@reg("coffee")
def coffee():
    def f(s, r):
        puts(s, [(4, 7), (5, 7), (9, 6)], "#8a5634")       # crema ring
        puts(s, [(8, 5), (9, 5), (4, 5)], "#6a3a1c")
        puts(s, [(5, 6), (6, 6)], "#b88a62")               # reflection
    return mug_hot("#3a1a0a", f, steam=[(5, 2), (5, 1), (6, 0), (8, 2), (9, 1), (9, 0)])


@reg("cafe_latte")
def cafe_latte():
    def f(s, r):
        heart = {"w": "#fffaf0", "W": "#f4e8d4"}
        puts(s, [(5, 6), (7, 6), (6, 7)], heart["w"])
        puts(s, [(6, 6)], heart["W"])
        puts(s, [(4, 5), (9, 7)], "#e8d0a8")
    return mug_hot("#c8986a", f, steam=False)


@reg("green_tea")
def green_tea():
    def f(s, r):
        # tea-bag string over the rim with a paper tag hanging outside
        # tea-bag string over the front lip with the paper tag hanging on the mug
        puts(s, [(5, 7), (5, 8), (5, 9)], "#f4f0e0")
        stamp(s, ["tt", "TT"], {"t": "#f8f4e8", "T": "#7cb84a"}, 4, 10)
    return mug_hot("#a8c86a", f)


@reg("mint_tea")
def mint_tea():
    def f(s, r):
        leaf = {"l": "#7cd06a", "b": "#3a9a3a", "d": "#256a26", "s": "#4a7a2a"}
        stamp(s, [".l.", "lbl", ".bd", "..s"], leaf, 6, 1)
        stamp(s, ["lb", "bd"], leaf, 9, 3)
        put(s, 8, 5, leaf["s"])
    return mug_hot("#c8d890", f, steam=False)


@reg("ginger_tea")
def ginger_tea():
    def f(s, r):
        stamp(s, [".yy", "ywy", "yy."], {"y": "#f2d020", "w": "#fcf4b8"}, 6, 5)   # lemon slice
        puts(s, [(4, 7), (5, 7)], "#f2e2b8")                                      # ginger slice
    return mug_hot("#e2b45c", f)


@reg("hot_cocoa")
def hot_cocoa():
    def f(s, r):
        m = {"h": "#ffffff", "l": "#f6f0f0", "d": "#d8ccd0"}
        stamp(s, ["hl", "ld"], m, 4, 4)
        stamp(s, ["hl", "ld"], m, 7, 3)
        stamp(s, ["hl", "ld"], m, 8, 6)
        put(s, 6, 6, "#9a6a4a")
    return mug_hot("#6a3418", f, steam=False)
