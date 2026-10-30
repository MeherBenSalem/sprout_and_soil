"""Roots, tubers and alliums: radish, turnip, sweet potato, ginger, peanut, garlic, onion, leek.

Root crops follow the vanilla carrot/beetroot layout: two or three plants side by side with the
produce showing at the soil line in stage 3, so a field reads as neat rows.
"""
from __future__ import annotations

from .core import hexc, mix
from .plants_kit import Plant, fruit, green, line, rect
from .plants_lib import STEM, curve_leaf, flower, leaf, sprout, stamp, stem


def ramp_hex(*cols):
    return [hexc(c) for c in cols]


def radish(st: int) -> Plant:
    p = Plant()
    G = green("#5a9a3c")
    RSTEM = ramp_hex("#7a2a44", "#9a3a56", "#b04a6a", "#c8607e", "#d8789a")
    RAD = fruit("#d23a5a")
    xs = (2, 8, 13)
    for i, x in enumerate(xs):
        if st == 0:
            sprout(p, x, G, "tiny", stem_h=i % 2, stem_r=RSTEM)
            continue
        hh = [0, 7, 10, 12][st] - (i % 2)
        stem(p, [(x, 15), (x, 14)], RSTEM, base=2)
        leaf(p, (x, 14), (x - 2, 15 - hh + 2), 2.8, G, "spoon", depth=-1, vein=1)
        leaf(p, (x, 14), (x + 2, 15 - hh + 3), 2.8, G, "spoon", vein=1)
        if st >= 2:
            leaf(p, (x, 13), (x, 15 - hh), 3.0, G, "spoon", vein=1)
        if st == 2:
            stamp(p, ["32", "21"], x, 14, RAD)
        if st == 3:
            stamp(p, [".43.", "3w32", "2321"], x - 1, 13, RAD)
            p.px(x, 12, RSTEM[2])
    return p


def turnip(st: int) -> Plant:
    p = Plant()
    G = green("#4f8f3a")
    PUR = fruit("#9a4a8a")
    WH = ramp_hex("#a8a094", "#c8c0b0", "#ddd6c8", "#ece4d6", "#f8f4ec")
    for i, x in enumerate((4, 11)):
        if st == 0:
            sprout(p, x, G, "round", stem_h=0 if i else 1)
            continue
        sc = [0, 6, 9, 11][st]
        stem(p, [(x, 15), (x, 14), (x - 2, 15 - sc + 3)], STEM)
        stem(p, [(x + 1, 14), (x + 3, 15 - sc + 4)], STEM)
        leaf(p, (x - 2, 15 - sc + 4), (x - 4, 15 - sc), 3.4, G, "ovate", depth=-1, vein=4)
        leaf(p, (x + 3, 15 - sc + 5), (x + 5, 15 - sc + 1), 3.4, G, "ovate", vein=4)
        if st >= 2:
            leaf(p, (x, 14), (x + 1, 15 - sc - 1), 3.4, G, "lance", vein=4)
            leaf(p, (x - 1, 13), (x - 5, 12), 2.6, G, "ovate", depth=-1)
        if st == 2:
            stamp(p, [".33.", "3221"], x - 1, 14, PUR)
        if st == 3:
            leaf(p, (x + 2, 12), (x + 6, 12), 2.6, G, "ovate")
            stamp(p, [".3333.", "3w3332", "322221", "AAAAAB"], x - 2, 12, PUR, {"A": (WH, 3), "B": (WH, 1)})
    return p


def sweet_potato(st: int) -> Plant:
    """Low trailing vines with heart-shaped leaves (some purple-flushed) and tubers at the soil."""
    p = Plant()
    G = green("#4e8a36")
    GP = green("#5e7e3a")   # older, olive leaves
    VINE = ramp_hex("#4a2a3a", "#62384a", "#7a4a5a", "#94606e", "#a8788a")
    TUB = fruit("#b8503a")
    if st == 0:
        sprout(p, 7, G, "broad", stem_h=0, stem_r=VINE)
        return p
    vines = [[(7, 15), (4, 13), (1, 14)], [(8, 15), (11, 13), (14, 14)], [(7, 15), (6, 10), (3, 8)],
             [(8, 15), (10, 9), (12, 7)]]
    for v in vines[: [0, 2, 3, 4][st]]:
        p.add(line(v), VINE, base=2)
    hearts = [((2, 13), (0, 10), 0), ((13, 13), (15, 10), 0), ((5, 12), (4, 9), 1), ((10, 12), (12, 9), 0),
              ((4, 9), (2, 6), 0), ((11, 8), (13, 5), 1), ((7, 11), (7, 7), 0), ((8, 7), (9, 3), 1)]
    for i, (a, b, purple) in enumerate(hearts[: [0, 3, 6, 8][st]]):
        oid = leaf(p, a, b, 3.6, GP if purple else G, "heart", depth=-1 if i in (2, 3) else 0, vein=1)
        if purple:   # purple flush along the midrib of young leaves
            for q in line([a, b])[1:-1]:
                if p.own(*q) == oid:
                    p.px(q[0], q[1], VINE[3])
    if st == 3:
        stamp(p, [".3332.", "3w2221", ".1111."], 0, 13, TUB)
        stamp(p, [".332.", "34221", ".111."], 10, 13, TUB)
    return p


def ginger(st: int) -> Plant:
    """Tall reed-like pseudostems with alternating long narrow leaves; tan rhizome knobs at stage 3."""
    p = Plant()
    G = green("#4e9a3a")
    RH = ramp_hex("#8a6a3a", "#b08a4e", "#d0aa66", "#e2c286", "#f0d8a4")
    stems = [(4, 0), (8, 2), (12, 1)]
    hh = [5, 9, 13, 16][st]
    for k, (x, off) in enumerate(stems[: (2 if st == 0 else 3)]):
        topy = max(0, 16 - hh + off)
        p.add(line([(x, 15), (x, topy)]), STEM, base=2)
        y = 14 - (k % 2)
        side = -1 if k % 2 else 1
        while y > topy + 1:
            leaf(p, (x, y), (x + side * 3, y - 2), 1.8, G, "lance", depth=-1 if side > 0 else 0)
            side = -side
            y -= 3
        leaf(p, (x, topy + 1), (x, topy - 1), 1.6, G, "lance")
    if st == 3:
        stamp(p, [".33..3.", "3433232", ".12111."], 1, 13, RH)
        stamp(p, [".33.", "3431", ".11."], 11, 13, RH)
    return p


def peanut(st: int) -> Plant:
    """Low, wide, clover-like bush: leaves of two pairs of small oval leaflets; yellow flowers;
    pods at the soil when ripe."""
    p = Plant()
    G = green("#5aa040")
    POD = ramp_hex("#7a5a34", "#9a7a4a", "#bc9a64", "#d4b47e", "#e6cc9a")
    if st == 0:
        sprout(p, 4, G, "round", stem_h=0)
        sprout(p, 11, G, "round", stem_h=1)
        return p

    def pinnate(base, tip, depth=0):
        stem(p, [base, tip])
        dx, dy = tip[0] - base[0], tip[1] - base[1]
        for t, dd in ((0.55, depth - 1), (1.0, depth)):
            cx, cy = round(base[0] + dx * t), round(base[1] + dy * t)
            leaf(p, (cx, cy), (cx - 2, cy - 1), 2.2, G, "ellipse", depth=dd)
            leaf(p, (cx, cy), (cx + 2, cy - 1), 2.2, G, "ellipse", depth=dd)

    hh = [0, 7, 8, 9][st]
    for k, x in enumerate((4, 11)):
        t = 16 - hh + k
        pinnate((x, 15), (x - 2, t + 3), -1)
        pinnate((x, 15), (x + 2, t + 4), 0)
        pinnate((x, 15), (x, t + (1 if st == 1 else 0)), 0)
    if st >= 2:
        for x, y in ((2, 10), (8, 11), (13, 9), (6, 8)):
            flower(p, x, y, "#f4c82a", "#d89a1a")
    if st == 3:
        for x in (2, 7, 12):
            stamp(p, ["3.43", "2121"], x - 1, 14, POD)
    return p


def garlic(st: int) -> Plant:
    """Flat blue-green strap leaves; ripe plants yellow at the tips and show white bulbs."""
    p = Plant()
    G = green("#5c9c62")
    TIPY = ramp_hex("#7a7a3a", "#9a9a48", "#b8b45a", "#d0c870", "#e2dc8c")
    BULB = ramp_hex("#a89a9a", "#c8bcbc", "#e0d8d0", "#efe8de", "#fbf8f2")

    def plant_(x, k):
        hh = [5, 8, 11, 13][st] - k
        straps = [(-3, 0.6), (3, 0.6), (-1, 1.0), (2, 0.9)][: (2 if st == 0 else 4)]
        if st == 0:
            straps = [(-1, 0.9), (1, 0.7)]
        for i, (dx, f) in enumerate(straps):
            tip = (x + dx, 15 - round(hh * f))
            mid = (x + dx * 0.3, 15 - hh * f * 0.6)
            curve_leaf(p, [(x, 15), mid, tip], 2.0, G, "strap", depth=-1 if i >= 2 else 0, vein=None)
            if st == 3:
                # yellowing tips
                p.px(tip[0], tip[1], TIPY[3])
                p.px(tip[0] + (1 if dx > 0 else -1) * 0, tip[1] + 1, TIPY[2])
        if st == 3:
            stamp(p, [".44.", "4332", "B22B"], x - 1, 13, BULB, {"B": (BULB, 1)})
            p.px(x, 13, mix(BULB[2], hexc("#b07aa0"), 0.5))
        if st == 2:
            stamp(p, ["43", "21"], x, 14, BULB)

    for k, x in enumerate((3, 8, 13)):
        plant_(x, k % 2)
    return p


def onion(st: int) -> Plant:
    """Hollow tubular leaves; ripe onions flop over and show golden bulbs at the soil."""
    p = Plant()
    G = green("#5a9a52", sat=-0.04)
    BULB = fruit("#c88a3a")

    def tube(x, dx, hh, flop=False, depth=0):
        if flop:
            ctrl = [(x, 15), (x + dx * 0.4, 15 - hh * 0.75), (x + dx * 2.2, 15 - hh * 0.45)]
        else:
            ctrl = [(x, 15), (x + dx * 0.4, 15 - hh * 0.6), (x + dx, 15 - hh)]
        curve_leaf(p, ctrl, 1.6, G, "strap", depth=depth, vein=4, vein_span=(0.2, 0.9))

    for k, x in enumerate((3, 8, 12)):
        if st == 0:
            # onion sprouts come up as a single bent "flag"
            pts = line([(x, 15), (x, 12 - k % 2), (x + 1, 11 - k % 2)])
            p.add(pts, G, base=3)
            continue
        hh = [4, 8, 12, 12][st] - (k % 2) * 2
        tube(x, -2, hh, depth=-1)
        tube(x, 2, hh - 1, flop=st == 3 and k != 1)
        tube(x, 0, hh + 1, flop=st == 3 and k == 1)
        if st >= 2:
            sz = ["32", "21"] if st == 2 else [".44.", "3w32", "2221"]
            stamp(p, sz, x - (0 if st == 2 else 1), 16 - len(sz), BULB)
            if st == 3:
                p.px(x, 12, BULB[3])
    return p


def leek(st: int) -> Plant:
    """Fan of flat blue-green leaves on a thick white shaft (blanched by hilling)."""
    p = Plant()
    G = green("#3f7a5a", sat=-0.04)
    SH = ramp_hex("#a8b098", "#c8d0b4", "#e0e4c8", "#f0f0d8", "#fafaee")
    for k, x in enumerate((4, 11)):
        hh = [5, 9, 13, 15][st] - k
        shaft = [0, 2, 4, 6][st]
        if shaft:
            p.add(rect(x, 16 - shaft, x, 15), SH, base=3)
            p.add(rect(x + 1, 16 - shaft, x + 1, 15), SH, base=1)
        y0 = 15 - shaft
        fan = [(-3, 0.7), (4, 0.75), (-1, 1.0), (2, 0.95), (-5, 0.45), (6, 0.5)][: 2 + st]
        if st == 0:
            fan = [(-1, 1.0), (2, 0.8)]
        for i, (dx, f) in enumerate(fan):
            top = 16 - hh * f
            curve_leaf(p, [(x + (dx > 0), y0), (x + dx * 0.3, (y0 + top) / 2), (x + dx, top)], 2.2, G, "blade",
                       depth=-1 if i % 2 else 0, vein=4, vein_span=(0.1, 0.5))
    return p
