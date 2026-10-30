"""Plants lane generator: crop growth stages, fruit-tree saplings & leaves, wild gardens.

Run ``python3 -m sas.art.plants`` (from tools/assetgen) to write every texture of the lane into
``ASSETS`` and the review sheets into ``build/previews/plants_*.png``:

* ``plants_crops_*.png``   contact sheets of all crop stages (4 per crop, corn tops included)
* ``plants_trees.png``     saplings + the four leaf ages per tree
* ``plants_gardens.png``   wild gardens
* ``plants_field_*.png``   pseudo-3D render of crop rows on farmland (crop '#', cross and tall models)
* ``plants_leaves_tiled.png`` 3x3 tiling of every leaves texture

Modules: ``plants_kit`` (renderer), ``plants_lib`` (shared helpers), one module per crop family,
``plants_trees`` and ``plants_gardens``.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from ..paths import ASSETS, BUILD
from .core import Sprite, contact_sheet
from .plants_crops import crop_textures
from .plants_gardens import garden_textures
from .plants_kit import binarize
from .plants_trees import tree_textures

PREVIEWS = BUILD / "previews"


def all_textures() -> dict[str, Sprite]:
    """Every texture of the lane keyed by its path relative to the assets dir."""
    out: dict[str, Sprite] = {}
    for stem, s in {**crop_textures(), **tree_textures(), **garden_textures()}.items():
        out[f"textures/block/{stem}.png"] = binarize(s)
    return out


def contract_paths() -> list[str]:
    from ..contract import by_lane

    return [t.path for t in by_lane("plants")]


def generate() -> list[Path]:
    tex = all_textures()
    expected = contract_paths()
    missing = [p for p in expected if p not in tex]
    extra = [p for p in tex if p not in set(expected)]
    if missing or extra:
        raise SystemExit(f"plants lane mismatch: missing={missing} extra={extra}")
    written = []
    for rel in expected:
        written.append(tex[rel].save(ASSETS / rel))
    return written


# --------------------------------------------------------------------------- field preview renderer

FARM_TOP = [(0x52, 0x34, 0x1e), (0x46, 0x2c, 0x18), (0x5e, 0x3e, 0x24)]
FARM_SIDE = (0x6a, 0x4c, 0x32)
FARM_SIDE_DK = (0x52, 0x3a, 0x26)
SKY = (124, 168, 220, 255)


def _proj(x: float, y: float, z: float, S: float, ox: float, oy: float) -> tuple[float, float]:
    """Isometric-ish projection; +x goes right-down, +z left-down, +y up."""
    return ox + (x - z) * S * 0.9, oy + (x + z) * S * 0.33 - y * S


def _plane_quads(img: Image.Image, corner_a, corner_b, y0: float, y1: float, block_origin, S, ox, oy, quads,
                 shade_k: float = 1.0) -> None:
    """Texture ``img`` stretched over a vertical plane from (xa,za) to (xb,zb), y0..y1 (block units)."""
    bx, by, bz = block_origin
    w, hgt = img.size
    px = img.load()
    for v in range(hgt):
        for u in range(w):
            c = px[u, v]
            if c[3] == 0:
                continue
            t0, t1 = u / w, (u + 1) / w
            ya = by + y1 - (y1 - y0) * v / hgt
            yb = by + y1 - (y1 - y0) * (v + 1) / hgt
            xa = bx + corner_a[0] + (corner_b[0] - corner_a[0]) * t0
            xb = bx + corner_a[0] + (corner_b[0] - corner_a[0]) * t1
            za = bz + corner_a[1] + (corner_b[1] - corner_a[1]) * t0
            zb = bz + corner_a[1] + (corner_b[1] - corner_a[1]) * t1
            poly = [_proj(xa, ya, za, S, ox, oy), _proj(xb, ya, zb, S, ox, oy), _proj(xb, yb, zb, S, ox, oy),
                    _proj(xa, yb, za, S, ox, oy)]
            depth = (xa + xb + za + zb) / 2
            col = tuple(min(255, round(ch * shade_k)) for ch in c[:3]) + (255,)
            quads.append((depth, poly, col))


def _farmland(draw: ImageDraw.ImageDraw, nx: int, nz: int, S, ox, oy) -> None:
    # top faces with furrows
    for bz in range(nz):
        for bx in range(nx):
            for k in range(8):
                z0, z1 = bz + k / 8, bz + (k + 1) / 8
                poly = [_proj(bx, -1 / 16, z0, S, ox, oy), _proj(bx + 1, -1 / 16, z0, S, ox, oy),
                        _proj(bx + 1, -1 / 16, z1, S, ox, oy), _proj(bx, -1 / 16, z1, S, ox, oy)]
                draw.polygon(poly, fill=FARM_TOP[(k + bx) % 3 if k % 4 else 1])
    # front sides
    lo = -0.3
    draw.polygon([_proj(0, -1 / 16, nz, S, ox, oy), _proj(nx, -1 / 16, nz, S, ox, oy), _proj(nx, lo, nz, S, ox, oy),
                  _proj(0, lo, nz, S, ox, oy)], fill=FARM_SIDE)
    draw.polygon([_proj(nx, -1 / 16, 0, S, ox, oy), _proj(nx, -1 / 16, nz, S, ox, oy), _proj(nx, lo, nz, S, ox, oy),
                  _proj(nx, lo, 0, S, ox, oy)], fill=FARM_SIDE_DK)


def _block_planes(model: str, tex: Image.Image, top: Image.Image | None, origin, S, ox, oy, quads) -> None:
    if model == "cross":
        a, b = 0.15, 0.85
        for ca, cb in (((a, a), (b, b)), ((a, b), (b, a))):
            _plane_quads(tex, ca, cb, 0, 1, origin, S, ox, oy, quads)
        return
    layers = [(tex, 0)] + ([(top, 1)] if top is not None else [])
    for img, dy in layers:
        o = (origin[0], origin[1] + dy, origin[2])
        for x in (4 / 16, 12 / 16):
            _plane_quads(img, (x, 0), (x, 1), -1 / 16, 15 / 16, o, S, ox, oy, quads, 0.92)
        for z in (4 / 16, 12 / 16):
            _plane_quads(img, (0, z), (1, z), -1 / 16, 15 / 16, o, S, ox, oy, quads)


def field_preview(crops: list[tuple[str, str]], textures: dict[str, Sprite], out: Path, S: int = 64) -> Path:
    """One field per crop: 4 blocks along x = stages 0..3, 2 blocks deep, on farmland."""
    nx, nz = 4, 2
    fw = int((nx + nz) * S * 0.9) + 20
    fh = int((nx + nz) * S * 0.33 + 2.6 * S) + 30
    cols = 2
    rows = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * fw, rows * fh), SKY)
    d = ImageDraw.Draw(sheet)
    for i, (name, model) in enumerate(crops):
        cx, cy = (i % cols) * fw, (i // cols) * fh
        ox = cx + nz * S * 0.9 + 10
        oy = cy + 2.2 * S + 16
        _farmland(d, nx, nz, S, ox, oy)
        quads = []
        for bz in range(nz):
            for bx in range(nx):
                key = f"textures/block/{name}_stage{bx}.png"
                tex = textures[key].image()
                tkey = f"textures/block/{name}_stage{bx}_top.png"
                top = textures[tkey].image() if tkey in textures else None
                _block_planes(model, tex, top, (bx, 0, bz), S, ox, oy, quads)
        quads.sort(key=lambda q: q[0])
        for _, poly, col in quads:
            d.polygon(poly, fill=col)
        d.text((cx + 6, cy + 4), f"{name} ({model})  stages 0-3 left to right", fill=(20, 24, 30, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def tiled_leaves_preview(textures: dict[str, Sprite], out: Path, scale: int = 4) -> Path:
    from ..spec import TREES

    cell = 48 * scale + 10
    sheet = Image.new("RGBA", (4 * cell, len(TREES) * (cell + 12)), (60, 63, 70, 255))
    d = ImageDraw.Draw(sheet)
    for r, t in enumerate(TREES):
        for age in range(4):
            im = textures[f"textures/block/{t.leaves}_{age}.png"].image()
            big = Image.new("RGBA", (48, 48))
            for a in range(3):
                for b in range(3):
                    big.alpha_composite(im, (a * 16, b * 16))
            sheet.alpha_composite(big.resize((48 * scale, 48 * scale), Image.NEAREST),
                                  (age * cell + 5, r * (cell + 12) + 5))
            d.text((age * cell + 5, r * (cell + 12) + 48 * scale + 6), f"{t.leaves}_{age}", fill=(230, 230, 230, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def previews(textures: dict[str, Sprite] | None = None) -> list[Path]:
    from ..spec import CROPS, GARDENS, TREES

    textures = textures or all_textures()
    outs = []
    # crops: 10 crops per sheet, 4 stages each (corn tops shown on their own row)
    crop_paths = []
    for c in CROPS:
        for st in range(4):
            crop_paths.append(ASSETS / f"textures/block/{c.id}_stage{st}.png")
        if c.model == "tall":
            crop_paths += [ASSETS / f"textures/block/{c.id}_stage{st}_top.png" for st in (2, 3)]
    for k in range(0, len(crop_paths), 40):
        outs.append(contact_sheet(crop_paths[k:k + 40], PREVIEWS / f"plants_crops_{k // 40 + 1}.png", scale=6, cols=8))
    tree_paths = []
    for t in TREES:
        tree_paths.append(ASSETS / f"textures/block/{t.sapling}.png")
        tree_paths += [ASSETS / f"textures/block/{t.leaves}_{a}.png" for a in range(4)]
    outs.append(contact_sheet(tree_paths, PREVIEWS / "plants_trees.png", scale=6, cols=10))
    outs.append(contact_sheet([ASSETS / f"textures/block/{g.id}.png" for g in GARDENS], PREVIEWS / "plants_gardens.png",
                              scale=8, cols=6))
    crops = [(c.id, "crop" if c.model == "tall" else c.model) for c in CROPS]
    for k in range(0, len(crops), 10):
        outs.append(field_preview(crops[k:k + 10], textures, PREVIEWS / f"plants_field_{k // 10 + 1}.png"))
    outs.append(tiled_leaves_preview(textures, PREVIEWS / "plants_leaves_tiled.png"))
    return outs


def main() -> None:
    written = generate()
    print(f"plants: wrote {len(written)} textures under {ASSETS}")
    for p in previews():
        print("preview:", p)


if __name__ == "__main__":
    main()
