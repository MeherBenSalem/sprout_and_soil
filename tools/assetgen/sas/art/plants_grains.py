"""Grains and legumes: barley, oat, rice, soybean.

Grain fields mimic vanilla wheat's layout (several stalks across the full width) but each has
its own head: barley = upright spike with long bristly awns, oat = open panicle of dangling
spikelets, rice = dense arching tuft with drooping grain sprays.
"""
from __future__ import annotations

from .core import hexc
from .plants_kit import Plant, green, line
from .plants_lib import H, STEM, STEM_DK, TOP, curve_leaf, flower, sprout, stamp, stem, trifoliate


def ramp_hex(*cols):
    return [hexc(c) for c in cols]


def grass_tufts(p: Plant, xs, hh, G, lean=1) -> None:
    """Young grain: pairs of thin blades per plant, alternating lean."""
    for i, x in enumerate(xs):
        t = 16 - hh + (i % 2) * 2
        d = lean if i % 2 else -lean
        curve_leaf(p, [(x, 15), (x + d * 0.3, (15 + t) / 2), (x + d * 1.5, t)], 1.8, G, "blade", depth=-(i % 2))
        if hh > 5:
            curve_leaf(p, [(x, 15), (x - d, 13), (x - d * 3, 16 - hh * 0.6)], 1.6, G, "blade", depth=-1)


# barley spike: 2px kernel column, long awns fanning up from the top and short ones off the sides
BARLEY_HEAD = ["a...a",
               ".a.a.",
               ".a.a.",
               "..a..",
               ".43..",
               "a32a.",
               ".43..",
               "a32a.",
               ".21..",
               "..s.."]


def barley(st: int) -> Plant:
    p = Plant()
    G = green("#6a9a3a")
    GOLD = ramp_hex("#9a7a30", "#bc9a40", "#d8b85a", "#e8cc74", "#f4e0a0")
    STR = ramp_hex("#8a7030", "#a88c40", "#c4a656", "#d8bc6c", "#e8d08a")
    UNR = green("#9ac25a", spread=0.9)
    if st <= 1:
        grass_tufts(p, (1, 4, 7, 10, 13), H[st], G)
        return p
    ripe = st == 3
    head = GOLD if ripe else UNR
    stalk = STR if ripe else G
    awn = hexc("#efdca0") if ripe else hexc("#c8e090")
    # staggered heads so the field reads as individual bristly spikes, not a wall
    heads = [(0, 2), (4, 0), (8, 3), (11, 1)] if ripe else [(0, 5), (4, 3), (8, 6), (11, 4)]
    for i, (x, top) in enumerate(heads):
        sx = x + 2
        curve_leaf(p, [(sx, 15), (sx - 2, 12), (sx - 3, 11)], 1.6, stalk, "blade", depth=-1)
        p.add(line([(sx, 15), (sx, top + 9)]), stalk, base=2 + (i % 2))
        stamp(p, BARLEY_HEAD, x, top, head, {"a": awn, "s": (stalk, 2)})
    return p


def oat(st: int) -> Plant:
    p = Plant()
    G = green("#7aa04a", sat=-0.04)
    PALE = ramp_hex("#9a8a5a", "#bcae78", "#d6ca96", "#e8deb0", "#f6f0d0")
    STR = ramp_hex("#8a7e4e", "#a89c66", "#c4b880", "#d8cc96", "#e8e0b0")
    UNR = green("#a4c86e", spread=0.9)
    if st <= 1:
        grass_tufts(p, (1, 4, 7, 10, 13), H[st], G, lean=-1)
        return p
    ripe = st == 3
    stalk = STR if ripe else G
    sp = PALE if ripe else UNR
    hair = stalk[3]
    # (stalk x, top y, spikelets as (dx, dy) offsets of the bell top)
    plants = [(3, 2, ((-2, 1), (1, 2), (-2, 5), (2, 6), (-1, 8))),
              (8, 0, ((2, 1), (-2, 2), (2, 5), (-2, 6), (1, 9))),
              (13, 3, ((-2, 1), (1, 3), (-2, 5), (1, 7)))]
    for i, (x, top, bells) in enumerate(plants):
        if not ripe:
            top += 3
        curve_leaf(p, [(x, 15), (x - 2, 12), (x - 3, 10)], 1.6, stalk, "blade", depth=-1)
        curve_leaf(p, [(x, 13), (x + 2, 11), (x + 3, 10)], 1.4, stalk, "blade", depth=-1)
        p.add(line([(x, 15), (x, top + 1)]), stalk, base=2)
        p.px(x, top, hair)
        # nodding stalk tip
        p.px(x + 1, top - 1 if top > 0 else top, sp[3])
        for dx, dy in bells:
            yy = top + dy
            if yy > 12:
                continue
            sgn = 1 if dx > 0 else -1
            # hairline pedicel then a dangling 2-px "bell" spikelet
            p.px(x + sgn, yy, hair)
            p.px(x + dx, yy + 1, sp[4])
            p.px(x + dx, yy + 2, sp[2])
            p.px(x + dx + sgn, yy + 2, sp[1])
    return p


def rice(st: int) -> Plant:
    p = Plant()
    G = green("#5a9a40")
    GY = green("#8aa448")
    GOLD = ramp_hex("#9a7a2a", "#bc9838", "#d8b44e", "#ead070", "#f6e49a")
    hh = [5, 8, 11, 12][st]
    ripe = st == 3
    col = GOLD if ripe else green("#a8c860", spread=0.9)
    stalk_r = ramp_hex("#6a6a2a", "#8a8438", "#a8a050", "#c0b868", "#d4cc84") if ripe else STEM
    panicles = []
    if st >= 2:
        # culms first, so the tuft blades drawn afterwards hide their lower part
        for k, (cx, d, top) in enumerate(((1, 1, 2), (6, 1, 0), (14, -1, 1))):
            top += 0 if ripe else 3
            arch = line([(cx, 12), (cx, top + 1), (cx + d, top), (cx + d * 2, top + 1), (cx + d * 3, top + 5)])
            p.add(arch, stalk_r, base=3, cast=False)
            panicles.append((cx, d, top, arch))
    # upright V-shaped tufts; outer blades arch over at the tip
    blades = [(-5, 0.75), (5, 0.75), (-3, 0.95), (3, 0.95), (-1, 1.0), (1, 1.0), (-6, 0.5), (6, 0.5)]
    for k, cx in enumerate((4, 11)):
        for i, (dx, f) in enumerate(blades[: [3, 5, 6, 8][st]]):
            top = 16 - hh * f - k
            bx = cx + (1 if dx > 0 else 0)
            if abs(dx) >= 3:
                ctrl = [(bx, 15), (bx + dx * 0.2, top + 1), (bx + dx * 0.6, top - 1), (bx + dx, top + 2)]
            else:
                ctrl = [(bx, 15), (bx + dx * 0.3, (15 + top) / 2), (bx + dx, top)]
            curve_leaf(p, ctrl, 1.25, GY if ripe and i in (0, 3) else G, "blade", depth=-1 if i % 3 == 2 else 0)
    for cx, d, top, arch in panicles:
        # drooping spray: grains on both sides of the hanging part of the arch
        hang = [q for q in arch if (q[0] - cx) * d >= 2 or (q[0] - cx) * d == 1 and q[1] == top]
        for j, (x, y) in enumerate(hang):
            p.px(x + d, y, col[3 if j % 2 == 0 else 2])
            if j % 2:
                p.px(x - d, y + 1, col[2])
        ex, ey = arch[-1]
        p.px(ex, ey + 1, col[1])
    return p


def soybean(st: int) -> Plant:
    p = Plant()
    G = green("#4e8a30")
    YEL = ramp_hex("#6a6a2a", "#8a8a34", "#a8a844", "#c4c05a", "#d8d478")
    POD = ramp_hex("#5a5a2a", "#7a7838", "#9a9650", "#b8b46a", "#d0cc88")
    if st == 0:
        sprout(p, 4, G, "round", stem_h=1)
        sprout(p, 11, G, "round", stem_h=0)
        return p
    t = TOP[st]
    stem(p, [(7, 15), (7, t + 3)], STEM_DK)
    trif = [((7, 13), (3, 11)), ((8, 12), (12, 10)), ((7, 9), (3, 6)), ((8, 8), (12, 5)), ((7, 6), (6, 2)),
            ((8, 5), (11, 2))]
    for i, (a, b) in enumerate(trif[: [0, 2, 4, 6][st]]):
        rmp = YEL if st == 3 and i in (0, 3, 4) else G
        trifoliate(p, a, b, rmp, 2.6, prof="ovate")
    if st == 2:
        for x, y in ((6, 10), (9, 7), (5, 5)):
            flower(p, x, y, "#c8a0d8", "#a070b0")
    if st == 3:
        # clusters of fuzzy pods hugging the stem
        for x, y in ((5, 10), (9, 11), (5, 6), (10, 7), (6, 13), (9, 4)):
            stamp(p, ["4", "3", "2", "1"], x, y, POD)
            p.px(x + (1 if x > 7 else -1), y + 1, POD[3])
    return p
