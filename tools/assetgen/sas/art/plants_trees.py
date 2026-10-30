"""Fruit trees: tileable fruiting leaves (4 ages) and saplings.

Leaves are ``cube_all`` cutout textures.  Every age of a tree shares one base pattern (a wrapped
leaf-cell texture with transparent holes); age 1 adds blossoms, age 2 small unripe fruit and age 3
ripe fruit clusters at the *same* spots, so the block visibly ripens in place.  Decorations never
cross the texture edge, which keeps the 3x3 tiling seamless.
"""
from __future__ import annotations

from .core import Color, Sprite, hexc, mix, shade
from .plants_kit import Plant, disc, fruit, h, jitter_seeds, leaf_cells, line, poisson_seeds, rect
from .plants_lib import curve_leaf, stamp


def ramp_hex(*cols) -> list[Color]:
    return [hexc(c) for c in cols]


def leaf_ramp(dark: str, light: str) -> list[Color]:
    d, l_ = hexc(dark), hexc(light)
    return [shade(d, -0.13, hue_shift=0.07), d, mix(d, l_, 0.55), l_, shade(l_, 0.08, hue_shift=0.05)]


# log palettes (dark -> light) for sapling trunks, matched to the vanilla log each tree uses
LOGS = {
    "minecraft:oak_log": ramp_hex("#3c2c18", "#54401f", "#6c522c", "#86683a", "#9c7c48"),
    "minecraft:birch_log": ramp_hex("#3a3830", "#8a887c", "#c8c8bc", "#e2e2d8", "#f4f4ee"),
    "minecraft:dark_oak_log": ramp_hex("#241a0e", "#33261a", "#443320", "#56422a", "#6a5434"),
    "minecraft:cherry_log": ramp_hex("#24141e", "#33202a", "#462c38", "#5a3a48", "#704a5a"),
    "minecraft:jungle_log": ramp_hex("#3a2c12", "#503e18", "#66501e", "#7c6226", "#94782e"),
    "minecraft:acacia_log": ramp_hex("#3e3a32", "#565048", "#6c655a", "#847c70", "#9c9488"),
}

# --------------------------------------------------------------------------- per-tree art


class TreeArt:
    """Leaf texture style + blossom/fruit decorations for one fruit tree."""

    def __init__(self, tid: str, leaf_colors, blossom: str, fruit_colors, log: str, *, cell=2.6, stretch=(1.0, 1.0),
                 holes=0.27, gloss=False, fruit_kind="round", spots=None, salt=0):
        self.id = tid
        self.ramp = leaf_ramp(*leaf_colors[:2])
        self.blossom = hexc(blossom)
        self.fruit_colors = [hexc(c) for c in fruit_colors]
        self.log = LOGS.get(log, LOGS["minecraft:oak_log"])
        self.cell, self.stretch, self.holes, self.gloss = cell, stretch, holes, gloss
        self.kind = fruit_kind
        self.salt = salt or sum(map(ord, tid)) * 13
        # decoration anchors (top-left of each fruit / blossom); kept away from the edges
        self.spots = spots or SPOT_SETS[sum(map(ord, tid)) % len(SPOT_SETS)]


# irregular decoration layouts (4 spots, >=1px from the edges so tiling stays seamless)
SPOT_SETS = [
    [(2, 2), (10, 4), (4, 10), (12, 12)],
    [(3, 1), (11, 2), (8, 8), (1, 11)],
    [(1, 4), (9, 1), (12, 9), (5, 11)],
    [(4, 2), (12, 5), (2, 9), (9, 11)],
]


_BASE_CACHE: dict = {}


def _banding(holes: set) -> float:
    """How strongly holes line up in rows/columns/diagonals when tiled (lower is better)."""
    import statistics

    def spread(key):
        counts = [0] * 16
        for q in holes:
            counts[key(q) % 16] += 1
        # use 2-wide bands, which is what the eye picks up in a tiled wall
        bands = [counts[i] + counts[(i + 1) % 16] for i in range(16)]
        return statistics.pstdev(bands)

    return (spread(lambda q: q[1]) + spread(lambda q: q[0]) + spread(lambda q: q[0] + q[1])
            + spread(lambda q: q[0] - q[1]))


def base_leaves(t: TreeArt) -> tuple[dict, set]:
    """Tileable leaf-cell tones + hole pixels; the seed layout with the least visible banding wins."""
    if t.id not in _BASE_CACHE:
        best = None
        for k in range(10):
            tones_, holes = _base_leaves(t, t.salt + k * 1009)
            score = _banding(holes)
            if best is None or score < best[0]:
                best = (score, tones_, holes)
        _BASE_CACHE[t.id] = best[1:]
    tones_, holes = _BASE_CACHE[t.id]
    return dict(tones_), set(holes)


def _base_leaves(t: TreeArt, salt: int) -> tuple[dict, set]:
    """Tileable leaf-cell tones + set of hole pixels (~``t.holes`` of the block, in leaf-sized gaps)."""
    seeds = poisson_seeds(16, 16, t.cell, salt)
    allpx = {(x, y) for x in range(16) for y in range(16)}
    tones_ = leaf_cells(allpx, seeds, salt=salt, wrap=(16, 16), stretch=t.stretch, vary=0.3, grad=1.6)
    # cell ownership again (cheap): nearest seed with wrap
    def owner(x, y):
        best, bi = 1e9, 0
        for i, (qx, qy) in enumerate(seeds):
            dx = (x + 0.5 - qx + 8) % 16 - 8
            dy = (y + 0.5 - qy + 8) % 16 - 8
            d = (dx * t.stretch[0]) ** 2 + (dy * t.stretch[1]) ** 2
            if d < best:
                best, bi = d, i
        return bi
    own = {q: owner(*q) for q in allpx}
    order = sorted(range(len(seeds)), key=lambda i: h(i, 3, salt + 77))
    holes: set = set()
    target = t.holes * 256
    chosen: list[int] = []

    def wdist(a, b):
        dx = (seeds[a][0] - seeds[b][0] + 8) % 16 - 8
        dy = (seeds[a][1] - seeds[b][1] + 8) % 16 - 8
        return (dx * dx + dy * dy) ** 0.5

    # scatter hole cells evenly: each new hole keeps its distance from the previous ones
    for min_d in (t.cell * 1.9, t.cell * 1.5, t.cell * 1.1):
        for i in order:
            if len(holes) >= target * 0.95:
                break
            if i in chosen or any(wdist(i, j) < min_d for j in chosen):
                continue
            chosen.append(i)
            holes |= {q for q, o in own.items() if o == i}
    # no lonely single opaque pixels
    for (x, y) in list(allpx - holes):
        nb = [((x + dx) % 16, (y + dy) % 16) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if sum(n in holes for n in nb) >= 4:
            holes.add((x, y))
    # the pixel right below a hole catches the light of the open sky
    for (x, y) in list(allpx - holes):
        if (x, (y - 1) % 16) in holes and tones_[(x, y)] < 3:
            tones_[(x, y)] += 1
    return tones_, holes


def leaves_texture(t: TreeArt, age: int) -> Sprite:
    p = Plant(wrap=True)
    tones_, holes = base_leaves(t)
    body = {q: v for q, v in tones_.items() if q not in holes}
    p.fixed(body, t.ramp)
    if t.gloss:
        for (x, y), v in body.items():
            if v == 4 and h(x, y, t.salt + 5) < 0.55:
                p.px(x, y, shade(t.ramp[4], 0.1))
    if t.kind == "banana":
        _banana_leaves(p, t)
    if age == 1:
        _blossoms(p, t)
    elif age >= 2:
        _fruit(p, t, ripe=age == 3)
    return p.render()


def _blossoms(p: Plant, t: TreeArt) -> None:
    pc = t.blossom
    if t.kind == "banana":
        # a single big purple-red banana bud hanging on a stalk
        BUD = [shade(pc, -0.2), shade(pc, -0.1), pc, shade(pc, 0.1), shade(pc, 0.2)]
        for (x, y) in t.spots[:2]:
            rows = [".s.", ".s.", "443", "432", "321", ".1."]
            _rim(p, rows, x, y, t.ramp[0])
            stamp(p, rows, x, y, BUD, {"s": hexc("#6a7a3a")})
        return
    light = shade(pc, 0.06) if pc[0] + pc[1] + pc[2] < 700 else pc
    mid = shade(pc, -0.1)
    dark = shade(pc, -0.22)
    centre = hexc("#e8c84a") if t.id not in ("mango", "avocado", "olive") else shade(pc, -0.3)
    for i, (x, y) in enumerate(t.spots):
        if t.id in ("mango", "avocado", "olive"):
            # small clustered flower panicles
            for dx, dy, c in ((0, 0, light), (1, 0, mid), (0, 1, mid), (1, 1, dark), (1, -1, light)):
                p.px(x + dx, y + dy, c)
            continue
        cx, cy = x + 1, y + 1
        p.px(cx, cy - 1, light)
        p.px(cx - 1, cy, light)
        p.px(cx + 1, cy, mid)
        p.px(cx, cy + 1, dark)
        p.px(cx, cy, centre)
        if i % 2 == 0:
            # second smaller blossom beside it
            p.px(cx + 2, cy + 1, mid)
            p.px(cx + 2, cy + 2, dark)


def _fruit(p: Plant, t: TreeArt, ripe: bool) -> None:
    fc = t.fruit_colors
    main = fc[0]
    if ripe:
        R = fruit(main)
    else:
        R = ramp_hex("#3a5a1a", "#5a7e24", "#86a834", "#acc84e", "#d0e27a")
    stem_c = hexc("#5a4020")
    spots = t.spots
    k = t.kind
    for i, (x, y) in enumerate(spots):
        if not ripe:
            # small unripe fruitlets
            if k in ("cherries",):
                stamp(p, ["s.s", "3.3", "2.2"], x, y, R, {"s": hexc("#4a7a2a")})
            elif k == "banana":
                if i < 2:
                    rows = ["..s..", "4.s.4", "34s43", "3434.", ".121."]
                    _rim(p, rows, x - 1, y, t.ramp[0])
                    stamp(p, rows, x - 1, y, R, {"s": hexc("#5a6a2a")})
            elif k == "olive":
                stamp(p, ["3", "2"], x, y, R)
            else:
                stamp(p, [".s", "43", "21"], x, y, R, {"s": hexc("#4a6a2a")})
            continue
        if k == "round":
            stamp(p, [".s.", "343", "432", ".21"], x, y, R, {"s": stem_c})
            if t.id == "apple":
                p.px(x, y + 1, hexc("#f8d0b0"))
        elif k == "blush":   # peach
            blush = fruit(fc[1])
            stamp(p, [".s.", "343", "4BA", ".AB"], x, y, R, {"s": hexc("#4a7a2a"), "A": (blush, 2), "B": (blush, 1)})
        elif k == "oval":    # lemon: pointed ends
            stamp(p, [".s.", ".4.", "343", "332", ".2."], x, y, R, {"s": hexc("#4a7a2a")})
        elif k == "small":   # lime: bright, with a dark rim so it separates from the dark leaves
            LI = ramp_hex("#1e4a14", "#4a8a24", "#78bc3a", "#a2d860", "#d2f09a")
            rows = [".s.", "443", "432", ".21"]
            _rim(p, rows, x, y, t.ramp[0])
            stamp(p, rows, x, y, LI, {"s": stem_c})
        elif k == "pear":
            stamp(p, [".s.", ".4.", ".3.", "432", "321"], x, y - 1, R, {"s": stem_c})
            p.px(x + 2, y + 2, shade(fc[1], 0.1) if len(fc) > 1 else R[1])
        elif k == "plum":
            BL = mix(R[3], hexc("#b0a8d0"), 0.55)
            stamp(p, [".s", "B3", "32", "21"], x, y, R, {"s": stem_c, "B": BL})
        elif k == "cherries":
            stamp(p, [".s.", "s.s", "4.3", "21.", "...", "..."][:4], x, y, R, {"s": hexc("#4a7a2a")})
            p.px(x + 2, y + 3, R[1])
            p.px(x + 2, y + 2, R[3])
        elif k == "mango":
            blush = fruit(fc[1])
            stamp(p, ["s..", ".s.", "34.", "432", "A32", ".A1"], x, y - 1, R,
                  {"s": hexc("#5a6a2a"), "A": (blush, 2)})
        elif k == "avocado":
            AV = ramp_hex("#1e2a12", "#2e4018", "#46602a", "#6a8a3a", "#a8c060")
            rows = [".s.", ".4.", "343", "322", "211", ".1."]
            _rim(p, rows, x, y - 1, t.ramp[0])
            stamp(p, rows, x, y - 1, AV, {"s": stem_c})
        elif k == "banana":
            if i < 2:
                # a hand of upturned fingers hanging from the bunch stalk
                BAN = ramp_hex("#8a6a10", "#c09a1a", "#f2d23a", "#f8e46a", "#fcf0a0")
                rows = ["..s..", "4.s.4", "34s43", "3434.", "23232", ".121."]
                _rim(p, rows, x - 1, y - 1, t.ramp[0])
                stamp(p, rows, x - 1, y - 1, BAN, {"s": hexc("#5a6a2a")})
                for (dx, dy) in ((0, 1), (4, 1)):
                    p.px(x - 1 + dx, y - 1 + dy, hexc("#5a4a20"))
        elif k == "olive":
            OL = ramp_hex("#120e14", "#241c26", "#382c3a", "#5a4a5c", "#8a7a8e")
            GR = ramp_hex("#3a4214", "#56601e", "#74802a", "#94a03c", "#b4c060")
            a_, b_ = (OL, GR) if i % 2 else (GR, OL)
            _rim(p, [".s.", "43.", "21.", "..."], x, y, t.ramp[0])
            stamp(p, [".s.", "43.", "21."], x, y, a_, {"s": hexc("#5a5a3a")})
            stamp(p, ["4", "2"], x + 2, y + 1, b_)
            stamp(p, ["3", "1"], x + 1, y + 3, OL)


def _rim(p: Plant, rows, x: int, y: int, col) -> None:
    """Dark separation rim around a stamp's silhouette (right/bottom/left), painted under it."""
    sil = {(x + i, y + j) for j, r in enumerate(rows) for i, c in enumerate(r) if c != "."}
    for (qx, qy) in sil:
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (1, 1)):
            n = (qx + dx, qy + dy)
            if n not in sil and p.own(*n) >= 0:
                p.px(n[0], n[1], col)


def _banana_leaves(p: Plant, t: TreeArt) -> None:
    """Overlay broad palm-like banana paddles with ribbed veins on top of the base texture."""
    R = t.ramp
    # paddles: (start, end) along a diagonal, drawn wrapped so they tile
    for (a, b) in (((-2, 3), (17, 10)), ((-3, 12), (16, 19)), ((4, -2), (14, 3))):
        ax = line([a, b])
        for k, (x, y) in enumerate(ax):
            for dy in (-2, -1, 0, 1, 2):
                q = (x, y + dy)
                tone = 3 if dy < 0 else 2 if dy > 0 else 4
                if abs(dy) == 2:
                    tone = 1 if dy > 0 else 2
                if (k + dy) % 3 == 0 and dy != 0:
                    tone -= 1      # parallel ribbing
                if abs(dy) == 2 and h(x, y, t.salt + 41) < 0.35:
                    continue       # shredded edges
                p.px(q[0], q[1], R[max(0, min(4, tone))])


def sapling_texture(t: TreeArt) -> Sprite:
    p = Plant()
    W = t.log
    if t.kind == "banana":
        # banana sucker: green-brown pseudostem with broad arching paddle leaves
        PS = ramp_hex("#4a5a2a", "#62723a", "#7a8a48", "#94a45a", "#aeba70")
        p.add(rect(7, 9, 7, 15), PS, base=3)
        p.add(rect(8, 10, 8, 15), PS, base=1)
        for ctrl, d in (([(7, 10), (3, 4), (0, 6)], 0), ([(8, 10), (12, 3), (15, 5)], -1), ([(7, 9), (6, 3), (5, 0)], 0),
                        ([(8, 11), (11, 8), (14, 10)], -1)):
            curve_leaf(p, ctrl, 3.2, t.ramp, "strap", depth=d, vein=4, vein_span=(0.05, 0.9))
        stamp(p, [".s", "44", "32", "21"], 9, 9, [shade(t.blossom, a) for a in (-0.2, -0.1, 0, 0.1, 0.2)],
              {"s": hexc("#6a7a3a")})
        return p.render()
    # per-tree silhouettes: (branch tip / cluster centre x, y, radius x, radius y)
    shapes = {
        "pear": [(5.5, 6.5, 2.4, 2.6), (10.5, 5.0, 2.4, 2.8), (8.0, 2.4, 2.2, 2.4)],
        "olive": [(3.5, 6.5, 3.2, 2.0), (12.0, 5.5, 3.2, 2.0), (7.5, 3.0, 3.0, 2.0)],
        "mango": [(4.0, 6.0, 3.0, 3.0), (11.5, 5.5, 3.0, 3.2), (7.5, 2.5, 2.8, 2.6)],
        "avocado": [(4.0, 6.5, 3.2, 2.8), (11.5, 6.0, 3.2, 2.8), (8.0, 2.8, 3.0, 2.6)],
        "orange": [(4.5, 6.0, 3.0, 2.8), (11.0, 5.5, 3.0, 2.8), (7.8, 2.8, 3.0, 2.6)],
    }
    shapes["lemon"] = shapes["lime"] = shapes["orange"]
    clusters = shapes.get(t.id, [(4.5, 6.0, 2.8, 2.6), (11.0, 5.0, 2.8, 2.8), (7.6, 2.6, 2.6, 2.4)])
    twisted = t.id == "olive"
    p.add(rect(7, 10, 7, 15), W, base=3)
    p.add(rect(8, 11 if not twisted else 12, 8, 15), W, base=1)
    for (cx, cy, rx, ry) in clusters:
        p.add(line([(7 + (cx > 8), 11), (round(cx), round(cy + ry * 0.5))]), W, base=2)
    if twisted:
        p.px(6, 13, W[2])
        p.px(8, 12, W[3])
    if t.id in ("lemon", "lime"):   # birch: dark marks
        p.px(7, 13, W[0])
        p.px(8, 11, W[0])
    mask = set()
    for cx, cy, rx, ry in clusters:
        mask |= disc(cx, cy, rx, ry)
    rim = {q for q in mask if any(n not in mask for n in ((q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] - 1),
                                                           (q[0], q[1] + 1)))}
    mask -= {q for q in rim if h(q[0], q[1], t.salt + 3) < 0.3}
    tones_ = leaf_cells(mask, jitter_seeds(16, 16, min(t.cell, 2.3), t.salt + 1), salt=t.salt, stretch=t.stretch,
                        form=(5, 2, 7, 0.8), grad=0.8)
    p.fixed(tones_, t.ramp)
    # hint: one fruit or blossom
    k = t.kind
    if t.id in ("peach", "pear", "plum", "sweet_cherry"):
        for (x, y) in ((4, 5), (11, 4), (7, 2)):
            pc = t.blossom
            p.px(x, y, pc)
            p.px(x + 1, y, shade(pc, -0.12))
            p.px(x, y + 1, shade(pc, -0.2))
    else:
        R = fruit(t.fruit_colors[0])
        if k == "avocado":
            R = ramp_hex("#1a2a10", "#2a3e18", "#3e5a24", "#5a7a34", "#8aa050")
        x, y = 10, 7
        _rim(p, [".3.", "342", "321", ".1."], x, y, t.ramp[0])
        if k in ("small", "olive"):
            stamp(p, ["32", "21"], x, y, R)
        elif k in ("oval", "pear", "avocado", "mango"):
            stamp(p, [".3.", "342", "321", ".1."], x, y, R)
        else:
            stamp(p, [".3.", "342", "321"], x, y, R)
            if t.id == "apple":
                p.px(x, y + 1, hexc("#f8d0b0"))
    return p.render()


# --------------------------------------------------------------------------- registry


def tree_arts() -> list[TreeArt]:
    from ..spec import TREES

    style = {
        "apple": dict(fruit_kind="round"),
        "orange": dict(fruit_kind="round", gloss=True, cell=2.8),
        "lemon": dict(fruit_kind="oval", gloss=True, cell=2.8),
        "lime": dict(fruit_kind="small", gloss=True, cell=2.8),
        "peach": dict(fruit_kind="blush", stretch=(1.3, 0.8)),
        "pear": dict(fruit_kind="pear", cell=2.4),
        "plum": dict(fruit_kind="plum", cell=2.4),
        "sweet_cherry": dict(fruit_kind="cherries", stretch=(1.2, 0.9)),
        "mango": dict(fruit_kind="mango", stretch=(1.5, 0.6), cell=2.6, gloss=True),
        "avocado": dict(fruit_kind="avocado", stretch=(1.3, 0.8), cell=2.9),
        "banana": dict(fruit_kind="banana", cell=3.2, holes=0.3, spots=[(3, 4), (11, 9), (6, 11), (12, 1)]),
        "olive": dict(fruit_kind="olive", cell=2.0, stretch=(1.0, 1.6), holes=0.3),
    }
    out = []
    for tr in TREES:
        fc = ["#d0302a", "#8a1a1a"] if isinstance(tr.fruit, str) else tr.fruit.art.colors
        out.append(TreeArt(tr.id, tr.leaf_colors, tr.blossom, fc, tr.log, **style.get(tr.id, {})))
    return out


def tree_textures() -> dict[str, Sprite]:
    """``<tree>_sapling`` and ``<tree>_leaves_<age>`` sprites keyed by file stem."""
    from ..spec import TREES_BY_ID

    out: dict[str, Sprite] = {}
    for t in tree_arts():
        tr = TREES_BY_ID[t.id]
        out[tr.sapling] = sapling_texture(t)
        for age in range(4):
            out[f"{tr.leaves}_{age}"] = leaves_texture(t, age)
    return out
