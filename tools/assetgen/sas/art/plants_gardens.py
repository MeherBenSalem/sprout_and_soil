"""Wild gardens: dense cross-model clumps found in the wild that hint at the crops they drop."""
from __future__ import annotations

from .core import Sprite, hexc
from .plants_kit import Plant, disc, fruit, green, h, jitter_seeds, leaf_cells, line, rect
from .plants_lib import curve_leaf, leaf, stamp, stem, trifoliate


def ramp_hex(*cols):
    return [hexc(c) for c in cols]


def grass(p: Plant, G, xs, hmin=6, hmax=11, salt=0, width=1.4) -> None:
    """Tangle of grass blades leaning both ways."""
    for i, x in enumerate(xs):
        hh = hmin + int(h(x, i, salt) * (hmax - hmin + 1))
        d = -1 if h(i, x, salt + 1) < 0.5 else 1
        top = 16 - hh
        curve_leaf(p, [(x, 15), (x + d * 0.5, (15 + top) / 2), (x + d * 2, top)], width, G, "blade",
                   depth=-1 if i % 3 == 0 else 0)


def bush(p: Plant, G, cx, cy, rx, ry, salt=0, cell=2.3, cut=13) -> set:
    mask = {q for q in disc(cx, cy, rx, ry) if q[1] <= cut}
    rim = {q for q in mask if any(n not in mask for n in ((q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] - 1)))}
    mask -= {q for q in rim if h(q[0], q[1], salt) < 0.35}
    t = leaf_cells(mask, jitter_seeds(16, 16, cell, salt), salt=salt, form=(cx - 1.5, cy - 2, max(rx, ry), 0.9))
    p.fixed(t, G)
    return mask


def meadow_garden() -> Plant:
    p = Plant()
    G = green("#5a9a3a")
    TOM = fruit("#d8322a")
    TAS = ramp_hex("#9a7a2a", "#c09a3a", "#e0bc4e", "#f2c63a", "#f8e08a")
    # corn stalk at the back right with a golden tassel
    p.add(rect(12, 3, 12, 15), ramp_hex("#4a6a2a", "#5e8034", "#76983e", "#90b050", "#a8c466"), base=3)
    curve_leaf(p, [(12, 9), (14, 6), (15, 8)], 2.0, G, "blade", depth=-1)
    for dx, dy, tn in ((0, -1, 4), (0, 0, 3), (-1, 1, 3), (1, 0, 2), (-2, 2, 2), (2, 1, 2), (0, 1, 2)):
        p.px(12 + dx, 2 + dy, TAS[tn])
    grass(p, G, (0, 2, 4, 6, 8, 10, 13, 15), 5, 10, salt=3)
    # tomato vine tumbling through the grass
    p.add(line([(4, 15), (3, 10), (6, 6), (9, 7)]), ramp_hex("#3a5a20", "#4a7028", "#5e8a32", "#74a03e", "#8ab64c"),
          base=2)
    for a, b in (((3, 10), (0, 8)), ((5, 7), (3, 4)), ((7, 6), (9, 4)), ((4, 12), (7, 11))):
        leaf(p, a, b, 2.4, G, "ovate")
    stamp(p, [".Gg.", "3w43", "3332", ".21."], 1, 10, TOM)
    stamp(p, [".G.", "3w3", "321"], 7, 8, TOM)
    for x, y in ((10, 10), (14, 12), (2, 4), (9, 3)):
        p.px(x, y, hexc("#f6f4ee"))
        p.px(x + 1, y, hexc("#dcd8cc"))
        p.px(x, y - 1, hexc("#f6f4ee"))
    return p


def woodland_garden() -> Plant:
    p = Plant()
    G = green("#3f7a30")
    RAS = ramp_hex("#7a1028", "#a01c38", "#c82c4a", "#e2506a", "#f4849a")
    CANE = ramp_hex("#5a3a32", "#764a3e", "#8e5c4a", "#a8725e", "#bc8a74")
    RSTEM = ramp_hex("#7a2a44", "#9a3a56", "#b04a6a", "#c8607e", "#d8789a")
    CREAM = ramp_hex("#9a9468", "#c2bb90", "#ddd5b2", "#f0e9d0", "#fbf7ea")
    # bramble canes arching over
    for ctrl in ([(6, 15), (4, 4), (0, 7)], [(8, 15), (10, 3), (15, 6)], [(7, 15), (7, 6), (5, 2)]):
        p.add(line(ctrl), CANE, base=2)
    for (x, y, d) in ((3, 6, -1), (5, 9, 1), (9, 5, 1), (11, 8, -1), (6, 4, -1), (13, 6, 1), (8, 11, -1)):
        trifoliate(p, (x, y), (x + d, y - 2), G, 2.4)
    # radish top at the front right: rough leaves on red stems, a red shoulder at the soil
    for (bx, tx, ty) in ((12, 10, 9), (12, 14, 9), (12, 12, 8)):
        stem(p, [(12, 15), (bx, 13)], RSTEM)
        leaf(p, (bx, 13), (tx, ty), 2.6, green("#5a9a3c"), "spoon", vein=1)
    stamp(p, [".43.", "3w32"], 11, 14, fruit("#d23a5a"))
    # pale cauliflower curd + leaf peeking out on the left
    leaf(p, (3, 15), (0, 11), 3.0, green("#5e9a3e"), "ovate", vein=4)
    stamp(p, [".43.", "4332", "3221"], 2, 13, CREAM)
    for x, y in ((1, 6), (11, 4), (6, 2), (8, 8)):
        stamp(p, ["343", "323", ".2."], x, y, RAS)
        p.px(x + 1, y, RAS[4])
    return p


def highland_garden() -> Plant:
    p = Plant()
    G = green("#3a6a4a", sat=-0.02)
    B = ramp_hex("#1e2462", "#2c3884", "#3e4ea6", "#6070c0", "#9aa8dc")
    PALE = ramp_hex("#9a8a5a", "#bcae78", "#d6ca96", "#e8deb0", "#f6f0d0")
    STR = ramp_hex("#8a7e4e", "#a89c66", "#c4b880", "#d8cc96", "#e8e0b0")
    # oat stalks rising behind the shrub
    for (x, top, bells) in ((3, 1, ((-2, 1), (1, 2), (-2, 4), (1, 6))), (12, 2, ((2, 1), (-2, 2), (2, 4)))):
        p.add(line([(x, 15), (x, top)]), STR, base=2)
        for dx, dy in bells:
            sgn = 1 if dx > 0 else -1
            p.px(x + sgn, top + dy, STR[3])
            p.px(x + dx, top + dy + 1, PALE[4])
            p.px(x + dx, top + dy + 2, PALE[2])
        p.px(x, top - 1, PALE[3])
    bush(p, G, 7.5, 10.0, 6.8, 5.2, salt=21, cut=14)
    p.add(line([(7, 15), (7, 13)]), ramp_hex("#3a2a24", "#4a3830", "#5e4a3c", "#74604e", "#8a7662"), base=2)
    for x, y in ((3, 8), (9, 6), (11, 10), (5, 11), (7, 8)):
        stamp(p, ["32", "21"], x, y, B)
        p.px(x, y, B[4])
        p.px(x + 2, y + 1, B[2])
    return p


def arid_garden() -> Plant:
    """Dry-climate shrub: warm sage and olive lance leaves on woody branches, sun-bleached tan
    stalks, dangling red chilies and a white cotton boll as focal points."""
    p = Plant()
    SAGE = green("#98a64a", sat=0.04)
    OLIVE = green("#6c8c2c", sat=0.04)
    WOOD = ramp_hex("#4e3a26", "#664c32", "#7e6040", "#967650", "#ac8c62")
    TAN = ramp_hex("#7a5e3a", "#967648", "#b2925a", "#c8aa70", "#dcc28a")
    CH = ramp_hex("#6a0e0a", "#981a12", "#cc2a1c", "#e8503a", "#f68a6a")
    BOLL = ramp_hex("#a8a49c", "#ccc8be", "#e4e0d8", "#f2f0ea", "#fcfcf8")
    HUSK = ramp_hex("#4a3424", "#62442e", "#7a583a", "#94704c", "#aa8660")
    # sun-bleached dry stalks: one tall on the left, one short on the right
    p.add(line([(6, 15), (4, 8), (2, 1)]), TAN, base=3, cast=False)
    p.px(1, 0, TAN[4])
    p.px(3, 0, TAN[2])
    p.add(line([(9, 15), (13, 10), (15, 6)]), TAN, base=3, cast=False)
    p.px(15, 5, TAN[4])
    # woody branches, leaning right where the cotton boll sits
    for ctrl in ([(7, 15), (4, 11), (2, 7)], [(8, 15), (11, 12), (13, 9)], [(7, 15), (8, 9), (10, 4)]):
        p.add(line(ctrl), WOOD, base=2)
    # clear, separate lance leaves (base -> tip, palette, depth), deliberately asymmetric
    leaves = [((5, 12), (2, 13), OLIVE, 0), ((4, 10), (1, 9), SAGE, -1), ((2, 7), (1, 4), SAGE, 0),
              ((3, 8), (5, 6), OLIVE, -1), ((10, 12), (13, 14), OLIVE, 0), ((12, 10), (15, 10), SAGE, -1),
              ((13, 9), (14, 6), SAGE, 0), ((8, 10), (5, 8), OLIVE, 0), ((9, 7), (12, 6), SAGE, 0),
              ((9, 6), (7, 3), OLIVE, -1)]
    for a, b, rmp, d in leaves:
        leaf(p, a, b, 2.6, rmp, "lance", depth=d)
    # red chilies dangling in the open, each with a green cap
    for (x, y, shape) in ((3, 9, ["G", "4", "3", "2", "1"]), (11, 7, [".G", ".4", ".3", ".2", "1."]),
                          (6, 10, ["G.", "4.", "3.", ".1"]), (14, 11, ["G", "4", "3", "1"])):
        stamp(p, shape, x, y, CH)
    # cotton boll on the leaning central branch
    stamp(p, [".444.", "44434", "34332", ".H.H."], 9, 0, BOLL, {"H": (HUSK, 1)})
    return p


def tropical_garden() -> Plant:
    p = Plant()
    G = green("#2a7a2a", sat=0.04)
    GOLD = ramp_hex("#9a5a1a", "#c07a22", "#e0a830", "#f0c454", "#f8de8a")
    PG = green("#4e7e56", sat=-0.04)
    R = ramp_hex("#6a1010", "#921a1a", "#c02a2a", "#e04a3a", "#f88a6a")
    # big broad paddle leaves fanning out
    for ctrl, w, d in (([(7, 15), (2, 6), (0, 2)], 4.4, -1), ([(8, 15), (13, 6), (15, 1)], 4.4, -1),
                       ([(7, 15), (6, 6), (7, 0)], 4.0, 0), ([(7, 15), (3, 11), (0, 12)], 3.6, 0),
                       ([(8, 15), (12, 11), (15, 12)], 3.6, 0)):
        curve_leaf(p, ctrl, w, G, "ovate", depth=d, vein=4, vein_span=(0.05, 0.85))
    # small pineapple at the base
    for (dx, dy) in ((-2, -3), (2, -3), (0, -4), (-1, -4), (1, -4)):
        curve_leaf(p, [(9, 12), (9 + dx, 12 + dy)], 1.6, PG, "blade")
    stamp(p, [".343.", "34343", "43434", ".232."], 7, 12, GOLD)
    # coffee cherries clustered on a twig
    for (x, y) in ((2, 8), (12, 7), (4, 4)):
        stamp(p, ["32.", "213"], x, y, R)
        p.px(x, y, R[4])
    return p


def marsh_garden() -> Plant:
    """Reedy wetland tuft: tall reeds, nodding rice sprays, a mint sprig and cranberries at the foot."""
    p = Plant()
    G = green("#4a8a5a", sat=-0.04)
    MINT = green("#4aa84a")
    RICE = ramp_hex("#9a8a4a", "#bcaa62", "#d6c87e", "#e8d8a0", "#f6ecc4")
    STK = ramp_hex("#5a6a2a", "#76843a", "#94a04e", "#aeb866", "#c6ce84")
    CR = ramp_hex("#6a0a18", "#920e22", "#b81a2a", "#d8404a", "#f08a8a")
    # rice stalks first (behind the reeds), each nodding over at the top
    for (cx, d, top) in ((3, 1, 1), (12, -1, 0)):
        p.add(line([(cx, 14), (cx, top + 1), (cx + d, top)]), STK, base=3, cast=False)
        spray = line([(cx + d, top), (cx + d * 3, top + 2), (cx + d * 3, top + 6)])
        for j, (x, y) in enumerate(spray):
            p.px(x, y, RICE[3 if j % 2 else 2])
            if j % 2:
                p.px(x - d, y + 1, RICE[1])
    # reeds
    for i, (x, top, d) in enumerate(((1, 3, 1), (5, 2, -1), (6, 5, 1), (9, 3, 1), (10, 6, -1), (14, 4, -1),
                                     (8, 7, -1))):
        curve_leaf(p, [(x, 15), (x, (15 + top) / 2), (x + d, top)], 1.5, G, "blade", depth=-1 if i % 2 else 0)
    # mint sprig at the front
    p.add(rect(7, 8, 7, 15), ramp_hex("#4a5a34", "#5e7040", "#74884c", "#8aa05a", "#a2b86c"), base=2)
    for y in (13, 10):
        leaf(p, (7, y), (5, y - 1), 2.4, MINT, "ovate")
        leaf(p, (7, y), (9, y - 1), 2.4, MINT, "ovate", depth=-1)
    leaf(p, (7, 8), (7, 6), 2.2, MINT, "ovate")
    # cranberries on low runners
    run = ramp_hex("#4a2a22", "#62382c", "#7a4a3a", "#94604c", "#a87660")
    p.add(line([(7, 15), (3, 14), (0, 14)]), run, base=2)
    p.add(line([(8, 15), (12, 14), (15, 14)]), run, base=2)
    for (x, y) in ((1, 12), (12, 12), (10, 13), (3, 12)):
        stamp(p, ["32", "21"], x, y, CR)
        p.px(x, y, CR[4])
    return p


GARDEN_FNS = {
    "meadow_garden": meadow_garden, "woodland_garden": woodland_garden, "highland_garden": highland_garden,
    "arid_garden": arid_garden, "tropical_garden": tropical_garden, "marsh_garden": marsh_garden,
}


def garden_textures() -> dict[str, Sprite]:
    return {k: fn().render() for k, fn in GARDEN_FNS.items()}
