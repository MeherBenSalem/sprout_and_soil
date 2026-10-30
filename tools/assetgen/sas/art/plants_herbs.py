"""Cash crops and herbs: coffee, tea, cotton, basil, mint, peppercorn."""
from __future__ import annotations

from .core import hexc
from .plants_kit import Plant, disc, green, h, jitter_seeds, leaf_cells, line, rect
from .plants_lib import H, STEM, STEM_DK, TOP, flower, leaf, sprout, stake, stamp, stem


def ramp_hex(*cols):
    return [hexc(c) for c in cols]


BARK = ramp_hex("#3e2a22", "#54382c", "#6a4a3a", "#82604c", "#9a7860")


def coffee(st: int) -> Plant:
    """Glossy dark tiered shrub (layered, roughly conical); cherries cluster under each tier."""
    p = Plant()
    G = green("#2f6e30", sat=0.06)
    GL = hexc("#86c86e")
    R = ramp_hex("#6a1010", "#921a1a", "#c02a2a", "#e04a3a", "#f88a6a")
    OR = ramp_hex("#7a3a10", "#a8521a", "#d07028", "#e89040", "#f4b86a")
    if st == 0:
        sprout(p, 7, G, "round", stem_h=1, stem_r=BARK)
        return p
    hh = H[st]
    top = 16 - hh
    p.add(line([(7, 15), (7, top + 1)]), BARK, base=2)
    # tiers: (centre y, half width, half height) from the top down
    tiers = {1: [(top + 2, 2.6, 1.6), (top + 5, 4.2, 1.8)],
             2: [(top + 2, 2.4, 1.6), (top + 5, 4.6, 1.8), (top + 8, 6.2, 1.9)],
             3: [(top + 2, 2.4, 1.6), (top + 5, 4.6, 1.8), (top + 8, 6.4, 2.0), (top + 11, 7.6, 1.8)]}[st]
    shape = set()
    for (cy, rx, ry) in tiers:
        tier = {q for q in disc(7.5, cy, rx, ry)}
        # drooping tier tips
        tier |= {(round(7.5 - rx), round(cy + ry * 0.6)), (round(7.5 + rx) - 1, round(cy + ry * 0.6))}
        shape |= tier
    shape = {q for q in shape if q[1] <= 14}
    t = leaf_cells(shape, jitter_seeds(16, 16, 2.4, 31 + st), salt=st, stretch=(0.75, 1.5),
                   form=(6, top + 3, 8, 0.6))
    # tiers separate: the row just under each tier is darker
    for (cy, rx, ry) in tiers:
        for x in range(16):
            q = (x, round(cy + ry))
            if q in t:
                t[q] = max(0, t[q] - 1)
    p.fixed(t, G)
    for q, v in t.items():
        if v == 4 and h(q[0], q[1], 3) < 0.6:
            p.px(q[0], q[1], GL)
    for k, (cy, rx, ry) in enumerate(tiers[1:]):
        y = round(cy + ry) - 1
        spots = [round(7.5 - rx * 0.6), round(7.5 + rx * 0.45)]
        for j, x in enumerate(spots):
            if st == 2:
                p.px(x, y, hexc("#f8f6f0"))
                p.px(x + 1, y, hexc("#e4e0d4"))
                p.px(x, y - 1, hexc("#f0eee6"))
            if st == 3:
                rr = OR if (k + j) % 3 == 2 else R
                stamp(p, ["32.", "213"], x - 1, y, rr)
                p.px(x - 1, y, rr[4])
    return p


def tea(st: int) -> Plant:
    """Compact, rounded tea bush: a dome of small glossy leaves; pale new flushes on top when ripe."""
    p = Plant()
    G = green("#3a7a2a", sat=0.04)
    SHOOT = ramp_hex("#5a9a3a", "#78b44a", "#98cc5e", "#b6e07a", "#d2f09c")
    if st == 0:
        sprout(p, 7, G, "round", stem_h=1, stem_r=BARK)
        return p
    hh = [0, 8, 11, 13][st]
    rx = [0, 4.2, 5.8, 7.4][st]
    ry = hh * 0.55
    cx, cy = 8.0, 15.5 - hh + ry
    p.add(line([(7, 15), (7, 12)]), BARK, base=2)
    p.add(line([(8, 15), (9, 13)]), BARK, base=1)
    dome = {q for q in disc(cx, cy, rx, ry) if q[1] <= 13}
    # ragged outline: nibble some rim pixels so the bush edge reads as individual leaves
    rim = {q for q in dome if any(n not in dome for n in ((q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] - 1)))}
    dome -= {q for q in rim if h(q[0], q[1], 5) < 0.3}
    t = leaf_cells(dome, jitter_seeds(16, 16, 2.3, 11 + st), salt=st, form=(cx - 1.5, cy - 2, rx, 1.0))
    p.fixed(t, G)
    for q, v in t.items():
        if v == 4 and h(q[0], q[1], 9) < 0.5:
            p.px(q[0], q[1], hexc("#8ccc6a"))
    if st == 3:
        for x, y in ((3, 4), (7, 2), (11, 4), (5, 3), (9, 3)):
            p.px(x, y, SHOOT[3])
            p.px(x, y - 1, SHOOT[4])
            p.px(x + 1, y, SHOOT[2])
    if st == 2:
        for x, y in ((4, 6), (10, 5)):
            p.px(x, y - 1, SHOOT[3])
    return p


def cotton(st: int) -> Plant:
    p = Plant()
    G = green("#4e8a36")
    GR = green("#8a7040", sat=-0.08)
    BOLL = ramp_hex("#a8a49c", "#ccc8be", "#e4e0d8", "#f2f0ea", "#fcfcf8")
    HUSK = ramp_hex("#4a3424", "#62442e", "#7a583a", "#94704c", "#aa8660")
    BR = ramp_hex("#4a3a24", "#5e4a2e", "#73603a", "#8a7648", "#a08c58")
    if st == 0:
        sprout(p, 7, G, "broad", stem_h=0)
        return p
    t = TOP[st]
    stem(p, [(7, 15), (7, t + 2)], BR)
    if st >= 2:
        stem(p, [(7, 12), (3, 8)], BR)
        stem(p, [(7, 11), (12, 7)], BR)
    lv = [((7, 13), (3, 12)), ((7, 13), (11, 12)), ((4, 9), (1, 7)), ((11, 8), (14, 6)), ((7, 7), (5, 4)),
          ((7, 6), (10, 3)), ((7, 10), (4, 11)), ((8, 9), (11, 10))]
    if st == 1:
        lv = [((7, 14), (3, 13)), ((7, 13), (11, 12)), ((7, 11), (4, 9)), ((7, 11), (10, 9)), ((7, 10), (7, 8))]
    for i, (a, b) in enumerate(lv[: [0, 5, 8, 8][st]]):
        leaf(p, a, b, 3.4, GR if st == 3 and i % 3 == 1 else G, "heart", vein=1, depth=-1 if i >= 4 else 0)
    if st == 2:
        for x, y in ((3, 7), (12, 6), (7, 3)):
            flower(p, x, y, "#f2e8b8", "#d8b8c8", big=True)
    if st == 3:
        for x, y in ((1, 5), (10, 4), (5, 1), (5, 9), (11, 10)):
            stamp(p, [".444.", "44434", "34332", ".H.H."], x, y, BOLL, {"H": (HUSK, 1)})
    return p


def basil(st: int) -> Plant:
    """Bushy herb: a mound of big cupped, glossy bright-green leaves; white flower spikes when mature."""
    p = Plant()
    G = green("#3c8e2c", sat=0.06)
    GL = hexc("#b0e88a")
    if st == 0:
        sprout(p, 7, G, "round", stem_h=1)
        return p
    # (base, tip, width, depth) back to front; the mound grows with the stage
    tiers = {
        1: [((7, 13), (4, 11), 3.2, 0), ((8, 13), (11, 11), 3.2, 0), ((7, 11), (7, 8), 3.0, 0)],
        2: [((7, 10), (4, 6), 3.4, -1), ((8, 10), (11, 6), 3.4, -1), ((7, 14), (2, 12), 3.8, 0),
            ((8, 14), (13, 12), 3.8, 0), ((7, 12), (3, 9), 3.6, 0), ((8, 12), (12, 9), 3.6, 0),
            ((7, 8), (7, 4), 3.2, 0)],
        3: [((7, 7), (5, 3), 3.2, -1), ((8, 7), (10, 3), 3.2, -1), ((7, 9), (2, 6), 3.6, -1),
            ((8, 9), (13, 6), 3.6, -1), ((7, 14), (1, 12), 3.8, 0), ((8, 14), (14, 12), 3.8, 0),
            ((7, 12), (3, 9), 3.8, 0), ((8, 12), (12, 9), 3.8, 0), ((7, 10), (6, 6), 3.4, 1),
            ((8, 10), (10, 7), 3.2, 1), ((7, 5), (7, 2), 2.8, 0)],
    }[st]
    p.add(line([(7, 15), (7, 4 if st == 3 else 8)]), STEM, base=2)
    for (a, b, w, d) in tiers:
        oid = leaf(p, a, b, w, G, "ellipse", depth=d, vein=1, vein_span=(0.2, 0.7))
        # glossy highlight on the cupped blade
        gx, gy = round(a[0] + (b[0] - a[0]) * 0.55) - 1, round(a[1] + (b[1] - a[1]) * 0.55) - 1
        if p.own(gx, gy) == oid:
            p.px(gx, gy, GL)
    if st == 3:
        for (x, y0) in ((7, 0), (3, 3), (12, 4)):
            for yy in range(y0, y0 + 3):
                p.px(x, yy, hexc("#f4f2ea") if yy % 2 == 0 else hexc("#d8cce0"))
    return p


def mint(st: int) -> Plant:
    """Upright square stems with large opposite leaves in clean pairs; lilac flower spikes at stage 3."""
    p = Plant()
    G = green("#4aa84a", sat=-0.02)
    MST = ramp_hex("#4a5a34", "#5e7040", "#74884c", "#8aa05a", "#a2b86c")
    LIL = ramp_hex("#8a6aa0", "#a684bc", "#c0a0d4", "#d6bce4", "#ead8f2")
    if st == 0:
        sprout(p, 5, G, "tiny", stem_h=1, stem_r=MST)
        sprout(p, 10, G, "v", stem_h=0, stem_r=MST)
        return p
    if st == 1:
        stems = [(5, 9, (13, 10)), (10, 8, (14, 11))]
        size, reach = 2.8, 2
    else:
        # two stems, pairs every 4 px, so each leaf keeps a clean silhouette
        stems = [(4, 4 if st == 2 else 1, (13, 9, 5)), (11, 5 if st == 2 else 2, (14, 10, 6))]
        size, reach = 3.4, 3
    for k, (x, top, pairs) in enumerate(stems):
        p.add(rect(x, top, x, 15), MST, base=2 + k % 2)
        for j, y in enumerate(pairs):
            if y <= top + 1:
                continue
            for d in (-1, 1):
                # leaves on the lit (left) side sit in front; the right ones tuck behind.
                # Pairs tilt a little differently per stem so the two stems are not mirror copies.
                rise = 2 if (d < 0) == (k == 0) else 1
                leaf(p, (x, y), (x + d * reach, y - rise), size, G, "ovate", depth=0 if d < 0 else -1)
        leaf(p, (x, top + 2), (x, top), 2.4, G, "ovate")
        if st == 3:
            for dy, c in ((-1, LIL[3]), (-2, LIL[4]), (0, LIL[2])):
                p.px(x, top + dy, c)
            p.px(x + 1, top, LIL[1])
    return p


def peppercorn(st: int) -> Plant:
    """Climbing vine on a stake with glossy heart leaves and hanging spikes of berries (green, then red)."""
    p = Plant()
    G = green("#2f6e30", sat=0.06)
    GB = ramp_hex("#2a4a1a", "#3e6a24", "#5a8a2e", "#78a83c", "#98c454")
    RB = ramp_hex("#5a0e0e", "#801a14", "#a82a1e", "#d04a2e", "#ec7a4a")
    if st == 0:
        sprout(p, 7, G, "broad", stem_h=0)
        return p
    top = TOP[st] + 1
    stake(p, 7, top, ties=[12, 7, 3][:st])
    stem(p, [(8, 15), (6, 12), (9, 9), (6, 6), (9, 3)][: 2 + st], STEM_DK)
    lv = [((6, 12), (2, 10)), ((9, 10), (13, 8)), ((6, 7), (2, 5)), ((9, 5), (13, 3)), ((7, 3), (4, 1)),
          ((8, 2), (11, 0))]
    for i, (a, b) in enumerate(lv[: [0, 2, 4, 6][st]]):
        leaf(p, a, b, 3.6, G, "heart", vein=4, depth=-1 if i in (1, 4) else 0)
    if st >= 2:
        # long dangling catkin-like spikes, 1px wide beaded strings
        for (x, y, n) in ((3, 11, 5), (11, 9, 5), (2, 6, 4), (13, 4, 4)):
            p.px(x, y - 1, STEM_DK[2])
            for j in range(n):
                if st == 2:
                    col = GB[3 if j % 2 == 0 else 2]
                else:
                    col = (RB if j < n - 1 else GB)[3 if j % 2 == 0 else 2]
                p.px(x, y + j, col)
                if j % 2 and j < n - 1:
                    p.px(x + 1, y + j, (RB if st == 3 else GB)[1])
    return p
