"""Hardware lane: feast blocks (cakes, pies, pizza).

Cakes reuse vanilla ``block/cake`` / ``block/cake_sliceN`` (auto-UV): visible texels are
top 1..14 x 1..14, side and inner rows 8..15 (cols 1..14), bottom 1..14. Unused texels are
filled with matching material so break particles look right.

Pies and pizza use our own template models ``template_<kind>_<n>`` (n = quarters eaten):
a 14px disc approximated by four stacked row-boxes per quarter. Quarters are removed
north-east first, then south-east, then south-west (north-west is the last piece).
Faces: ``#top`` (one disc picture mapped by absolute x/z), ``#side`` (outer crust, bottom
rows of the texture), ``#inner`` (cut faces, crust walls at columns 1 and 14, centre at 8),
``#bottom``.
"""
from __future__ import annotations

from .core import Color, Sprite, hexc, shade
from .hardware_mdl import Paint, _num, display
from .render3d import fit_display

# --------------------------------------------------------------------------- geometry

# half-width of the disc for pixel row z (0..15); rows outside -> 0
DISC_HALF = {1: 3, 2: 5, 3: 6, 4: 6, 5: 7, 6: 7, 7: 7, 8: 7, 9: 7, 10: 7, 11: 6, 12: 6, 13: 5, 14: 3}
# north-half row boxes (z0, z1, half-width); the south half mirrors them
ROWS_NORTH = [(1, 2, 3), (2, 3, 5), (3, 5, 6), (5, 8, 7)]

QUARTERS = ("ne", "se", "sw", "nw")        # removal order: first eaten first
EATEN_ORDER = ["ne", "se", "sw"]


def in_disc(x: int, z: int) -> bool:
    h = DISC_HALF.get(z, 0)
    return h > 0 and 8 - h <= x < 8 + h


def _quarter_boxes(q: str):
    """Row boxes (x1, z1, x2, z2) covering quarter ``q``."""
    out = []
    for z0, z1, hw in ROWS_NORTH:
        if q[0] == "s":
            z0, z1 = 16 - z1, 16 - z0
        if q[1] == "e":
            x1, x2 = 8, 8 + hw
        else:
            x1, x2 = 8 - hw, 8
        out.append((x1, z0, x2, z1))
    return out


def _uv(d, x1, y1, z1, x2, y2, z2):
    return {
        "down": [x1, 16 - z2, x2, 16 - z1],
        "up": [x1, z1, x2, z2],
        "north": [16 - x2, 16 - y2, 16 - x1, 16 - y1],
        "south": [x1, 16 - y2, x2, 16 - y1],
        "west": [z1, 16 - y2, z2, 16 - y1],
        "east": [16 - z2, 16 - y2, 16 - z1, 16 - y1],
    }[d]


def template_model(kind: str, eaten: int) -> dict:
    h = {"pie": 4, "pizza": 1.5}[kind]
    gone = set(EATEN_ORDER[:eaten])
    present = [q for q in QUARTERS if q not in gone]
    els = []
    for q in ("nw", "ne", "sw", "se"):
        if q not in present:
            continue
        # neighbours across the two cut planes
        ew_nb = q[0] + ("w" if q[1] == "e" else "e")         # across x = 8
        ns_nb = ("s" if q[0] == "n" else "n") + q[1]         # across z = 8
        boxes = _quarter_boxes(q)
        for i, (x1, z1, x2, z2) in enumerate(boxes):
            faces = {}
            for d in ("down", "up", "north", "south", "west", "east"):
                tex = "#side"
                if d == "up":
                    tex = "#top"
                elif d == "down":
                    tex = "#bottom"
                elif d in ("west", "east"):
                    on_cut = (d == "west" and x1 == 8) or (d == "east" and x2 == 8)
                    if on_cut:
                        if ew_nb in present:
                            continue
                        tex = "#inner"
                else:
                    on_cut = (d == "north" and z1 == 8) or (d == "south" and z2 == 8)
                    if on_cut:
                        if ns_nb in present:
                            continue
                        tex = "#inner"
                    else:
                        # step faces between row boxes: only the face pointing away from the
                        # centre is (partly) visible; the inward one is always buried
                        towards_centre = (d == "south") if q[0] == "n" else (d == "north")
                        if towards_centre:
                            continue
                f = {"uv": [_num(c) for c in _uv(d, x1, 0, z1, x2, h, z2)], "texture": tex}
                if d == "down":
                    f["cullface"] = "down"
                faces[d] = f
            els.append({"from": [_num(x1), 0, _num(z1)], "to": [_num(x2), _num(h), _num(z2)], "faces": faces})
    model = {
        "parent": "minecraft:block/block",
        "textures": {"particle": "#top"},
        "elements": els,
    }
    full = template_elements_bbox(kind)
    model["display"] = display(gui=fit_display(full, [30, 225, 0], extent=15.0, max_scale=1.0),
                               fixed={"rotation": [-90, 0, 0], "translation": [0, 0, _num(-(16 - h) * 0.375)],
                                      "scale": [0.75, 0.75, 0.75]},
                               ground={"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.4, 0.4, 0.4]})
    return model


def template_elements_bbox(kind: str) -> list[dict]:
    h = {"pie": 4, "pizza": 1.5}[kind]
    return [{"from": [1, 0, 1], "to": [15, h, 15]}]


# --------------------------------------------------------------------------- palettes

CRUST = [hexc(c) for c in ("#6a3a14", "#8a521e", "#a86c2a", "#c88a3c", "#e0a856", "#ecc070", "#f6d894")]
DOUGH = [hexc(c) for c in ("#7a4a1c", "#9a6226", "#b87c34", "#d29a48", "#e8b060", "#f2c87e", "#fadc9e")]


FILLINGS = {
    # id: ramp (0 deep shadow .. 5 glint), glossy
    "apple_pie": (["#8a5a1c", "#a87a2c", "#e0c470", "#f2e09a", "#faf0c4", "#fffbe8"], False),
    "cherry_pie": (["#3a0610", "#5e0a18", "#8a1424", "#b01e2e", "#d8404a", "#ffb0b0"], True),
    "berry_pie": (["#1a0e30", "#2e1a52", "#45287a", "#5e3aa0", "#8a64c8", "#d8c8ff"], True),
}


def _fr(fid):
    ramp_, glossy = FILLINGS[fid]
    return [hexc(c) for c in ramp_], glossy


# --------------------------------------------------------------------------- pies


STRIPS = ((4, 5), (10, 11))      # 2px lattice strips (both directions)


def _strip_index(v: int):
    for i, (a, b) in enumerate(STRIPS):
        if v in (a, b):
            return i, v == a           # (strip number, is first/lit pixel)
    return None, False


def _rim(x, z) -> bool:
    return in_disc(x, z) and any(not in_disc(x + dx, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def pie_top(fid: str) -> Sprite:
    F, glossy = _fr(fid)
    p = Paint(seed=fid + "_top")
    for z in range(16):
        for x in range(16):
            if not in_disc(x, z):
                continue
            if _rim(x, z):
                lit = x + z <= 15
                bump = (x + z) % 2 == 0
                p.px(x, z, CRUST[(6 if bump else 5) if lit else (4 if bump else 3)])
                continue
            vi, vfirst = _strip_index(x)
            hi, hfirst = _strip_index(z)
            if vi is not None and hi is not None:
                v_on_top = (vi + hi) % 2 == 0          # basket weave
                first = vfirst if v_on_top else hfirst
                c = CRUST[6] if first else CRUST[4]
                p.px(x, z, c)
            elif vi is not None:
                # vertical strip: lit left column, shaded right; shadow where it dives under
                c = CRUST[5] if vfirst else CRUST[3]
                for (a, b) in STRIPS:
                    hi2 = STRIPS.index((a, b))
                    if (vi + hi2) % 2 == 1 and z in (a - 1, b + 1):
                        c = CRUST[2]
                p.px(x, z, c)
            elif hi is not None:
                c = CRUST[5] if hfirst else CRUST[3]
                for (a, b) in STRIPS:
                    vi2 = STRIPS.index((a, b))
                    if (vi2 + hi) % 2 == 0 and x in (a - 1, b + 1):
                        c = CRUST[2]
                p.px(x, z, c)
            else:
                # filling window: shadow along strips/rim to the top-left, glint top-left inside
                shadow = _strip_index(x - 1)[0] is not None or _strip_index(z - 1)[0] is not None \
                    or _rim(x - 1, z) or _rim(x, z - 1)
                c = F[1] if shadow else F[3]
                if not shadow and ((x * 5 + z * 3) % 7 == 0):
                    c = F[2]
                if not shadow and ((x + z * 2) % 9 == 4):
                    c = F[4]
                p.px(x, z, c)
    # glints on glossy fillings, sugar sparkle on the lattice for apple
    if glossy:
        for (x, z) in ((7, 7), (3, 8), (8, 3), (12, 7), (7, 12), (12, 12)):
            if in_disc(x, z) and not _rim(x, z):
                p.px(x, z, F[5])
    else:
        for (x, z) in ((8, 7), (12, 8), (7, 12), (3, 7)):
            if in_disc(x, z) and not _rim(x, z):
                p.px(x, z, F[5])
    return p.s


def pie_inner(fid: str) -> Sprite:
    F, glossy = _fr(fid)
    p = Paint(seed=fid + "_inner")

    def cell(x, y):
        yy = 12 + (y % 4)            # rows 12..15 are used by the 4px-tall pie; repeated above
        if x in (0, 15):
            return CRUST[3]
        if yy == 12:
            return CRUST[5] if x % 3 else CRUST[6]       # lattice / top crust
        if yy == 15:
            return CRUST[3] if x % 4 else CRUST[2]       # bottom crust
        if x in (1, 14):
            return CRUST[4]                              # crust wall at the rim
        if yy == 13:
            c = F[3] if (x * 3) % 5 else F[4]
            if glossy and x % 5 == 2:
                c = F[5]
        else:
            c = F[2] if (x * 7) % 5 else F[1]
        return c

    p.region(0, 0, 16, 16, cell)
    return p.s


def pie_side() -> Sprite:
    p = Paint(seed="pie_side")

    def cell(x, y):
        yy = 12 + (y % 4)
        if yy == 12:   # crimped rim
            return CRUST[6] if x % 2 == 0 else CRUST[5]
        if yy == 13:
            return CRUST[5] if x % 2 == 0 else CRUST[4]
        if yy == 14:
            return CRUST[4] if (x + 1) % 4 else CRUST[3]
        return CRUST[2] if x % 3 else CRUST[1]

    p.region(0, 0, 16, 16, cell)
    return p.s


def pie_bottom() -> Sprite:
    p = Paint(seed="pie_bottom")
    p.noise(0, 0, 16, 16, CRUST[1:5], 1, 0.4)
    for (x, y) in ((4, 5), (10, 3), (7, 11), (12, 9)):
        p.px(x, y, CRUST[0])
    return p.s


# --------------------------------------------------------------------------- pizza

SAUCE = [hexc(c) for c in ("#7a140e", "#a01e14", "#c8281e", "#dc4030")]
CHEESE = [hexc(c) for c in ("#d8a83a", "#e8c048", "#f2d060", "#f8e08a", "#fdf0c0")]
BASIL = [hexc(c) for c in ("#1e5a18", "#2e7a22", "#3a8a2a", "#5aaa3a")]


MOZZ = [hexc(c) for c in ("#d8b860", "#f0dca0", "#fbf0cc", "#fffaf0")]


def pizza_top() -> Sprite:
    p = Paint(seed="pizza_top")
    for z in range(16):
        for x in range(16):
            if not in_disc(x, z):
                continue
            if _rim(x, z):
                lit = x + z < 16
                c = DOUGH[5] if lit else DOUGH[3]
                if (x * 7 + z * 3) % 6 == 0:
                    c = DOUGH[2]          # charred blister
                p.px(x, z, c)
                continue
            near = any(_rim(x + dx, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            c = SAUCE[1] if near else SAUCE[2]
            if not near and (x * 3 + z * 5) % 8 == 0:
                c = SAUCE[3]
            p.px(x, z, c)
    # torn mozzarella blobs (lit top-left, shadow bottom-right)
    blobs = [(3, 5, 2), (7, 3, 2), (10, 6, 3), (5, 8, 3), (11, 11, 2), (6, 12, 2), (2, 9, 1), (9, 9, 1), (12, 3, 1)]
    for (bx, bz, sz) in blobs:
        for dz in range(sz):
            for dx in range(sz):
                if sz == 3 and (dx, dz) in ((0, 0), (2, 2)):
                    continue
                x, z = bx + dx, bz + dz
                if in_disc(x, z) and not _rim(x, z):
                    c = MOZZ[3] if dx + dz == 0 else MOZZ[1] if dx + dz >= sz else MOZZ[2]
                    p.px(x, z, c)
        sx, sz2 = bx + sz, bz + sz - 1
        if in_disc(sx, sz2) and not _rim(sx, sz2):
            p.px(sx, sz2, MOZZ[0])           # melted edge shadow
    # basil leaves: 3px, lighter vein
    for (x, z, flip) in ((8, 5, False), (4, 11, True), (12, 8, True), (8, 12, False), (3, 3, False)):
        pts = [(x, z), (x + 1, z), (x + 1, z + 1)] if not flip else [(x + 1, z), (x, z), (x, z + 1)]
        for i, (lx, lz) in enumerate(pts):
            if in_disc(lx, lz) and not _rim(lx, lz):
                p.px(lx, lz, (BASIL[3], BASIL[2], BASIL[1])[i])
    return p.s


def pizza_inner() -> Sprite:
    p = Paint(seed="pizza_inner")

    def cell(x, y):
        yy = 14 + (y % 2)
        if x in (0, 1, 14, 15):
            return DOUGH[4] if yy == 14 else DOUGH[3]       # puffy crust ends
        if yy == 14:
            return (CHEESE[2], SAUCE[2], CHEESE[3], CHEESE[2], SAUCE[1])[x % 5]
        return DOUGH[5] if x % 3 else DOUGH[4]

    p.region(0, 0, 16, 16, cell)
    return p.s


def pizza_side() -> Sprite:
    p = Paint(seed="pizza_side")

    def cell(x, y):
        yy = 14 + (y % 2)
        if yy == 14:
            return DOUGH[5] if (x * 3) % 7 else DOUGH[2]
        return DOUGH[3] if x % 3 else DOUGH[2]

    p.region(0, 0, 16, 16, cell)
    return p.s


def pizza_bottom() -> Sprite:
    p = Paint(seed="pizza_bottom")
    p.noise(0, 0, 16, 16, DOUGH[2:6], 1, 0.45)
    for (x, y) in ((3, 4), (9, 2), (12, 8), (6, 12), (10, 13), (4, 9)):
        p.px(x, y, DOUGH[0])
    return p.s


# --------------------------------------------------------------------------- cakes

CAKES = {
    "chocolate_cake": {
        "sponge": ["#2e140a", "#40200f", "#5a2e1a", "#6e3a22", "#84482c"],
        "frost": ["#1a0a04", "#2a1408", "#3a1a0a", "#52281a", "#6e3a26", "#8a5038"],
        "filling": ["#c89a7a", "#e0bca0"],
        "deco": "#f8f0e8",
    },
    "carrot_cake": {
        "sponge": ["#7a4618", "#9a5c24", "#b8732f", "#c8803a", "#d89650"],
        "frost": ["#bfb6a6", "#d8d0c0", "#e8e2d6", "#f2eee4", "#f8f4ec", "#ffffff"],
        "filling": ["#e8e2d6", "#f8f4ec"],
        "deco": "#e8702a",
    },
}


def _cr(fid):
    c = CAKES[fid]
    return ([hexc(x) for x in c["sponge"]], [hexc(x) for x in c["frost"]], [hexc(x) for x in c["filling"]],
            hexc(c["deco"]))


def cake_top(fid: str) -> Sprite:
    S, F, FL, D = _cr(fid)
    p = Paint(seed=fid + "_top")
    choc = fid == "chocolate_cake"

    def cell(x, y):
        rim = x in (1, 14) or y in (1, 14)
        if rim:
            return F[3] if (x == 1 or y == 1) else F[1]
        r = max(abs(x - 7.5), abs(y - 7.5))
        return F[3] if r < 2 else F[2] if (x + y) % 5 else F[3]

    p.region(0, 0, 16, 16, cell)
    if choc:
        # glossy ganache sheen in the top-left, then three continuous white drizzle lines
        for (x, y) in ((3, 3), (4, 3), (3, 4), (5, 3), (3, 5), (4, 4)):
            p.px(x, y, F[4])
        drizzle = hexc(CAKES[fid]["deco"])
        for k in (10, 15, 20):
            for x in range(2, 14):
                y = k - x
                if 2 <= y <= 13:
                    p.px(x, y, drizzle)
                    if 2 <= y + 1 <= 13 and (x + k) % 3 == 0:
                        p.px(x, y + 1, shade(drizzle, -0.2))    # drop shadow
        for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13), (7, 2), (2, 7), (13, 8), (8, 13)):
            p.px(x, y, F[5])          # piped ganache rosettes along the rim
    else:
        # cream-cheese swirl, ring of tiny piped carrots, cinnamon dusting in the centre
        for (x, y) in ((5, 5), (6, 5), (9, 10), (10, 10), (5, 9), (10, 6)):
            p.px(x, y, F[1])
        carrot, carrot_d, leaf = D, shade(D, -0.18), hexc("#4a8a2a")
        for (x, y) in ((3, 4), (11, 3), (3, 11), (11, 11), (7, 2), (2, 7), (12, 7), (7, 12)):
            p.px(x, y, carrot)
            p.px(x + 1, y + 1, carrot_d)
            p.px(x + 1, y, leaf)
        for (x, y) in ((7, 7), (8, 8), (8, 7), (7, 8)):
            p.px(x, y, hexc("#c08848") if (x + y) % 2 else hexc("#a8703a"))
    return p.s


def cake_side(fid: str) -> Sprite:
    S, F, FL, D = _cr(fid)
    p = Paint(seed=fid + "_side")
    choc = fid == "chocolate_cake"
    # sponge everywhere (rows 0..7 are only used by particles)
    p.noise(0, 0, 16, 16, S, 3, 0.4)
    # vertical light falloff: lit left
    for y in range(16):
        p.px(1, y, shade(p.s.get(1, y), 0.04))
    # frosting top band rows 8-9 with drips of uneven length
    drips = {1: 11, 2: 10, 4: 12, 5: 10, 7: 11, 9: 13, 10: 10, 12: 11, 13: 10, 14: 11}
    for x in range(16):
        bottom = drips.get(x, 9)
        for y in range(8, bottom + 1):
            c = F[3] if y == 8 else F[2]
            if y == bottom and bottom > 9:
                c = F[1]       # drip tip shadow
            p.px(x, y, c)
    if choc:
        # white drizzle dripping over the ganache on a few columns
        for (x, y) in ((3, 8), (3, 9), (8, 8), (8, 9), (8, 10), (11, 8), (11, 9)):
            p.px(x, y, hexc(CAKES[fid]["deco"]))
        # filling layer
        for x in range(16):
            if x not in drips or drips[x] < 12:
                p.px(x, 13, FL[0] if x % 3 else FL[1])
    else:
        # carrot flecks in the sponge + cream-cheese middle layer
        for x in range(16):
            p.px(x, 13, FL[1] if x % 4 else FL[0])
        for (x, y) in ((2, 11), (6, 12), (11, 12), (4, 15), (9, 14), (13, 15), (7, 15), (1, 14)):
            p.px(x, y, D)
        for (x, y) in ((5, 14), (12, 14), (10, 11)):
            p.px(x, y, hexc("#6a3a14"))           # walnut
    # bottom edge baked darker
    for x in range(16):
        p.px(x, 15, shade(p.s.get(x, 15), -0.06))
    return p.s


def cake_inner(fid: str) -> Sprite:
    S, F, FL, D = _cr(fid)
    p = Paint(seed=fid + "_inner")
    choc = fid == "chocolate_cake"
    p.noise(0, 0, 16, 16, S, 2, 0.5)
    for x in range(16):
        p.px(x, 8, F[3] if x % 4 else F[4])
        p.px(x, 9, F[2])
        p.px(x, 12, FL[0] if x % 3 else FL[1])
        if x in (0, 1, 14, 15):
            for y in range(10, 16):
                p.px(x, y, F[2] if not (y == 15) else F[1])     # frosted outer wall
    # crumb texture: lighter air pockets
    for (x, y) in ((3, 10), (7, 11), (11, 10), (5, 14), (9, 13), (12, 14), (2, 13)):
        p.px(x, y, S[4])
    if not choc:
        for (x, y) in ((4, 11), (8, 14), (10, 10), (6, 13), (12, 11)):
            p.px(x, y, D)
    else:
        for (x, y) in ((4, 11), (10, 14)):
            p.px(x, y, F[0])      # chocolate chips
    return p.s


def cake_bottom(fid: str) -> Sprite:
    S, F, FL, D = _cr(fid)
    p = Paint(seed=fid + "_bottom")
    p.noise(0, 0, 16, 16, S[:4], 1, 0.4)
    for x in range(16):
        p.px(x, 1, S[2])
        p.px(1, x, S[2])
    return p.s


# --------------------------------------------------------------------------- registry


def all_textures() -> dict[str, Sprite]:
    out: dict[str, Sprite] = {}
    for fid in CAKES:
        out[f"{fid}_top"] = cake_top(fid)
        out[f"{fid}_side"] = cake_side(fid)
        out[f"{fid}_inner"] = cake_inner(fid)
        out[f"{fid}_bottom"] = cake_bottom(fid)
    for fid in FILLINGS:
        out[f"{fid}_top"] = pie_top(fid)
        out[f"{fid}_inner"] = pie_inner(fid)
    out["pizza_top"] = pizza_top()
    out["pizza_inner"] = pizza_inner()
    out["pie_side"] = pie_side()
    out["pie_bottom"] = pie_bottom()
    out["pizza_side"] = pizza_side()
    out["pizza_bottom"] = pizza_bottom()
    return out


def all_templates() -> dict[str, dict]:
    return {f"template_{k}_{n}": template_model(k, n) for k in ("pie", "pizza") for n in range(4)}


# texture variables each feast's block models will bind (for previews / validation)
def feast_vars(fid: str, kind: str) -> dict[str, str]:
    ns = "sprout_and_soil:block/"
    if kind == "cake":
        return {"top": ns + f"{fid}_top", "side": ns + f"{fid}_side", "inside": ns + f"{fid}_inner",
                "bottom": ns + f"{fid}_bottom", "particle": ns + f"{fid}_side"}
    return {"top": ns + f"{fid}_top", "inner": ns + f"{fid}_inner", "side": ns + f"{kind}_side",
            "bottom": ns + f"{kind}_bottom", "particle": ns + f"{fid}_top"}
