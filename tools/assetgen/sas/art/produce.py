"""Produce lane: crop produce, seeds, tree fruit and crate textures.

    cd tools/assetgen && python3 -m sas.art.produce

``generate()`` writes every texture of the lane (checked against ``sas.contract``);
running the module also writes review previews to ``build/previews/produce_*.png``:

* ``produce_items.png`` / ``produce_fruits.png`` / ``produce_seeds.png`` / ``produce_crates.png``
  - contact sheets (core.contact_sheet)
* ``produce_slots.png`` - every item at 1x, 2x and 4x in vanilla inventory slots, each row
  starting with vanilla apple + carrot for scale/brightness comparison (if vanilla
  textures are available)
* ``produce_crates_tiled.png`` - each crate top, a 3x3 tiling and an isometric block render

Art modules: ``produce_kit`` (materials, renderer, shading), ``produce_items``,
``produce_seeds``, ``produce_crates``.
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw

from ..contract import by_lane
from ..paths import ASSETS, BUILD, VANILLA_REF
from .core import Sprite, contact_sheet
from .produce_crates import CRATES
from .produce_items import ITEMS
from .produce_kit import check_alpha, iso_block, slot_image
from .produce_seeds import SEEDS

PREVIEWS = BUILD / "previews"


def _maker(path: str):
    stem = Path(path).stem
    if path.startswith("textures/item/"):
        return ITEMS.get(stem) or SEEDS.get(stem)
    if path.startswith("textures/block/"):
        return CRATES.get(stem)
    return None


def sprites() -> dict[str, Sprite]:
    """contract path -> sprite, for every texture in the produce lane."""
    out: dict[str, Sprite] = {}
    missing = []
    for t in by_lane("produce"):
        fn = _maker(t.path)
        if fn is None:
            missing.append(t.path)
            continue
        s = fn()
        assert (s.w, s.h) == (16, 16), (t.path, s.w, s.h)
        check_alpha(s)
        out[t.path] = s
    if missing:
        raise SystemExit(f"produce lane: no generator for {missing}")
    return out


def generate() -> list[Path]:
    written = []
    for path, s in sprites().items():
        written.append(s.save(ASSETS / path))
    expected = len(by_lane("produce"))
    assert len(written) == expected, (len(written), expected)
    return written


# --------------------------------------------------------------------------- previews


def _vanilla_dir() -> Path | None:
    cands = [Path(VANILLA_REF) / "assets/minecraft/textures" if VANILLA_REF else None]
    for c in cands:
        if c and (Path(c) / "item" / "apple.png").exists():
            return Path(c)
    return None


def slot_sheet(paths: list[Path], out: Path, per_row: int = 6) -> Path:
    """Items at 1x/2x/4x in vanilla slots; every row starts with vanilla apple + carrot."""
    vdir = _vanilla_dir()
    refs = []
    if vdir:
        refs = [("apple (vanilla)", Image.open(vdir / "item" / "apple.png").convert("RGBA")),
                ("carrot (vanilla)", Image.open(vdir / "item" / "carrot.png").convert("RGBA"))]
    items = [(p.stem, Image.open(p).convert("RGBA")) for p in paths]
    cw, chh = 18 * 4 + 18 * 2 + 18 + 24, 18 * 4 + 16
    rows = [refs + items[i:i + per_row] for i in range(0, len(items), per_row)]
    ncols = max(len(r) for r in rows)
    sheet = Image.new("RGBA", (ncols * cw + 8, len(rows) * chh + 8), (198, 198, 198, 255))
    d = ImageDraw.Draw(sheet)
    for r, row in enumerate(rows):
        for c, (name, im) in enumerate(row):
            x, y = 6 + c * cw, 4 + r * chh
            sheet.alpha_composite(slot_image(im, 4), (x, y))
            sheet.alpha_composite(slot_image(im, 2), (x + 18 * 4 + 4, y))
            sheet.alpha_composite(slot_image(im, 1), (x + 18 * 4 + 4, y + 40))
            d.text((x, y + 18 * 4 + 2), name[:20], fill=(40, 40, 40, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def crate_sheet(out: Path) -> Path:
    side = CRATES["crate_side"]().image()
    bottom = CRATES["crate_bottom"]().image()
    names = sorted(n for n in CRATES if n.endswith("_top"))

    def tile(im, n=3, s=3):
        t = Image.new("RGBA", (16 * n, 16 * n))
        for i in range(n):
            for j in range(n):
                t.paste(im, (16 * i, 16 * j))
        return t.resize((16 * n * s, 16 * n * s), Image.NEAREST)

    cells = [("crate_side", side, CRATES["tomato_crate_top"]().image()),
             ("crate_bottom", bottom, CRATES["apple_crate_top"]().image())]
    cells += [(n, CRATES[n]().image(), None) for n in names]
    cw, chh = 112 + 8 + 144 + 8 + 128 + 12, 144 + 22
    cols = 2
    sheet = Image.new("RGBA", (cw * cols + 8, chh * ((len(cells) + cols - 1) // cols) + 8), (58, 60, 66, 255))
    d = ImageDraw.Draw(sheet)
    for i, (n, im, top) in enumerate(cells):
        x0, y0 = 6 + (i % cols) * cw, 6 + (i // cols) * chh
        sheet.alpha_composite(im.resize((112, 112), Image.NEAREST), (x0, y0))
        sheet.alpha_composite(tile(im), (x0 + 120, y0))
        sheet.alpha_composite(iso_block(top or im, side, scale=4), (x0 + 272, y0 + 8))
        d.text((x0, y0 + 118), n, fill=(235, 235, 235, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def previews(written: list[Path]) -> list[Path]:
    crop_ids = {Path(t.path).stem for t in by_lane("produce")}
    fruit = {"orange", "lemon", "lime", "peach", "pear", "plum", "cherries", "mango", "avocado", "banana", "olives"}
    items = [p for p in written if "/item/" in str(p)]
    seeds = [p for p in items if p.stem in SEEDS]
    fruits = [p for p in items if p.stem in fruit]
    produce = [p for p in items if p not in seeds and p not in fruits]
    blocks = [p for p in written if "/block/" in str(p)]
    assert crop_ids
    outs = [
        contact_sheet(produce, PREVIEWS / "produce_items.png", scale=6, cols=10),
        contact_sheet(fruits, PREVIEWS / "produce_fruits.png", scale=6, cols=11),
        contact_sheet(seeds, PREVIEWS / "produce_seeds.png", scale=6, cols=11),
        contact_sheet(blocks, PREVIEWS / "produce_crates.png", scale=6, cols=9),
        slot_sheet(produce + fruits, PREVIEWS / "produce_slots.png"),
        slot_sheet(seeds, PREVIEWS / "produce_slots_seeds.png"),
        crate_sheet(PREVIEWS / "produce_crates_tiled.png"),
    ]
    return outs


def main() -> None:
    written = generate()
    print(f"produce lane: wrote {len(written)} textures under {ASSETS}")
    for p in previews(written):
        print("preview:", p)


if __name__ == "__main__":
    main()
