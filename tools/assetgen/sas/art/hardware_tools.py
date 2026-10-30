"""Hardware lane: 16x16 tool item sprites (knives, sickles, watering can, mortar, fertilizer).

Every sprite is hand-placed ASCII art; letters index per-material ramps so the four/five
tiers of a family share one silhouette and only differ in material colours (like vanilla
swords/hoes). Outlines are added by :func:`outline_material`: a dark, hue-shifted tone of the
adjacent material, slightly lighter on the top-left edges, darkest on the bottom-right.
"""
from __future__ import annotations

from pathlib import Path

from .core import Color, Sprite, hexc, shade

# --------------------------------------------------------------------------- materials
# Each ramp: [outline, 1 dark, 2, 3 mid, 4 light, 5 highlight]

RAMPS: dict[str, list[str]] = {
    "iron": ["#2e3036", "#5a5d66", "#878a93", "#b1b4bb", "#d6d8dc", "#f6f7f9"],
    "gold": ["#4e2e08", "#9a5a0c", "#cf8a14", "#ecb422", "#f9da4e", "#fff6b0"],
    "diamond": ["#07302c", "#106457", "#1a9584", "#2ac7ad", "#5eeed6", "#cbfff6"],
    "netherite": ["#160f13", "#2b2228", "#40353d", "#564a53", "#6f646c", "#91868d"],
    "flint": ["#111113", "#252427", "#38373b", "#525156", "#76757b", "#a6a5ab"],
    "wood": ["#26170a", "#452b15", "#644223", "#83592f", "#a2733e", "#bf8f55"],
    "stick": ["#241a09", "#3f2f12", "#5e461b", "#7f6125", "#9a7830", "#b4913e"],
    "darkwood": ["#120b0d", "#251a1c", "#382a2c", "#4d3b3c", "#644f4e", "#7a6462"],
    "copper": ["#4a1e12", "#8a3c24", "#b4552f", "#d8774a", "#f0996a", "#ffc6a6"],
    "patina": ["#123a34", "#2a7064", "#3f9a86", "#58b8a0", "#86d8c0", "#c0f0e0"],
    "stone": ["#2a2a2e", "#4f4f55", "#6c6c72", "#8c8c92", "#acacb0", "#cdcdd0"],
    "burlap": ["#3a2812", "#6e5230", "#8e6e44", "#ab8a58", "#c6a771", "#dcc290"],
    "twine": ["#3a2a12", "#7a6236", "#a08654", "#c4ad78", "#ddc996", "#efe2b8"],
    "soil": ["#120a06", "#24160c", "#352212", "#4a311b", "#5e4026", "#755233"],
    "leaf": ["#14300e", "#24521a", "#357224", "#4a8f2e", "#68ad3e", "#93cc5c"],
    "white": ["#4a4a52", "#9a9aa4", "#c4c4cc", "#dedee4", "#f0f0f4", "#ffffff"],
    "netherite_gold": ["#3a2408", "#7a5418", "#a8782a", "#c89a42", "#e0bc66", "#f4dc9a"],
}


def ramp_of(name: str) -> list[Color]:
    return [hexc(c) for c in RAMPS[name]]


class Pal:
    """Palette builder: maps chars -> colours and remembers each colour's outline tone."""

    def __init__(self):
        self.chars: dict[str, Color] = {}
        self.outline: dict[Color, Color] = {}

    def add(self, chars: str, material: str, start: int = 1) -> "Pal":
        """``chars[i]`` -> ramp[start+i] of ``material``."""
        r = ramp_of(material)
        for i, ch in enumerate(chars):
            c = r[start + i]
            self.chars[ch] = c
            self.outline.setdefault(c, r[0])
        return self

    def put(self, ch: str, color: str | Color, outline: str | Color | None = None) -> "Pal":
        c = hexc(color) if isinstance(color, str) else color
        self.chars[ch] = c
        self.outline[c] = (hexc(outline) if isinstance(outline, str) else outline) if outline else shade(c, -0.38)
        return self


def draw(rows: list[str], pal: Pal) -> Sprite:
    s = Sprite(16, 16)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal.chars:
                s.set(x, y, pal.chars[ch])
    return s


def outline_material(s: Sprite, pal: Pal, light_lift: float = 0.06) -> Sprite:
    """4-connected outline using each neighbour's material outline colour.

    Pixels on the top/left side of the silhouette get a slightly lifted tone; bottom/right
    edges keep the darkest tone (vanilla convention)."""
    out = s.copy()
    for y in range(s.h):
        for x in range(s.w):
            if s.opaque(x, y):
                continue
            dark_src = light_src = None
            for dx, dy in ((-1, 0), (0, -1)):        # shape is left/above -> we are bottom/right edge
                if s.opaque(x + dx, y + dy):
                    dark_src = s.get(x + dx, y + dy)
            for dx, dy in ((1, 0), (0, 1)):          # shape is right/below -> top/left edge
                if s.opaque(x + dx, y + dy):
                    light_src = s.get(x + dx, y + dy)
            src = dark_src or light_src
            if src is None:
                continue
            base = pal.outline.get(src) or shade(src, -0.38)
            if dark_src is None:
                base = shade(base, light_lift, hue_shift=0.01)
            out.px[y][x] = base
    return out


# --------------------------------------------------------------------------- knives
# Chef's-knife profile: straight spine (top-left), curved belly toward the tip, the edge
# dropping one pixel below the handle line, a metal bolster and a riveted wooden handle.

KNIFE = [
    "................",
    "..............T.",
    ".............43.",
    "............543.",
    "...........4432.",
    "..........4432..",
    ".........4432...",
    "........4432....",
    ".......4321.....",
    "......BbbC......",
    ".....Hh.........",
    "....Hr..........",
    "...Jh...........",
    "..Hr............",
    ".Hh.............",
    "................",
]

# flint: knapped blade (facets + two chips in the edge) lashed to a stick with twine
FLINT_KNIFE = [
    "................",
    "..............4.",
    ".............53.",
    "............432.",
    "...........542..",
    "..........4321..",
    ".........5432...",
    "........4322....",
    ".......5321.....",
    "......wWwW......",
    ".....Wwh........",
    "....Hh..........",
    "...Jh...........",
    "..Hh............",
    ".Hh.............",
    "................",
]

KNIFE_TIERS = {
    # id: (blade ramp, handle ramp, bolster/rivet ramp)
    "iron_knife": ("iron", "wood", "iron"),
    "golden_knife": ("gold", "wood", "gold"),
    "diamond_knife": ("diamond", "wood", "iron"),
    "netherite_knife": ("netherite", "darkwood", "netherite_gold"),
}

BLADE_CHARS = set("12345T")


def _edge_pixels(rows: list[str], ys: range) -> list[tuple[int, int]]:
    """Right-most blade pixel of each row = the cutting edge of a diagonal knife."""
    out = []
    for y in ys:
        xs = [x for x, ch in enumerate(rows[y]) if ch in BLADE_CHARS]
        if xs:
            out.append((max(xs), y))
    return out


def knife(blade: str, handle: str, metal: str) -> Sprite:
    p = Pal().add("12345", blade)
    p.put("T", ramp_of(blade)[4], ramp_of(blade)[0])
    p.add("hHJ", handle, 2)
    b = ramp_of(metal)
    p.put("B", b[4], b[0]).put("b", b[2], b[0]).put("C", b[1], b[0]).put("r", b[4], ramp_of(handle)[0])
    s = draw(KNIFE, p)
    if blade == "netherite":
        # gold-ish honed edge running along the whole cutting edge
        g = ramp_of("netherite_gold")
        for i, (x, y) in enumerate(_edge_pixels(KNIFE, range(1, 9))):
            s.set(x, y, g[3] if i < 2 else g[2])
    return outline_material(s, p)


def flint_knife() -> Sprite:
    p = Pal().add("12345", "flint")
    p.add("hHJ", "stick", 2)
    p.add("wW", "twine", 1)
    return outline_material(draw(FLINT_KNIFE, p), p)


# --------------------------------------------------------------------------- sickles
# Crescent blade sweeping up and over from a riveted ferrule; the inner curve is the edge.

SICKLE = [
    "................",
    ".........4445...",
    ".......44333332.",
    "......453....32.",
    ".....443......2.",
    ".....43.......2.",
    ".....43.......2.",
    ".....43......21.",
    ".....43......1..",
    ".....F32........",
    "....HfF.........",
    "...Hh...........",
    "..Jh............",
    ".Hh.............",
    "................",
    "................",
]

# inner (cutting) edge of the crescent, used for the netherite gold edge
SICKLE_EDGE = [(9, 2), (10, 2), (11, 2), (12, 2), (13, 3), (14, 4), (14, 5), (14, 6), (13, 7), (13, 8)]

SICKLE_TIERS = {
    "iron_sickle": ("iron", "wood", "iron"),
    "golden_sickle": ("gold", "wood", "gold"),
    "diamond_sickle": ("diamond", "wood", "iron"),
    "netherite_sickle": ("netherite", "darkwood", "netherite_gold"),
}


def sickle(blade: str, handle: str, metal: str) -> Sprite:
    p = Pal().add("12345", blade)
    p.put("T", ramp_of(blade)[5], ramp_of(blade)[0])
    p.add("hHJ", handle, 2)
    m = ramp_of(metal)
    p.put("F", m[3], m[0]).put("f", m[1], m[0])
    s = draw(SICKLE, p)
    if blade == "netherite":
        g = ramp_of("netherite_gold")
        for i, (x, y) in enumerate(SICKLE_EDGE[4:]):
            s.set(x, y, g[2] if i % 3 else g[3])
    return outline_material(s, p)


# --------------------------------------------------------------------------- watering can

WATERING_CAN = [
    "................",
    "................",
    "....aAAa....ROR.",
    "...a....a..RooR.",
    "...A....a...RR..",
    "...a....a...s2..",
    "..5a4554a..s2...",
    "..5444444..s2...",
    "..4555554.s2....",
    "..4333332.s2....",
    "..4333332s2.....",
    "..4p333221......",
    "..4ppq3221......",
    "...2q2221.......",
    "................",
    "................",
]


def watering_can() -> Sprite:
    p = Pal().add("12345", "copper")
    c = ramp_of("copper")
    p.put("a", c[2], c[0]).put("A", c[4], c[0])          # handle
    p.put("s", c[3], c[0])                                 # spout
    p.put("R", c[2], c[0]).put("O", c[4], c[0]).put("o", "#3a1810", c[0])   # rose + holes
    pt = ramp_of("patina")
    p.put("p", pt[3], pt[0]).put("q", pt[2], pt[0])
    return outline_material(draw(WATERING_CAN, p), p)


# --------------------------------------------------------------------------- mortar & pestle

MORTAR = [
    "................",
    "............JW..",
    "...........JHh..",
    "..........JHh...",
    ".........JHh....",
    "........JHh.....",
    "...5544JHh4433..",
    "..54ddJHhddd432.",
    "..4ddddhdddddd2.",
    "..54ddddddddd32.",
    "..454444443332..",
    "...4333332222...",
    "....43322221....",
    "....54333221....",
    "................",
    "................",
]


def mortar_and_pestle() -> Sprite:
    p = Pal().add("12345", "stone")
    p.put("d", "#38383e", ramp_of("stone")[0])             # bowl interior shadow
    p.add("hHJ", "wood", 3)
    p.put("W", ramp_of("wood")[5], ramp_of("wood")[0])
    return outline_material(draw(MORTAR, p), p)


# --------------------------------------------------------------------------- fertilizer

FERTILIZER = [
    "................",
    "................",
    ".....5.4.5......",
    ".....44344......",
    "......ttT.......",
    ".....43332......",
    "....4343332.....",
    "...543L3L232....",
    "...43LlL33321...",
    "...4343l32321...",
    "...434l333221...",
    "...4333232221...",
    "....3322222cxc..",
    ".....22211cgcxc.",
    "..........cxcgc.",
    "................",
]


def fertilizer() -> Sprite:
    p = Pal().add("12345", "burlap")
    tw = ramp_of("twine")
    p.put("t", tw[2], tw[0]).put("T", tw[4], tw[0])
    lf = ramp_of("leaf")
    p.put("L", lf[4], lf[0]).put("l", lf[2], lf[0])
    so = ramp_of("soil")
    p.put("c", so[3], so[0]).put("x", so[1], so[0])
    p.put("g", "#f2efe6", so[0])
    return outline_material(draw(FERTILIZER, p), p)


# --------------------------------------------------------------------------- registry


def all_tools() -> dict[str, Sprite]:
    out: dict[str, Sprite] = {"flint_knife": flint_knife()}
    for tid, (b, h, m) in KNIFE_TIERS.items():
        out[tid] = knife(b, h, m)
    for tid, (b, h, m) in SICKLE_TIERS.items():
        out[tid] = sickle(b, h, m)
    out["watering_can"] = watering_can()
    out["mortar_and_pestle"] = mortar_and_pestle()
    out["fertilizer"] = fertilizer()
    return out


def generate(textures_dir: Path) -> list[Path]:
    paths = []
    for tid, spr in all_tools().items():
        paths.append(spr.save(textures_dir / "item" / f"{tid}.png"))
    return paths
