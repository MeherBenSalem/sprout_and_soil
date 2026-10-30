#!/usr/bin/env python3
"""Sprout & Soil asset pipeline.

    python3 tools/assetgen/build_assets.py            # data + models + lang + manifest, then validate
    python3 tools/assetgen/build_assets.py --art      # also regenerate every texture / 3D model
    python3 tools/assetgen/build_assets.py --check    # validate only

Everything is written to 1.21.1/common/src/generated/resources.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sas import datagen, spec  # noqa: E402
from sas.paths import ASSETS, DATA, GENERATED, MAIN_RESOURCES  # noqa: E402

ART_LANES = ["plants", "produce", "kitchen", "hardware"]


def run_art() -> None:
    for lane in ART_LANES:
        module = importlib.import_module(f"sas.art.{lane}")
        written = module.generate()
        print(f"art/{lane}: {len(written) if written else 0} files")


def texture_path(ref: str) -> Path | None:
    if ref.startswith("#"):
        return None
    namespace, path = ref.split(":", 1) if ":" in ref else ("minecraft", ref)
    if namespace != spec.MOD_ID:
        return None
    return ASSETS / "textures" / f"{path}.png"


def model_path(ref: str) -> Path | None:
    namespace, path = ref.split(":", 1) if ":" in ref else ("minecraft", ref)
    if namespace != spec.MOD_ID:
        return None
    return ASSETS / "models" / f"{path}.json"


def validate() -> list[str]:
    problems = [f"spec: {e}" for e in spec.validate()]
    # every model's textures and parents exist
    for model in (ASSETS / "models").rglob("*.json"):
        body = json.loads(model.read_text())
        parent = body.get("parent")
        if parent:
            mp = model_path(parent)
            if mp is not None and not mp.exists():
                problems.append(f"{model.relative_to(ASSETS)}: missing parent {parent}")
        for key, ref in body.get("textures", {}).items():
            tp = texture_path(ref)
            if tp is not None and not tp.exists():
                problems.append(f"{model.relative_to(ASSETS)}: missing texture {ref}")
    # every blockstate model exists
    for bs in (ASSETS / "blockstates").glob("*.json"):
        for variant in json.loads(bs.read_text()).get("variants", {}).values():
            mp = model_path(variant["model"])
            if mp is not None and not mp.exists():
                problems.append(f"blockstates/{bs.name}: missing model {variant['model']}")
    # every registered item has a model and a name
    lang = json.loads((ASSETS / "lang" / "en_us.json").read_text())
    manifest = json.loads((GENERATED / spec.MOD_ID / "content" / "manifest.json").read_text())
    item_ids = [i["id"] for i in manifest["items"]] + [i.id for i in spec.TOOLS + spec.WORKSTATIONS]
    item_ids += [t.sapling for t in spec.TREES] + [t.leaves for t in spec.TREES] + manifest["gardens"] + manifest["crates"]
    item_ids += [f["id"] for f in manifest["feasts"]]
    for item in item_ids:
        if not (ASSETS / "models" / "item" / f"{item}.json").exists():
            problems.append(f"item {item}: no item model")
        if f"item.{spec.MOD_ID}.{item}" not in lang and f"block.{spec.MOD_ID}.{item}" not in lang:
            problems.append(f"item {item}: no translation")
    for gui in ("textures/gui/container/cooking_pot.png", "textures/mob_effect/well_fed.png",
                "textures/mob_effect/cozy.png", "textures/mob_effect/caffeinated.png"):
        if not (ASSETS / gui).exists():
            problems.append(f"missing {gui}")
    if not (MAIN_RESOURCES / "logo.png").exists():
        problems.append("missing logo.png")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--art", action="store_true", help="regenerate textures and 3D models too")
    parser.add_argument("--check", action="store_true", help="only validate")
    args = parser.parse_args()

    if not args.check:
        if args.art:
            run_art()
        written = datagen.generate()
        print(f"datagen: {len(written)} json files")
    problems = validate()
    for p in problems[:200]:
        print("  !", p)
    print(f"validation: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
