"""Berries, grape and pineapple.

The four cross-model berry bushes have deliberately different habits so they read apart even
before the fruit shows: blueberry = compact upright twiggy shrub, raspberry = tall upright canes,
blackberry = wide arching thorny bramble, cranberry = low trailing evergreen mat.
"""
from __future__ import annotations

from .core import hexc
from .plants_kit import Plant, fruit, green, line, tones, wood
from .plants_lib import curve_leaf, flower, leaf, sprout, stake, stamp, stem, trifoliate


def ramp_hex(*cols):
    return [hexc(c) for c in cols]


WHITE = "#f6f4ee"


def strawberry(st: int) -> Plant:
    p = Plant()
    G = green("#4a8a2a")
    R = fruit("#e0303a")
    SEED = hexc("#f2d860")
    if st == 0:
        sprout(p, 7, G, "round", stem_h=0)
        return p
    sc = [0, 0.5, 0.85, 1.0][st]
    lv = [((7, 15), (2, 9)), ((8, 15), (13, 9)), ((7, 15), (7, 5)), ((7, 15), (4, 6)), ((8, 15), (11, 6))]
    for i, (a, b) in enumerate(lv[: [0, 3, 4, 5][st]]):
        tip = (round(a[0] + (b[0] - a[0]) * sc), round(a[1] + (b[1] - a[1]) * sc))
        trifoliate(p, a, tip, G, 2.4 + sc, prof="ovate")
    if st == 2:
        for x, y in ((3, 11), (12, 10), (8, 8)):
            flower(p, x, y, WHITE, "#f2c83a", big=True)
        stamp(p, ["G", "3", "2"], 5, 12, fruit("#c8d070"))
    if st == 3:
        for x, y in ((1, 11), (11, 11), (6, 12)):
            stamp(p, ["GgG", "343", "332", ".1."], x, y, R)
            p.px(x + 1, y + 2, SEED)
            p.px(x + 2, y + 1, SEED)
            p.px(x, y + 1, R[4])
        flower(p, 13, 7, WHITE, "#f2c83a", big=True)
    return p


def blueberry(st: int) -> Plant:
    """Compact upright twiggy shrub with small blue-green oval leaves; dusty indigo berry clusters."""
    p = Plant()
    W = ramp_hex("#4a3430", "#64463c", "#7e5a48", "#98705a", "#ae866c")
    G = green("#4a8a5a", sat=-0.04)
    B = ramp_hex("#1e2462", "#2c3884", "#3e4ea6", "#6070c0", "#9aa8dc")
    if st == 0:
        stem(p, [(7, 15), (7, 12)], W)
        leaf(p, (7, 12), (5, 10), 2.2, G)
        leaf(p, (7, 12), (9, 11), 2.2, G)
        leaf(p, (7, 13), (10, 13), 2.0, G, depth=-1)
        return p
    hh = [0, 9, 13, 15][st]
    top = 16 - hh
    # several upright twigs from the crown
    twigs = [[(7, 15), (5, 10), (4, top + 2)], [(8, 15), (10, 10), (11, top + 2)], [(7, 15), (7, top)],
             [(7, 14), (3, 11), (1, top + 5)], [(8, 14), (12, 11), (14, top + 5)]][: [0, 3, 5, 5][st]]
    for t in twigs:
        p.add(line(t), W, base=2)
    for t in twigs:
        pts = line(t)
        for j, (x, y) in enumerate(pts[2::2]):
            d = 1 if (j + x) % 2 else -1
            leaf(p, (x, y), (x + d * 2, y - 1), 2.2, G, "ellipse", depth=-1 if j % 2 else 0)
        x, y = pts[-1]
        leaf(p, (x, y), (x, y - 2), 2.2, G, "ellipse")
    if st == 2:
        # white urn-shaped flowers hanging in little bunches
        for x, y in ((4, 7), (10, 6), (7, 4), (12, 10), (2, 10)):
            p.px(x, y, hexc("#f6f2ea"))
            p.px(x, y + 1, hexc("#e2d4d8"))
            p.px(x + 1, y, hexc("#e8e2da"))
    if st == 3:
        for x, y in ((3, 8), (10, 6), (6, 3), (12, 10), (1, 11), (8, 10)):
            stamp(p, ["32", "21", ".3"], x, y, B)
            p.px(x, y, B[4])
            p.px(x + 2, y + 1, B[2]) if x < 13 else None
    return p


def canes(p: Plant, cane_r, specs) -> list[list[tuple[int, int]]]:
    out = []
    for ctrl in specs:
        pts = line(ctrl)
        p.add(pts, cane_r, base=2)
        out.append(pts)
    return out


def raspberry(st: int) -> Plant:
    """Tall upright canes with trifoliate leaves; bumpy red berries hanging along them."""
    p = Plant()
    CANE = ramp_hex("#5a3a32", "#764a3e", "#8e5c4a", "#a8725e", "#bc8a74")
    G = green("#4f9434")
    R = ramp_hex("#7a1028", "#a01c38", "#c82c4a", "#e2506a", "#f4849a")
    if st == 0:
        sprout(p, 7, G, "v", stem_h=1, stem_r=CANE)
        return p
    hh = [0, 9, 13, 16][st]
    specs = [[(5, 15), (4, 10), (3, 16 - hh + 2)], [(9, 15), (10, 9), (11, 16 - hh)],
             [(7, 15), (7, 8), (8, 16 - hh + 1)], [(6, 15), (2, 12), (0, 16 - hh + 6)],
             [(10, 15), (13, 12), (15, 16 - hh + 5)]][: [0, 2, 4, 5][st]]
    cs = canes(p, CANE, specs)
    for k, pts in enumerate(cs):
        for j, (x, y) in enumerate(pts[3::3]):
            d = -1 if (j + k) % 2 else 1
            trifoliate(p, (x, y), (x + d * 2, y - 1), G, 2.2, depth=-1 if j % 2 else 0)
        # thorns
        for (x, y) in pts[2::4]:
            p.px(x + 1, y, CANE[4])
    if st == 2:
        for x, y in ((3, 8), (11, 7), (7, 5)):
            p.px(x, y, hexc(WHITE))
            stamp(p, ["2"], x + 1, y + 1, fruit("#a8c860"))
    if st == 3:
        for x, y in ((1, 8), (11, 6), (6, 3), (12, 11), (4, 11), (8, 9)):
            stamp(p, ["343", "323", ".2."], x, y, R)
            p.px(x + 1, y, R[4])
    return p


def blackberry(st: int) -> Plant:
    """Wide arching thorny bramble with dark leaves; glossy black berries mixed with red unripe ones."""
    p = Plant()
    CANE = ramp_hex("#3e2232", "#562e42", "#6e3c52", "#884e66", "#a0687e")
    G = green("#3a7630")
    B = ramp_hex("#120a1e", "#24143a", "#3a2456", "#5e4482", "#9a82bc")
    RED = fruit("#c02a3a")
    if st == 0:
        sprout(p, 7, G, "v", stem_h=1, stem_r=CANE)
        return p
    hh = [0, 8, 11, 14][st]
    t = 16 - hh
    # arching canes: rise, then bow outwards and down (fountain habit)
    specs = [[(6, 15), (4, t), (0, t + 5)], [(9, 15), (11, t + 1), (15, t + 6)],
             [(7, 15), (6, t - 1), (2, t + 2)], [(8, 15), (10, t), (13, t + 2)]][: [0, 2, 4, 4][st]]
    cs = canes(p, CANE, specs)
    for k, pts in enumerate(cs):
        for j, (x, y) in enumerate(pts[2::3]):
            d = -1 if (j + k) % 2 else 1
            trifoliate(p, (x, y), (x + d, y - 2), G, 2.4, depth=-1 if j % 2 else 0)
        for (x, y) in pts[1::3]:
            p.px(x - 1, y, CANE[4])
    if st == 2:
        for x, y in ((3, 9), (11, 8), (7, 5), (12, 12)):
            stamp(p, ["32", "21"], x, y, RED)
    if st == 3:
        for (x, y, rmp) in ((1, 9, B), (11, 7, B), (6, 4, B), (13, 11, RED), (4, 12, B), (8, 9, RED), (9, 13, B)):
            stamp(p, ["34", "23", "12"], x, y, rmp)
            p.px(x, y, rmp[4])
    return p


def cranberry(st: int) -> Plant:
    """Low trailing evergreen mat of tiny leaves on wiry runners, dotted with crimson berries."""
    p = Plant()
    G = green("#3a6e3a", sat=-0.02)
    STM = ramp_hex("#4a2a22", "#62382c", "#7a4a3a", "#94604c", "#a87660")
    R = ramp_hex("#6a0a18", "#920e22", "#b81a2a", "#d8404a", "#f08a8a")
    hh = [5, 7, 9, 10][st]
    top = 16 - hh
    runners = [[(7, 15), (3, 14), (0, 13)], [(8, 15), (12, 14), (15, 13)], [(7, 15), (5, 12), (3, top + 1)],
               [(8, 15), (10, 12), (12, top + 2)], [(7, 15), (7, top)]]
    for r in runners[: [3, 4, 5, 5][st]]:
        pts = line(r)
        p.add(pts, STM, base=2)
        for j, (x, y) in enumerate(pts):
            if j % 2 == 0 and j > 0:
                d = 1 if j % 4 else -1
                p.add([(x + d, y - 1)], G, base=3 if d < 0 else 2)
                p.add([(x - d, y)], G, base=2)
                p.add([(x, y - 1)], G, base=3)
    if st == 2:
        for x, y in ((3, 12), (11, 12), (6, 9)):
            p.px(x, y, hexc("#f2c8d0"))
            p.px(x, y + 1, hexc("#d890a0"))
    if st == 3:
        for x, y in ((2, 12), (5, 10), (9, 11), (12, 12), (7, 7), (13, 10), (4, 13)):
            stamp(p, ["32", "21"], x, y, R)
            p.px(x, y, R[4])
    return p


def grape(st: int) -> Plant:
    """Vine trained on a small wooden trellis; green bunches at stage 2, purple at stage 3."""
    p = Plant()
    TW = wood("#8a6a3a")
    G = green("#5a9a3a")
    VINE = tones("#7a5a3a", (-0.15, -0.07, 0, 0.07, 0.13))
    if st == 0:
        sprout(p, 7, G, "broad", stem_h=0, stem_r=VINE)
        return p
    top = [0, 6, 2, 1][st]
    stake(p, 1, top)
    stake(p, 13, top)
    rails = [y for y in (12, 7, 2) if y >= top + 1]
    for y in rails:
        t = {(x, y): 3 for x in range(3, 13)}
        t.update({(x, y + 1): 1 for x in range(3, 13)})
        p.fixed(t, TW, cast=False)
    vine = [(7, 15), (8, 12), (6, 9), (8, 6), (7, 3)][: 2 + st]
    p.add(line(vine), VINE, base=2)
    for y in rails[: st]:
        p.add(line([(3, y - 1), (7, y - 1), (12, y - 1)]), VINE, base=3)
    lv = [((7, 12), (3, 10)), ((8, 11), (12, 9)), ((5, 6), (2, 4)), ((9, 6), (13, 4)), ((7, 2), (4, 0)),
          ((8, 2), (11, 0))]
    for i, (a, b) in enumerate(lv[: [0, 2, 4, 6][st]]):
        leaf(p, a, b, 4.2, G, "heart", depth=-1 if i % 2 else 0, vein=4)
    if st >= 2:
        col = fruit("#8ab84a") if st == 2 else ramp_hex("#2a0e2e", "#48184a", "#6a2a6a", "#8e4a8e", "#b682b4")
        bunch = ["343", "3232", ".32", ".2."] if st == 3 else ["32", "321", ".2"]
        for x, y in ((3, 8), (10, 9), (6, 3)):
            stamp(p, bunch, x, y, col)
            if st == 3:
                p.px(x + 1, y, col[4])
    return p


def pineapple(st: int) -> Plant:
    """Dense rosette of stiff, sword-like silvery leaves; the golden fruit sits in the centre at stage 3."""
    p = Plant()
    G = green("#5a8a5e", sat=-0.04)
    G2 = green("#4a7a4a", sat=-0.02)
    GOLD = ramp_hex("#9a5a1a", "#c07a22", "#e0a830", "#f0c454", "#f8de8a")
    sc = [0.4, 0.62, 0.85, 1.0][st]
    # (dx, dy) of each sword leaf tip, back to front
    spikes = [(-3, -12), (3, -12), (0, -11), (-5, -10), (5, -10), (-7, -7), (7, -7), (-8, -3), (8, -3),
              (-6, -5), (6, -5), (-2, -8), (2, -8)]
    n = [7, 9, 13, 13][st]
    for i in range(n):
        dx, dy = spikes[i]
        tip = (7.5 + dx * sc, 15 + dy * sc)
        ctrl = [(7 + (dx > 0), 15), (7.5 + dx * sc * 0.3, 15 + dy * sc * 0.55), tip]
        curve_leaf(p, ctrl, 3.0, G2 if i % 2 else G, "blade", depth=-1 if i < 5 else 0, vein=4,
                   vein_span=(0.15, 0.75))
    if st == 2:
        stamp(p, [".44.", "4232", "3232", ".11."], 6, 9, fruit("#c84a6a"))
        p.px(7, 8, G[3])
        p.px(8, 7, G[2])
    if st == 3:
        rows = [".3434.", "342434", "434243", "342434", "232423", ".2121."]
        stamp(p, rows, 5, 9, GOLD)
        for x, y, t in ((7, 8, 3), (8, 8, 2), (6, 7, 3), (9, 7, 2), (7, 6, 4), (8, 5, 2), (5, 6, 3), (10, 6, 1),
                        (7, 5, 3), (8, 6, 3)):
            p.px(x, y, G[t])
    return p
