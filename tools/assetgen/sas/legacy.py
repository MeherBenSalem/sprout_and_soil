"""Derives the Minecraft 1.20.1 resources from the 1.21.1 output of :mod:`sas.datagen`.

Assets (textures, models, blockstates, lang) and worldgen are identical. Data files differ in folder
names (``recipes/``, ``loot_tables/``, ``tags/items``...), in a few JSON shapes (``{"item": ...}``
results, list-valued item predicates, the old enchantment predicate) and in loader glue: Forge
1.20.1 reads biome modifiers from ``forge/biome_modifier`` and has no data maps or ``add_table``
loot modifier (compostables and the grass seed table are wired in Java instead).

Everything is written to ``1.20.1/common/src/generated/resources``.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import datagen
from .paths import GENERATED, LEGACY_GENERATED
from .spec.model import MOD_ID

M = MOD_ID
DATA_VERSION = 3465  # Minecraft 1.20.1

# data/<namespace>/<folder> renames, longest prefix first
FOLDERS = [("tags/item/", "tags/items/"), ("tags/block/", "tags/blocks/"), ("recipe/", "recipes/"),
           ("loot_table/", "loot_tables/"), ("advancement/", "advancements/"), ("structure/", "structures/")]
# 1.21 tags with no meaning (or no equivalent) in 1.20.1
DROPPED_TAGS = ("minecraft:enchantable/", "minecraft:chicken_food", "minecraft:parrot_food")
RENAMED_IDS = {"minecraft:short_grass": "minecraft:grass", "minecraft:blocks/short_grass": "minecraft:blocks/grass"}
KNIFE_TAG = "c:tools/knife"
# 1.21 convention tags -> 1.20.1 Forge / Fabric equivalents (mirrors only; the c: tags are kept too)
ITEM_TAG_MIRRORS = {"c:crops": ["forge:crops"], "c:seeds": ["forge:seeds"], "c:foods/vegetable": ["forge:vegetables"],
                    "c:foods/fruit": ["forge:fruits"], "c:foods/berry": ["forge:berries"],
                    KNIFE_TAG: ["forge:tools/knives", "c:tools/knives"]}
BIOME_TAGS = {"c:is_plains": ["c:plains", "forge:is_plains"], "c:is_birch_forest": ["c:birch_forest"],
              "c:is_desert": ["c:desert", "forge:is_desert"], "c:is_swamp": ["c:swamp", "forge:is_swamp"]}

WRITTEN: list[Path] = []


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    WRITTEN.append(path)


def _rename_ids(value):
    if isinstance(value, str):
        return RENAMED_IDS.get(value, value)
    if isinstance(value, list):
        return [_rename_ids(v) for v in value]
    if isinstance(value, dict):
        return {k: _rename_ids(v) for k, v in value.items()}
    return value


# --------------------------------------------------------------------------- per-format converters


def _stack(obj: dict) -> dict:
    """1.21 ``{"id", "count"}`` item stack -> 1.20.1 ``{"item", "count"}``."""
    out = {"item": obj["id"]}
    if obj.get("count", 1) != 1:
        out["count"] = obj["count"]
    return out


def _knife_ingredient(ing):
    if isinstance(ing, dict) and ing.get("tag") == KNIFE_TAG:
        return {"tag": f"{M}:knives"}
    return ing


def convert_recipe(body: dict) -> dict:
    body = dict(body)
    kind = body["type"]
    if kind in ("minecraft:smelting", "minecraft:smoking", "minecraft:campfire_cooking", "minecraft:blasting"):
        body["result"] = body["result"]["id"]
    elif "result" in body:
        body["result"] = _stack(body["result"])
    if "results" in body:
        body["results"] = [{**r, "item": _stack(r["item"])} for r in body["results"]]
    if "tool" in body:
        body["tool"] = _knife_ingredient(body["tool"])
    return body


def _item_predicate(pred: dict) -> dict:
    pred = dict(pred)
    if isinstance(pred.get("items"), str):
        pred["items"] = [pred["items"]]
    enchants = pred.pop("predicates", {}).get("minecraft:enchantments")
    if enchants:
        pred["enchantments"] = [{"enchantment": e["enchantments"], "levels": e["levels"]} for e in enchants]
    return pred


def convert_loot(value):
    if isinstance(value, list):
        return [convert_loot(v) for v in value]
    if isinstance(value, dict):
        out = {k: convert_loot(v) for k, v in value.items()}
        if out.get("condition") == "minecraft:match_tool" and "predicate" in out:
            out["predicate"] = _item_predicate(out["predicate"])
        return out
    return value


def convert_advancement(body: dict) -> dict:
    body = json.loads(json.dumps(body))
    icon = body.get("display", {}).get("icon")
    if icon and "id" in icon:
        body["display"]["icon"] = {"item": icon["id"]}
    return body


def convert_tag(tag: str, body: dict) -> dict:
    values = []
    for v in body["values"]:
        ref = v["id"] if isinstance(v, dict) else v
        bare = ref.lstrip("#")
        if bare in BIOME_TAGS:
            values.extend({"id": f"#{alias}", "required": False} for alias in BIOME_TAGS[bare])
            continue
        values.append(_rename_ids(v))
    return {**body, "values": values}


# --------------------------------------------------------------------------- driver


def _target(rel: str) -> str:
    """data/<ns>/<rest> folder renames."""
    parts = rel.split("/", 2)
    if len(parts) < 3 or parts[0] != "data":
        return rel
    for old, new in FOLDERS:
        if parts[2].startswith(old):
            return f"data/{parts[1]}/{new}{parts[2][len(old):]}"
    return rel


def _tag_id(rel: str) -> str | None:
    """'data/c/tags/item/crops/tomato.json' -> 'c:crops/tomato' (item tags only)."""
    parts = rel.split("/")
    if len(parts) > 4 and parts[0] == "data" and parts[2] == "tags" and parts[3] == "item":
        return f"{parts[1]}:{'/'.join(parts[4:])[:-5]}"
    return None


def generate() -> list[Path]:
    WRITTEN.clear()
    if LEGACY_GENERATED.exists():
        shutil.rmtree(LEGACY_GENERATED)
    item_tags: dict[str, dict] = {}

    for src in sorted(GENERATED.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(GENERATED).as_posix()
        if rel.startswith("data/neoforge/") or f"/{M}/loot_modifiers/" in f"/{rel}" or rel.endswith(".nbt"):
            continue
        if rel.startswith(f"data/{M}/neoforge/biome_modifier/"):
            body = json.loads(src.read_text())
            body["type"] = "forge:add_features"
            _write_json(LEGACY_GENERATED / rel.replace("/neoforge/biome_modifier/", "/forge/biome_modifier/"), body)
            continue
        dst = LEGACY_GENERATED / _target(rel)
        if src.suffix != ".json" or rel.startswith("assets/") or rel.startswith(f"{M}/"):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            WRITTEN.append(dst)
            continue
        body = json.loads(src.read_text())
        tag_kind = rel.split("/")[3] if rel.split("/")[2:3] == ["tags"] else None
        if tag_kind in ("item", "block"):
            namespace, path = rel.split("/")[1], "/".join(rel.split("/")[4:])[:-5]
            if f"{namespace}:{path}".startswith(DROPPED_TAGS):
                continue
            body = convert_tag(f"{namespace}:{path}", body)
            if tag_kind == "item":
                item_tags[f"{namespace}:{path}"] = body
        elif "/recipe/" in rel:
            body = convert_recipe(body)
        elif "/loot_table/" in rel:
            body = _rename_ids(convert_loot(body))
        elif "/advancement/" in rel:
            body = convert_advancement(body)
        elif "/tags/worldgen/biome/" in rel:
            body = convert_tag("", body)
        _write_json(dst, body)

    _mirror_item_tags(item_tags)
    datagen.write_test_structure(LEGACY_GENERATED / "data" / M / "structures" / "empty.nbt", DATA_VERSION)
    WRITTEN.append(LEGACY_GENERATED / "data" / M / "structures" / "empty.nbt")
    return list(WRITTEN)


def _mirror_item_tags(item_tags: dict[str, dict]) -> None:
    """forge:crops/tomato, forge:seeds/tomato, forge:tools/knives... mirroring our c: tags, plus the knives tag."""
    mirrors: dict[str, list] = {}
    for tag, body in item_tags.items():
        targets = list(ITEM_TAG_MIRRORS.get(tag, []))
        if tag.startswith(("c:crops/", "c:seeds/")):
            targets.append("forge:" + tag[2:])
        for target in targets:
            values = mirrors.setdefault(target, [])
            for v in body["values"]:
                ref = v["id"] if isinstance(v, dict) else v
                # point at the forge mirror of a referenced c: tag instead of the c: tag itself
                if ref.startswith("#c:crops/") or ref.startswith("#c:seeds/"):
                    v = "#forge:" + ref[3:]
                if v not in values:
                    values.append(v)
    for tag, values in sorted(mirrors.items()):
        namespace, path = tag.split(":")
        _write_json(LEGACY_GENERATED / "data" / namespace / "tags" / "items" / f"{path}.json",
                    {"replace": False, "values": values})
    # Knives from other mods also work on the cutting board.
    knives = LEGACY_GENERATED / "data" / M / "tags" / "items" / "knives.json"
    body = json.loads(knives.read_text())
    body["values"] += [{"id": "#forge:tools/knives", "required": False}, {"id": "#c:tools/knives", "required": False}]
    _write_json(knives, body)


def validate() -> list[str]:
    """Shape checks for the converted files (the shared content is validated on the 1.21.1 side)."""
    problems = []
    data = LEGACY_GENERATED / "data"
    for folder in ("recipe", "loot_table", "advancement", "structure"):
        if any(data.glob(f"*/{folder}/**/*")):
            problems.append(f"1.20.1: a 1.21 '{folder}/' folder was left behind")
    for path in data.glob(f"{M}/recipes/**/*.json"):
        body = json.loads(path.read_text())
        result = body.get("result")
        if isinstance(result, dict) and "id" in result:
            problems.append(f"1.20.1: {path.name} still uses a 1.21 result")
    for path in data.rglob("*.json"):
        text = path.read_text()
        if "short_grass" in text or '"minecraft:enchantments"' in text or "neoforge:" in text:
            problems.append(f"1.20.1: {path.relative_to(LEGACY_GENERATED)} has a 1.21-only reference")
    if not (data / M / "structures" / "empty.nbt").exists():
        problems.append("1.20.1: missing the GameTest structure")
    if not (LEGACY_GENERATED / M / "content" / "manifest.json").exists():
        problems.append("1.20.1: missing the content manifest")
    return problems


__all__ = ["generate", "validate", "convert_recipe", "convert_loot", "convert_advancement", "convert_tag"]
