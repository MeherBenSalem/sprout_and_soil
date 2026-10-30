"""Corn: stages 0-1 are single-block textures; stages 2-3 are painted on one 16x32 canvas and
split into ``corn_stageN_top`` (upper block) and ``corn_stageN`` (lower block), so stalks and
leaves run across the block seam without a break."""
from __future__ import annotations

from .core import hexc
from .plants_kit import Plant, green, rect
from .plants_lib import curve_leaf, stamp


def ramp_hex(*cols):
    return [hexc(c) for c in cols]


G = green("#4e8a2e")
STALK = ramp_hex("#4a6a2a", "#5e8034", "#76983e", "#90b050", "#a8c466")


def _stalk(p: Plant, x: int, top: int, bottom: int) -> None:
    p.add(rect(x, top, x, bottom), STALK, base=3)
    p.add(rect(x + 1, top + 1, x + 1, bottom), STALK, base=1)


def _leaf(p: Plant, x: int, y: int, d: int, L: float, w: float = 2.4, depth: int = 0, rise: float = 4) -> None:
    """Long arching corn leaf from the stalk node (x, y): up and out, tip drooping."""
    bx = x + (1 if d > 0 else 0)
    ctrl = [(bx, y), (bx + d * L * 0.45, y - rise), (bx + d * L * 0.85, y - rise * 0.6), (bx + d * L, y + 1)]
    curve_leaf(p, ctrl, w, G, "blade", depth=depth, vein=4, vein_span=(0.1, 0.55))


def corn_full(st: int) -> Plant:
    if st == 0:
        p = Plant()
        for k, x in enumerate((4, 11)):
            t = 11 + k
            curve_leaf(p, [(x, 15), (x, t + 1), (x - 2, t)], 2.0, G, "blade")
            curve_leaf(p, [(x, 15), (x + 1, t), (x + 2, t - 1)], 1.8, G, "blade", depth=-1)
        return p
    if st == 1:
        p = Plant()
        for k, x in enumerate((4, 11)):
            t = 6 + k
            _stalk(p, x, t + 3, 15)
            _leaf(p, x, 14, -1, 4, 2.2, rise=3)
            _leaf(p, x, 12, 1, 4, 2.2, depth=-1, rise=4)
            _leaf(p, x, 10, -1, 3, 2.0, rise=3)
            curve_leaf(p, [(x, t + 4), (x, t + 1), (x + 1, t)], 2.0, G, "blade")
        return p
    ripe = st == 3
    p = Plant(16, 32)
    tops = (3, 5) if ripe else (8, 10)
    xs = (4, 10)
    for k, x in enumerate(xs):
        _stalk(p, x, tops[k] + 2, 31)
    # leaves, low to high; outer side alternates per node
    nodes = [(29, -1, 4), (26, 1, 5), (23, -1, 5), (20, 1, 5), (17, -1, 5), (14, 1, 4), (11, -1, 4)]
    for k, x in enumerate(xs):
        for j, (y, d, L) in enumerate(nodes):
            y += k
            if y < tops[k] + 4:
                continue
            dd = d if k == 0 else -d
            _leaf(p, x, y, dd, L, 2.4, depth=-1 if j % 2 else 0)
    # tassels
    tas = ramp_hex("#8a6a2a", "#b08a3a", "#d4b05a", "#e8cc7a", "#f4e0a0") if ripe else green("#a0c060", spread=0.8)
    for k, x in enumerate(xs):
        t = tops[k]
        for (dx, dy, tone) in ((0, -1, 4), (0, 0, 3), (0, 1, 2), (-1, 1, 3), (-2, 2, 2), (1, 0, 2), (2, 1, 2),
                               (2, 2, 1), (-1, 0, 2), (-2, 3, 1), (1, 2, 3)):
            p.px(x + dx, t + dy, tas[tone])
    # cobs on the lower block, hugging the stalks on the outside
    if ripe:
        KERN = ramp_hex("#b07a10", "#d89a1a", "#f2c63a", "#f8dc6a", "#fcee9e")
        HUSK = ramp_hex("#6a7a3a", "#88984a", "#a8b862", "#c4d07e", "#dce49e")
        for (x, y, flip) in ((1, 18, False), (12, 20, True)):
            stamp(p, [".s.", "h4h", "h43", "h32", "H32", "H21", ".H."], x, y, KERN,
                  {"h": (HUSK, 3), "H": (HUSK, 1), "s": hexc("#9a6a3a")}, flip=flip)
    else:
        HUSK = green("#7aa848", spread=0.9)
        for (x, y) in ((2, 19), (12, 21)):
            stamp(p, [".s", "33", "32", "21", ".1"], x, y, HUSK, {"s": hexc("#e8d8a0")})
    return p
