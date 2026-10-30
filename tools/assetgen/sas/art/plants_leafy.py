"""Leafy greens and brassicas: lettuce, cabbage, spinach, broccoli, cauliflower, celery, asparagus."""
from __future__ import annotations

import math

from .core import hexc
from .plants_kit import Plant, disc, green, h, line, rect, tones
from .plants_lib import leaf, sprout, stem


def ramp_hex(*cols):
    return [hexc(c) for c in cols]


CREAM = ramp_hex("#9a9468", "#c2bb90", "#ddd5b2", "#f0e9d0", "#fbf7ea")


def ruffle(p: Plant, oid: int, col, salt: int = 0, every: int = 2) -> None:
    """Frilly rim: light pixels on the upward-facing edge of an object."""
    for y in range(p.h):
        for x in range(p.w):
            if p.own(x, y) == oid and p.own(x, y - 1) != oid and (x + y + salt) % every == 0:
                p.px(x, y, col)


def rosette(p: Plant, cx: float, base_y: int, spec, rmp, salt: int = 0, frill=None, vein=None) -> list[int]:
    """Leaves radiating from (cx, base_y): spec = [(angle_deg_from_up, length, width, depth)]."""
    ids = []
    for k, (ang, L, w, d) in enumerate(spec):
        a = math.radians(ang)
        tip = (cx + math.sin(a) * L, base_y - math.cos(a) * L)
        bx = cx + (0.5 if ang > 0 else -0.5 if ang < 0 else 0)
        oid = leaf(p, (round(bx), base_y), (round(tip[0]), round(tip[1])), w, rmp, "spoon", depth=d,
                   vein=vein, vein_span=(0.15, 0.6))
        ids.append(oid)
        if frill is not None:
            ruffle(p, oid, frill, salt + k)
    return ids


def florets(p: Plant, cx: int, top: int, widths, rmp, salt: int = 0) -> None:
    """Knobbly dome of 2x2 florets. ``widths`` = number of florets per row, top to bottom."""
    for r, n in enumerate(widths):
        y = top + r * 2 - (1 if r else 0)
        x0 = cx - n + (r % 2)
        for k in range(n):
            x = x0 + k * 2
            px = {(x, y): 3, (x + 1, y): 2, (x, y + 1): 2, (x + 1, y + 1): 1}
            if h(x, y, salt) < 0.5:
                px[(x, y)] = 4 if r == 0 or h(x, y, salt + 1) < 0.4 else 3
            p.fixed(px, rmp)


# --------------------------------------------------------------------------- crops


def lettuce(st: int) -> Plant:
    p = Plant()
    G = green("#7cc04a", sat=0.02)
    GO = green("#62a83c")
    FR = hexc("#c8ec8a")
    if st == 0:
        sprout(p, 4, G, "spoon", stem_h=0)
        sprout(p, 11, G, "spoon", stem_h=0)
        return p
    if st == 1:
        rosette(p, 7.5, 15, [(-70, 5, 3.4, -1), (70, 5, 3.4, -1), (-30, 6, 3.8, 0), (30, 6, 3.8, 0),
                             (0, 5, 3.4, 1)], G, frill=FR)
        return p
    if st == 2:
        rosette(p, 7.5, 15, [(-75, 7, 4.0, -1), (75, 7, 4.0, -1), (-40, 7, 4.4, -1), (40, 7, 4.4, -1),
                             (-15, 7, 4.4, 0), (15, 7, 4.4, 0), (0, 4, 4.0, 1)], G, frill=FR)
        return p
    rosette(p, 7.5, 15, [(-80, 8, 4.4, -1), (80, 8, 4.4, -1)], GO, frill=FR, salt=1)
    rosette(p, 7.5, 15, [(-50, 9, 5.0, -1), (50, 9, 5.0, -1), (-25, 10, 5.0, 0), (25, 10, 5.0, 0),
                         (0, 10, 5.0, 0)], G, frill=FR, salt=3)
    # tight heart of the head
    rosette(p, 7.5, 15, [(-30, 6, 4.4, 1), (30, 6, 4.4, 1), (0, 5, 4.4, 1)], G, frill=FR, salt=5)
    return p


def cabbage(st: int) -> Plant:
    p = Plant()
    G = green("#5f9a7a", sat=-0.06)
    HEAD = ramp_hex("#7a9a5a", "#98b874", "#b4d090", "#cce4a8", "#e2f2c4")
    if st == 0:
        sprout(p, 7, G, "round", stem_h=1)
        return p
    if st == 1:
        rosette(p, 7.5, 15, [(-70, 5, 4.0, 0), (70, 5, 4.0, 0), (-25, 6, 4.4, -1), (25, 6, 4.4, -1)], G, vein=4)
        return p
    # broad outer leaves spread low and wide
    rosette(p, 7.5, 15, [(-60, 8, 5.4, -1), (60, 8, 5.4, -1), (-85, 8, 4.4, 0), (85, 8, 4.4, 0)], G, vein=4)
    rosette(p, 7.5, 15, [(-30, 8 if st == 2 else 11, 5.0, -1), (30, 8 if st == 2 else 11, 5.0, -1)], G, vein=4)
    r = 2.8 if st == 2 else 4.2
    cy = 15.6 - r * 0.9
    oid = p.add(disc(8, cy, r, r * 0.9), HEAD, form=(7.6, cy - 0.3, r, 1.5), noise=0.2, salt=5)
    # overlapping leaf lines on the head
    for k, (dx, d) in enumerate(((-1, 1), (1, -1))):
        pts = line([(8 + dx * r * 0.2, cy - r * 0.8), (8 + dx * r * 0.65, cy), (8 + dx * r * 0.3, cy + r * 0.7)])
        for q in pts:
            if p.own(*q) == oid:
                p.px(q[0], q[1], HEAD[1] if dx > 0 else HEAD[2])
    # wrapper leaves hugging the head from the front
    leaf(p, (6, 15), (1, 15 - round(r * 0.9)), 3.4, G, "spoon", vein=4)
    leaf(p, (9, 15), (14, 15 - round(r * 0.9)), 3.4, G, "spoon", vein=4)
    return p


def spinach(st: int) -> Plant:
    """Upright clumps of dark, glossy spoon-shaped leaves: few, large blades with a clear lit half
    and shaded half, a pale glint and short pale petioles."""
    p = Plant()
    G = green("#2e7a2e", sat=0.05)
    PET = tones("#6aa040", (-0.15, -0.07, 0, 0.07, 0.13))
    GL = hexc("#a2dc84")

    def clump(x, spec, pet=2):
        for ang, L, w, d in spec:
            a = math.radians(ang)
            bx, by = round(x + math.sin(a) * pet), round(15 - math.cos(a) * pet)
            stem(p, [(x, 15), (bx, by)], PET, base=3)
            tip = (round(x + math.sin(a) * L), round(15 - math.cos(a) * L))
            oid = leaf(p, (bx, by), tip, w, G, "spoon", depth=d, vein=1, vein_span=(0.1, 0.6))
            # one glossy glint on the lit half, near the broad end of the blade
            gx = round(bx + (tip[0] - bx) * 0.72) - (1 if ang >= 0 else 0)
            gy = round(by + (tip[1] - by) * 0.72)
            for q in ((gx, gy), (gx - 1, gy), (gx, gy + 1)):
                if p.own(*q) == oid and p.own(q[0] - 1, q[1]) == oid:
                    p.px(q[0], q[1], GL)
                    break

    if st == 0:
        sprout(p, 4, G, "v", stem_h=0)
        sprout(p, 11, G, "tiny", stem_h=1)
        return p
    if st == 1:
        clump(4, [(-45, 5, 3.2, 0), (40, 5, 3.2, 0), (0, 6, 3.2, -1)])
        clump(11, [(-40, 5, 3.2, 0), (45, 4, 3.0, 0), (5, 6, 3.2, -1)])
        return p
    if st == 2:
        # two young clumps, three big blades each (back blade first)
        clump(3, [(0, 10, 4.2, 0), (-40, 7, 3.8, 0), (40, 7, 3.8, 0)])
        clump(12, [(5, 9, 4.2, 0), (-40, 7, 3.8, 0), (40, 6, 3.8, 0)])
        return p
    # one mature rosette: three tall back blades, two broad front blades
    clump(7, [(-35, 13, 5.0, 0), (35, 13, 5.0, 0), (0, 15, 4.6, 0), (-70, 9, 5.0, 1), (70, 9, 5.0, 1)], pet=3)
    return p


def broccoli(st: int) -> Plant:
    p = Plant()
    G = green("#4a8a6a", sat=-0.04)
    FL = ramp_hex("#1f4a22", "#2c6a2c", "#3f8a36", "#5aa444", "#86c460")
    STK = ramp_hex("#6a8a5a", "#8aa874", "#a8c490", "#c0d8a8", "#d6e8c0")
    if st == 0:
        sprout(p, 7, G, "round", stem_h=1)
        return p
    if st == 1:
        stem(p, [(7, 15), (7, 11)], STK, base=3)
        for a, b, bd, d in (((7, 14), (2, 12), -1, 0), ((7, 14), (12, 12), 1, 0), ((7, 12), (4, 8), 1, -1),
                            ((7, 12), (10, 8), -1, -1), ((7, 11), (7, 8), 0, 0)):
            leaf(p, a, b, 3.0, G, "lance", bend=bd * 0.8, depth=d, vein=4)
        return p
    top = 7 if st == 2 else 4
    p.add(rect(7, top + 2, 7, 15), STK, base=3)
    p.add(rect(8, top + 3, 8, 15), STK, base=1)
    lv = [((7, 14), (1, 11), 3.8, -1.2, 0), ((8, 14), (14, 11), 3.8, 1.2, 0), ((7, 12), (1, 6), 3.8, 1.0, -1),
          ((8, 12), (14, 6), 3.8, -1.0, -1)]
    if st == 3:
        lv += [((7, 10), (3, 3), 3.2, 0.8, -1), ((8, 10), (12, 3), 3.2, -0.8, -1)]
    for i, (a, b, w, bd, d) in enumerate(lv):
        leaf(p, a, b, w, G, "lance", bend=bd, depth=d, vein=4)
    if st == 2:
        florets(p, 8, top, [2, 2], FL, salt=3)
    if st == 3:
        florets(p, 8, top, [2, 3, 3], FL, salt=3)
        leaf(p, (7, 15), (3, 12), 3.0, G, "lance", bend=-0.8, vein=4)
        leaf(p, (8, 15), (12, 12), 3.0, G, "lance", bend=0.8, vein=4)
    return p


def cauliflower(st: int) -> Plant:
    p = Plant()
    G = green("#5e9a3e")
    if st == 0:
        sprout(p, 7, G, "round", stem_h=1)
        return p
    sc = [0, 0.6, 0.85, 1.0][st]
    back = [(-35, 11, 4.0, -1), (35, 11, 4.0, -1), (-10, 13, 3.8, -1), (12, 13, 3.6, -1)]
    rosette(p, 7.5, 15, [(a, L * sc, w, d) for a, L, w, d in back[: (2 if st == 1 else 4)]], G, vein=4)
    if st == 2:
        florets(p, 8, 10, [1, 2], CREAM, salt=9)
    if st == 3:
        florets(p, 8, 7, [2, 3, 3], CREAM, salt=9)
    # cupping front leaves
    front = [(-70, 8, 4.4, 0), (70, 8, 4.4, 0)]
    if st >= 2:
        front += [(-50, 6, 4.0, 1), (50, 6, 4.0, 1)]
    rosette(p, 7.5, 15, [(a, L * sc, w, d) for a, L, w, d in front], G, vein=4)
    return p


def celery(st: int) -> Plant:
    p = Plant()
    STK = ramp_hex("#6a9a46", "#86b45a", "#a2cc72", "#bcdc8c", "#d4eaa8")
    G = green("#4e9434")
    if st == 0:
        sprout(p, 7, G, "true", stem_h=1, stem_r=STK)
        return p
    hh = [0, 8, 12, 15][st]
    # fan of separate ribbed stalks with gaps between them
    xs = [(3, -2), (6, -1), (9, 1), (12, 2)] if st >= 2 else [(5, -1), (8, 0), (10, 1)]
    if st == 3:
        xs.insert(2, (8, 0))
    for i, (x, lean) in enumerate(xs):
        topy = 16 - hh + (i % 2) * 2 + (1 if abs(lean) == 2 else 0)
        tx = x + lean
        pts = line([(x, 15), (x + lean * 0.5, (15 + topy) / 2 + 1), (tx, topy + 3)])
        p.add(pts, STK, base=3)
        p.add([(q[0] + 1, q[1]) for q in pts if q[1] > topy + 4], STK, base=1)
        # frilly leaf tuft (small lobed leaflets) at the top
        d = -1 if lean < 0 else 1
        leaf(p, (tx, topy + 3), (tx - 2, topy + 1), 2.6, G, "ovate")
        leaf(p, (tx, topy + 3), (tx + 2, topy + 1), 2.6, G, "ovate", depth=-1)
        leaf(p, (tx, topy + 2), (tx + d, topy - 1), 2.4, G, "ovate")
    return p


def asparagus(st: int) -> Plant:
    p = Plant()
    SP = tones("#6a9a3a", (-0.2, -0.1, 0.0, 0.08, 0.15), hue=0.04)
    TIP = tones("#8a5a8a")
    FERN = green("#5f9a40")
    if st >= 2:
        # feathery fronds in the back: thin stems with dotted needles
        for (x, tx, ty) in ((3, 0, 16 - (12, 15)[st - 2] + 1), (12, 15, 16 - (12, 15)[st - 2] + 2),
                            (7, 9, 16 - (12, 15)[st - 2])):
            pts = line([(x, 15), ((x + tx) / 2, 9), (tx, ty)])
            p.add(pts, FERN, base=1, cast=False)
            for i, (qx, qy) in enumerate(pts[::2]):
                if qy < 12:
                    p.px(qx - 1, qy, FERN[2 + (i % 2)])
                    p.px(qx + 1, qy - 1, FERN[3 - (i % 2)])
    spears = {0: [(6, 12), (10, 13)], 1: [(4, 10), (8, 8), (11, 11)],
              2: [(3, 9), (6, 6), (9, 8), (12, 10)], 3: [(2, 7), (5, 3), (8, 5), (11, 2), (13, 8)]}[st]
    for x, ty in spears:
        p.add(rect(x, ty, x, 15), SP, base=3)
        p.add(rect(x + 1, ty + 1, x + 1, 15), SP, base=1)
        # scaly purple-tinged tip
        p.px(x, ty, TIP[3])
        p.px(x + 1, ty + 1, TIP[1])
        p.px(x, ty + 1, TIP[2])
        if 15 - ty > 4:
            p.px(x + 1, ty + 4, TIP[1])
            p.px(x, ty + 6, SP[4])
    return p
