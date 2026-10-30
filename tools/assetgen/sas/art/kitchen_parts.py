"""Reusable food parts (drawn without outline) shared by plates, handhelds and ingredients."""
from __future__ import annotations

from .core import Sprite
from .kitchen_kit import BASIL, C, puts, rp, stamp

# ---------------------------------------------------------------- palettes
EGG = {"h": "#ffffff", "w": "#f8f5ec", "s": "#e4ddcc", "e": "#c8a878", "y": "#f6b21c", "Y": "#fcd860",
       "o": "#d8840e"}
BACON_RAW = {"m": "#e8908a", "M": "#c8605e", "f": "#f8e0d4", "F": "#e8c4b4", "d": "#a84848"}
BACON_COOKED = {"m": "#b04a22", "M": "#8a3218", "f": "#eaa868", "F": "#d08848", "d": "#6a2412"}
LEMON = {"r": "#f2d83a", "R": "#c8a81a", "p": "#fcf2a0", "w": "#fffce8", "s": "#e8c830"}
BROCCOLI = {"h": "#82c050", "l": "#559e34", "b": "#3c7c28", "d": "#28581c", "s": "#a8d07a", "S": "#7aa850"}
TOAST = {"c": "#9a5a1e", "C": "#b8762e", "t": "#e8b868", "T": "#f2cc84", "d": "#c8904a"}
POTATO_SKIN = {"h": "#c8945a", "l": "#a87440", "b": "#8a5a2e", "d": "#5e3c1c"}


def fried_egg(s: Sprite, x: int, y: int, big: bool = True) -> None:
    """Sunny-side-up egg seen from above at 3/4: lacy white, glossy yolk."""
    if big:
        rows = [
            "..wwwhw...",
            ".whwwwwwe.",
            "wwwwYyywww",
            "wwwYyyyows",
            ".wwwyoowse",
            "..ewwssse.",
        ]
    else:
        rows = [
            ".whww.",
            "wwYyws",
            "wwyows",
            ".esse.",
        ]
    stamp(s, rows, EGG, x, y)


def bacon_strip(s: Sprite, x: int, y: int, cooked: bool = True, length: int = 9) -> None:
    """Wavy horizontal strip: meat / fat / meat bands."""
    pal = BACON_COOKED if cooked else BACON_RAW
    for i in range(length):
        dy = (0, 0, 1, 1)[i % 4] if cooked else (0, 0, 0, 1, 1, 1)[i % 6]
        col = x + i
        s.set(col, y + dy, C(pal["m"] if i % 3 else pal["M"]))
        s.set(col, y + dy + 1, C(pal["f"] if i % 4 else pal["F"]))
        s.set(col, y + dy + 2, C(pal["M"] if i % 2 else pal["d"]))


def lemon_wedge(s: Sprite, x: int, y: int) -> None:
    rows = [
        ".rrr.",
        "rppwr",
        "Rpsps",
        ".RRR.",
    ]
    stamp(s, rows, LEMON, x, y)


def broccoli(s: Sprite, x: int, y: int, small: bool = False) -> None:
    rows = [".hl.", "hlbb", "lbbd", ".sS."] if not small else ["hl", "bd", "s."]
    stamp(s, rows, BROCCOLI, x, y)


def basil(s: Sprite, x: int, y: int, flip: bool = False) -> None:
    rows = [".ll", "lbd", "dd."] if not flip else ["ll.", "dbl", ".dd"]
    stamp(s, rows, {"l": BASIL[3], "b": BASIL[2], "d": BASIL[1]}, x, y)


def tomato_slice(s: Sprite, x: int, y: int) -> None:
    rows = [
        ".RRR.",
        "RfsfR",
        "RsfsR",
        ".rrr.",
    ]
    stamp(s, rows, {"R": "#d8322a", "r": "#a8201a", "f": "#f07a5a", "s": "#f8c870"}, x, y)


def lettuce_frill(s: Sprite, x0: int, x1: int, y: int) -> None:
    """Wavy lettuce edge peeking out between layers."""
    pal = ["#4f9a2e", "#7cc04a", "#a8dc6a"]
    for x in range(x0, x1 + 1):
        dy = (0, 1, 1, 0)[x % 4]
        s.set(x, y + dy, C(pal[1] if x % 3 else pal[2]))
        if dy == 0:
            s.set(x, y + 1, C(pal[0]))


def cheese_slice_drip(s: Sprite, x0: int, x1: int, y: int, drips=(2, 6)) -> None:
    pal = rp("#f2b82a", 4, 0.09)
    for x in range(x0, x1 + 1):
        s.set(x, y, pal[2] if x > x0 else pal[3])
    for d in drips:
        s.set(x0 + d, y + 1, pal[2])
        s.set(x0 + d, y + 2, pal[1])


def sesame(s: Sprite, pts) -> None:
    puts(s, pts, "#fbf4dc")
