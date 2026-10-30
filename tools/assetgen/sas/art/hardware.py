"""Hardware lane generator: tools, workstation models, feast blocks, cooking pot GUI,
mob effect icons and the mod logo.

    cd tools/assetgen && python3 -m sas.art.hardware          # generate + validate + previews

``generate()`` writes every output of ``sas.contract.by_lane('hardware')`` (plus the
textures the workstation models reference) and returns the written paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from ..paths import ASSETS, BUILD, MAIN_RESOURCES, MODELS, TEXTURES
from . import hardware_feasts as feasts
from . import hardware_gui as gui
from . import hardware_models as models
from . import hardware_tools as tools
from .hardware_mdl import dump_model

PREVIEWS = BUILD / "previews"
WORKSTATIONS = ("cooking_pot", "cutting_board", "scarecrow", "sprinkler")


# --------------------------------------------------------------------------- generate


def generate() -> list[Path]:
    written: list[Path] = []
    written += tools.generate(TEXTURES)
    for mid in WORKSTATIONS:
        model, texs = models.BUILDERS[mid]()
        for rel, spr in texs.items():
            written.append(spr.save(TEXTURES / "block" / f"{rel}.png"))
        written.append(dump_model(MODELS / "block" / f"{mid}.json", model))
    for name, spr in feasts.all_textures().items():
        written.append(spr.save(TEXTURES / "block" / f"{name}.png"))
    for name, model in feasts.all_templates().items():
        written.append(dump_model(MODELS / "block" / f"{name}.json", model))
    written.append(gui.cooking_pot_gui().save(TEXTURES / "gui" / "container" / "cooking_pot.png"))
    for eid, spr in gui.effect_icons().items():
        written.append(spr.save(TEXTURES / "mob_effect" / f"{eid}.png"))
    MAIN_RESOURCES.mkdir(parents=True, exist_ok=True)
    logo_path = MAIN_RESOURCES / "logo.png"
    gui.logo().save(logo_path, optimize=True)
    written.append(logo_path)
    return written


# --------------------------------------------------------------------------- validate

TEMPLATE_VARS = ("top", "side", "inner", "bottom", "particle")


def _contract_path(rel: str) -> Path:
    return MAIN_RESOURCES / "logo.png" if rel == "logo.png" else ASSETS / rel


def _alpha_ok(path: Path) -> bool:
    hist = Image.open(path).convert("RGBA").getchannel("A").histogram()
    return sum(hist[1:255]) == 0


def _uv_transparent(model: dict) -> list[str]:
    """Faces whose UV rectangle covers transparent texels (needs cutout) or is fully empty."""
    from . import render3d as r3

    rm = r3.load_model(model)
    out = []
    for i, el in enumerate(rm.elements):
        for d, f in el.get("faces", {}).items():
            ref = rm.texture_ref(f["texture"])
            if not ref or "__provided__" in ref:
                continue
            tex = r3.load_texture(ref)
            th, tw = tex.shape[:2]
            uv = f.get("uv") or r3.auto_uv(el["from"], el["to"], d)
            u1, u2 = sorted((uv[0], uv[2]))
            v1, v2 = sorted((uv[1], uv[3]))
            x0, x1 = int(u1 * tw / 16), max(int(u1 * tw / 16) + 1, int(-(-u2 * tw // 16)))
            y0, y1 = int(v1 * th / 16), max(int(v1 * th / 16) + 1, int(-(-v2 * th // 16)))
            region = tex[y0:y1, x0:x1, 3]
            if region.size and (region < 128).all():
                out.append(f"element {i} {d}: maps a fully transparent area")
            elif region.size and (region < 255).any():
                out.append(f"element {i} {d}: transparent texels")
    return out


def validate() -> list[str]:
    from ..contract import by_lane
    from . import render3d as r3

    r3.clear_texture_cache()
    errors: list[str] = []
    for t in by_lane("hardware"):
        p = _contract_path(t.path)
        if not p.exists():
            errors.append(f"missing contract output {t.path}")
            continue
        if p.suffix == ".png":
            w, h = Image.open(p).size
            want = {"16x16": (16, 16), "256x256": (256, 256), "18x18": (18, 18)}.get(t.size, (128, 128))
            if (w, h) != want:
                errors.append(f"{t.path}: size {w}x{h}, expected {want}")
            if t.size in ("16x16", "18x18") and not _alpha_ok(p):
                errors.append(f"{t.path}: semi-transparent pixels")
        elif p.suffix == ".json":
            provided = TEMPLATE_VARS if "template_" in p.name else ()
            for e in r3.validate_model(p, provided_vars=provided):
                errors.append(f"{t.path}: {e}")
            data = json.loads(p.read_text())
            if "template_" not in p.name:
                cut = data.get("render_type") == "minecraft:cutout"
                for e in _uv_transparent(data):
                    if "fully transparent" in e or not cut:
                        errors.append(f"{t.path}: {e}")
                mid = p.stem
                for k, ref in data["textures"].items():
                    rel = ref.split(":", 1)[1]
                    if not (rel.startswith(f"block/{mid}/") or rel.startswith(f"block/{mid}_")):
                        errors.append(f"{t.path}: texture {ref} outside block/{mid}/")
                if len(data["elements"]) >= 40:
                    errors.append(f"{t.path}: too many elements")
    for mid in WORKSTATIONS:
        data = json.loads((MODELS / "block" / f"{mid}.json").read_text())
        for ref in set(data["textures"].values()):
            if not (TEXTURES / (ref.split(":", 1)[1] + ".png")).exists():
                errors.append(f"{mid}: missing texture {ref}")
            elif not _alpha_ok(TEXTURES / (ref.split(":", 1)[1] + ".png")):
                errors.append(f"{mid}: semi-transparent texels in {ref}")
    return errors


# --------------------------------------------------------------------------- previews


def _upscale(im: Image.Image, f: int) -> Image.Image:
    return im.resize((im.width * f, im.height * f), Image.NEAREST)


def preview_tools() -> Path:
    from .core import contact_sheet

    paths = [TEXTURES / "item" / f"{tid}.png" for tid in tools.all_tools()]
    out = contact_sheet(paths, PREVIEWS / "hardware_tools.png", scale=8, cols=6)
    # append a hotbar-scale strip (1x and 2x) under the sheet
    sheet = Image.open(out).convert("RGBA")
    strip = Image.new("RGBA", (sheet.width, 44), (52, 54, 60, 255))
    x = 6
    for p in paths:
        im = Image.open(p).convert("RGBA")
        strip.alpha_composite(im, (x, 14))
        strip.alpha_composite(_upscale(im, 2), (x + 20, 6))
        x += 58
    full = Image.new("RGBA", (sheet.width, sheet.height + strip.height), (52, 54, 60, 255))
    full.alpha_composite(sheet)
    full.alpha_composite(strip, (0, sheet.height))
    full.save(out)
    return out


def _board_scene():
    """Cutting board with an item lying on top at y~1.5 (as the block entity renderer will)."""
    from . import render3d as r3

    rm = r3.load_model("cutting_board")
    rm.textures["item"] = str(TEXTURES / "item" / "iron_knife.png")
    rm.elements = list(rm.elements) + [{
        "from": [3, 1.45, 3], "to": [13, 1.55, 13],
        "faces": {"up": {"uv": [0, 0, 16, 16], "texture": "#item"}},
    }]
    return rm


def preview_models() -> Path:
    from . import render3d as r3

    r3.clear_texture_cache()
    gui_bg = (139, 139, 139, 255)
    cells = []
    for mid in WORKSTATIONS:
        cells.append((f"{mid} (front-right)", r3.render_image(mid, yaw=225, scale=8, size=(230, 300 if mid == "scarecrow" else 190))))
        cells.append((f"{mid} (back-left)", r3.render_image(mid, yaw=45, scale=8, size=(230, 300 if mid == "scarecrow" else 190))))
        cells.append((f"{mid} gui 4x", r3.render_display(mid, "gui", ppu=4, ss=1, bg=gui_bg)))
        cells.append((f"{mid} gui 1x/2x", _gui_small(mid, gui_bg)))
        if mid == "cooking_pot":
            scene = r3.combine([("minecraft:block/campfire", (0, 0, 0)), (mid, (0, 16, 0))])
            cells.append(("pot on campfire", r3.render_image(scene, yaw=225, scale=5, size=(230, 190))))
        elif mid == "cutting_board":
            cells.append(("board + item at y1.5", r3.render_image(_board_scene(), yaw=225, scale=8, size=(230, 190))))
        else:
            cells.append(("", Image.new("RGBA", (1, 1))))
    for kind, fid in (("pie", "apple_pie"), ("pizza", "pizza")):
        v = feasts.feast_vars(fid, kind)
        for n in range(4):
            cells.append((f"template_{kind}_{n}", r3.render_image(f"sprout_and_soil:block/template_{kind}_{n}", v,
                                                                 yaw=225, scale=8, size=(230, 190))))
        cells.append((f"template_{kind}_1 back", r3.render_image(f"sprout_and_soil:block/template_{kind}_1", v,
                                                                 yaw=45, scale=8, size=(230, 190))))
    return r3.label_sheet(cells, PREVIEWS / "hardware_models.png", cols=5,
                          title="hardware models: yaw 225 shows north (front) on the right, as in the GUI")


def _gui_small(mid, bg) -> Image.Image:
    from . import render3d as r3

    one = r3.render_display(mid, "gui", ppu=1, ss=1, bg=bg)
    two = r3.render_display(mid, "gui", ppu=2, ss=1, bg=bg)
    im = Image.new("RGBA", (16 + 32 + 12, 36), (52, 54, 60, 255))
    im.alpha_composite(one, (2, 10))
    im.alpha_composite(two, (24, 2))
    return _upscale(im, 2)


def preview_feasts() -> Path:
    from . import render3d as r3

    cells = []
    for f in (("apple_pie", "pie"), ("cherry_pie", "pie"), ("berry_pie", "pie"), ("pizza", "pizza"),
              ("chocolate_cake", "cake"), ("carrot_cake", "cake")):
        fid, kind = f
        v = feasts.feast_vars(fid, kind)
        for n in range(4):
            if kind == "cake":
                ref = "minecraft:block/cake" if n == 0 else f"minecraft:block/cake_slice{2 * n}"
            else:
                ref = f"sprout_and_soil:block/template_{kind}_{n}"
            cells.append((f"{fid} {n}", r3.render_image(ref, v, yaw=225, scale=7, size=(170, 140))))
    for name, spr in feasts.all_textures().items():
        cells.append((name, _upscale(spr.image(), 6)))
    return r3.label_sheet(cells, PREVIEWS / "hardware_feasts.png", cols=8)


def preview_gui() -> Path:
    sheet = Image.open(TEXTURES / "gui" / "container" / "cooking_pot.png").convert("RGBA")
    panel = sheet.crop((0, 0, gui.PANEL_W, gui.PANEL_H))
    sim = panel.copy()
    h = 9
    sim.alpha_composite(sheet.crop((176, 14 - h, 190, 14)), (gui.FLAME_POS[0], gui.FLAME_POS[1] + 14 - h))
    sim.alpha_composite(sheet.crop((176, 14, 176 + 13, 31)), gui.ARROW_POS)
    d = ImageDraw.Draw(sim)
    d.text((8, 6), "Cooking Pot", fill=(64, 64, 64, 255))
    d.text((8, 72), "Inventory", fill=(64, 64, 64, 255))
    out = Image.new("RGBA", (gui.PANEL_W * 6 + 40, gui.PANEL_H * 3 + 20), (52, 54, 60, 255))
    out.alpha_composite(_upscale(panel, 3), (0, 0))
    out.alpha_composite(_upscale(sim, 3), (gui.PANEL_W * 3 + 20, 0))
    out.save(PREVIEWS / "hardware_gui.png")
    _upscale(sheet, 2).save(PREVIEWS / "hardware_gui_sheet.png")
    return PREVIEWS / "hardware_gui.png"


def preview_effects_logo() -> list[Path]:
    icons = [TEXTURES / "mob_effect" / f"{e}.png" for e in ("well_fed", "cozy", "caffeinated")]
    out = Image.new("RGBA", (3 * 160 + 3 * 34, 160), (52, 54, 60, 255))
    for i, p in enumerate(icons):
        bg = Image.new("RGBA", (24, 24), (33, 33, 33, 255))
        bg.alpha_composite(Image.open(p).convert("RGBA"), (3, 3))
        out.alpha_composite(_upscale(bg, 6), (8 + 160 * i, 8))
        out.alpha_composite(bg, (3 * 160 + 6 + 34 * i, 20))
    out.save(PREVIEWS / "hardware_effects.png")
    logo = Image.open(MAIN_RESOURCES / "logo.png").convert("RGBA")
    lp = Image.new("RGBA", (128 * 3 + 30, 256), (52, 54, 60, 255))
    lp.alpha_composite(_upscale(logo, 2), (0, 0))
    lp.alpha_composite(logo, (270, 0))
    light = Image.new("RGBA", (128, 128), (238, 238, 238, 255))
    light.alpha_composite(logo)
    lp.alpha_composite(light, (270, 128))
    lp.save(PREVIEWS / "hardware_logo.png")
    return [PREVIEWS / "hardware_effects.png", PREVIEWS / "hardware_logo.png"]


def previews() -> list[Path]:
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    out = [preview_tools(), preview_models(), preview_feasts(), preview_gui()]
    out += preview_effects_logo()
    return out


def main() -> int:
    written = generate()
    print(f"hardware: wrote {len(written)} files")
    errors = validate()
    for e in errors:
        print("  ERROR", e)
    print("hardware: validation", "OK" if not errors else f"FAILED ({len(errors)})")
    try:
        for p in previews():
            print("  preview", p)
    except Exception as e:  # noqa: BLE001 - previews need numpy / vanilla refs; never block generation
        print("  previews skipped:", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
