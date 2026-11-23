"""Derives the Minecraft 26.2 and 26.3 resources from the 1.21.1 output of :mod:`sas.datagen`.

    python3 tools/assetgen/build_assets.py            # runs this after datagen and the 1.20.1 conversion

Textures, blockstates, lang, tags and the content manifest are copied as they are. What changed format:

26.2 (and 26.3)
- every item needs an item model definition in ``assets/<ns>/items/<id>.json``;
- recipe ingredients are an item id, a ``#tag`` or a list of those; the mortar recipes are plain
  ``minecraft:crafting_shapeless`` (the mortar keeps itself in the grid through its crafting-remainder hooks);
- vanilla ids renamed by the copper update (``minecraft:chain`` -> ``minecraft:iron_chain``);
- advancement backgrounds name a texture without ``textures/`` and ``.png``;
- ``minecraft:random_patch`` is gone: a wild garden patch is its ``simple_block`` feature placed with
  count + random_offset + block_predicate_filter modifiers (the same spread, as triangular distributions);
- tree configs lost ``dirt_provider``/``force_dirt``: what goes under the trunk is ``below_trunk_provider``
  (26.2: a rule-based provider that puts dirt where ``#minecraft:cannot_replace_below_tree_trunk`` allows;
  26.3: the built-in ``minecraft:soil_beneath_tree``). Without it the data pack fails to load and the server stops;
- NeoForge loads every ``data/<ns>/loot_modifiers/*.json``; the global list file is gone;
- tool materials name their repair items with an item tag (``sprout_and_soil:flint_tool_materials``).

(pack.mcmeta is hand-written in each workspace's ``common/src/main/resources``: one ``min_format``/``max_format``
range for the mod's resource pack and data pack.)

26.3 only
- the ``minecraft:recipe_unlocked`` trigger takes a ``recipes`` list instead of one ``recipe`` (the old key stops
  the advancement, and the recipe book unlock it carries, from loading);
- loot conditions and functions are keyed by ``type``; a ``condition`` field holds one condition (several are
  wrapped in ``minecraft:all_of``), ``functions`` became ``modifier``, rolls and counts are integer providers,
  and ``block_state_property`` became ``match_block`` (``blocks`` and ``state``);
- configured features live in ``worldgen/feature`` with their config flattened into the feature object,
  block states are ``{"id", "properties"}`` and simple state providers are the bare state;
  ``minecraft:weighted_state_provider`` is registered as ``minecraft:weighted`` (the old name stops the data pack
  from loading);
  ``random_offset`` became ``minecraft:offset`` with ``x``/``y``/``z``;
- block model elements: ``"shade": false`` became ``"shade_direction_override": "up"``;
- compost chances are an item component (set in Java), so NeoForge's compostables data map is not shipped.

Everything is written to ``26.2/common/src/generated/resources`` and ``26.3/common/src/generated/resources``.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .paths import GENERATED, REPO
from .spec.model import MOD_ID

M = MOD_ID
TARGETS = {
    "26.2": {"v263": False},
    "26.3": {"v263": True},
}
RENAMED_26 = {"minecraft:chain": "minecraft:iron_chain"}
MORTAR_RECIPE = f"{M}:tool_shapeless"

WRITTEN: list[Path] = []


def target_root(game: str) -> Path:
    return REPO / game / "common" / "src" / "generated" / "resources"


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    WRITTEN.append(path)


def _renamed(node):
    if isinstance(node, dict):
        return {k: _renamed(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_renamed(v) for v in node]
    if isinstance(node, str):
        prefix = "#" if node.startswith("#") else ""
        return prefix + RENAMED_26.get(node[len(prefix):], node[len(prefix):])
    return node


# --------------------------------------------------------------------------- 26.2


def ingredient(value):
    """{"item": id} / {"tag": t} / [...] -> "id" / "#t" / [...]"""
    if isinstance(value, list):
        return [ingredient(v) for v in value]
    if isinstance(value, dict):
        if "tag" in value:
            return "#" + value["tag"]
        if "item" in value:
            return value["item"]
    return value


def recipe(body: dict) -> dict:
    body = dict(body)
    if body.get("type") == MORTAR_RECIPE:
        body["type"] = "minecraft:crafting_shapeless"
    if "key" in body:
        body["key"] = {k: ingredient(v) for k, v in body["key"].items()}
    for field in ("ingredient", "tool", "container", "base", "addition", "template"):
        if field in body:
            body[field] = ingredient(body[field])
    if "ingredients" in body:
        body["ingredients"] = [ingredient(i) for i in body["ingredients"]]
    return body


def advancement(body: dict) -> dict:
    body = json.loads(json.dumps(body))
    display = body.get("display", {})
    background = display.get("background")
    if background:
        ns, path = background.split(":", 1) if ":" in background else ("minecraft", background)
        if path.startswith("textures/") and path.endswith(".png"):
            display["background"] = f"{ns}:{path[len('textures/'):-len('.png')]}"
    return body


def _trapezoid(spread: int) -> dict:
    return {"type": "minecraft:trapezoid", "min": -spread, "max": spread, "plateau": 0}


def split_patches(data: Path) -> None:
    """random_patch configured features -> the inner feature, with the patch spread moved onto the placed feature."""
    configured = data / M / "worldgen" / "configured_feature"
    placed = data / M / "worldgen" / "placed_feature"
    for path in sorted(configured.rglob("*.json")):
        body = _read(path)
        if body.get("type") != "minecraft:random_patch":
            continue
        config = body["config"]
        inner = config["feature"]
        _write(path, inner["feature"])
        placed_path = placed / path.relative_to(configured)
        placed_body = _read(placed_path)
        placed_body["placement"] += [
            {"type": "minecraft:count", "count": config["tries"]},
            {"type": "minecraft:random_offset", "xz_spread": _trapezoid(config["xz_spread"]),
             "y_spread": _trapezoid(config["y_spread"])},
        ] + inner.get("placement", [])
        _write(placed_path, placed_body)


BELOW_TRUNK_262 = {
    "type": "minecraft:rule_based_state_provider",
    "rules": [{
        "if_true": {"type": "minecraft:not", "predicate": {"type": "minecraft:matching_block_tag",
                                                           "tag": "minecraft:cannot_replace_below_tree_trunk"}},
        "then": {"type": "minecraft:simple_state_provider", "state": {"Name": "minecraft:dirt"}},
    }],
}
BELOW_TRUNK_263 = "minecraft:soil_beneath_tree"


def trees(data: Path, v263: bool) -> None:
    """Tree configs: dirt_provider + force_dirt -> below_trunk_provider."""
    configured = data / M / "worldgen" / "configured_feature"
    for path in sorted(configured.rglob("*.json")):
        body = _read(path)
        if body.get("type") != "minecraft:tree":
            continue
        config = body["config"]
        config.pop("dirt_provider", None)
        config.pop("force_dirt", None)
        config["below_trunk_provider"] = BELOW_TRUNK_263 if v263 else BELOW_TRUNK_262
        _write(path, body)


def item_definitions(assets: Path) -> None:
    for model in sorted((assets / "models" / "item").glob("*.json")):
        _write(assets / "items" / model.name, {"model": {"type": "minecraft:model", "model": f"{M}:item/{model.stem}"}})


# --------------------------------------------------------------------------- 26.3


def _is_condition_list(value) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(v, dict) and isinstance(v.get("condition"), str)
                                                          for v in value)


def condition_263(cond: dict) -> dict:
    cond = dict(cond)
    if cond["condition"] == "minecraft:block_state_property":
        cond = {"condition": "minecraft:match_block", "blocks": cond["block"],
                **({"state": cond["properties"]} if "properties" in cond else {})}
    out = {"type": cond.pop("condition")}
    for key, value in cond.items():
        if key == "terms":
            out[key] = [condition_263(t) for t in value]
        elif key == "term":
            out[key] = condition_263(value)
        else:
            out[key] = value
    return out


def conditions_263(conds: list) -> dict:
    terms = [condition_263(c) for c in conds]
    return terms[0] if len(terms) == 1 else {"type": "minecraft:all_of", "terms": terms}


def _int_provider(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {k: _int_provider(v) if k in ("min", "max", "value") else v for k, v in value.items()}
    return value


def function_263(fn: dict) -> dict:
    out = {"type": fn["function"]}
    for key, value in fn.items():
        if key == "function":
            continue
        if key == "conditions":
            out["condition"] = conditions_263(value)
        elif fn["function"] == "minecraft:set_count" and key == "count":
            out[key] = _int_provider(value)
        else:
            out[key] = value
    return out


def loot_263(node):
    if isinstance(node, list):
        return [loot_263(v) for v in node]
    if not isinstance(node, dict):
        return node
    out = {}
    for key, value in node.items():
        if key == "conditions" and _is_condition_list(value):
            out["condition"] = conditions_263(value)
        elif key == "functions":
            out["modifier"] = [function_263(f) for f in value]
        elif key == "rolls":
            out[key] = _int_provider(value)
        else:
            out[key] = loot_263(value)
    return out


def advancement_263(body: dict) -> dict:
    for criterion in body.get("criteria", {}).values():
        conditions = criterion.get("conditions", {})
        if criterion.get("trigger") == "minecraft:recipe_unlocked" and isinstance(conditions.get("recipe"), str):
            conditions["recipes"] = [conditions.pop("recipe")]
        for key, value in list(conditions.items()):
            if _is_condition_list(value):
                conditions[key] = conditions_263(value)
    return body


def loot_modifier_263(body: dict) -> dict:
    body = dict(body)
    if "conditions" in body:
        body["condition"] = conditions_263(body.pop("conditions"))
    return body


def block_states_263(node):
    """{"Name", "Properties"} -> {"id", "properties"}; simple_state_provider -> the bare state;
    weighted_state_provider -> weighted; random_offset -> offset."""
    if isinstance(node, list):
        return [block_states_263(v) for v in node]
    if not isinstance(node, dict):
        return node
    if isinstance(node.get("Name"), str) and set(node) <= {"Name", "Properties"}:
        state = {"id": node["Name"]}
        if "Properties" in node:
            state["properties"] = node["Properties"]
        return state
    if node.get("type") == "minecraft:simple_state_provider" and "state" in node:
        return block_states_263(node["state"])
    if node.get("type") == "minecraft:weighted_state_provider":
        return {"type": "minecraft:weighted", **{k: block_states_263(v) for k, v in node.items() if k != "type"}}
    if node.get("type") == "minecraft:random_offset":
        xz, y = node.get("xz_spread", 0), node.get("y_spread", 0)
        return {"type": "minecraft:offset", "x": xz, "y": y, "z": xz}
    return {k: block_states_263(v) for k, v in node.items()}


def worldgen_263(data: Path) -> None:
    root = data / M / "worldgen"
    configured = root / "configured_feature"
    for path in sorted(configured.rglob("*.json")):
        body = _read(path)
        flat = {"type": body["type"], **body.get("config", {})}
        _write(root / "feature" / path.relative_to(configured), block_states_263(flat))
    shutil.rmtree(configured)
    for path in sorted((root / "placed_feature").rglob("*.json")):
        _write(path, block_states_263(_read(path)))


def model_263(body: dict) -> dict:
    if not isinstance(body.get("elements"), list):
        return body
    for element in body["elements"]:
        if isinstance(element, dict) and isinstance(element.get("shade"), bool):
            if not element.pop("shade"):
                element.setdefault("shade_direction_override", "up")
    return body


# --------------------------------------------------------------------------- driver


def port(game: str) -> None:
    formats = TARGETS[game]
    target = target_root(game)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(GENERATED, target)
    data = target / "data"
    assets = target / "assets" / M

    shutil.rmtree(data / "neoforge" / "loot_modifiers")
    split_patches(data)
    trees(data, formats["v263"])
    _write(data / M / "tags" / "item" / "flint_tool_materials.json", {"values": ["minecraft:flint"]})
    for path in sorted(data.rglob("*.json")):
        rel = path.relative_to(data).as_posix()
        body = _renamed(_read(path))
        folder = rel.split("/")[1] if rel.count("/") >= 2 else ""
        if folder == "recipe":
            body = recipe(body)
        elif folder == "advancement":
            body = advancement(body)
            if formats["v263"]:
                body = advancement_263(body)
        elif folder == "loot_table" and formats["v263"]:
            body = loot_263(body)
        elif folder == "loot_modifiers" and formats["v263"]:
            body = loot_modifier_263(body)
        _write(path, body)
    if formats["v263"]:
        worldgen_263(data)
        # Compost chances are the item's minecraft:compostable component on 26.3 (see ModItems).
        shutil.rmtree(data / "neoforge" / "data_maps")
        if not any((data / "neoforge").iterdir()):
            (data / "neoforge").rmdir()
        for path in sorted((assets / "models").rglob("*.json")):
            _write(path, model_263(_read(path)))
    for path in sorted(assets.rglob("*.json")):
        if "/lang/" not in path.as_posix():
            body = _read(path)
            renamed = _renamed(body)
            if renamed != body:
                _write(path, renamed)
    item_definitions(assets)


def generate() -> list[Path]:
    WRITTEN.clear()
    for game in TARGETS:
        port(game)
    return list(WRITTEN)


def validate() -> list[str]:
    problems = []
    for game, formats in TARGETS.items():
        target = target_root(game)
        data = target / "data"
        for path in data.glob(f"{M}/recipe/**/*.json"):
            body = _read(path)
            text = path.read_text()
            fields = [body.get(f) for f in ("ingredient", "tool", "container", "base", "addition", "template")]
            fields += list(body.get("key", {}).values()) + list(body.get("ingredients", []))
            if any(isinstance(f, dict) for f in fields):
                problems.append(f"{game}: {path.name} still has an object ingredient")
            if MORTAR_RECIPE in text:
                problems.append(f"{game}: {path.name} still uses {MORTAR_RECIPE}")
        if (data / "neoforge" / "loot_modifiers").exists():
            problems.append(f"{game}: global_loot_modifiers.json left behind")
        for path in target.rglob("*.json"):
            text = path.read_text()
            if "minecraft:random_patch" in text or '"minecraft:chain"' in text or '"dirt_provider"' in text:
                problems.append(f"{game}: {path.relative_to(target)} has a pre-26 reference")
            if formats["v263"] and ('"condition": "' in text or '"function": "' in text or '"Name":' in text
                                    or '_state_provider"' in text):
                problems.append(f"{game}: {path.relative_to(target)} still has a 26.2 loot or block-state shape")
            if formats["v263"] and "/advancement/" in path.as_posix() and '"recipe": "' in text:
                problems.append(f"{game}: {path.relative_to(target)} still has a single recipe_unlocked recipe")
        if formats["v263"] and (data / M / "worldgen" / "configured_feature").exists():
            problems.append(f"{game}: worldgen/configured_feature left behind")
        models = target / "assets" / M / "models" / "item"
        for model in models.glob("*.json"):
            if not (target / "assets" / M / "items" / model.name).exists():
                problems.append(f"{game}: no item model definition for {model.stem}")
    return problems


__all__ = ["generate", "validate", "TARGETS"]
