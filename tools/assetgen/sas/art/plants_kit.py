"""Drawing kit for the *plants* lane (crops, fruit trees, wild gardens).

The core idea is a tiny "object buffer" renderer: a plant is assembled from shapes (stems,
leaves, fruit...) that each own a set of pixels and a colour ramp.  Shapes added later sit in
front.  ``Plant.render()`` then shades every shape by *form* with a single top-left light:

* pixels whose top/left neighbour belongs to something else catch the light (+1 tone)
* pixels whose bottom/right neighbour belongs to something else fall into shadow (-1 tone)
* a shape casts a 1px shadow on whatever sits directly below/right of it (-1 tone)
* optional sphere-ish ``form`` term, deterministic ``noise`` texture and per-shape tone bias

Thin (1px) structures get both terms and stay on their mid tone, which keeps stems crisp.
After shading, ``post`` overlays (veins, glints, seeds, flower centres) are painted on top.

Everything is deterministic: noise comes from a hash of (x, y, salt), never from global RNG.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

from .core import CLEAR, Color, Sprite, hexc, shade

Pt = tuple[int, int]


# --------------------------------------------------------------------------- colour helpers


def C(c: Color | str) -> Color:
    return hexc(c) if isinstance(c, str) else c


def tones(base: Color | str, steps: Sequence[float] = (-0.2, -0.105, 0.0, 0.085, 0.165), hue: float = 0.045,
          sat: float = 0.0) -> list[Color]:
    """Hue-shifted ramp darkest -> lightest at the given lightness offsets."""
    base = C(base)
    return [base if a == 0 else shade(base, a, hue_shift=hue, sat=sat) for a in steps]


def green(base: Color | str = "#4e8a2e", spread: float = 1.0, sat: float = 0.04) -> list[Color]:
    """Leaf ramp in the vanilla crop register: deep blue-green darks, warm yellow-green lights."""
    s = spread
    return tones(base, (-0.16 * s, -0.08 * s, 0.0, 0.08 * s, 0.155 * s), hue=0.07, sat=sat)


def fruit(base: Color | str, spread: float = 1.0) -> list[Color]:
    s = spread
    return tones(base, (-0.22 * s, -0.11 * s, 0.0, 0.09 * s, 0.17 * s), hue=0.04)


def wood(base: Color | str = "#8a6a3a") -> list[Color]:
    return tones(base, (-0.17, -0.09, 0.0, 0.07, 0.13), hue=0.03)


def h(x: int, y: int, salt: int = 0) -> float:
    """Deterministic hash in [0, 1)."""
    n = (x * 374761393 + y * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n ^= n >> 16
    return (n & 0xFFFFFF) / float(0x1000000)


# --------------------------------------------------------------------------- geometry


def _bez(ctrl: Sequence[tuple[float, float]], t: float) -> tuple[float, float]:
    pts = list(ctrl)
    while len(pts) > 1:
        pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(pts, pts[1:])]
    return pts[0]


def sample(ctrl: Sequence[tuple[float, float]], n: int = 64) -> list[tuple[float, float]]:
    """Sample a Bezier curve (2 points = straight line) given in *pixel index* coordinates."""
    return [_bez(ctrl, i / (n - 1)) for i in range(n)]


def pixel_perfect(pts: list[Pt]) -> list[Pt]:
    """Remove L-corners from a staircase so 1px lines stay crisp."""
    out: list[Pt] = []
    for p in pts:
        if out and out[-1] == p:
            continue
        out.append(p)
        if len(out) >= 3:
            a, b, c = out[-3], out[-2], out[-1]
            if abs(a[0] - c[0]) == 1 and abs(a[1] - c[1]) == 1 and (b[0] == a[0] or b[1] == a[1]):
                out.pop(-2)
    return out


def line(ctrl: Sequence[tuple[float, float]], n: int = 80) -> list[Pt]:
    """1px pixel-perfect curve through Bezier control points (pixel index coords)."""
    raw = [(int(math.floor(x + 0.5)), int(math.floor(y + 0.5))) for x, y in sample(ctrl, n)]
    # fill gaps (keep 8-connectivity)
    filled: list[Pt] = []
    for p in raw:
        if filled:
            q = filled[-1]
            while max(abs(p[0] - q[0]), abs(p[1] - q[1])) > 1:
                q = (q[0] + (p[0] > q[0]) - (p[0] < q[0]), q[1] + (p[1] > q[1]) - (p[1] < q[1]))
                filled.append(q)
        filled.append(p)
    return pixel_perfect(filled)


PROFILES: dict[str, Callable[[float], float]] = {}


def _beta(a: float, b: float) -> Callable[[float], float]:
    peak = a / (a + b)
    m = peak ** a * (1 - peak) ** b
    return lambda u: 0.0 if u <= 0 or u >= 1 else (u ** a * (1 - u) ** b) / m


PROFILES.update({
    "ovate": _beta(0.65, 0.9),
    "lance": _beta(0.9, 1.25),
    "ellipse": _beta(0.5, 0.5),
    "heart": _beta(0.32, 0.95),
    "spoon": _beta(1.5, 0.55),
    "blade": lambda u: max(0.0, 1 - u) ** 0.7,
    "strap": lambda u: 1.0 if u < 0.75 else max(0.0, (1 - u) / 0.25) ** 0.8,
    "const": lambda u: 1.0,
    "tip": lambda u: min(1.0, u / 0.35) if u < 1 else 0.0,
})


def blob(ctrl: Sequence[tuple[float, float]], width: float, profile: str | Callable[[float], float] = "ovate",
         axis: bool = True, min_w: float = 0.0) -> tuple[set[Pt], list[Pt]]:
    """Rasterise a (possibly curved) leaf-like shape along a Bezier axis.

    ``width`` is the full width at the profile's widest point. Returns (pixels, axis_pixels).
    The axis is always included (when ``axis``) so tips and narrow parts stay connected.
    """
    prof = PROFILES[profile] if isinstance(profile, str) else profile
    pts = sample(ctrl, 96)
    # cumulative length
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    L = cum[-1] or 1.0
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    r = width / 2 + 1
    out: set[Pt] = set()
    for py in range(int(min(ys) - r), int(max(ys) + r) + 2):
        for px in range(int(min(xs) - r), int(max(xs) + r) + 2):
            best, bi = 1e9, 0
            for i, (qx, qy) in enumerate(pts):
                d = (px - qx) ** 2 + (py - qy) ** 2
                if d < best:
                    best, bi = d, i
            u = cum[bi] / L
            hw = max(min_w, width * prof(u)) / 2
            if math.sqrt(best) <= hw - 0.02 and 0 < bi < len(pts) - 1:
                out.add((px, py))
    ax = line(ctrl) if axis else []
    if axis:
        # trim the axis where the profile is ~0 at the very base so stems can attach cleanly
        out.update(ax)
    return out, ax


LIGHT = (-0.5, -0.87)   # direction *towards* the light (up, slightly left)


def leaf_tones(ctrl: Sequence[tuple[float, float]], width: float, profile: str | Callable[[float], float] = "ovate",
               depth: int = 0, vein: int | None = 2, vein_span=(0.12, 0.72), tip: int | None = None,
               min_w: float = 0.0, light=LIGHT, n_tones: int = 5, edge_dark: int = 1) -> dict[Pt, int]:
    """Rasterise a leaf with classic split shading.

    The half facing the light is light (tone 3, its rim 4), the other half mid (2) with a dark
    rim (1); the midrib gets ``vein``. ``depth`` shifts the whole leaf (negative = further back).
    Returns {pixel: tone index} for ``Plant.add(..., fixed=...)`` via :func:`add_leaf`.
    """
    prof = PROFILES[profile] if isinstance(profile, str) else profile
    pts = sample(ctrl, 96)
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    L = cum[-1] or 1.0
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    r = width / 2 + 1
    info: dict[Pt, tuple[float, float, float]] = {}   # pixel -> (u, signed v, lit-side sign)
    for py in range(int(min(ys) - r), int(max(ys) + r) + 2):
        for px in range(int(min(xs) - r), int(max(xs) + r) + 2):
            best, bi = 1e9, 0
            for i, (qx, qy) in enumerate(pts):
                d = (px - qx) ** 2 + (py - qy) ** 2
                if d < best:
                    best, bi = d, i
            u = cum[bi] / L
            hw = max(min_w, width * prof(u)) / 2
            if math.sqrt(best) <= hw - 0.02 and 0 < bi < len(pts) - 1:
                j = min(bi, len(pts) - 2)
                tx, ty = pts[j + 1][0] - pts[j][0], pts[j + 1][1] - pts[j][1]
                tl = math.hypot(tx, ty) or 1
                nx, ny = -ty / tl, tx / tl
                v = (px - pts[bi][0]) * nx + (py - pts[bi][1]) * ny
                facing = nx * light[0] + ny * light[1]
                info[(px, py)] = (u, v, facing)
    ax = line(ctrl)
    axset = set(ax)
    out: dict[Pt, int] = {}
    allpx = set(info) | axset
    for p in allpx:
        u, v, facing = info.get(p, (0.5, 0.0, 0.0))
        side = v * facing   # >0: on the lit side
        nb_out = [q for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)) if q not in allpx]
        rim = bool(nb_out)
        if p in axset and abs(v) < 0.5:
            t = 2 if not rim else 2
            k = ax.index(p) / max(1, len(ax) - 1)
            if vein is not None and vein_span[0] <= k <= vein_span[1] and not rim:
                t = vein
        elif side > 0.05:
            t = 3 + (1 if rim and not any(q[1] > p[1] for q in nb_out) else 0)
        else:
            t = 2 - (edge_dark if rim else 0)
        out[p] = t
    # tip
    if tip is not None and ax:
        out[ax[-1]] = tip
    for p in out:
        out[p] = max(0, min(n_tones - 1, out[p] + depth))
    return out


def jitter_seeds(w: int, h_: int, cell: float, salt: int, jit: float = 0.8) -> list[tuple[float, float]]:
    """Jittered grid of seed points covering a w x h area (used for leaf-cell textures)."""
    seeds = []
    ny, nx = max(1, round(h_ / cell)), max(1, round(w / cell))
    sx, sy = w / nx, h_ / ny
    for j in range(ny):
        for i in range(nx):
            off = (sx / 2) if j % 2 else 0.0
            x = (i * sx + off + (h(i, j, salt) - 0.5) * jit * sx) % w
            y = j * sy + (h(i, j, salt + 7) - 0.5) * jit * sy
            seeds.append((x, y % h_))
    return seeds


def poisson_seeds(w: int, h_: int, r: float, salt: int, wrap: bool = True, tries: int = 400) -> list[tuple[float, float]]:
    """Deterministic dart-throwing Poisson-disc points (min distance ``r``), wrap-aware for tiling."""
    import random

    rng = random.Random(salt)
    pts: list[tuple[float, float]] = []
    for _ in range(tries):
        x, y = rng.uniform(0, w), rng.uniform(0, h_)
        ok = True
        for qx, qy in pts:
            dx, dy = abs(x - qx), abs(y - qy)
            if wrap:
                dx, dy = min(dx, w - dx), min(dy, h_ - dy)
            if dx * dx + dy * dy < r * r:
                ok = False
                break
        if ok:
            pts.append((x, y))
    return pts


def leaf_cells(pts: Iterable[Pt], seeds: Sequence[tuple[float, float]], salt: int = 0, wrap: tuple | None = None,
               stretch: tuple = (1.0, 1.25), vary: float = 0.35, form: tuple | None = None,
               grad: float = 0.0) -> dict[Pt, int]:
    """Scaly leafy texture: every pixel belongs to its nearest seed ("leaf"); each leaf is lit on
    its top-left rim and shaded on its bottom-right rim, with a random per-leaf tone offset.

    Returns {pixel: tone} on a 5-tone scale (0..4). ``wrap`` = (w, h) makes it tileable.
    ``form`` = (cx, cy, r, k) adds a dome light term (lighter up-left, darker down-right).
    """
    pts = set(pts)
    sxs, sys_ = stretch

    def nearest(x: float, y: float) -> int:
        best, bi = 1e9, 0
        for i, (qx, qy) in enumerate(seeds):
            dx, dy = x - qx, y - qy
            if wrap:
                dx = (dx + wrap[0] / 2) % wrap[0] - wrap[0] / 2
                dy = (dy + wrap[1] / 2) % wrap[1] - wrap[1] / 2
            d = (dx * sxs) ** 2 + (dy * sys_) ** 2
            if d < best:
                best, bi = d, i
        return bi

    cell = {p: nearest(p[0] + 0.5, p[1] + 0.5) for p in pts}
    span = max(1.0, (len(pts) / max(1, len(seeds))) ** 0.5)

    def cell_of(x: int, y: int) -> int:
        if wrap:
            x, y = x % wrap[0], y % wrap[1]
        return cell.get((x, y), -1)

    out = {}
    for (x, y), c in cell.items():
        t = 2.0
        up, lf = cell_of(x, y - 1) != c, cell_of(x - 1, y) != c
        dn, rt = cell_of(x, y + 1) != c, cell_of(x + 1, y) != c
        if (up or lf) and not (dn or rt):
            t += 1
        elif (dn or rt) and not (up or lf):
            t -= 1
        elif dn and not up:
            t -= 1
        if grad:
            qx, qy = seeds[c]
            dx, dy = qx - (x + 0.5), qy - (y + 0.5)
            if wrap:
                dx = (dx + wrap[0] / 2) % wrap[0] - wrap[0] / 2
                dy = (dy + wrap[1] / 2) % wrap[1] - wrap[1] / 2
            t += grad * (dx * 0.6 + dy * 0.8) / span
        r = h(c, 0, salt + 3)
        if r < vary / 2:
            t -= 1
        elif r > 1 - vary / 2:
            t += 1
        if form:
            cx, cy, rr, k = form
            dx, dy = (x + 0.5 - cx) / rr, (y + 0.5 - cy) / rr
            t += k * max(-1.2, min(1.2, -(dx * 0.6 + dy * 0.8)))
        out[(x, y)] = max(0, min(4, int(math.floor(t + 0.5))))
    return out


def disc(cx: float, cy: float, rx: float, ry: float | None = None) -> set[Pt]:
    """Filled ellipse; centre in continuous coords (pixel (i,j) centre = i+0.5, j+0.5)."""
    ry = rx if ry is None else ry
    out = set()
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                out.add((x, y))
    return out


def rect(x0: int, y0: int, x1: int, y1: int) -> set[Pt]:
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def mask(rows: Sequence[str], ox: int = 0, oy: int = 0, ch: str | None = None) -> set[Pt]:
    """Pixels of an ASCII mask (any non '.'/space char, or only ``ch``)."""
    out = set()
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c in ". ":
                continue
            if ch is None or c in ch:
                out.add((x + ox, y + oy))
    return out


def flipx(pts: Iterable[Pt], cx: float) -> set[Pt]:
    """Mirror pixels around the vertical line through pixel-centre ``cx`` (e.g. 7.5 for the canvas)."""
    return {(int(round(2 * cx - x)), y) for x, y in pts}


# --------------------------------------------------------------------------- renderer


@dataclass
class Obj:
    ramp: list[Color]
    base: int
    shade: bool = True
    edge: int = 1            # strength of the light/shadow edge terms
    cast: bool = True        # casts a shadow on what lies below-right
    receive: bool = True     # receives cast shadows
    gloss: bool = False      # extra highlight on exposed top-left corners
    form: tuple | None = None  # (cx, cy, r, strength) sphere term
    noise: float = 0.0       # probability of +-1 tone jitter on interior pixels
    salt: int = 0
    vgrad: tuple | None = None  # (y_top, y_bottom, tones) darken towards the bottom
    fixed: dict = field(default_factory=dict)  # (x,y) -> tone index (no shading)
    light_bias: float = 0.0  # shifts lit/dark balance (<0 favours shadow)


class Plant:
    def __init__(self, w: int = 16, h: int = 16, wrap: bool = False):
        self.w, self.h, self.wrap = w, h, wrap
        self.owner = [[-1] * w for _ in range(h)]
        self.objs: list[Obj] = []
        self.post: list[tuple[int, int, Color]] = []
        self.erase: set[Pt] = set()

    # ---- ownership
    def _norm(self, x: int, y: int) -> Pt | None:
        if self.wrap:
            return x % self.w, y % self.h
        if 0 <= x < self.w and 0 <= y < self.h:
            return x, y
        return None

    def own(self, x: int, y: int) -> int:
        p = self._norm(x, y)
        return -1 if p is None else self.owner[p[1]][p[0]]

    def add(self, pts: Iterable[Pt], ramp_: list[Color], base: int | None = None, **kw) -> int:
        i = len(self.objs)
        o = Obj(ramp_, len(ramp_) // 2 if base is None else base, **kw)
        if not o.salt:
            o.salt = i * 7919 + 13
        self.objs.append(o)
        for x, y in pts:
            p = self._norm(x, y)
            if p is not None:
                self.owner[p[1]][p[0]] = i
        return i

    def add_rows(self, rows: Sequence[str], ox: int, oy: int, key: dict[str, tuple[list[Color], int]], **kw) -> list[int]:
        """Add fixed-tone objects from ASCII art. ``key`` maps char -> (ramp, tone_index)."""
        ids = []
        groups: dict[int, dict] = {}
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch not in key:
                    continue
                rmp, t = key[ch]
                groups.setdefault(id(rmp), {"ramp": rmp, "px": {}})["px"][(x + ox, y + oy)] = t
        for g in groups.values():
            ids.append(self.add(g["px"].keys(), g["ramp"], shade=False, fixed=g["px"], **kw))
        return ids

    def leaf(self, ctrl, width: float, ramp_: list[Color], profile="ovate", depth: int = 0, **kw) -> int:
        """Split-shaded leaf (see :func:`leaf_tones`). Extra kw go to ``leaf_tones`` or ``add``."""
        lt_keys = {"vein", "vein_span", "tip", "min_w", "light", "edge_dark"}
        lt = {k: v for k, v in kw.items() if k in lt_keys}
        ad = {k: v for k, v in kw.items() if k not in lt_keys}
        t = leaf_tones(ctrl, width, profile, depth=depth, n_tones=len(ramp_), **lt)
        return self.add(t.keys(), ramp_, shade=False, fixed=t, **ad)

    def fixed(self, tones_: dict[Pt, int], ramp_: list[Color], **kw) -> int:
        return self.add(tones_.keys(), ramp_, shade=False, fixed=dict(tones_), **kw)

    def stamp(self, rows: Sequence[str], ox: int, oy: int, key: dict[str, tuple[list[Color], int] | Color | str],
              flip: bool = False, **kw) -> list[int]:
        """ASCII stamp; ``key`` maps char -> (ramp, tone) for shaded-object pixels or a plain colour
        (painted as a post overlay). Each distinct ramp becomes one object (casts/receives shadows)."""
        rows = [r[::-1] for r in rows] if flip else list(rows)
        w = max(len(r) for r in rows)
        if flip:
            rows = [r.rjust(w, ".") for r in rows]
        groups: dict[int, tuple[list[Color], dict]] = {}
        posts = []
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch not in key:
                    continue
                k = key[ch]
                if isinstance(k, tuple) and len(k) == 2 and isinstance(k[0], list):
                    groups.setdefault(id(k[0]), (k[0], {}))[1][(x + ox, y + oy)] = k[1]
                else:
                    posts.append((x + ox, y + oy, k))
        ids = [self.fixed(px_, rmp, **kw) for rmp, px_ in groups.values()]
        for x, y, c in posts:
            self.px(x, y, c)
        return ids

    def px(self, x: int, y: int, c: Color | str | None) -> None:
        if c is None:
            return
        p = self._norm(x, y)
        if p is not None:
            self.post.append((p[0], p[1], C(c)))

    def pxs(self, pts: Iterable[Pt], c: Color | str) -> None:
        for x, y in pts:
            self.px(x, y, c)

    def clear(self, pts: Iterable[Pt]) -> None:
        for x, y in pts:
            p = self._norm(x, y)
            if p is not None:
                self.owner[p[1]][p[0]] = -1

    def tone_at(self, x: int, y: int) -> int:
        """Index of the owning object (or -1)."""
        return self.own(x, y)

    # ---- shading
    def render(self) -> Sprite:
        s = Sprite(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                i = self.owner[y][x]
                if i < 0:
                    continue
                o = self.objs[i]
                n = len(o.ramp)
                if (x, y) in o.fixed:
                    t = o.fixed[(x, y)]
                    # fixed pixels still receive cast shadows from shapes in front
                    if o.receive and o.cast is not None:
                        a, b = self.own(x, y - 1), self.own(x - 1, y - 1)
                        if (a > i and self.objs[a].cast) or (b > i and self.objs[b].cast and a != i):
                            t = max(min(t, 1), t - 1)
                    s.px[y][x] = o.ramp[max(0, min(n - 1, t))]
                    continue
                t = float(o.base)
                if o.shade:
                    up, lf = self.own(x, y - 1) != i, self.own(x - 1, y) != i
                    dn, rt = self.own(x, y + 1) != i, self.own(x + 1, y) != i
                    lit = up or lf
                    dim = dn or rt
                    if lit and not dim:
                        t += o.edge
                        if o.gloss and up and lf:
                            t += 1
                    elif dim and not lit:
                        t -= o.edge
                    elif not lit and not dim and o.noise and h(x, y, o.salt) < o.noise:
                        t += 1 if h(x, y, o.salt + 1) < 0.5 + o.light_bias else -1
                    if o.form:
                        cx, cy, r, k = o.form
                        dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
                        t += k * max(-1.2, min(1.2, -(dx * 0.65 + dy * 0.75)))
                    if o.vgrad:
                        y0, y1, k = o.vgrad
                        if y > y0:
                            t -= k * min(1.0, (y - y0) / max(1, y1 - y0))
                if o.receive:
                    a, b = self.own(x, y - 1), self.own(x - 1, y - 1)
                    if (a > i and self.objs[a].cast) or (b > i and self.objs[b].cast and self.own(x - 1, y) != i):
                        t = max(min(t, 1.0), t - 1)
                s.px[y][x] = o.ramp[max(0, min(n - 1, int(math.floor(t + 0.5))))]
        for x, y, c in self.post:
            if c[3] == 0:
                s.px[y][x] = CLEAR
            else:
                s.set(x, y, c)
        return s


# --------------------------------------------------------------------------- misc sprite helpers


def binarize(s: Sprite) -> Sprite:
    """Force alpha to 0/255 (cutout renderer)."""
    for y in range(s.h):
        for x in range(s.w):
            c = s.px[y][x]
            if c[3] == 0:
                s.px[y][x] = CLEAR
            elif c[3] != 255:
                s.px[y][x] = (c[0], c[1], c[2], 255) if c[3] >= 128 else CLEAR
    return s


def opaque_count(s: Sprite) -> int:
    return sum(1 for row in s.px for c in row if c[3])


def top_row(s: Sprite) -> int:
    for y in range(s.h):
        if any(c[3] for c in s.px[y]):
            return y
    return s.h
