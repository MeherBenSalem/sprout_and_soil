"""Fruiting vegetables: staked vines (tomato, cucumber, green bean) and bushes (peppers, eggplant),
plus the sprawling zucchini."""
from __future__ import annotations

from .core import hexc
from .plants_kit import Plant, fruit, green, tones
from .plants_lib import (G_STD, STEM, STEM_DK, TOP, compound, flower, leaf, sprout, stake, stamp, stem,
                         tendril, trifoliate)

# produce stamps: digits index the fruit ramp, G/g calyx greens, w glint
TOMATO = [".3Gg.", "3w433", "33332", "23321", ".221."]
TOMATO_S = [".Gg.", "3w43", "3332", ".21."]
TOMATO_XS = ["Gg", "32", "21"]
BELL = [".Gg.", "3w43", "3432", "3332", "2.21"]
BELL_S = [".G.", "3w3", "332", "2.1"]
CHILI = ["G", "3", "3", "2", "1"]
CHILI_C = ["G.", "3.", "3.", "2.", ".1"]
EGGPLANT = [".G.", "gGg", "343", "3w2", "332", "221", ".1."]
EGGPLANT_S = [".G.", "gGg", "3w2", "321", ".1."]
CUCUMBER = ["G.", "41", "31", "40", "31", "41", "30", ".1"]
CUCUMBER_S = ["G.", "41", "31", "40", ".1"]
POD = ["s", "4", "3", "3", "2", "1"]
POD_C = ["s.", "4.", "3.", "3.", ".2", ".1"]

YELLOW = "#f4d22a"
YELLOW_C = "#c8901a"
WHITE = "#f6f4ee"


def tomato(st: int) -> Plant:
    p = Plant()
    R = fruit("#d8322a")
    UN = fruit("#8cbc4c")
    G = G_STD
    if st == 0:
        sprout(p, 7, G, "true", stem_h=0)
        return p
    top = TOP[st] + 1
    stake(p, 7, top, ties=[13, 8, 4][:st])
    vine = [(8, 15), (6, 13), (9, 10), (6, 7), (9, 4), (7, 2)]
    stem(p, vine[: 2 + st + (st == 3)], STEM_DK)
    leaves = [((6, 13), (2, 11)), ((9, 11), (13, 10)), ((7, 8), (3, 6)), ((9, 7), (13, 5)),
              ((7, 4), (3, 2)), ((8, 4), (12, 2)), ((7, 3), (6, 1))]
    for i, (a, b) in enumerate(leaves[: [0, 2, 4, 7][st]]):
        compound(p, a, b, G, n=1, size=2.0, depth=-1 if i in (2, 5) else 0)
    if st == 1:
        leaf(p, (8, 10), (9, 8), 2.2, G)
    if st == 2:
        for x, y in ((4, 9), (12, 7), (5, 4)):
            flower(p, x, y, YELLOW, YELLOW_C)
        stamp(p, TOMATO_XS, 2, 12, UN)
        stamp(p, TOMATO_S, 10, 11, UN)
    if st == 3:
        stamp(p, TOMATO_S, 1, 11, R)
        stamp(p, TOMATO, 9, 9, R)
        stamp(p, TOMATO_S, 2, 5, R)
        stamp(p, TOMATO_XS, 12, 3, fruit("#e0782a"))
        flower(p, 5, 1, YELLOW, YELLOW_C)
    return p


def bell_pepper(st: int) -> Plant:
    p = Plant()
    R = fruit("#c8281e")
    UN = fruit("#3f8f2a")
    G = green("#3f8a2e")
    if st == 0:
        sprout(p, 7, G, "round", stem_h=1)
        return p
    t = TOP[st]
    if st == 1:
        stem(p, [(7, 15), (7, 10)], STEM_DK)
        leaf(p, (7, 14), (3, 13), 3.0, G, bend=-0.6)
        leaf(p, (7, 13), (11, 12), 3.0, G, bend=0.6)
        leaf(p, (7, 11), (4, 9), 2.8, G, depth=-1)
        leaf(p, (7, 11), (10, 9), 2.8, G, depth=-1)
        leaf(p, (7, 10), (7, 8), 2.4, G)
        return p
    stem(p, [(7, 15), (7, t + 3)], STEM_DK)
    stem(p, [(7, 11), (4, 8), (3, t + 3)], STEM_DK)
    stem(p, [(7, 10), (11, 7), (12, t + 3)], STEM_DK)
    big = [((7, 13), (3, 12), 3.2, -1), ((7, 12), (12, 11), 3.2, 1),
           ((7, 9), (5, 6), 3.0, 1), ((7, 8), (10, 6), 3.0, -1),
           ((4, 8), (0, 6), 3.4, -1), ((11, 7), (15, 6), 3.4, 1),
           ((3, 6), (2, 2), 3.2, 1), ((12, 5), (13, 1), 3.2, -1), ((7, 6), (8, 1), 3.6, 0)]
    if st == 2:   # keep stage 2 around 12px: shorter top shoots
        big = big[:6] + [((3, 6), (2, 4), 3.0, 1), ((12, 5), (13, 4), 3.0, -1), ((7, 6), (8, 4), 3.2, 0)]
    for i, (a, b, w, bd) in enumerate(big[: [0, 4, 9, 9][st]]):
        leaf(p, a, b, w, G, "ovate", bend=bd * 0.8, depth=-1 if i in (2, 3) else 0)
    if st == 2:
        flower(p, 6, 5, WHITE, "#e8d070", big=True)
        flower(p, 12, 9, WHITE, "#e8d070")
        stamp(p, BELL_S, 2, 9, UN)
        stamp(p, BELL_S, 9, 10, UN)
    if st == 3:
        stamp(p, BELL, 1, 8, R)
        stamp(p, BELL, 10, 9, R)
        stamp(p, BELL_S, 6, 11, fruit("#d8781e"))
        flower(p, 11, 3, WHITE, "#e8d070")
    return p


def chili_pepper(st: int) -> Plant:
    p = Plant()
    R = fruit("#d7261e")
    UN = fruit("#5aa82c")
    G = green("#4a8e30")
    if st == 0:
        sprout(p, 7, G, "v", stem_h=0)
        return p
    t = TOP[st] + 2
    stem(p, [(7, 15), (7, t)], STEM_DK)
    stem(p, [(7, 12), (4, 9), (3, t + 1)], STEM_DK)
    stem(p, [(7, 11), (10, 8), (12, t)], STEM_DK)
    lv = [((7, 13), (4, 13)), ((7, 13), (10, 12)), ((4, 9), (1, 9)), ((5, 10), (6, 7)), ((10, 8), (13, 9)),
          ((9, 9), (8, 6)), ((3, t + 2), (0, t)), ((12, t + 1), (15, t)), ((7, t + 1), (5, t - 1)),
          ((7, t + 1), (9, t - 2)), ((3, t + 1), (4, t - 2)), ((12, t), (11, t - 2))]
    for i, (a, b) in enumerate(lv[: [0, 6, 10, 12][st]]):
        leaf(p, a, b, 2.2, G, "lance", depth=-1 if i % 4 == 3 else 0)
    if st == 2:
        for x, y in ((2, 7), (13, 6), (8, 4)):
            flower(p, x, y, WHITE, "#e8e0a0")
        stamp(p, CHILI_C, 4, 11, UN)
        stamp(p, CHILI, 10, 10, UN)
    if st == 3:
        for (x, y, shape) in ((1, 10, CHILI), (4, 11, CHILI_C), (6, 8, CHILI), (9, 10, CHILI_C), (12, 9, CHILI),
                              (13, 4, CHILI_C), (2, 4, CHILI), (9, 3, CHILI)):
            stamp(p, shape, x, y, R if (x + y) % 5 else fruit("#e8701e"))
    return p


def eggplant(st: int) -> Plant:
    p = Plant()
    P = fruit("#4a2160", 1.2)
    G = green("#4c8a3c")
    ST_P = tones("#6a4a6a", (-0.15, -0.07, 0, 0.07, 0.13))
    if st == 0:
        sprout(p, 7, G, "round", stem_h=1, stem_r=ST_P)
        return p
    t = TOP[st]
    if st == 1:
        stem(p, [(7, 15), (7, 10)], ST_P)
        leaf(p, (7, 14), (2, 13), 3.6, G, bend=-0.8, vein=1)
        leaf(p, (7, 13), (12, 11), 3.6, G, bend=0.8, vein=1)
        leaf(p, (7, 11), (6, 8), 3.0, G, vein=1)
        return p
    stem(p, [(7, 15), (8, t + 3)], ST_P)
    stem(p, [(7, 12), (4, 9)], ST_P)
    stem(p, [(8, 11), (11, 8)], ST_P)
    big = [((7, 14), (2, 13), 4.0, -1), ((8, 13), (14, 12), 4.0, 1), ((7, 10), (3, 6), 4.4, 1),
           ((8, 9), (13, 5), 4.4, -1), ((8, 6), (6, 1), 4.0, 1), ((8, 6), (11, 2), 3.6, -1)]
    for i, (a, b, w, bd) in enumerate(big[: [0, 3, 4, 6][st]]):
        leaf(p, a, b, w, G, "ovate", bend=bd, depth=-1 if i in (2, 3) and st == 3 else 0, vein=1)
    if st == 2:
        flower(p, 4, 9, "#b48ad8", "#f2d02a", big=True)
        flower(p, 11, 8, "#b48ad8", "#f2d02a", big=True)
        flower(p, 7, 4, "#b48ad8", "#f2d02a")
    if st == 3:
        stamp(p, EGGPLANT, 2, 8, P)
        stamp(p, EGGPLANT, 10, 7, P)
        stamp(p, EGGPLANT_S, 6, 10, P)
        flower(p, 9, 3, "#b48ad8", "#f2d02a", big=True)
    return p


def cucumber(st: int) -> Plant:
    p = Plant()
    CU = fruit("#2e6a2c", 1.15)
    G = green("#5fa03a")
    if st == 0:
        sprout(p, 7, G, "broad", stem_h=0)
        return p
    top = TOP[st] + 1
    stake(p, 7, top, ties=[12, 7, 3][:st])
    stem(p, [(8, 15), (6, 12), (9, 8), (6, 5), (8, 2)][: 2 + st], STEM)
    big = [((6, 12), (2, 11), 4.4), ((9, 10), (13, 8), 4.4), ((6, 7), (2, 5), 4.6), ((9, 5), (13, 3), 4.4),
           ((7, 3), (4, 1), 3.6), ((9, 2), (11, 0), 3.2)]
    if st == 3:   # leaves climb higher so the fruit can hang in the open below them
        big = [((6, 10), (2, 9), 4.4), ((9, 8), (13, 6), 4.4), ((6, 6), (2, 4), 4.4), ((9, 4), (13, 2), 4.2),
               ((7, 2), (4, 0), 3.4), ((8, 12), (11, 12), 3.0)]
    for i, (a, b, w) in enumerate(big[: [0, 2, 4, 6][st]]):
        leaf(p, a, b, w, G, "heart", bend=-0.6 if b[0] < 7 else 0.6, depth=-1 if i in (1, 4) else 0, vein=4)
    tendril(p, 10, 13, 1)
    if st >= 2:
        tendril(p, 3, 9, -1)
        flower(p, 4, 9, YELLOW, YELLOW_C, big=True)
        flower(p, 12, 6, YELLOW, YELLOW_C)
    if st == 2:
        stamp(p, CUCUMBER_S, 11, 10, fruit("#6aa840"))
    if st == 3:
        stamp(p, CUCUMBER, 2, 10, CU)
        stamp(p, CUCUMBER, 12, 8, CU)
        stamp(p, CUCUMBER_S, 4, 5, CU)
    return p


def zucchini(st: int) -> Plant:
    """Low sprawling squash: huge silvery-veined leaves on long petioles, fruit lying on the ground."""
    p = Plant()
    Z = fruit("#2f6526", 1.0)
    G = green("#5a9a3a")
    SILVER = hexc("#b8d0a0")
    FL = fruit("#f2c42a", 0.8)
    if st == 0:
        sprout(p, 7, G, "broad", stem_h=0)
        return p
    # (leaf base, leaf tip, width): big leaves held low on short petioles, overlapping
    lv = {1: [((6, 14), (2, 11), 4.6), ((9, 14), (13, 11), 4.6), ((7, 13), (7, 9), 3.8)],
          2: [((5, 13), (1, 9), 5.2), ((10, 13), (14, 9), 5.2), ((7, 11), (5, 6), 5.0), ((9, 11), (11, 7), 4.6)],
          3: [((5, 12), (1, 8), 5.4), ((10, 12), (14, 8), 5.4), ((6, 9), (4, 4), 5.2), ((9, 9), (12, 4), 5.0),
              ((8, 8), (8, 3), 4.6)]}[st]
    for i, (a, b, w) in enumerate(lv):
        stem(p, [(7 + (a[0] > 7), 15), a], STEM, base=3)
    for i, (a, b, w) in enumerate(lv):
        leaf(p, a, b, w, G, "heart", depth=-1 if i in (2, 3) else 0, vein=4, vein_span=(0.1, 0.8))
        # silvery blotches typical of zucchini leaves
        mx, my = (a[0] + b[0]) // 2, (a[1] + b[1]) // 2
        p.px(mx - 1, my + 1, SILVER)
    if st >= 2:
        # big yellow trumpet flower in the middle
        stamp(p, [".4.4.", "34443", ".323.", "..g.."], 5, 10 if st == 2 else 10, FL)
    if st == 3:
        stamp(p, ["G3343433", ".2121221"], 0, 14, Z)
        stamp(p, ["G33433", ".21221"], 10, 14, Z)
    return p


def green_bean(st: int) -> Plant:
    p = Plant()
    POD_R = fruit("#9acc58", 0.9)
    G = green("#4a8c30")
    if st == 0:
        sprout(p, 7, G, "broad", stem_h=0)
        return p
    top = [0, 4, 0, 0][st]
    stake(p, 7, top, ties=[11, 5, 1][:st])
    ytop = [0, 6, 2, 1][st]
    sp = []
    y, side = 15, 0
    while y > ytop:
        sp += [(9 if side else 6, y), (9 if side else 6, y - 1)]
        y -= 2
        side ^= 1
    p.add(sp, STEM, base=3)
    trif = [((6, 12), (3, 11)), ((9, 10), (12, 9)), ((6, 7), (3, 6)), ((9, 5), (12, 4)), ((6, 3), (3, 2)),
            ((9, 2), (12, 1))]
    for i, (a, b) in enumerate(trif[: [0, 2, 4, 6][st]]):
        trifoliate(p, a, b, G, 2.4, depth=0, prof="heart")
    if st == 2:
        for x, y in ((4, 9), (11, 7), (4, 4)):
            flower(p, x, y, WHITE, "#c8b8e0")
    if st == 3:
        for x, y, s in ((1, 9, POD), (4, 10, POD_C), (13, 7, POD), (11, 11, POD_C), (4, 4, POD_C), (14, 2, POD)):
            stamp(p, s, x, y, POD_R)
    return p
