"""Pixel-art kit for the *produce* lane (items, seeds, crates).

Builds on :mod:`sas.art.core` (never edits it).  The central idea: sprites are
hand-drawn as 16 ASCII rows whose letters are *tones of a material*, e.g.
``1..5`` = darkest..lightest tone of the primary material.  :func:`render`
then adds a vanilla-style 1 px outline whose colour comes from the material
it touches and whose value depends on the edge direction (lighter on the
top-left, darkest on the bottom-right).

Letter scheme used by :func:`pal` (``.``/space = transparent)::

    primary     1 2 3 4 5   ink 0   glint w   no-outline overlay: 6 7 8 9 (=1..4)
    secondary   a b c d e   ink z           overlay A B C D E,  ink Z
    tertiary    f g h i j   ink y           overlay F G H I J,  ink Y
    quaternary  k l m n o   ink x           overlay K L M N O,  ink X
    W = glint overlay (does not cast an outline)

"Overlay" pixels are drawn after the outline and never get one: use them for
1 px stems, awns, tendrils and seeds.
"""
from __future__ import annotations

import colorsys
from dataclasses import dataclass

from PIL import Image

from .core import Color, Sprite, hexc, mix

WHITE: Color = (255, 255, 255, 255)


# --------------------------------------------------------------------------- colour helpers


def _c(c) -> Color:
    return hexc(c) if isinstance(c, str) else c


def hls_adjust(c, l_mul: float = 1.0, l_add: float = 0.0, hue: float = 0.0, sat: float = 0.0) -> Color:
    c = _c(c)
    h, l, s = colorsys.rgb_to_hls(c[0] / 255, c[1] / 255, c[2] / 255)
    l = max(0.0, min(1.0, l * l_mul + l_add))
    s = max(0.0, min(1.0, s + sat))
    r, g, b = colorsys.hls_to_rgb((h + hue) % 1.0, l, s)
    return (round(r * 255), round(g * 255), round(b * 255), c[3])


def toward(c, target_hue: float, amount: float) -> float:
    """Signed hue delta that rotates ``c`` toward ``target_hue`` by at most ``amount``."""
    h = colorsys.rgb_to_hls(*(v / 255 for v in _c(c)[:3]))[0]
    d = ((target_hue - h + 0.5) % 1.0) - 0.5
    return max(-amount, min(amount, d))


def tone(c, dl: float, hue_amt: float = 0.045, sat: float | None = None) -> Color:
    """Hue-shifted lighten/darken: darker -> toward blue/purple, lighter -> toward yellow."""
    c = _c(c)
    if dl == 0:
        return c
    target = 1 / 6 if dl > 0 else 0.70
    dh = toward(c, target, abs(dl) * hue_amt * 4)
    ds = (0.06 * -dl if dl < 0 else -0.10 * dl) if sat is None else sat
    return hls_adjust(c, l_add=dl, hue=dh, sat=ds)


@dataclass
class Mat:
    """A material: a 5-tone ramp (dark -> light), outline tones and a glint colour."""

    ramp: list[Color]
    ol: tuple[Color, Color, Color]   # top-left / side / bottom-right outline
    glint: Color

    @property
    def ink(self) -> Color:
        return self.ol[1]


def mat(base, spread: float = 0.10, *, lift: float = 0.0, hue: float = 0.045, ramp=None,
        ol: tuple[float, float, float] = (0.66, 0.50, 0.38), ol_sat: float = 0.12, glint=None,
        steps: tuple[float, ...] | None = None) -> Mat:
    """Build a material from a base colour.

    ``steps`` are lightness offsets for the 5 tones (default ``-2..2 * spread``);
    ``ol`` are lightness multipliers of the base for the three outline tones.
    """
    base = _c(base)
    if ramp is not None:
        r = [_c(c) for c in ramp]
    else:
        steps = steps or tuple((i - 2) * spread + lift for i in range(5))
        r = [tone(base, s, hue) for s in steps]
    olc = tuple(hls_adjust(base, l_mul=m, hue=toward(base, 0.72, 0.06 * (1 - m) * 2), sat=ol_sat) for m in ol)
    g = _c(glint) if glint is not None else mix(r[4], WHITE, 0.62)
    return Mat(r, olc, g)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- palette & render

Entry = tuple  # (colour, mat | None, casts_outline: bool)

_SLOTS = {
    "P": ("12345", "0", "6789"),
    "S": ("abcde", "z", "ABCDE"),
    "T": ("fghij", "y", "FGHIJ"),
    "Q": ("klmno", "x", "KLMNO"),
}
_INK_OVERLAY = {"S": "Z", "T": "Y", "Q": "X"}


def pal(P: Mat | None = None, S: Mat | None = None, T: Mat | None = None, Q: Mat | None = None,
        glint: Color | str | None = None, **extra) -> dict[str, Entry]:
    """Standard letter palette.  ``extra`` maps single chars to colour / (colour, mat, cast)."""
    out: dict[str, Entry] = {}
    for key, m in (("P", P), ("S", S), ("T", T), ("Q", Q)):
        if m is None:
            continue
        tones, ink, over = _SLOTS[key]
        for i, ch in enumerate(tones):
            out[ch] = (m.ramp[i], m, True)
        out[ink] = (m.ink, m, True)
        for i, ch in enumerate(over):
            out[ch] = (m.ramp[i], m, False)
        if key in _INK_OVERLAY:
            out[_INK_OVERLAY[key]] = (m.ink, m, False)
    if P is not None:
        g = _c(glint) if glint is not None else P.glint
        out["w"] = (g, P, True)
        out["W"] = (g, P, False)
    for ch, v in extra.items():
        if isinstance(v, tuple) and len(v) == 3 and not isinstance(v[0], int):
            out[ch] = (_c(v[0]), v[1], v[2])
        elif isinstance(v, tuple) and len(v) == 3 and isinstance(v[0], tuple):
            out[ch] = v
        else:
            out[ch] = (_c(v), None, True)
    return out


def ov(c, m: Mat | None = None) -> Entry:
    """Palette entry for an overlay (no outline) colour."""
    return (_c(c), m, False)


def render(rows: list[str], palette: dict[str, Entry], outline: bool = True, w: int = 16, h: int = 16,
           ol_bias: float = 0.0) -> Sprite:
    """Render ASCII rows.  Unknown characters (``.``, `` ``) are transparent."""
    s = Sprite(w, h)
    mats: list[list[Mat | None]] = [[None] * w for _ in range(h)]
    cast = [[False] * w for _ in range(h)]
    overlay: list[tuple[int, int, Color]] = []
    for y, row in enumerate(rows[:h]):
        for x, ch in enumerate(row[:w]):
            e = palette.get(ch)
            if e is None:
                continue
            col, m, c = e
            if c:
                s.px[y][x] = col
                mats[y][x] = m
                cast[y][x] = True
            else:
                overlay.append((x, y, col))
    if outline:
        add = []
        for y in range(h):
            for x in range(w):
                if s.px[y][x][3]:
                    continue
                nx = ny = 0
                seen: dict[int, tuple[int, Mat | None, Color]] = {}
                for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    qx, qy = x + dx, y + dy
                    if 0 <= qx < w and 0 <= qy < h and cast[qy][qx]:
                        nx -= dx
                        ny -= dy
                        m = mats[qy][qx]
                        k = id(m) if m is not None else hash(s.px[qy][qx])
                        cnt = seen.get(k, (0, m, s.px[qy][qx]))
                        seen[k] = (cnt[0] + 1, m, s.px[qy][qx])
                if not seen:
                    continue
                _, m, src = max(seen.values(), key=lambda t: t[0])
                score = nx + ny + ol_bias
                idx = 0 if score < 0 else (1 if score == 0 else 2)
                if m is not None:
                    col = m.ol[idx]
                else:
                    col = hls_adjust(src, l_mul=(0.66, 0.5, 0.38)[idx], sat=0.1)
                add.append((x, y, col))
        for x, y, col in add:
            s.px[y][x] = col
    for x, y, col in overlay:
        s.px[y][x] = col
    return s


# --------------------------------------------------------------------------- form shading

# shape-layer letters -> (material slot, part id).  Different parts of the same material
# (e.g. neighbouring berries) are shaded as separate volumes.
SHAPE_KEYS = {
    "P": ("P", 0), "p": ("P", 1), "R": ("P", 2), "r": ("P", 3), "U": ("P", 4), "u": ("P", 5),
    "V": ("P", 6), "v": ("P", 7),
    "G": ("S", 0), "g": ("S", 1), "H": ("S", 2), "h": ("S", 3), "M": ("S", 4), "m": ("S", 5),
    "T": ("T", 0), "t": ("T", 1), "Y": ("T", 2), "y": ("T", 3),
    "K": ("Q", 0), "k": ("Q", 1), "N": ("Q", 2), "n": ("Q", 3),
}
_TONES = {"P": "12345", "S": "abcde", "T": "fghij", "Q": "klmno"}


def _dist_field(mask: list[list[bool]], w: int, h: int) -> list[list[float]]:
    edge = [(x, y) for y in range(-1, h + 1) for x in range(-1, w + 1)
            if not (0 <= x < w and 0 <= y < h and mask[y][x])]
    out = [[0.0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if mask[y][x]:
                out[y][x] = min(((x - ex) ** 2 + (y - ey) ** 2) ** 0.5 for ex, ey in edge
                                if abs(x - ex) < 9 and abs(y - ey) < 9)
    return out


def shade_rows(shape: list[str], light=(-0.62, -0.78), z: float = 1.3, bias: dict | float = 0.0,
               cut: tuple[float, float, float, float] = (-0.35, 0.05, 0.42, 0.58), keys: dict | None = None,
               flat: dict | float = 0.0, seam: str | None = None, seam_tone: int = 0,
               w: int = 16, h: int = 16) -> list[str]:
    """Turn a silhouette (part letters) into tone rows using distance-field normals.

    ``bias`` (per slot or global) brightens/darkens a material, ``flat`` (0..1) reduces
    the form contrast, ``cut`` are the intensity thresholds for tones 2..5.
    """
    keys = keys or SHAPE_KEYS
    rows = [r.ljust(w, ".")[:w] for r in shape] + ["." * w] * (h - len(shape))
    parts: dict[tuple, list[tuple[int, int]]] = {}
    for y in range(h):
        for x in range(w):
            k = keys.get(rows[y][x])
            if k:
                parts.setdefault(k, []).append((x, y))
    out = [["."] * w for _ in range(h)]
    lx, ly = light
    norm = (lx * lx + ly * ly + z * z) ** 0.5
    L = (lx / norm, ly / norm, z / norm)
    for (slot, _pid), pts in parts.items():
        mask = [[False] * w for _ in range(h)]
        for x, y in pts:
            mask[y][x] = True
        d = _dist_field(mask, w, h)
        R = max(max(d[y][x] for x, y in pts), 1.0)
        hf = [[0.0] * w for _ in range(h)]
        for x, y in pts:
            t = min(d[y][x] / R, 1.0)
            hf[y][x] = (1 - (1 - t) ** 2) ** 0.5
        b = bias.get(slot, 0.0) if isinstance(bias, dict) else bias
        fl = flat.get(slot, 0.0) if isinstance(flat, dict) else flat

        def H(x, y):
            return hf[y][x] if 0 <= x < w and 0 <= y < h else 0.0

        for x, y in pts:
            gx = (H(x + 1, y) - H(x - 1, y)) / 2 * R * 0.9
            gy = (H(x, y + 1) - H(x, y - 1)) / 2 * R * 0.9
            n = (-gx, -gy, 1.0)
            nn = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
            I = (n[0] * L[0] + n[1] * L[1] + n[2] * L[2]) / nn
            I = (I - L[2]) * (1 - fl) + L[2] - 0.35 + b
            # map: I relative to flat-facing (L[2]-0.35)
            ti = sum(1 for c in cut if I > c)
            out[y][x] = _TONES[slot][ti]
    if seam:
        # occlusion seams: a pixel of a part that touches a part drawn later (in front) darkens
        rank = {ch: i for i, ch in enumerate(seam)}
        for y in range(h):
            for x in range(w):
                ch = rows[y][x]
                if ch not in rank or ch not in keys:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    qx, qy = x + dx, y + dy
                    if 0 <= qx < w and 0 <= qy < h:
                        o = rows[qy][qx]
                        if o in rank and rank[o] > rank[ch] and keys.get(o) != keys.get(ch):
                            out[y][x] = _TONES[keys[ch][0]][seam_tone]
                            break
    return ["".join(r) for r in out]


_SEQS = ("12345", "abcde", "fghij", "klmno")


def adj(ch: str, d: int) -> str:
    """Move a tone letter ``d`` steps along its ramp (clamped)."""
    for seq in _SEQS:
        if ch in seq:
            return seq[max(0, min(4, seq.index(ch) + d))]
    return ch


_ADJ = {"-": -1, "=": -2, "+": 1, "*": 2}
_SWAP = {"#": 0, "^": 1, "%": 2, "&": 3}


def swap(ch: str, target: int) -> str:
    """Same tone index, different material ramp (P/S/T/Q)."""
    for seq in _SEQS:
        if ch in seq:
            return _SEQS[target][seq.index(ch)]
    return ch


def apply_detail(base: list[str], detail: list[str] | None, w: int = 16) -> list[str]:
    """Detail layer: tone letters replace, ``-``/``=`` darken 1/2 steps, ``+``/``*`` lighten,
    ``~`` erases, ``.``/space keep."""
    if not detail:
        return base
    out = []
    for y in range(max(len(base), len(detail))):
        b = base[y].ljust(w, ".") if y < len(base) else "." * w
        d = detail[y].ljust(w, ".") if y < len(detail) else "." * w
        row = []
        for bc, dc in zip(b, d):
            if dc in ". ":
                row.append(bc)
            elif dc in _ADJ:
                row.append(adj(bc, _ADJ[dc]))
            elif dc in _SWAP:
                row.append(swap(bc, _SWAP[dc]))
            elif dc == "~":
                row.append(".")
            else:
                row.append(dc)
        out.append("".join(row))
    return out


class Grid:
    """A 16x16 character canvas for composing silhouettes / detail layers from primitives."""

    def __init__(self, rows: list[str] | None = None, w: int = 16, h: int = 16):
        self.w, self.h = w, h
        self.g = [["."] * w for _ in range(h)]
        self.order: list[str] = []          # first-draw order of characters (back -> front)
        if rows:
            self.rows(rows)

    def _seen(self, ch: str) -> None:
        if ch not in ". " and ch not in self.order:
            self.order.append(ch)

    def put(self, x: int, y: int, ch: str) -> "Grid":
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = ch
            self._seen(ch)
        return self

    def get(self, x: int, y: int) -> str:
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else "."

    def rows(self, rows: list[str], ox: int = 0, oy: int = 0) -> "Grid":
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch not in ". ":
                    self.put(x + ox, y + oy, ch)
        return self

    def pts(self, pts, ch: str) -> "Grid":
        for x, y in pts:
            self.put(x, y, ch)
        return self

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, ch: str, angle: float = 0.0,
                only: str | None = None) -> "Grid":
        """Filled ellipse; centre in pixel coordinates (pixel centres at +0.5); ``angle`` in degrees."""
        import math

        a = math.radians(angle)
        ca, sa = math.cos(a), math.sin(a)
        for y in range(self.h):
            for x in range(self.w):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                u, v = dx * ca + dy * sa, -dx * sa + dy * ca
                if (u / rx) ** 2 + (v / ry) ** 2 <= 1.0 and (only is None or self.g[y][x] in only):
                    self.g[y][x] = ch
                    self._seen(ch)
        return self

    def capsule(self, x0: float, y0: float, x1: float, y1: float, r0: float, r1: float | None = None,
                ch: str = "P", only: str | None = None) -> "Grid":
        r1 = r0 if r1 is None else r1
        vx, vy = x1 - x0, y1 - y0
        L2 = vx * vx + vy * vy or 1e-9
        for y in range(self.h):
            for x in range(self.w):
                px, py = x + 0.5 - x0, y + 0.5 - y0
                t = max(0.0, min(1.0, (px * vx + py * vy) / L2))
                dx, dy = px - t * vx, py - t * vy
                r = r0 + (r1 - r0) * t
                if dx * dx + dy * dy <= r * r and (only is None or self.g[y][x] in only):
                    self.g[y][x] = ch
                    self._seen(ch)
        return self

    def curve(self, pts: list[tuple[float, float]], r0: float, r1: float | None = None, ch: str = "P",
              only: str | None = None, n: int = 24, profile: list[float] | None = None) -> "Grid":
        """Thick quadratic/cubic bezier through control points ``pts`` (radius r0 -> r1, or a
        ``profile`` of radii sampled uniformly along the curve)."""
        r1 = r0 if r1 is None else r1

        def rad(t):
            if not profile:
                return r0 + (r1 - r0) * t
            f = t * (len(profile) - 1)
            i = min(int(f), len(profile) - 2)
            return profile[i] + (profile[i + 1] - profile[i]) * (f - i)

        def bez(t):
            p = list(pts)
            while len(p) > 1:
                p = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(p, p[1:])]
            return p[0]

        samples = [bez(i / n) for i in range(n + 1)]
        for i in range(n):
            (x0, y0), (x1, y1) = samples[i], samples[i + 1]
            self.capsule(x0, y0, x1, y1, rad(i / n), rad((i + 1) / n), ch, only)
        return self

    def bezier_pts(self, pts: list[tuple[float, float]], n: int = 32) -> list[tuple[int, int]]:
        def bez(t):
            p = list(pts)
            while len(p) > 1:
                p = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(p, p[1:])]
            return p[0]
        out = []
        for i in range(n + 1):
            x, y = bez(i / n)
            q = (int(x), int(y))
            if not out or out[-1] != q:
                out.append(q)
        return out

    def line(self, x0: int, y0: int, x1: int, y1: int, ch: str) -> "Grid":
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.put(x0, y0, ch)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        return self

    def where(self, ch: str) -> list[tuple[int, int]]:
        return [(x, y) for y in range(self.h) for x in range(self.w) if self.g[y][x] == ch]

    def replace(self, old: str, new: str) -> "Grid":
        for y in range(self.h):
            for x in range(self.w):
                if self.g[y][x] in old:
                    self.g[y][x] = new
        return self

    def out(self) -> list[str]:
        return ["".join(r) for r in self.g]

    def __str__(self) -> str:
        return "\n".join(self.out())


def check_alpha(s: Sprite) -> None:
    for row in s.px:
        for c in row:
            assert c[3] in (0, 255), c


# --------------------------------------------------------------------------- previews

SLOT_BG = (0x8b, 0x8b, 0x8b, 255)
PANEL = (0xc6, 0xc6, 0xc6, 255)


def slot_image(item: Image.Image | None, scale: int) -> Image.Image:
    """A vanilla inventory slot (18x18: dark top-left bevel, white bottom-right) at ``scale``."""
    im = Image.new("RGBA", (18, 18), SLOT_BG)
    for i in range(17):
        im.putpixel((i, 0), (0x37, 0x37, 0x37, 255))
        im.putpixel((0, i), (0x37, 0x37, 0x37, 255))
        im.putpixel((17 - i, 17), (255, 255, 255, 255))
        im.putpixel((17, 17 - i), (255, 255, 255, 255))
    im.putpixel((17, 0), SLOT_BG)
    im.putpixel((0, 17), SLOT_BG)
    if item is not None:
        im.alpha_composite(item.convert("RGBA"), (1, 1))
    return im.resize((18 * scale, 18 * scale), Image.NEAREST)


def iso_block(top: Image.Image, side: Image.Image, scale: int = 6) -> Image.Image:
    """Tiny isometric render of a cube (top + two shaded sides) for checking block textures."""
    n = 16 * scale
    W, H = 2 * n, 2 * n
    out = Image.new("RGBA", (W, H + 4), (0, 0, 0, 0))

    def face(img: Image.Image, mapping, shade_f: float):
        src = img.convert("RGBA").resize((n, n), Image.NEAREST)
        r, g, b, a = src.split()
        r, g, b = (ch.point(lambda v: min(255, int(v * shade_f))) for ch in (r, g, b))
        src = Image.merge("RGBA", (r, g, b, a))
        # mapping: output (x,y) -> input (u,v) affine coefficients
        return src.transform((W, H), Image.AFFINE, mapping, resample=Image.NEAREST)

    hw = n  # half width of the diamond
    qh = n // 2
    # top: u along +x/+y diagonal.  Output point (X,Y): u = (X - hw)/2/ (hw/n) ... solve affine
    # top-face corners: (0,qh)=(u0,v0) ; (hw,0)=(n,0)... choose: u axis -> (hw, -qh) per n, v axis -> (hw, qh) per n
    # X = u*hw/n + v*hw/n ; Y = qh - u*qh/n + v*qh/n
    a, b, c_, d = hw / n, hw / n, -qh / n, qh / n
    det = a * d - b * c_
    ia, ib, ic, id_ = d / det, -b / det, -c_ / det, a / det
    top_f = face(top, (ia, ib, -ib * qh, ic, id_, -id_ * qh), 1.0)
    # left face: u -> (hw, qh) per n, v -> (0, n) per n ; origin (0, qh)
    a, b, c_, d = hw / n, 0, qh / n, 1
    det = a * d - b * c_
    ia, ib, ic, id_ = d / det, -b / det, -c_ / det, a / det
    left_f = face(side, (ia, ib, -(ia * 0 + ib * qh), ic, id_, -(ic * 0 + id_ * qh)), 0.80)
    # right face: origin (hw, n) ; u -> (hw, -qh) per n, v -> (0,n)
    a, b, c_, d = hw / n, 0, -qh / n, 1
    det = a * d - b * c_
    ia, ib, ic, id_ = d / det, -b / det, -c_ / det, a / det
    ox, oy = hw, n
    right_f = face(side, (ia, ib, -(ia * ox + ib * oy), ic, id_, -(ic * ox + id_ * oy)), 0.62)
    for f in (left_f, right_f, top_f):
        out.alpha_composite(f)
    return out
