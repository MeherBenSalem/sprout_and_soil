"""Item sprites for crop produce and tree fruit (produce lane).

Each function draws one 16x16 item: a silhouette (part letters, see
``produce_kit.SHAPE_KEYS``) is form-shaded from the top-left, then a *detail*
layer adds glints, creases, seeds, stems... (see ``produce_kit.apply_detail``:
tone letters replace, ``-``/``+`` shift tone, ``^``/``%`` swap ramps).
Overlay letters (upper-case secondary/tertiary, ``W``) are drawn without outline.
"""
from __future__ import annotations

import math
import random
from typing import Callable

from .core import Sprite
from .produce_kit import Grid, apply_detail, mat, pal, render, shade_rows

ITEMS: dict[str, Callable[[], Sprite]] = {}


def item(name: str):
    def deco(fn):
        ITEMS[name] = fn
        return fn
    return deco


def S(*rows: str) -> list[str]:
    for r in rows:
        assert len(r) <= 16, (len(r), r)
    return [r.ljust(16, ".") for r in rows]


def _shift(rows: list[str] | None, dx: int, dy: int) -> list[str] | None:
    if not rows or (dx, dy) == (0, 0):
        return rows
    g = Grid()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch not in ". ":
                g.put(x + dx, y + dy, ch)
    return g.out()


def build(shape, palette, detail=None, outline=True, seam="auto", shift=(0, 0), **kw) -> Sprite:
    """Shade a silhouette, apply the detail layer and render with outline.

    ``shift`` moves both layers (used to keep outlines inside the canvas)."""
    order = None
    if isinstance(shape, Grid):
        order = "".join(shape.order)
        shape = shape.out()
    if seam == "auto":
        seam = order
    if isinstance(detail, Grid):
        detail = detail.out()
    shape, detail = _shift(shape, *shift), _shift(detail, *shift)
    rows = shade_rows(shape, seam=seam, **kw)
    rows = apply_detail(rows, detail)
    return render(rows, palette, outline=outline)


def on(shape: Grid, chars: str, pts, d: Grid, ch: str) -> None:
    """Put detail ``ch`` at ``pts`` but only where the silhouette has one of ``chars``."""
    for x, y in pts:
        if shape.get(x, y) in chars:
            d.put(x, y, ch)


def cells(shape: Grid, chars: str):
    return [(x, y) for y in range(16) for x in range(16) if shape.get(x, y) in chars]


def bez(pts, t):
    p = list(pts)
    while len(p) > 1:
        p = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(p, p[1:])]
    return p[0]


def bez_frame(pts, t, eps=0.01):
    """Point and unit normal (pointing 'right' of travel) on a bezier."""
    x, y = bez(pts, t)
    x2, y2 = bez(pts, min(1.0, t + eps))
    x1, y1 = bez(pts, max(0.0, t - eps))
    tx, ty = x2 - x1, y2 - y1
    n = math.hypot(tx, ty) or 1
    return (x, y), (-ty / n, tx / n)


# shared materials
LEAF = mat("#3f8a2a", 0.10)
TWIG = mat("#6a4a2a", 0.09)


# =========================================================================== fruiting vegetables


@item("tomato")
def tomato():
    P = mat("#d8322a", 0.11)
    G = mat("#3f8a2a", 0.10)
    shape = S(
        "................",
        "................",
        "................",
        ".......GG.......",
        "....GGGGGGGG....",
        "...PPGPGGPGPP...",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "...PPPPPPPPPP...",
        "....PPPPPPPP....",
        "......PPPP......",
    )
    detail = S(
        "................",
        "................",
        "........C.......",
        ".......cb.......",
        "....cdcbbcdc....",
        ".....c.cb.c.....",
        "....-...-..-....",
        "....w...........",
        "...w+...........",
    )
    return build(shape, pal(P, G), detail)


@item("bell_pepper")
def bell_pepper():
    P = mat("#c8281e", 0.11)
    G = mat("#3c7a26", 0.10)
    shape = S(
        "................",
        "................",
        "................",
        ".......GG.......",
        "....PPPGGPPP....",
        "...PPPggggPPP...",
        "...PPPPPPPPPP...",
        "...PPPPPPPPPP...",
        "...PPPPPPPPPP...",
        "...PPPPPPPPPP...",
        "...PPPPPPPPPP...",
        "...PPPPPPPPPP...",
        "...PPPPPPPPPP...",
        "...PP.PPPP.PP...",
    )
    detail = S(
        "................",
        "................",
        "........C.......",
        "................",
        "................",
        "................",
        "....w...........",
        "....w..w..-.....",
        ".....-+w..-.....",
        ".....-+...-.....",
        ".....-....-.....",
        ".....=....=.....",
        ".....=....=.....",
    )
    return build(shape, pal(P, G), detail)


@item("chili_pepper")
def chili_pepper():
    P = mat("#d7261e", 0.11)
    G = mat("#3c7a26", 0.10)
    shape = S(
        "................",
        "................",
        "................",
        ".........GGGG...",
        "........GPPPG...",
        ".........PPP....",
        "........PPP.....",
        "........PPP.....",
        ".......PPP......",
        ".......PPP......",
        "......PPP.......",
        ".....PPP........",
        "....PPP.........",
        "..PPP...........",
    )
    detail = S(
        "................",
        "............B...",
        "...........C....",
        "................",
        "................",
        ".........w......",
        "........w.......",
        "................",
        ".......w........",
    )
    return build(shape, pal(P, G), detail)


@item("eggplant")
def eggplant():
    P = mat("#4a2160", 0.10, lift=0.02)
    G = mat("#4a7a2a", 0.10)
    shape = S(
        "................",
        "................",
        "...........GG...",
        "..........GGGG..",
        ".........GPGPG..",
        "........PPPPP...",
        ".......PPPPPP...",
        ".....PPPPPPPP...",
        "....PPPPPPPP....",
        "...PPPPPPPPP....",
        "..PPPPPPPPPP....",
        "..PPPPPPPPP.....",
        "...PPPPPPP......",
        "....PPPPP.......",
    )
    detail = S(
        "................",
        "............B...",
        "................",
        "................",
        "................",
        "................",
        "................",
        "......w.........",
        ".....w..........",
        "....w...........",
    )
    return build(shape, pal(P, G), detail)


@item("cucumber")
def cucumber():
    P = mat("#3e7d2e", 0.10, lift=-0.02)
    G = mat("#a7d06a", 0.08)
    T = mat("#7a6a2a", 0.08)
    ctrl = [(3.3, 12.7), (6.0, 6.6), (12.4, 3.6)]
    g = Grid().curve(ctrl, 2.3, 2.0, "P")
    d = Grid()
    for i, t in enumerate([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]):
        (x, y), (nx, ny) = bez_frame(ctrl, t)
        off = -1.3 if i % 2 == 0 else 0.9
        px, py = int(x + nx * off), int(y + ny * off)
        on(g, "P", [(px, py)], d, "d" if off < 0 else "c")
    d.put(14, 1, "K").put(13, 2, "k")
    return build(g, pal(P, G, None, T), d)


@item("zucchini")
def zucchini():
    P = mat("#2f6a26", 0.10, lift=-0.01)
    G = mat("#8fbf5a", 0.08)
    T = mat("#9aa060", 0.09)
    g = Grid().capsule(3.2, 12.8, 11.2, 4.8, 2.6, 2.1, "P")
    g.capsule(12.0, 4.0, 13.4, 2.6, 1.15, 1.0, "T")
    d = Grid()
    for i in range(14):
        t = i / 13
        x, y = 3.2 + 8.0 * t, 12.8 - 8.0 * t
        for off, ch in ((-1.25, "c"), (1.1, "b")):
            if (i + (0 if off < 0 else 1)) % 2 == 0:
                on(g, "P", [(int(x - off * 0.707), int(y - off * 0.707))], d, ch)
    d.put(13, 2, "i")
    return build(g, pal(P, G, T), d)


@item("green_beans")
def green_beans():
    P = mat("#5a9a32", 0.10)
    g = Grid()
    pods = [("R", [(12.2, 2.6), (7.0, 3.6), (2.4, 8.6)]),
            ("p", [(12.8, 3.2), (8.2, 7.0), (4.0, 13.0)]),
            ("P", [(13.4, 4.0), (10.6, 9.4), (8.8, 14.2)])]
    for ch, ctrl in pods:
        g.curve(ctrl, 0, ch=ch, profile=[0.75, 0.95, 0.95, 0.9, 0.5])
    d = Grid()
    for ch, ctrl in pods:
        for t in (0.3, 0.52, 0.74):
            (x, y), (nx, ny) = bez_frame(ctrl, t)
            on(g, ch, [(int(x - nx * 0.5), int(y - ny * 0.5))], d, "+")
    d.pts([(13, 1), (14, 2)], "C").put(14, 1, "B")
    return build(g, pal(P, LEAF), d)


# =========================================================================== leafy & brassicas


@item("lettuce")
def lettuce():
    P = mat("#7cc04a", 0.10)
    G = mat("#c9e88a", 0.08)
    shape = Grid(S(
        "................",
        "................",
        "................",
        ".....P.PP.P.....",
        "....PPPPPPPP....",
        "...PPPGGGGPPP...",
        "..ppPGGGGGGPRR..",
        ".pppGGGGGGGGRRR.",
        "..ppGGGGGGGGRR..",
        ".ppppGGGGGGRRRR.",
        "..ppprGGGGrRRR..",
        ".ppprrrrrrrrRRR.",
        "..pprrrrrrrrrR..",
        "...rr.rrrr.rr...",
    ))
    shape.order = list("PGpRr")
    detail = S(
        "................",
        "................",
        "................",
        "................",
        "....+.+..+......",
        "......+..+......",
        ".....+....-.....",
        "...+........+...",
        "..+..........+..",
        "...+........+...",
        "......+..+......",
        "...+...++...+...",
        "....+......+....",
    )
    return build(shape, pal(P, G), detail)


@item("cabbage")
def cabbage():
    P = mat("#8cbc66", 0.09)
    T = mat("#5f9a48", 0.10)
    g = Grid().ellipse(7.8, 8.0, 5.8, 5.6, "P")
    g.curve([(1.8, 7.6), (3.4, 14.6), (9.6, 13.6)], 0, ch="T", profile=[0.6, 2.2, 2.8, 2.4, 1.2])
    g.curve([(14.0, 7.2), (12.4, 14.4), (6.6, 13.8)], 0, ch="t", profile=[0.6, 2.2, 2.8, 2.4, 1.2])
    d = Grid()
    # veins on the wrapper leaves, fanning up from the base
    for pts in ([(7, 13), (5, 12), (3, 10), (2, 8)], [(6, 13), (4, 13)],
                [(8, 13), (10, 12), (12, 10), (13, 8)], [(9, 13), (11, 13)]):
        on(g, "Tt", pts, d, "*")
    # the head's own leaf seams
    on(g, "P", [(5, 4), (4, 5), (4, 6)], d, "+")
    on(g, "P", [(8, 3), (9, 4), (10, 5), (11, 6), (11, 7)], d, "-")
    on(g, "P", [(7, 5), (6, 6)], d, "+")
    return build(g, pal(P, None, T), d, shift=(0, -1))


@item("spinach")
def spinach():
    P = mat("#2e7a2a", 0.10, lift=0.03)
    T = mat("#8ab858", 0.08)
    g = Grid()
    g.line(3, 14, 5, 10, "T").line(3, 14, 7, 10, "T").line(4, 14, 8, 12, "T")
    leaves = [("P", [(5.0, 10.0), (2.6, 5.4), (4.6, 1.4)]),
              ("p", [(7.0, 10.0), (9.6, 4.6), (13.8, 2.6)]),
              ("R", [(8.0, 12.2), (11.6, 9.4), (14.6, 11.6)])]
    for ch, ctrl in leaves:
        g.curve(ctrl, 0, ch=ch, profile=[0.6, 2.0, 2.5, 2.2, 1.4, 0.4])
    d = Grid()
    for ch, ctrl in leaves:
        for t in (0.15, 0.3, 0.45, 0.6, 0.75):
            x, y = bez(ctrl, t)
            on(g, ch, [(int(x), int(y))], d, "+")
    return build(g, pal(P, None, T), d)


@item("broccoli")
def broccoli():
    P = mat("#2f6e2c", 0.10, lift=0.02)
    G = mat("#7fb04a", 0.09)
    g = Grid()
    g.capsule(7.0, 14.0, 7.8, 9.5, 1.7, 1.5, "G")
    g.line(7, 10, 5, 8, "G").line(8, 10, 10, 8, "G")
    for (cx, cy, r, ch) in [(11.3, 6.4, 2.5, "R"), (8.2, 4.2, 2.7, "p"), (4.8, 6.0, 2.6, "P"),
                            (6.3, 8.6, 2.2, "r"), (10.0, 9.0, 2.1, "U")]:
        g.ellipse(cx, cy, r, r, ch)
    d = Grid()
    for x, y in cells(g, "PpRrU"):
        if (x + 2 * y) % 4 == 0:
            d.put(x, y, "-")
        elif (x + 2 * y) % 4 == 2 and (x * 3 + y) % 3 == 0:
            d.put(x, y, "+")
    return build(g, pal(P, G), d, shift=(0, -1))


@item("cauliflower")
def cauliflower():
    P = mat("#f1ead2", 0.08, lift=-0.03)
    G = mat("#5e9a3e", 0.10)
    g = Grid()
    g.ellipse(3.5, 8.6, 1.8, 4.2, "G", angle=-28)
    g.ellipse(12.3, 8.6, 1.8, 4.2, "g", angle=28)
    g.ellipse(7.8, 7.6, 5.0, 4.4, "P")
    g.ellipse(4.6, 12.0, 3.4, 2.2, "H", angle=-20, only="GgP.")
    g.ellipse(11.0, 12.0, 3.4, 2.2, "h", angle=20, only="GgP.")
    d = Grid()
    for x, y in cells(g, "P"):
        if (x + 3 * y) % 4 == 0 or (x % 3 == 0 and y % 2 == 0):
            d.put(x, y, "-")
    on(g, "G", [(2, 7), (3, 9), (3, 11)], d, "+")
    on(g, "g", [(13, 7), (12, 9), (12, 11)], d, "+")
    on(g, "Hh", [(5, 13), (10, 13), (6, 12), (9, 12)], d, "+")
    return build(g, pal(P, G), d)


@item("celery")
def celery():
    P = mat("#9cc86a", 0.09)
    G = mat("#5c9a3a", 0.10)
    g = Grid()
    g.capsule(2.4, 11.8, 7.6, 5.6, 1.15, 0.9, "R")
    g.capsule(3.6, 13.6, 9.8, 6.6, 1.2, 0.95, "P")
    g.capsule(6.0, 14.4, 11.6, 8.6, 1.15, 0.9, "p")
    g.ellipse(8.0, 3.8, 2.0, 1.7, "G").ellipse(6.4, 3.0, 1.3, 1.3, "G")
    g.ellipse(10.8, 5.2, 1.9, 1.9, "g").ellipse(12.4, 3.8, 1.2, 1.2, "g")
    g.ellipse(12.8, 7.6, 1.8, 1.8, "H").ellipse(14.0, 6.2, 1.0, 1.0, "H")
    d = Grid()
    for ch, (x0, y0, x1, y1) in (("R", (2.4, 11.8, 7.6, 5.6)), ("P", (3.6, 13.6, 9.8, 6.6)),
                                  ("p", (6.0, 14.4, 11.6, 8.6))):
        for i in range(1, 9):
            t = i / 9
            on(g, ch, [(int(x0 + (x1 - x0) * t - 0.4), int(y0 + (y1 - y0) * t - 0.4))], d, "+")
    for x, y in cells(g, "GgH"):
        if (x + y) % 3 == 0:
            d.put(x, y, "-")
    return build(g, pal(P, G), d)


@item("asparagus")
def asparagus():
    P = mat("#6a9a3a", 0.10)
    G = mat("#8a5a8a", 0.09)
    T = mat("#c49a5a", 0.08)
    # hand-toned: four thin spears fanning out of a twine-tied bundle, purple scaly heads
    rows = S(
        "................",
        "......d.........",
        "...d..dc...d....",
        "...dc.dc..dc....",
        "...cb..4..cb..d.",
        "....4..4..4..dc.",
        "....4..3..4..cb.",
        "....4..4..3.4...",
        ".....3.4.4..3...",
        ".....3.4.4.3....",
        "....hihihihi....",
        "......3432......",
        "......3432......",
        "......2321......",
        "......5545......",
    )
    return render(rows, pal(P, G, T))


# =========================================================================== roots & bulbs


@item("garlic")
def garlic():
    P = mat("#efe6d6", 0.08, lift=-0.02)
    G = mat("#b89ab0", 0.08)
    T = mat("#c8a878", 0.08)
    shape = Grid(S(
        "................",
        "................",
        "........U.......",
        ".......UU.......",
        "......UUUU......",
        ".....PPppRR.....",
        "...PPPPppRRRR...",
        "..PPPPPppRRRRR..",
        "..PPPPPppRRRRR..",
        "..PPPPPppRRRRR..",
        "..PPPPPppRRRRR..",
        "...PPPPppRRRR...",
        "....PPPppRRR....",
    ))
    shape.order = list("RpPU")
    detail = S(
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "...........c....",
        "....c......c....",
        "....c.........d.",
        "...........d....",
        "....d...........",
        "................",
        "................",
        ".....J.JJ.J.....",
        "......J..J......",
    )
    return build(shape, pal(P, G, T), detail)


@item("onion")
def onion():
    P = mat("#c88a3a", 0.10)
    G = mat("#f0d6a0", 0.08)
    T = mat("#7a4a22", 0.08)
    shape = S(
        "................",
        "................",
        "........T.......",
        "........P.......",
        ".......PPP......",
        ".....PPPPPP.....",
        "...PPPPPPPPPP...",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "...PPPPPPPPPP...",
        ".....PPPPPP.....",
    )
    detail = S(
        "................",
        ".........H......",
        "................",
        "................",
        "................",
        "......-.........",
        ".....-....-.....",
        "....-......-....",
        "....w......-....",
        "...+-......-....",
        "....-.....-.....",
        ".....-...-......",
        "................",
        ".....G.GG.G.....",
        "......G..G......",
    )
    return build(shape, pal(P, G, T), detail)


@item("leek")
def leek():
    P = mat("#f0f0d8", 0.08, lift=-0.03)
    G = mat("#3f7a3a", 0.10)
    T = mat("#9ac860", 0.09)
    g = Grid()
    g.capsule(9.0, 7.0, 11.4, 1.5, 1.25, 0.55, "G")
    g.capsule(9.4, 7.4, 14.6, 4.4, 1.25, 0.55, "g")
    g.capsule(9.2, 7.2, 13.4, 2.4, 1.3, 0.7, "H")
    g.capsule(3.2, 12.8, 7.8, 8.2, 1.95, 1.75, "P")
    g.capsule(7.4, 8.6, 9.4, 6.6, 1.75, 1.5, "T")
    d = Grid()
    on(g, "P", [(4, 10), (5, 9), (6, 8)], d, "+")
    on(g, "P", [(5, 13), (6, 12), (7, 11)], d, "-")
    d.pts([(1, 14), (2, 15), (0, 13), (3, 15), (1, 15)], "K")
    K = mat("#c8b088", 0.08)
    return build(g, pal(P, G, T, K), d)


@item("radish")
def radish():
    P = mat("#d23a5a", 0.11)
    G = mat("#5e9a3e", 0.10)
    T = mat("#f2ecea", 0.07, lift=-0.03)
    g = Grid()
    g.line(7, 6, 6, 4, "H").line(8, 6, 9, 4, "H")
    g.ellipse(4.6, 3.4, 2.7, 1.6, "G", angle=30)
    g.ellipse(11.0, 3.2, 2.7, 1.6, "g", angle=-30)
    g.ellipse(7.8, 9.8, 3.8, 3.6, "P")
    g.capsule(7.8, 12.4, 7.2, 14.6, 1.3, 0.4, "T", only=".")
    d = Grid()
    d.pts([(5, 8)], "w").pts([(6, 7)], "+")
    on(g, "G", [(3, 3), (4, 3), (5, 3)], d, "+")
    on(g, "g", [(10, 3), (11, 3), (12, 3)], d, "+")
    d.put(7, 15, "~")
    return build(g, pal(P, G, T), d)


@item("turnip")
def turnip():
    P = mat("#ece4d6", 0.08, lift=-0.02)
    G = mat("#9a4a8a", 0.10)
    T = mat("#5e9a3e", 0.10)
    g = Grid()
    g.capsule(6.0, 5.5, 3.5, 1.5, 0.9, 0.7, "T")
    g.capsule(8.0, 5.5, 8.5, 1.7, 0.9, 0.7, "t")
    g.capsule(10.0, 5.5, 12.5, 2.0, 0.9, 0.7, "Y")
    g.ellipse(7.8, 9.6, 5.6, 4.2, "P")
    g.capsule(7.8, 13.0, 7.8, 15.0, 1.2, 0.4, "P", only=".")
    # purple top half dithered into white
    d = Grid()
    for x, y in cells(g, "P"):
        if y <= 8 or (y == 9 and x % 2 == 0):
            d.put(x, y, "^")
    d.pts([(4, 8), (5, 7)], "+")
    return build(g, pal(P, G, T), d)


@item("sweet_potato")
def sweet_potato():
    P = mat("#b8503a", 0.10, lift=-0.02)
    g = Grid().curve([(2.4, 13.0), (6.0, 11.0), (13.2, 2.6)], 0, profile=[0.6, 2.6, 3.3, 3.1, 2.2, 0.7])
    d = Grid()
    for x, y in [(5, 9), (6, 8), (9, 6), (10, 5), (7, 11), (8, 10), (11, 8)]:
        on(g, "P", [(x, y)], d, "-")
    on(g, "P", [(4, 10), (7, 7), (8, 6)], d, "+")
    d.put(1, 14, "8").put(14, 1, "7")
    return build(g, pal(P), d)


@item("ginger")
def ginger():
    P = mat("#d8b06a", 0.09)
    G = mat("#f0dca0", 0.07)
    g = Grid()
    g.ellipse(4.2, 6.2, 1.7, 2.4, "R", angle=-25)
    g.ellipse(11.2, 5.6, 1.8, 3.0, "p", angle=25)
    g.ellipse(7.2, 10.2, 5.2, 2.7, "P")
    g.ellipse(13.0, 10.4, 1.9, 1.6, "r")
    d = Grid()
    on(g, "P", [(4, 9), (4, 10), (4, 11), (8, 9), (8, 10), (8, 11), (11, 10), (11, 11)], d, "-")
    on(g, "p", [(10, 6), (11, 6), (12, 6)], d, "-")
    on(g, "R", [(3, 7), (4, 7), (5, 7)], d, "-")
    on(g, "R", [(4, 4), (3, 5)], d, "c")
    on(g, "p", [(11, 3), (12, 3)], d, "c")
    on(g, "r", [(14, 10)], d, "c")
    return build(g, pal(P, G), d)


@item("peanuts")
def peanuts():
    P = mat("#c8a06a", 0.10)
    g = Grid()
    shells = [("p", [(8.6, 13.6), (14.0, 8.8)], [1.0, 1.9, 2.0, 1.2, 1.9, 1.8, 0.9]),
              ("P", [(2.0, 12.4), (11.2, 3.2)], [1.1, 2.3, 2.5, 1.5, 2.4, 2.3, 1.1])]
    for ch, ctrl, prof in shells:
        g.curve(ctrl, 0, ch=ch, profile=prof)
    d = Grid()
    for ch, (a, b), _ in shells:
        L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = -uy, ux
        for i in range(2, int(L) - 1):
            t = i / L
            cx, cy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for off, tone in ((-1.0, "+"), (1.1, "-")):
                if i % 2 == (0 if off < 0 else 1):
                    on(g, ch, [(int(cx + nx * off), int(cy + ny * off))], d, tone)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        on(g, ch, [(int(mx + nx * k), int(my + ny * k)) for k in (-1.2, 0, 1.2)], d, "=")
    return build(g, pal(P), d)


# =========================================================================== grains


@item("corn")
def corn():
    P = mat("#f2c63a", 0.10)
    G = mat("#a8c86a", 0.10)
    g = Grid()
    g.capsule(5.0, 11.0, 11.6, 4.2, 2.7, 2.3, "P")
    g.curve([(3.4, 13.4), (1.4, 10.0), (2.6, 6.6)], 1.5, 0.5, "G")
    g.curve([(4.2, 13.6), (8.0, 14.2), (10.6, 12.6)], 1.4, 0.5, "g")
    g.curve([(4.0, 13.0), (4.8, 10.0), (7.4, 8.4)], 1.3, 0.6, "H")
    d = Grid()
    for x, y in cells(g, "P"):
        u, v = x - y, x + y
        if v % 2 == 0:
            d.put(x, y, "-" if u % 4 == 0 else ("+" if u % 4 == 2 else "."))
    d.pts([(13, 2), (14, 3), (14, 1)], "K")
    K = mat("#a8783a", 0.08)
    return build(g, pal(P, G, None, K), d)


@item("rice")
def rice():
    P = mat("#f2ecd8", 0.07, lift=-0.04)
    shape = Grid(S(
        "................",
        "................",
        "................",
        "................",
        "................",
        "......PPP.......",
        ".....PPPPPP.....",
        "....PPPPPPPP....",
        "...PPPPPPPPPP...",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPPP.",
        ".PPPPPPPPPPPPPP.",
        "..PPPPPPPPPPPP..",
        "................",
        "...pp......RR...",
    ))
    shape.put(9, 5, "P").put(4, 6, "P").put(12, 7, "P")
    d = Grid()
    rng = random.Random(5)
    for x, y in cells(shape, "P"):
        d.put(x, y, "-")
    # stamp short grains (2 px, random orientation) over the gap-tone heap
    for y in range(5, 13):
        for x in range(1, 15):
            if shape.get(x, y) == "P" and (x * 2 + y * 3) % 4 == 0:
                dx, dy = rng.choice([(1, 0), (1, 1), (0, 1), (1, -1)])
                d.put(x, y, "*")
                if shape.get(x + dx, y + dy) == "P":
                    d.put(x + dx, y + dy, "+")
    d.pts([(3, 14), (12, 14)], "*")
    return build(shape, pal(P), d)


@item("barley")
def barley():
    P = mat("#e0c070", 0.09)
    T = mat("#c8a050", 0.08)
    K = mat("#8a5a2a", 0.08)
    g = Grid()
    # stalks gathered at the bottom-left, tied with a band
    g.line(2, 14, 6, 9, "T").line(3, 14, 8, 10, "T").line(4, 14, 9, 11, "T").line(3, 13, 6, 10, "T")
    heads = [("R", (6.6, 8.6), (7.6, 3.4)), ("P", (8.4, 9.4), (11.4, 5.4)), ("p", (9.6, 11.0), (13.8, 9.0))]
    for ch, a, b in heads:
        g.capsule(a[0], a[1], b[0], b[1], 1.1, 0.85, ch)
    g.line(3, 11, 5, 13, "K").line(4, 11, 6, 13, "K")
    d = Grid()
    for x, y in cells(g, "RPp"):
        if (x + y) % 2 == 0:
            d.put(x, y, "-")
    # long whiskery awns continuing each head (overlay, no outline)
    awns = [((7, 2), (8, 0)), ((6, 3), (5, 0)), ((8, 3), (10, 0)),
            ((11, 4), (14, 1)), ((10, 5), (11, 2)), ((12, 5), (15, 4)),
            ((14, 8), (15, 8)), ((13, 9), (15, 10)), ((14, 9), (15, 9))]
    for (x0, y0), (x1, y1) in awns:
        for x, y in Grid().line(x0, y0, x1, y1, "x").where("x"):
            if g.get(x, y) == ".":
                d.put(x, y, "9" if (x + y) % 2 else "8")
    return build(g, pal(P, None, T, K), d)


@item("oats")
def oats():
    P = mat("#ecdca4", 0.08)
    T = mat("#a89050", 0.08)
    g = Grid()
    # thin straw stems (overlay) branching from a bundle at the bottom-left
    stems = [((3, 14), (6, 7)), ((6, 7), (7, 3)), ((6, 7), (10, 5)), ((4, 14), (10, 9)),
             ((10, 9), (13, 6)), ((10, 9), (13, 11))]
    spk = [(4.4, 5.6, "P"), (8.4, 3.0, "p"), (11.8, 5.6, "R"), (7.6, 9.4, "r"), (14.0, 8.6, "U"),
           (12.2, 12.2, "u")]
    for cx, cy, ch in spk:
        g.ellipse(cx, cy, 1.0, 1.7, ch, angle=15)
    d = Grid()
    for (x0, y0), (x1, y1) in stems:
        for x, y in Grid().line(x0, y0, x1, y1, "x").where("x"):
            if g.get(x, y) == ".":
                d.put(x, y, "G")
    for cx, cy, ch in spk:
        on(g, ch, [(int(cx), int(cy - 1))], d, "+")
        on(g, ch, [(int(cx), int(cy + 1))], d, "-")
    return build(g, pal(P, None, T), d)


@item("soybeans")
def soybeans():
    P = mat("#e8d898", 0.09, hue=0.012)
    G = mat("#7a9a3a", 0.09)
    T = mat("#7a5a30", 0.08)
    g = Grid()
    pod = [(3.8, 8.0), (7.6, 2.0), (13.6, 4.2)]
    g.curve(pod, 1.8, 1.4, "G")
    for t in (0.2, 0.5, 0.8):
        (x, y), _ = bez_frame(pod, t)
        g.ellipse(x, y, 2.1, 2.1, "G")
    bean = [".54.", "5443", "4432", ".3g."]
    spots = [(2, 10), (7, 9), (11, 11)]
    d = Grid()
    for ox, oy in spots:
        for yy, r in enumerate(bean):
            for xx, ch in enumerate(r):
                if ch != ".":
                    g.put(ox + xx, oy + yy, "P")
                    d.put(ox + xx, oy + yy, ch)
    for x, y in cells(g, "G"):
        edge = any(g.get(x + dx, y + dy) == "." for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
        if edge and (x + y) % 2 == 0:
            d.put(x, y, "+")
    return build(g, pal(P, G, T), d, seam=None)


@item("strawberry")
def strawberry():
    P = mat("#e0303a", 0.11)
    G = mat("#4a8a2a", 0.10)
    Y = mat("#f2d24a", 0.06)
    shape = S(
        "................",
        "................",
        "................",
        "......GGGG......",
        "....GGGGGGGG....",
        "...PGPGGGGPGP...",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "..PPPPPPPPPPPP..",
        "...PPPPPPPPPP...",
        "...PPPPPPPPPP...",
        "....PPPPPPPP....",
        ".....PPPPPP.....",
        "......PPPP......",
        ".......PP.......",
    )
    detail = S(
        "................",
        "................",
        "........B.......",
        "................",
        "......d..c......",
        "................",
        "...w.n...n..n...",
        "...wn..n...n....",
        "...n..n..n...n..",
        "......n...n.....",
        "....n...n..n....",
        "......n...n.....",
        ".......n........",
    )
    return build(shape, pal(P, G, None, Y), detail)


@item("blueberries")
def blueberries():
    P = mat("#3a4aa0", 0.10, lift=0.02)
    K = mat("#9aa8d8", 0.06)
    spec = [(10.4, 5.4, 2.6, "p"), (5.0, 5.8, 2.6, "P"), (11.8, 10.6, 2.5, "U"), (3.6, 11.2, 2.4, "r"),
            (7.6, 9.8, 2.7, "R")]
    g = Grid()
    for cx, cy, r, ch in spec:
        g.ellipse(cx, cy, r, r, ch)
    d = Grid()
    for cx, cy, r, ch in spec:
        on(g, ch, [(int(cx + 0.3), int(cy - 0.2))], d, "1")
        on(g, ch, [(int(cx + 0.3) + 1, int(cy - 0.2)), (int(cx + 0.3), int(cy - 0.2) - 1)], d, "-")
        on(g, ch, [(int(cx - 1.4), int(cy - 1.4))], d, "m")
    return build(g, pal(P, None, None, K), d)


@item("raspberries")
def raspberries():
    P = mat("#d02a4a", 0.10)
    spec = [(10.8, 5.8, 3.0, 3.3, "p"), (5.0, 6.6, 3.0, 3.3, "P"), (8.2, 11.2, 3.2, 3.3, "R")]
    g = Grid()
    for cx, cy, rx, ry, ch in spec:
        g.ellipse(cx, cy, rx, ry, ch)
    d = Grid()
    for x, y in cells(g, "PpR"):
        if y % 2 == 0 and (x + (y // 2) % 2) % 2 == 0:
            d.put(x, y, "+")
            if g.get(x + 1, y + 1) == g.get(x, y):
                d.put(x + 1, y + 1, "-")
    d.pts([(4, 5), (10, 4), (7, 10)], "w")
    d.pts([(10, 2), (11, 2)], "1")
    return build(g, pal(P), d)


@item("blackberries")
def blackberries():
    P = mat("#3a2450", 0.10)
    G = mat("#4a7a2a", 0.10)
    spec = [(10.4, 9.4, 3.0, 3.6, "p"), (5.4, 8.2, 3.0, 3.6, "P")]
    g = Grid()
    for cx, cy, rx, ry, ch in spec:
        g.ellipse(cx, cy, rx, ry, ch)
    g.ellipse(5.4, 4.4, 2.2, 1.0, "G")
    d = Grid()
    for x, y in cells(g, "Pp"):
        if x % 2 == 0 and y % 2 == 1:
            d.put(x, y, "+")
        elif x % 2 == 1 and y % 2 == 0:
            d.put(x, y, "-")
    d.pts([(4, 7), (9, 8)], "w")
    d.put(6, 3, "C").put(7, 2, "C")
    return build(g, pal(P, G), d)


@item("cranberries")
def cranberries():
    P = mat("#b81a2a", 0.10)
    spec = [(8.2, 5.0, "p"), (4.5, 6.5, "P"), (11.6, 7.0, "R"), (10.0, 10.4, "U"), (6.4, 9.6, "r"),
            (3.6, 12.2, "u"), (7.6, 13.0, "V"), (11.6, 13.4, "v")]
    g = Grid()
    for cx, cy, ch in spec:
        g.ellipse(cx, cy, 1.9, 1.8, ch)
    d = Grid()
    for cx, cy, ch in spec:
        on(g, ch, [(int(cx - 0.8), int(cy - 0.8))], d, "w")
    return build(g, pal(P), d)


@item("grapes")
def grapes():
    P = mat("#6a2a6a", 0.10, lift=0.03)
    G = mat("#4f8a34", 0.10)
    T = mat("#7a5a2a", 0.09)
    g = Grid()
    g.ellipse(12.0, 3.0, 2.6, 1.7, "G", angle=-25)
    g.line(8, 4, 9, 2, "T").put(10, 2, "T")
    pos = [(8.2, 5.6), (5.0, 6.0), (11.2, 6.4), (3.8, 9.2), (9.8, 8.8), (6.6, 8.6), (8.4, 11.6),
           (5.2, 11.4), (6.8, 13.7)]
    keys = "pPRrUuvVP"
    for (cx, cy), ch in zip(pos, keys):
        g.ellipse(cx, cy, 1.75, 1.75, ch)
    d = Grid()
    for (cx, cy), ch in zip(pos, keys):
        on(g, ch, [(int(cx - 0.8), int(cy - 0.8))], d, "+")
    d.put(4, 6, "w").put(7, 5, "w")
    d.pts([(13, 6), (14, 6), (14, 7), (13, 8)], "C")
    on(g, "G", [(11, 3), (12, 3), (13, 2)], d, "+")
    return build(g, pal(P, G, T), d)


@item("pineapple")
def pineapple():
    P = mat("#e0a830", 0.10)
    G = mat("#3a7a3a", 0.10)
    g = Grid()
    g.capsule(6.6, 6.6, 2.6, 3.8, 0.9, 0.4, "h")
    g.capsule(9.0, 6.6, 13.0, 3.8, 0.9, 0.4, "M")
    g.capsule(7.2, 6.2, 4.6, 1.4, 1.0, 0.45, "g")
    g.capsule(8.4, 6.2, 11.2, 1.4, 1.0, 0.45, "H")
    g.capsule(7.8, 6.4, 7.8, 1.3, 1.0, 0.45, "G")
    g.ellipse(7.8, 10.8, 4.2, 4.4, "P")
    d = Grid()
    for x, y in cells(g, "P"):
        if (x + y) % 3 == 0 or (x - y) % 3 == 0:
            d.put(x, y, "-")
        elif (x + y) % 3 == 2 and (x - y) % 3 == 2:
            d.put(x, y, "+")
    return build(g, pal(P, G), d)


# =========================================================================== cash crops & herbs


@item("coffee_beans")
def coffee_beans():
    P = mat("#c02a2a", 0.11)
    T = mat("#b4ae74", 0.09)
    Z = mat("#6a3a1a", 0.08)
    g = Grid()
    g.ellipse(9.8, 4.8, 2.5, 2.5, "p").ellipse(5.0, 6.2, 2.7, 2.7, "P")
    g.ellipse(5.6, 11.6, 2.2, 3.0, "T", angle=35).ellipse(11.0, 10.8, 2.2, 3.0, "t", angle=-30)
    d = Grid()
    d.pts([(4, 5), (9, 4)], "w").pts([(5, 5), (3, 6)], "+")
    d.pts([(5, 3), (10, 2)], "Z")
    for (x, y) in [(7, 10), (6, 11), (5, 12), (4, 13)]:
        on(g, "T", [(x, y)], d, "f")
    for (x, y) in [(10, 9), (11, 10), (11, 11), (12, 12)]:
        on(g, "t", [(x, y)], d, "f")
    on(g, "T", [(5, 10), (4, 11)], d, "+")
    on(g, "t", [(10, 10), (9, 11)], d, "+")
    return build(g, pal(P, Z, T), d)


@item("tea_leaves")
def tea_leaves():
    """'Two leaves and a bud': the classic plucked tea shoot, bright and fresh."""
    P = mat("#4a8a2a", 0.10, lift=0.03)
    G = mat("#a8d070", 0.08)
    T = mat("#6a8a3a", 0.09)
    g = Grid()
    g.line(4, 14, 7, 8, "T").line(7, 8, 8, 5, "T")
    leaves = [("P", [(6.0, 11.0), (2.4, 10.6), (2.2, 5.2)], [0.6, 2.1, 2.3, 1.7, 0.3]),
              ("p", [(7.4, 9.4), (12.0, 10.6), (14.2, 5.6)], [0.6, 2.0, 2.3, 1.6, 0.3])]
    for ch, ctrl, prof in leaves:
        g.curve(ctrl, 0, ch=ch, profile=prof)
    g.curve([(8.0, 6.6), (8.4, 3.2), (10.4, 1.5)], 0, ch="G", profile=[1.0, 1.3, 1.1, 0.4])
    g.curve([(7.6, 6.4), (5.6, 4.4), (5.2, 2.2)], 0, ch="g", profile=[0.6, 1.0, 0.8, 0.3])
    d = Grid()
    for ch, ctrl, _ in leaves:
        for t in (0.2, 0.35, 0.5, 0.65, 0.8):
            x, y = bez(ctrl, t)
            on(g, ch, [(int(x), int(y))], d, "+")
        for x, y in cells(g, ch):
            edge = any(g.get(x + dx, y + dy) == "." for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
            if edge and (x * 3 + y) % 4 == 0:
                d.put(x, y, "-")
    d.pts([(3, 8), (12, 8)], "w")
    return build(g, pal(P, G, T), d)


@item("cotton")
def cotton():
    P = mat("#f6f4f0", 0.07, lift=-0.06)
    G = mat("#8a6a4a", 0.10)
    g = Grid()
    g.capsule(7.8, 12.0, 7.8, 14.2, 1.0, 0.6, "G")
    for (x1, y1) in [(1.6, 12.6), (14.2, 12.4), (1.2, 4.0), (14.4, 4.4), (8.0, 0.8)]:
        g.capsule(7.8, 8.4, x1, y1, 1.6, 0.5, "g")
    for cx, cy, r, ch in [(10.4, 5.8, 2.8, "p"), (5.4, 6.0, 2.8, "P"), (10.6, 10.0, 2.7, "r"),
                          (5.0, 10.0, 2.7, "R"), (7.8, 8.0, 2.4, "U")]:
        g.ellipse(cx, cy, r, r, ch)
    return build(g, pal(P, G))


@item("basil")
def basil():
    P = mat("#3a8a2a", 0.10, lift=0.05)
    T = mat("#5a8a2a", 0.09)
    g = Grid().line(3, 14, 10, 5, "T")
    leaves = [("P", [(5.0, 11.0), (2.4, 10.4), (2.6, 5.6)], [0.6, 2.1, 2.4, 1.8, 0.4]),
              ("p", [(6.0, 11.0), (9.0, 13.8), (13.2, 12.0)], [0.6, 2.0, 2.3, 1.7, 0.4]),
              ("R", [(8.0, 7.8), (5.0, 6.2), (5.4, 2.0)], [0.5, 1.8, 2.1, 1.4, 0.4]),
              ("r", [(8.6, 8.2), (12.4, 9.4), (14.6, 6.4)], [0.5, 1.8, 2.1, 1.4, 0.4]),
              ("U", [(10.0, 5.2), (10.4, 2.2), (12.8, 1.0)], [0.4, 1.3, 1.4, 0.4])]
    for ch, ctrl, prof in leaves:
        g.curve(ctrl, 0, ch=ch, profile=prof)
    d = Grid()
    for ch, ctrl, _ in leaves:
        for t in (0.25, 0.45, 0.65):
            x, y = bez(ctrl, t)
            on(g, ch, [(int(x), int(y))], d, "-")
    d.pts([(3, 8), (10, 12), (5, 4), (12, 8)], "w")
    return build(g, pal(P, None, T), d)


@item("mint")
def mint():
    P = mat("#52b452", 0.10, lift=0.04)
    T = mat("#6a8a3a", 0.09)
    g = Grid().line(7, 14, 8, 3, "T")
    leaves = [("U", [(8.0, 4.0), (7.2, 2.4), (8.4, 1.2)], [0.4, 1.2, 1.2, 0.3]),
              ("R", [(7.4, 6.0), (4.6, 5.6), (3.0, 3.4)], [0.5, 1.6, 1.8, 0.4]),
              ("r", [(8.6, 6.0), (11.4, 5.6), (13.0, 3.4)], [0.5, 1.6, 1.8, 0.4]),
              ("P", [(7.2, 10.6), (3.6, 10.8), (1.2, 8.2)], [0.5, 2.0, 2.3, 0.4]),
              ("p", [(8.6, 10.4), (12.2, 10.8), (14.6, 8.2)], [0.5, 2.0, 2.3, 0.4])]
    for ch, ctrl, prof in leaves:
        g.curve(ctrl, 0, ch=ch, profile=prof)
    d = Grid()
    for ch in "PpRr":
        for x, y in cells(g, ch):
            edge = any(g.get(x + dx, y + dy) == "." for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
            if edge and (x * 2 + y) % 3 == 0:
                d.put(x, y, "~")
            elif not edge and (x + y) % 2 == 0:
                d.put(x, y, "-")
    return build(g, pal(P, None, T), d)


@item("peppercorns")
def peppercorns():
    P = mat("#4a3e36", 0.10, lift=0.04)
    G = mat("#8a3a2a", 0.10)
    g = Grid()
    pos = [(7.8, 4.6, "V"), (5.4, 7.4, "U"), (10.2, 7.6, "g"), (3.2, 10.8, "P"), (7.8, 10.2, "G"),
           (12.4, 11.0, "u"), (5.6, 13.4, "p"), (10.2, 13.4, "R")]
    for cx, cy, ch in pos:
        g.ellipse(cx, cy, 1.9, 1.9, ch)
    d = Grid()
    rng = random.Random(9)
    for cx, cy, ch in pos:
        on(g, ch, [(int(cx - 0.8), int(cy - 0.8))], d, "w")
        on(g, ch, [(int(cx) + rng.choice((-1, 0)), int(cy) + 1)], d, "-")
    return build(g, pal(P, G), d)


# =========================================================================== tree fruit


@item("orange")
def orange():
    P = mat("#f08a1a", 0.10)
    G = mat("#3f7a2a", 0.10)
    g = Grid().ellipse(7.6, 9.2, 5.6, 5.4, "P")
    g.ellipse(11.0, 3.4, 2.6, 1.3, "G", angle=-25)
    d = Grid()
    for x, y in cells(g, "P"):
        if (x * 3 + y * 5) % 7 == 0:
            d.put(x, y, "-")
    d.put(8, 3, "B").put(8, 4, "b")
    d.pts([(4, 6), (5, 6), (4, 7)], "+")
    on(g, "G", [(10, 3), (11, 3)], d, "+")
    return build(g, pal(P, G), d)


@item("lemon")
def lemon():
    P = mat("#f2d83a", 0.10)
    g = Grid().ellipse(7.8, 8.4, 6.0, 4.0, "P", angle=-30)
    g.put(13, 4, "P").put(2, 12, "P")
    d = Grid()
    for x, y in cells(g, "P"):
        if (x * 3 + y * 5) % 9 == 0:
            d.put(x, y, "-")
    d.pts([(5, 7), (6, 6)], "+")
    return build(g, pal(P), d)


@item("lime")
def lime():
    P = mat("#6ab83a", 0.10)
    g = Grid().ellipse(7.6, 9.0, 4.6, 4.4, "P")
    g.put(11, 5, "P")
    d = Grid()
    for x, y in cells(g, "P"):
        if (x * 3 + y * 5) % 7 == 0:
            d.put(x, y, "-")
    d.put(12, 4, "4")
    d.pts([(5, 7)], "w")
    return build(g, pal(P), d)


@item("peach")
def peach():
    P = mat("#f4b26a", 0.10)
    G = mat("#e8684e", 0.10)
    g = Grid().ellipse(7.8, 9.2, 5.6, 5.4, "P")
    g.ellipse(11.2, 3.4, 2.6, 1.3, "T", angle=-25)
    d = Grid()
    for x, y in cells(g, "P"):
        k = x - 0.45 * y
        if k > 7.6 or (k > 6.2 and (x + y) % 2 == 0):
            d.put(x, y, "^")
    for x, y in [(8, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, 10), (8, 11)]:
        on(g, "P", [(x, y)], d, "-")
    for x, y in [(8, 6), (8, 7), (8, 8), (8, 9)]:
        on(g, "P", [(x, y)], d, "+")
    d.put(8, 3, "F").put(9, 2, "F")
    on(g, "T", [(10, 3), (11, 3)], d, "+")
    return build(g, pal(P, G, LEAF), d)


@item("pear")
def pear():
    P = mat("#c8d050", 0.10)
    K = mat("#9a8a3a", 0.08)
    g = Grid().ellipse(7.6, 10.4, 4.7, 4.3, "P").ellipse(8.2, 5.6, 2.6, 3.0, "P")
    d = Grid()
    rng = random.Random(11)
    for x, y in cells(g, "P"):
        if rng.random() < 0.08:
            d.put(x, y, "l")
    d.put(9, 1, "F").put(8, 2, "F")
    d.pts([(5, 8), (5, 9), (6, 7)], "+")
    return build(g, pal(P, None, TWIG, K), d)


@item("plum")
def plum():
    P = mat("#5a2a6a", 0.10, lift=0.04)
    K = mat("#a890c0", 0.06)
    g = Grid().ellipse(7.8, 9.0, 4.8, 5.2, "P", angle=-15)
    d = Grid()
    for x, y in [(4, 6), (5, 5), (6, 5), (4, 8), (7, 4), (5, 7)]:
        on(g, "P", [(x, y)], d, "m")
    for x, y in [(9, 5), (10, 6), (10, 7), (10, 8), (10, 9), (9, 10)]:
        on(g, "P", [(x, y)], d, "-")
    d.put(8, 2, "F").put(9, 3, "F")
    return build(g, pal(P, None, TWIG, K), d)


@item("cherries")
def cherries():
    P = mat("#b01a2a", 0.10)
    G = mat("#4a7a2a", 0.10)
    g = Grid().ellipse(4.8, 11.4, 2.8, 2.8, "P").ellipse(10.8, 11.8, 2.8, 2.8, "p")
    g.ellipse(11.6, 2.6, 2.4, 1.3, "G", angle=-20)
    d = Grid()
    for x, y in Grid().line(5, 8, 9, 2, "x").where("x") + Grid().line(10, 9, 9, 3, "x").where("x"):
        if g.get(x, y) == ".":
            d.put(x, y, "C")
    d.pts([(3, 10), (9, 10)], "w").pts([(4, 9), (10, 10)], "+")
    return build(g, pal(P, G), d)


@item("mango")
def mango():
    P = mat("#f2b02a", 0.10)
    G = mat("#e05a2a", 0.10)
    T = mat("#7aa03a", 0.10)
    g = Grid().ellipse(7.4, 9.0, 6.1, 4.8, "P", angle=-42)
    g.ellipse(10.2, 5.4, 2.6, 2.4, "P")
    d = Grid()
    for x, y in cells(g, "P"):
        s = x - y
        if s > 2 or (s > 0 and (x + y) % 2 == 0):
            d.put(x, y, "^")
    on(g, "P", [(12, 3), (11, 3)], d, "%")
    d.put(12, 2, "F").put(13, 1, "F")
    d.pts([(4, 9), (5, 8), (4, 10)], "+")
    return build(g, pal(P, G, T), d)


@item("avocado")
def avocado():
    P = mat("#3a5a2a", 0.10, lift=0.05)
    g = Grid().ellipse(7.6, 10.0, 4.7, 4.6, "P").ellipse(8.6, 5.4, 2.8, 3.2, "P")
    d = Grid()
    rng = random.Random(3)
    for x, y in cells(g, "P"):
        r = rng.random()
        if r < 0.16:
            d.put(x, y, "-")
        elif r < 0.26:
            d.put(x, y, "+")
    d.put(9, 1, "F").put(9, 2, "~")
    return build(g, pal(P, None, TWIG), d)


@item("banana")
def banana():
    P = mat("#f2d23a", 0.10)
    T = mat("#6a4a22", 0.08)
    ctrl = [(2.0, 10.6), (10.6, 12.2), (12.6, 2.6)]
    g = Grid().curve(ctrl, 0, ch="P", profile=[0.6, 1.5, 2.0, 2.1, 1.8, 1.1])
    g.capsule(12.6, 2.8, 13.3, 1.5, 0.75, 0.6, "T")
    d = Grid()
    for t in [0.2, 0.35, 0.5, 0.65, 0.8]:
        (x, y), (nx, ny) = bez_frame(ctrl, t)
        on(g, "P", [(int(x - nx * 1.0), int(y - ny * 1.0))], d, "-")
    d.put(1, 10, "%").put(2, 10, "%")
    return build(g, pal(P, None, T), d)


@item("olives")
def olives():
    P = mat("#8a9a32", 0.10)
    G = mat("#3a2a34", 0.10, lift=0.08)
    K = mat("#a8c098", 0.08)
    g = Grid()
    g.line(2, 4, 13, 1, "T")
    g.curve([(6.0, 3.0), (8.6, 4.8), (11.6, 5.0)], 0, ch="K", profile=[0.5, 1.1, 0.9, 0.3])
    g.curve([(9.6, 2.0), (12.0, 3.6), (14.6, 3.6)], 0, ch="k", profile=[0.5, 1.0, 0.8, 0.3])
    g.ellipse(4.6, 8.6, 2.1, 2.7, "P", angle=-25)
    g.ellipse(10.6, 9.2, 2.1, 2.7, "G", angle=20)
    g.ellipse(4.4, 13.2, 2.1, 2.4, "g", angle=65)
    g.ellipse(9.0, 13.2, 2.1, 2.6, "p", angle=-55)
    d = Grid()
    d.pts([(4, 7), (10, 8), (4, 12), (8, 12)], "w")
    on(g, "Kk", [(7, 3), (8, 4), (11, 3), (12, 3)], d, "+")
    return build(g, pal(P, G, TWIG, K), d)
