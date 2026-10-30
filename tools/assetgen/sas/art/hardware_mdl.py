"""Hardware lane: helpers for writing Minecraft block-model JSON and painting atlas textures.

* :func:`box` builds an element whose faces get explicit, integer-aligned UVs: each face
  maps 1 texel per model unit (vanilla density) from a per-face origin in its atlas.
* :func:`dump_model` writes compact, vanilla-looking JSON (one face per line).
* :class:`Paint` is a tiny deterministic painter for 16x16 atlas textures.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Callable

from .core import Color, Sprite, hexc, ramp

DIRS = ("down", "up", "north", "south", "west", "east")


def _num(v: float):
    v = round(float(v), 4)
    return int(v) if v == int(v) else v


def face_size(frm, to, d) -> tuple[float, float]:
    dx, dy, dz = (to[i] - frm[i] for i in range(3))
    if d in ("north", "south"):
        return dx, dy
    if d in ("east", "west"):
        return dz, dy
    return dx, dz


def box(frm, to, faces: dict[str, tuple], rotation: dict | None = None, name: str | None = None,
        shade_: bool | None = None) -> dict:
    """``faces``: dir -> (texture_var, (u0, v0)) or (texture_var, (u0, v0), rot) or
    (texture_var, [u1, v1, u2, v2]) for an explicit rectangle.

    With an origin, the UV rect is ``[u0, v0, u0+w, v0+h]`` where (w, h) is the face size
    (for rot 90/270 the rect is transposed so texels stay square)."""
    el: dict = {}
    if name:
        el["__comment"] = name
    el["from"] = [_num(c) for c in frm]
    el["to"] = [_num(c) for c in to]
    if rotation:
        el["rotation"] = rotation
    if shade_ is False:
        el["shade"] = False
    fs = {}
    for d in DIRS:
        if d not in faces:
            continue
        spec = faces[d]
        tex, where = spec[0], spec[1]
        rot = spec[2] if len(spec) > 2 else 0
        if len(where) == 4:
            uv = list(where)
        else:
            w, h = face_size(frm, to, d)
            if rot in (90, 270):
                w, h = h, w
            u0, v0 = where
            uv = [u0, v0, u0 + w, v0 + h]
        f = {"uv": [_num(c) for c in uv], "texture": tex if tex.startswith("#") else "#" + tex}
        if rot:
            f["rotation"] = rot
        fs[d] = f
    el["faces"] = fs
    return el


def all_faces(tex: str, side: tuple, top: tuple | None = None, bottom: tuple | None = None,
              skip: tuple = ()) -> dict:
    """Same UV origin for the four sides, optional top/bottom origins."""
    out = {}
    for d in ("north", "south", "west", "east"):
        if d not in skip:
            out[d] = (tex, side)
    if top is not None and "up" not in skip:
        out["up"] = (tex, top)
    if bottom is not None and "down" not in skip:
        out["down"] = (tex, bottom)
    return out


def rot_y(angle: float, origin=(8, 8, 8), rescale: bool = False) -> dict:
    return {"angle": angle, "axis": "y", "origin": [_num(c) for c in origin], **({"rescale": True} if rescale else {})}


# --------------------------------------------------------------------------- display

DEFAULT_DISPLAY = {
    "gui": {"rotation": [30, 225, 0], "translation": [0, 0, 0], "scale": [0.625, 0.625, 0.625]},
    "ground": {"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.25, 0.25, 0.25]},
    "fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.5, 0.5, 0.5]},
    "head": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
    "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.375, 0.375, 0.375]},
    "thirdperson_lefthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.375, 0.375, 0.375]},
    "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
    "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
}


def display(**over) -> dict:
    out = {k: json.loads(json.dumps(v)) for k, v in DEFAULT_DISPLAY.items()}
    for k, v in over.items():
        out[k] = v
    order = ["gui", "ground", "fixed", "head", "thirdperson_righthand", "thirdperson_lefthand",
             "firstperson_righthand", "firstperson_lefthand"]
    return {k: _clean_disp(out[k]) for k in order if k in out}


def _clean_disp(d: dict) -> dict:
    return {k: [_num(c) for c in d[k]] for k in ("rotation", "translation", "scale") if k in d}


# --------------------------------------------------------------------------- json


def _fmt(v, ind: int = 0) -> str:
    pad = "  " * ind
    if isinstance(v, dict):
        if not v:
            return "{}"
        # faces / small dicts on one line
        if all(not isinstance(x, (dict,)) for x in v.values()) and len(json.dumps(v)) < 110:
            return json.dumps(v)
        items = [f'{pad}  {json.dumps(k)}: {_fmt(x, ind + 1)}' for k, x in v.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v):
            return "[" + ", ".join(json.dumps(x) for x in v) + "]"
        items = [pad + "  " + _fmt(x, ind + 1) for x in v]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return json.dumps(v)


def dump_model(path: Path, data: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = _fmt(data) + "\n"
    json.loads(text)  # sanity
    path.write_text(text)
    return path


def tex_ref(path_under_block: str) -> str:
    return f"sprout_and_soil:block/{path_under_block}"


# --------------------------------------------------------------------------- painting


class Paint:
    """Deterministic painter for a 16x16 (or larger) atlas texture."""

    def __init__(self, w: int = 16, h: int = 16, seed: str = "x"):
        self.s = Sprite(w, h)
        self.rng = random.Random(seed)

    def px(self, x: int, y: int, c: Color | str) -> None:
        self.s.set(x, y, hexc(c) if isinstance(c, str) else c)

    def rect(self, x0: int, y0: int, w: int, h: int, c) -> None:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.px(x, y, c)

    def region(self, x0: int, y0: int, w: int, h: int, fn: Callable[[int, int], Color | str | None]) -> None:
        """``fn(local_x, local_y)`` -> colour (None leaves the pixel)."""
        for y in range(h):
            for x in range(w):
                c = fn(x, y)
                if c is not None:
                    self.px(x0 + x, y0 + y, c)

    def noise(self, x0, y0, w, h, ramp_: list[Color], base: int, spread: float = 0.35, bias=None) -> None:
        """Speckled fill around ``ramp_[base]``; ``bias(x,y)`` adds an index offset."""
        for y in range(h):
            for x in range(w):
                r = self.rng.random()
                i = base + (1 if r > 1 - spread / 2 else -1 if r < spread / 2 else 0)
                if bias:
                    i += bias(x, y)
                self.px(x0 + x, y0 + y, ramp_[max(0, min(len(ramp_) - 1, i))])

    def save(self, path: Path) -> Path:
        return self.s.save(path)


def mk_ramp(base: str, steps: int = 7, spread: float = 0.075) -> list[Color]:
    return ramp(base, steps, spread)


def has_transparency_in(img: Sprite, uv, scale: float = 1.0) -> bool:
    u1, v1, u2, v2 = uv
    x0, x1 = sorted((u1, u2))
    y0, y1 = sorted((v1, v2))
    for y in range(int(y0 * scale), max(int(y0 * scale) + 1, int(round(y1 * scale)))):
        for x in range(int(x0 * scale), max(int(x0 * scale) + 1, int(round(x1 * scale)))):
            if img.get(x, y)[3] < 255:
                return True
    return False
