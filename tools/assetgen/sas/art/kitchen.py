"""Kitchen lane texture generator: ingredients, dishes, drinks, slices, containers, feast icons.

    cd tools/assetgen && python3 -m sas.art.kitchen      # writes textures + preview sheets

Drawers live in ``kitchen_*.py`` modules and register themselves in ``kitchen_kit.REG``.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

from .. import spec
from ..contract import by_lane
from ..paths import ASSETS, BUILD, VANILLA_REF
from . import core
from . import kitchen_kit as K
from . import kitchen_bowls, kitchen_plates, kitchen_hand, kitchen_drinks, kitchen_ingredients, kitchen_baked  # noqa: F401  (register drawers)

LANE = "kitchen"
PREVIEWS = BUILD / "previews"
# vanilla items are only *displayed* next to ours in previews (never copied); skipped if absent
VANILLA_ITEMS = Path(VANILLA_REF or "/nonexistent") / "assets/minecraft/textures/item"


def validate(s: core.Sprite, sid: str) -> None:
    assert (s.w, s.h) == (16, 16), f"{sid}: wrong size {s.w}x{s.h}"
    for row in s.px:
        for c in row:
            assert c[3] in (0, 255), f"{sid}: semi-transparent pixel {c}"


def render(sid: str) -> core.Sprite:
    if sid not in K.REG:
        raise KeyError(f"kitchen: no drawer for {sid}")
    s = K.binarize(K.REG[sid]())
    validate(s, sid)
    return s


def generate() -> list[Path]:
    out = []
    for t in by_lane(LANE):
        sid = Path(t.path).stem
        out.append(render(sid).save(ASSETS / t.path))
    return out


def groups() -> dict[str, list[str]]:
    feasts = [f.id for f in spec.FEASTS]
    slices = [i.id for i in spec.slice_items()]
    g = {
        "containers": [i.id for i in spec.CONTAINERS],
        "ingredients": [i.id for i in spec.INGREDIENTS],
        "bowls": [i.id for i in spec.SOUPS],
        "plates": [i.id for i in spec.PLATES],
        "handhelds": [i.id for i in spec.HANDHELDS],
        "baked": [i.id for i in spec.BAKED],
        "drinks": [i.id for i in spec.DRINKS],
        "slices_feasts": slices + feasts,
    }
    return g


def slot_preview(ids: list[str], out: Path, refs=("mushroom_stew", "bread", "honey_bottle", "rabbit_stew",
                                                     "cookie", "pumpkin_pie")) -> Path:
    """Items at 1x and 4x on vanilla-like #8b8b8b inventory slots, next to vanilla references."""
    slot = (139, 139, 139, 255)
    ims: list[tuple[str, Image.Image]] = []
    for r in refs:
        p = VANILLA_ITEMS / f"{r}.png"
        if p.exists():
            ims.append(("v:" + r, Image.open(p).convert("RGBA")))
    for i in ids:
        ims.append((i, Image.open(ASSETS / "textures/item" / f"{i}.png").convert("RGBA")))
    cols = 10
    cell_w, cell_h = 4 * 18 + 8, 4 * 18 + 18 + 22
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w + 8, rows * cell_h + 8), (198, 198, 198, 255))
    d = ImageDraw.Draw(sheet)

    def frame(x, y, size):
        d.rectangle((x, y, x + size - 1, y + size - 1), fill=slot)
        d.line((x, y, x + size - 1, y), fill=(55, 55, 55, 255))
        d.line((x, y, x, y + size - 1), fill=(55, 55, 55, 255))
        d.line((x + 1, y + size - 1, x + size - 1, y + size - 1), fill=(255, 255, 255, 255))
        d.line((x + size - 1, y + 1, x + size - 1, y + size - 1), fill=(255, 255, 255, 255))

    for n, (name, im) in enumerate(ims):
        x0 = 8 + (n % cols) * cell_w
        y0 = 8 + (n // cols) * cell_h
        frame(x0, y0, 4 * 18)
        sheet.alpha_composite(im.resize((64, 64), Image.NEAREST), (x0 + 4, y0 + 4))
        frame(x0, y0 + 4 * 18 + 2, 18)
        sheet.alpha_composite(im, (x0 + 1, y0 + 4 * 18 + 3))
        frame(x0 + 20, y0 + 4 * 18 + 2, 18)
        sheet.alpha_composite(im, (x0 + 21, y0 + 4 * 18 + 3))
        d.text((x0 + 40, y0 + 4 * 18 + 6), name[:9], fill=(40, 40, 40, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def previews(only: list[str] | None = None) -> list[Path]:
    outs = []
    for name, ids in groups().items():
        if only and name not in only:
            continue
        paths = [ASSETS / "textures/item" / f"{i}.png" for i in ids]
        outs.append(core.contact_sheet(paths, PREVIEWS / f"kitchen_{name}.png", scale=6, cols=8))
        outs.append(slot_preview(ids, PREVIEWS / f"kitchen_{name}_slots.png"))
    return outs


def main(argv: list[str]) -> None:
    written = generate()
    expected = len(by_lane(LANE))
    print(f"kitchen: wrote {len(written)} / {expected} textures")
    assert len(written) == expected
    for p in previews(argv or None):
        print("preview:", p)


if __name__ == "__main__":
    main(sys.argv[1:])
