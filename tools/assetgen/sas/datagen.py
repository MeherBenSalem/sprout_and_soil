"""Generates every JSON resource (and the Java content manifest) from ``sas.spec``.

Targets Minecraft 1.21.1 folder layout (``recipe/``, ``loot_table/``, ``tags/item``...).
Run through ``tools/assetgen/build_assets.py``.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import spec
from .paths import ASSETS, DATA, GENERATED
from .spec import (CROPS, FEASTS, GARDENS, TOOLS, TREES, WORKSTATIONS, ItemDef, ns, title)
from .spec.model import MOD_ID, Recipe

M = MOD_ID
WRITTEN: list[Path] = []

# vanilla foods that belong in convention food tags next to ours
CONTAINERS = {"minecraft:bowl", "minecraft:glass_bottle", ns("mug"), ns("plate")}


def write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    WRITTEN.append(path)


def data(namespace: str, rel: str) -> Path:
    return DATA / namespace / rel


def asset(rel: str) -> Path:
    return ASSETS / rel


def ingredient(ref: str) -> dict:
    return {"tag": ref[1:]} if ref.startswith("#") else {"item": ns(ref)}


def stack(item: str, count: int = 1) -> dict:
    return {"count": count, "id": ns(item)}


# =========================================================================== manifest (Java)


def build_manifest() -> dict:
    items = spec.CONTAINERS + spec.crop_items() + spec.fruit_items() + spec.INGREDIENTS + spec.DISHES + spec.DRINKS \
        + spec.slice_items()
    item_json = []
    for i in items:
        e = {"id": i.id, "stack": i.stack}
        if i.food:
            e["food"] = i.food.to_json()
        if i.container:
            e["container"] = ns(i.container)
        if i.remainder:
            e["remainder"] = ns(i.remainder)
        if i.drink:
            e["drink"] = True
        if i.plants:
            e["plants"] = i.plants
        if i.tooltip:
            e["tooltip"] = True
        item_json.append(e)

    compost = {}
    for i in spec.all_item_defs():
        if i.compost:
            compost[ns(i.id)] = i.compost
    for t in TREES:
        compost[ns(t.sapling)] = 0.3
        compost[ns(t.leaves)] = 0.3
    for g in GARDENS:
        compost[ns(g.id)] = 0.65

    worldgen = [{"feature": f"{M}:wild_garden/{g.id}", "biomes": f"{M}:spawns/{g.biomes[0]}"} for g in GARDENS]
    worldgen += [{"feature": f"{M}:fruit_tree/{t.id}", "biomes": f"{M}:spawns/{t.biomes}"} for t in TREES]

    seeds = [ns(c.planting_item.id) for c in CROPS]
    produce = [ns(c.produce.id) for c in CROPS if c.produce.food]
    fruits = [ns(i.id) for i in spec.fruit_items()]
    saplings = [ns(t.sapling) for t in TREES]
    meals = [ns(i.id) for i in spec.SOUPS + spec.PLATES if i.container]

    return {
        "format": 1,
        "crops": [{"id": c.id, "block": c.block, "planting_item": c.planting_item.id, "produce": c.produce.id,
                   "model": c.model, "regrow_age": c.regrow_age} for c in CROPS],
        "trees": [{"id": t.id, "sapling": t.sapling, "leaves": t.leaves, "fruit": t.fruit_id,
                   "feature": f"{M}:fruit_tree/{t.id}"} for t in TREES],
        "items": item_json,
        "feasts": [{"id": f.id, "kind": f.kind, **({"slice": f.slice.id} if f.slice else {})} for f in FEASTS],
        "crates": list(spec.crate_sources()),
        "gardens": [g.id for g in GARDENS],
        "compost": compost,
        "worldgen": worldgen,
        "tabs": {"farm": tab_order("farm"), "kitchen": tab_order("kitchen")},
        "trades": {"seeds": seeds, "produce": produce, "fruits": fruits, "saplings": saplings, "meals": meals},
    }


def tab_order(tab: str) -> list[str]:
    out = []
    if tab == "farm":
        out += [ns(i.id) for i in TOOLS if i.tab == "farm"]
        out += [ns(w.id) for w in WORKSTATIONS if w.tab == "farm"]
        out += [ns(c.seed.id) for c in CROPS if c.seed]
        out += [ns(c.produce.id) for c in CROPS]
        out += [ns(t.sapling) for t in TREES]
        out += [ns(i.id) for i in spec.fruit_items()]
        out += [ns(t.leaves) for t in TREES]
        out += [ns(g.id) for g in GARDENS]
        out += [ns(c) for c in spec.crate_sources()]
    else:
        out += [ns(w.id) for w in WORKSTATIONS if w.tab == "kitchen"]
        out += [ns(i.id) for i in TOOLS if i.tab == "kitchen"]
        out += [ns(i.id) for i in spec.CONTAINERS + spec.INGREDIENTS + spec.DISHES + spec.DRINKS]
        for f in FEASTS:
            out.append(ns(f.id))
            if f.slice:
                out.append(ns(f.slice.id))
    return out


# =========================================================================== models & blockstates


def stage_of(age: int) -> int:
    return 0 if age <= 1 else 1 if age <= 3 else 2 if age <= 6 else 3


def gen_models() -> None:
    bm = lambda name: f"{M}:block/{name}"  # noqa: E731

    # tall crop template: two stacked #-shaped crop planes
    def planes(y0, y1, tex):
        out = []
        for axis, pos in (("x", 4), ("x", 12), ("z", 4), ("z", 12)):
            if axis == "x":
                frm, to = [pos, y0, 0], [pos, y1, 16]
                faces = {"west": {"uv": [0, 0, 16, 16], "texture": tex}, "east": {"uv": [0, 0, 16, 16], "texture": tex}}
            else:
                frm, to = [0, y0, pos], [16, y1, pos]
                faces = {"north": {"uv": [0, 0, 16, 16], "texture": tex}, "south": {"uv": [0, 0, 16, 16], "texture": tex}}
            out.append({"from": frm, "to": to, "shade": False, "faces": faces})
        return out

    write(asset("models/block/template_tall_crop.json"), {
        "ambientocclusion": False,
        "textures": {"particle": "#bottom"},
        "elements": planes(-1, 15, "#bottom") + planes(15, 31, "#top"),
    })

    for c in CROPS:
        for n in range(4):
            name = f"{c.id}_stage{n}"
            if c.model == "tall" and n >= 2:
                model = {"parent": bm("template_tall_crop"),
                         "textures": {"bottom": bm(name), "top": bm(f"{name}_top")}}
            elif c.model == "cross":
                model = {"parent": "minecraft:block/cross", "textures": {"cross": bm(name)}}
            else:
                model = {"parent": "minecraft:block/crop", "textures": {"crop": bm(name)}}
            model["render_type"] = "minecraft:cutout"
            write(asset(f"models/block/{name}.json"), model)
        write(asset(f"blockstates/{c.block}.json"), {"variants": {
            f"age={a}": {"model": bm(f"{c.id}_stage{stage_of(a)}")} for a in range(8)}})

    for t in TREES:
        write(asset(f"models/block/{t.sapling}.json"), {"parent": "minecraft:block/cross",
                                                       "textures": {"cross": bm(t.sapling)},
                                                       "render_type": "minecraft:cutout"})
        write(asset(f"blockstates/{t.sapling}.json"), {"variants": {"": {"model": bm(t.sapling)}}})
        write(asset(f"models/item/{t.sapling}.json"), {"parent": "minecraft:item/generated",
                                                      "textures": {"layer0": bm(t.sapling)}})
        for n in range(4):
            write(asset(f"models/block/{t.leaves}_{n}.json"), {"parent": "minecraft:block/cube_all",
                                                               "textures": {"all": bm(f"{t.leaves}_{n}")},
                                                               "render_type": "minecraft:cutout_mipped"})
        write(asset(f"blockstates/{t.leaves}.json"), {"variants": {
            f"age={n}": {"model": bm(f"{t.leaves}_{n}")} for n in range(4)}})
        write(asset(f"models/item/{t.leaves}.json"), {"parent": bm(f"{t.leaves}_3")})

    for g in GARDENS:
        write(asset(f"models/block/{g.id}.json"), {"parent": "minecraft:block/cross",
                                                  "textures": {"cross": bm(g.id)}, "render_type": "minecraft:cutout"})
        write(asset(f"blockstates/{g.id}.json"), {"variants": {"": {"model": bm(g.id)}}})
        write(asset(f"models/item/{g.id}.json"), {"parent": "minecraft:item/generated",
                                                 "textures": {"layer0": bm(g.id)}})

    for crate in spec.crate_sources():
        write(asset(f"models/block/{crate}.json"), {"parent": "minecraft:block/cube_bottom_top", "textures": {
            "top": bm(f"{crate}_top"), "side": bm("crate_side"), "bottom": bm("crate_bottom")}})
        write(asset(f"blockstates/{crate}.json"), {"variants": {"": {"model": bm(crate)}}})
        write(asset(f"models/item/{crate}.json"), {"parent": bm(crate)})

    for f in FEASTS:
        if f.kind == "cake":
            tex = {"particle": bm(f"{f.id}_side"), "bottom": bm(f"{f.id}_bottom"), "top": bm(f"{f.id}_top"),
                   "side": bm(f"{f.id}_side"), "inside": bm(f"{f.id}_inner")}
            write(asset(f"models/block/{f.id}.json"), {"parent": "minecraft:block/cake", "textures": tex})
            for n in range(1, 7):
                write(asset(f"models/block/{f.id}_slice{n}.json"), {"parent": f"minecraft:block/cake_slice{n}",
                                                                    "textures": tex})
            write(asset(f"blockstates/{f.id}.json"), {"variants": {
                f"bites={n}": {"model": bm(f.id if n == 0 else f"{f.id}_slice{n}")} for n in range(7)}})
        else:
            kind = f.kind
            tex = {"particle": bm(f"{f.id}_top"), "top": bm(f"{f.id}_top"), "inner": bm(f"{f.id}_inner"),
                   "side": bm(f"{kind}_side"), "bottom": bm(f"{kind}_bottom")}
            for n in range(4):
                write(asset(f"models/block/{f.id}_{n}.json"), {"parent": bm(f"template_{kind}_{n}"), "textures": tex})
            write(asset(f"blockstates/{f.id}.json"), {"variants": {
                f"servings_taken={n}": {"model": bm(f"{f.id}_{n}")} for n in range(4)}})
        write(asset(f"models/item/{f.id}.json"), {"parent": "minecraft:item/generated",
                                                 "textures": {"layer0": f"{M}:item/{f.id}"}})

    for w in WORKSTATIONS:
        if w.id == "sprinkler":
            write(asset(f"blockstates/{w.id}.json"), {"variants": {"": {"model": bm(w.id)}}})
        else:
            rot = {"north": 0, "east": 90, "south": 180, "west": 270}
            write(asset(f"blockstates/{w.id}.json"), {"variants": {
                f"facing={d}": ({"model": bm(w.id), "y": r} if r else {"model": bm(w.id)}) for d, r in rot.items()}})
        write(asset(f"models/item/{w.id}.json"), {"parent": bm(w.id)})

    for i in spec.manifest_items() + TOOLS:
        parent = "minecraft:item/handheld" if i.category == "tool" and i.stack == 1 and i.id != "watering_can" \
            else "minecraft:item/generated"
        write(asset(f"models/item/{i.id}.json"), {"parent": parent, "textures": {"layer0": f"{M}:item/{i.id}"}})


# =========================================================================== recipes


def recipe_json(owner: str, r: Recipe) -> tuple[str, dict]:
    name = r.name or owner
    if r.kind == "crafting_shaped":
        body = {"type": "minecraft:crafting_shaped", "category": "misc",
                "key": {k: ingredient(v) for k, v in r.ingredients.items()}, "pattern": r.pattern,
                "result": stack(owner, r.count)}
    elif r.kind == "crafting_shapeless":
        body = {"type": "minecraft:crafting_shapeless", "category": "misc",
                "ingredients": [ingredient(i) for i in r.ingredients], "result": stack(owner, r.count)}
    elif r.kind == "tool_shapeless":
        body = {"type": f"{M}:tool_shapeless", "category": "misc",
                "ingredients": [ingredient(i) for i in r.ingredients], "result": stack(owner, r.count)}
    elif r.kind == "cooking_pot":
        body = {"type": f"{M}:cooking", "ingredients": [ingredient(i) for i in r.ingredients],
                "result": stack(owner, r.count), "experience": r.xp, "cookingtime": r.time}
        if r.container:
            body["container"] = ingredient(r.container)
        name = f"cooking/{name}"
    elif r.kind == "cutting":
        body = {"type": f"{M}:cutting", "ingredient": ingredient(r.ingredients[0]), "tool": ingredient(r.tool),
                "results": [{"item": stack(item, count), **({"chance": chance} if chance < 1 else {})}
                            for item, count, *rest in r.results for chance in [rest[0] if rest else 1.0]]}
        name = f"cutting/{name}"
    else:
        raise ValueError(r.kind)
    return name, body


def gen_recipes() -> list[tuple[str, dict, list[str]]]:
    """Returns (recipe id, body, unlock items) for recipe-book advancements."""
    out = []

    def add(name, body, unlock):
        write(data(M, f"recipe/{name}.json"), body)
        out.append((name, body, unlock))

    for owner, r in spec.all_recipes():
        if r.kind == "cooking":
            ing = r.ingredients[0]
            for kind in r.cook_kinds:
                vt = {"smelting": ("minecraft:smelting", r.time, ""), "smoking": ("minecraft:smoking", r.time // 2, "_from_smoking"),
                      "campfire": ("minecraft:campfire_cooking", r.time * 3, "_from_campfire_cooking")}[kind]
                body = {"type": vt[0], "category": "food", "cookingtime": vt[1], "experience": r.xp,
                        "ingredient": ingredient(ing), "result": {"id": ns(owner)}}
                add(f"{r.name or owner}{vt[2]}", body, [ing])
            continue
        name, body = recipe_json(owner, r)
        unlock = [i for i in (r.ingredients.values() if isinstance(r.ingredients, dict) else r.ingredients)
                  if not i.startswith("#") and i not in ("mortar_and_pestle",)]
        add(name, body, unlock[:3])

    for crate, item in spec.crate_sources().items():
        add(crate, {"type": "minecraft:crafting_shaped", "category": "building", "key": {"#": {"item": item}},
                    "pattern": ["###", "###", "###"], "result": stack(crate)}, [item])
        add(f"{item.split(':')[1]}_from_crate", {"type": "minecraft:crafting_shapeless", "category": "misc",
                                                "ingredients": [{"item": ns(crate)}], "result": {"count": 9, "id": item}},
            [crate])

    for base in ("knife", "sickle"):
        add(f"netherite_{base}_smithing", {"type": "minecraft:smithing_transform",
                                           "addition": {"item": "minecraft:netherite_ingot"},
                                           "base": {"item": ns(f"diamond_{base}")},
                                           "template": {"item": "minecraft:netherite_upgrade_smithing_template"},
                                           "result": stack(f"netherite_{base}")}, [f"diamond_{base}"])

    # seeds from produce, for crops whose produce is not itself planted
    for c in CROPS:
        if c.seed is not None and c.produce.food is not None and c.model != "tall":
            add(f"{c.seed.id}_from_{c.produce.id}", {"type": "minecraft:crafting_shapeless", "category": "misc",
                                                     "ingredients": [{"item": ns(c.produce.id)}],
                                                     "result": stack(c.seed.id, 2)}, [c.produce.id])
    add("corn_seeds_from_corn", {"type": "minecraft:crafting_shapeless", "category": "misc",
                                 "ingredients": [{"item": ns("corn")}], "result": stack("corn_seeds", 3)}, ["corn"])
    add("string_from_cotton", {"type": "minecraft:crafting_shapeless", "category": "misc",
                               "ingredients": [{"item": ns("cotton")}] * 3, "result": {"count": 2, "id": "minecraft:string"}},
        ["cotton"])
    add("white_wool_from_cotton", {"type": "minecraft:crafting_shaped", "category": "building",
                                   "key": {"#": {"item": ns("cotton")}}, "pattern": ["##", "##"],
                                   "result": {"count": 1, "id": "minecraft:white_wool"}}, ["cotton"])
    add("melon_slices_from_cutting", {"type": f"{M}:cutting", "ingredient": {"item": "minecraft:melon"},
                                      "tool": {"tag": "c:tools/knife"},
                                      "results": [{"item": {"count": 8, "id": "minecraft:melon_slice"}}]}, [])
    for vanilla, out_count in (("minecraft:cake", None),):
        pass
    return out


def gen_recipe_advancements(recipes) -> None:
    for name, body, unlock in recipes:
        if body["type"].startswith(f"{M}:cooking") or body["type"].startswith(f"{M}:cutting") or not unlock:
            continue
        rid = f"{M}:{name}"
        crit = {"has_the_recipe": {"trigger": "minecraft:recipe_unlocked", "conditions": {"recipe": rid}}}
        items = sorted({ns(u) for u in unlock})
        crit["has_ingredient"] = {"trigger": "minecraft:inventory_changed", "conditions": {"items": [{"items": items}]}}
        write(data(M, f"advancement/recipes/{name}.json"), {
            "parent": "minecraft:recipes/root", "criteria": crit,
            "requirements": [list(crit)], "rewards": {"recipes": [rid]}})


# =========================================================================== loot tables


SHEARS_OR_SILK = {"condition": "minecraft:any_of", "terms": [
    {"condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}},
    {"condition": "minecraft:match_tool", "predicate": {"predicates": {"minecraft:enchantments": [
        {"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}]}


def age_is(block: str, prop: str, value) -> dict:
    return {"condition": "minecraft:block_state_property", "block": ns(block), "properties": {prop: str(value)}}


def self_drop(block: str, conditions=None) -> dict:
    pool = {"bonus_rolls": 0.0, "rolls": 1.0, "entries": [{"type": "minecraft:item", "name": ns(block)}],
            "conditions": [{"condition": "minecraft:survives_explosion"}] + (conditions or [])}
    return {"type": "minecraft:block", "pools": [pool], "random_sequence": f"{M}:blocks/{block}"}


def gen_loot() -> None:
    lt = lambda name: data(M, f"loot_table/blocks/{name}.json")  # noqa: E731
    bonus = lambda extra: {"function": "minecraft:apply_bonus", "enchantment": "minecraft:fortune",  # noqa: E731
                           "formula": "minecraft:binomial_with_bonus_count",
                           "parameters": {"extra": extra, "probability": 0.5714286}}
    for c in CROPS:
        ripe = age_is(c.block, "age", 7)
        produce, planting = ns(c.produce.id), ns(c.planting_item.id)
        lo, hi = c.drops
        if c.seed is None:
            pools = [
                {"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": produce}]},
                {"rolls": 1.0, "bonus_rolls": 0.0, "conditions": [ripe], "entries": [{
                    "type": "minecraft:item", "name": produce,
                    "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}},
                                  bonus(1)]}]},
            ]
        else:
            produce_entry = {"type": "minecraft:item", "name": produce, "conditions": [ripe]}
            if (lo, hi) != (1, 1):
                produce_entry["functions"] = [{"function": "minecraft:set_count",
                                               "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]
            produce_entry.setdefault("functions", []).append(bonus(1) if c.perennial else
                                                             {"function": "minecraft:apply_bonus",
                                                              "enchantment": "minecraft:fortune",
                                                              "formula": "minecraft:uniform_bonus_count",
                                                              "parameters": {"bonusMultiplier": 1}})
            seed_pool = {"rolls": 1.0, "bonus_rolls": 0.0, "conditions": [ripe],
                         "entries": [{"type": "minecraft:item", "name": planting,
                                      **({} if c.perennial else {"functions": [bonus(3)]})}]}
            pools = [
                {"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:alternatives", "children": [
                    produce_entry, {"type": "minecraft:item", "name": planting}]}]},
                seed_pool,
            ]
        write(lt(c.block), {"type": "minecraft:block", "pools": pools,
                            "functions": [{"function": "minecraft:explosion_decay"}],
                            "random_sequence": f"{M}:blocks/{c.block}"})

    for t in TREES:
        not_shears = {"condition": "minecraft:inverted", "term": SHEARS_OR_SILK}
        write(lt(t.leaves), {"type": "minecraft:block", "random_sequence": f"{M}:blocks/{t.leaves}", "pools": [
            {"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:alternatives", "children": [
                {"type": "minecraft:item", "name": ns(t.leaves), "conditions": [SHEARS_OR_SILK]},
                {"type": "minecraft:item", "name": ns(t.sapling), "conditions": [
                    {"condition": "minecraft:survives_explosion"},
                    {"condition": "minecraft:table_bonus", "enchantment": "minecraft:fortune",
                     "chances": [0.05, 0.0625, 0.083333336, 0.1]}]}]}]},
            {"rolls": 1.0, "bonus_rolls": 0.0, "conditions": [not_shears], "entries": [{
                "type": "minecraft:item", "name": "minecraft:stick",
                "conditions": [{"condition": "minecraft:table_bonus", "enchantment": "minecraft:fortune",
                                "chances": [0.02, 0.022222223, 0.025, 0.033333335, 0.1]}],
                "functions": [{"function": "minecraft:set_count", "add": False,
                               "count": {"type": "minecraft:uniform", "min": 1.0, "max": 2.0}},
                              {"function": "minecraft:explosion_decay"}]}]},
            {"rolls": 1.0, "bonus_rolls": 0.0, "conditions": [age_is(t.leaves, "age", 3)], "entries": [{
                "type": "minecraft:item", "name": t.fruit_id,
                "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1.0, "max": 2.0}},
                              {"function": "minecraft:explosion_decay"}]}]},
        ]})
        write(lt(t.sapling), self_drop(t.sapling))

    for g in GARDENS:
        pool = [{"type": "minecraft:item", "name": ns(spec.CROPS_BY_ID[c].planting_item.id)} for c in g.crops]
        produce = [{"type": "minecraft:item", "name": ns(spec.CROPS_BY_ID[c].produce.id)} for c in g.crops]
        write(lt(g.id), {"type": "minecraft:block", "random_sequence": f"{M}:blocks/{g.id}", "pools": [
            {"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": ns(g.id)}],
             "conditions": [{"condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}}]},
            {"rolls": {"type": "minecraft:uniform", "min": 1.0, "max": 2.0}, "bonus_rolls": 0.0,
             "conditions": [{"condition": "minecraft:inverted", "term": {
                 "condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}}}],
             "entries": pool},
            {"rolls": 1.0, "bonus_rolls": 0.0,
             "conditions": [{"condition": "minecraft:inverted", "term": {
                 "condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}}},
                 {"condition": "minecraft:random_chance", "chance": 0.35}],
             "entries": produce},
        ]})

    # Seeds from breaking grass (temperate crops only). Injected by a NeoForge loot modifier / Fabric loot event.
    temperate = {"meadow_garden", "woodland_garden", "highland_garden"}
    grass_seeds = sorted({ns(c.planting_item.id) for c in CROPS if c.seed and temperate & set(c.gardens)})
    write(data(M, "loot_table/gameplay/grass_seeds.json"), {"type": "minecraft:block", "pools": [{
        "rolls": 1.0, "bonus_rolls": 0.0,
        "conditions": [{"condition": "minecraft:inverted", "term": {
            "condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}}},
            {"condition": "minecraft:random_chance", "chance": 0.04}],
        "entries": [{"type": "minecraft:item", "name": seed} for seed in grass_seeds]}]})
    write(data(M, "loot_modifiers/grass_seeds.json"), {
        "type": "neoforge:add_table",
        "conditions": [{"condition": "neoforge:loot_table_id", "loot_table_id": "minecraft:blocks/short_grass"}],
        "table": f"{M}:gameplay/grass_seeds"})
    write(data("neoforge", "loot_modifiers/global_loot_modifiers.json"), {"replace": False,
                                                                        "entries": [f"{M}:grass_seeds"]})

    for crate in spec.crate_sources():
        write(lt(crate), self_drop(crate))
    for w in WORKSTATIONS:
        write(lt(w.id), self_drop(w.id))
    for f in FEASTS:
        if f.kind != "cake":
            write(lt(f.id), self_drop(f.id, [age_is(f.id, "servings_taken", 0)]))


# =========================================================================== tags


def gen_tags() -> None:
    item_tags: dict[str, list] = {}
    block_tags: dict[str, list] = {}

    def it(tag, *ids):
        item_tags.setdefault(tag, []).extend(ids)

    def bt(tag, *ids):
        block_tags.setdefault(tag, []).extend(ids)

    kind_tag = {"vegetable": "c:foods/vegetable", "fruit": "c:foods/fruit", "berry": "c:foods/berry"}
    for c in CROPS:
        p = ns(c.produce.id)
        crop_name = c.produce.id
        it(f"c:crops/{crop_name}", p)
        it("c:crops", f"#c:crops/{crop_name}")
        kind = c.produce.category.split(":")[1]
        if kind in kind_tag and c.produce.food:
            it(kind_tag[kind], p)
        if kind == "grain":
            it("c:crops/grain", p) if False else None
        planting = ns(c.planting_item.id)
        it(f"c:seeds/{c.id}", planting)
        it("c:seeds", f"#c:seeds/{c.id}")
        it("minecraft:villager_plantable_seeds", planting)
        if c.seed is not None:
            it("minecraft:chicken_food", planting)
            it("minecraft:parrot_food", planting)
        bt("minecraft:crops", ns(c.block))
        bt("minecraft:maintains_farmland", ns(c.block))
        bt(f"{M}:mineable/sickle", ns(c.block))
    for i in spec.fruit_items():
        it(kind_tag["berry" if i.id == "cherries" else "fruit"], ns(i.id))
        it(f"c:crops/{i.id}", ns(i.id))
        it("c:crops", f"#c:crops/{i.id}")

    for i in spec.FOOD_ITEMS + spec.slice_items() + spec.crop_items() + spec.fruit_items():
        if i.food:
            it("c:foods", ns(i.id))
        for tag in i.tags:
            it(tag, ns(i.id))
    for f in FEASTS:
        it("c:foods/edible_when_placed", ns(f.id))
        if f.kind == "pie":
            it("c:foods/pie", ns(f.id))
    for i in spec.DRINKS:
        it("c:drinks", ns(i.id))

    for t in TOOLS + WORKSTATIONS:
        for tag in t.tags:
            it(tag, ns(t.id))
    knives = [ns(t.id) for t in TOOLS if "knife" in t.id]
    sickles = [ns(t.id) for t in TOOLS if "sickle" in t.id]
    it("c:tools", "#c:tools/knife", *sickles)
    for tag in ("minecraft:enchantable/durability", "minecraft:enchantable/weapon", "minecraft:enchantable/sharp_weapon",
                "minecraft:breaks_decorated_pots"):
        it(tag, *knives)
    for tag in ("minecraft:enchantable/durability", "minecraft:enchantable/mining", "minecraft:enchantable/mining_loot",
                "minecraft:breaks_decorated_pots"):
        it(tag, *sickles)
    it("minecraft:enchantable/durability", ns("mortar_and_pestle"))
    it(f"{M}:crafting_tools", ns("mortar_and_pestle"))
    it(f"{M}:serving_containers", "minecraft:bowl", "minecraft:glass_bottle", ns("mug"), ns("plate"))

    for t in TREES:
        it("minecraft:saplings", ns(t.sapling))
        it("minecraft:leaves", ns(t.leaves))
        bt("minecraft:saplings", ns(t.sapling))
        bt("minecraft:leaves", ns(t.leaves))
        bt("minecraft:mineable/hoe", ns(t.leaves))
        bt(f"{M}:mineable/sickle", ns(t.leaves))
    for g in GARDENS:
        bt("minecraft:sword_efficient", ns(g.id))
        bt("minecraft:replaceable_by_trees", ns(g.id))
        bt("minecraft:enderman_holdable", ns(g.id))
        bt(f"{M}:mineable/sickle", ns(g.id))
        it(f"{M}:wild_gardens", ns(g.id))
    bt(f"{M}:mineable/sickle", "#minecraft:crops", "#minecraft:leaves", "minecraft:short_grass", "minecraft:tall_grass",
       "minecraft:fern", "minecraft:large_fern", "minecraft:sweet_berry_bush", "minecraft:vine", "minecraft:hay_block",
       "minecraft:dead_bush", "minecraft:seagrass")
    for crate in spec.crate_sources():
        bt("minecraft:mineable/axe", ns(crate))
        it(f"{M}:crates", ns(crate))
    bt("minecraft:mineable/axe", ns("cutting_board"), ns("scarecrow"))
    bt("minecraft:mineable/pickaxe", ns("cooking_pot"), ns("sprinkler"))
    bt(f"{M}:heat_sources", "minecraft:campfire", "minecraft:soul_campfire", "minecraft:fire", "minecraft:soul_fire",
       "minecraft:magma_block", "minecraft:lava", "minecraft:lava_cauldron",
       {"id": "#c:campfires", "required": False})

    def emit(kind, tags):
        for tag, values in tags.items():
            namespace, path = tag.split(":")
            seen, uniq = set(), []
            for v in values:
                key = json.dumps(v, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    uniq.append(v)
            write(data(namespace, f"tags/{kind}/{path}.json"), {"replace": False, "values": uniq})

    emit("item", item_tags)
    emit("block", block_tags)
    TAG_NAMES.clear()
    for tag in item_tags:
        namespace, path = tag.split(":")
        if namespace == M or path.startswith(("crops/", "seeds/")):
            TAG_NAMES[f"tag.item.{namespace}.{path.replace('/', '.')}"] = _tag_title(path)


def _tag_title(path: str) -> str:
    parts = path.split("/")
    if parts[0] in ("crops", "seeds") and len(parts) == 2:
        return f"{title(parts[1])} {'Crops' if parts[0] == 'crops' else 'Seeds'}"
    return title(parts[-1].replace("mineable", ""))


TAG_NAMES: dict[str, str] = {}


# =========================================================================== worldgen


def gen_worldgen() -> None:
    for group, biomes in spec.BIOME_GROUPS.items():
        values = []
        for b in biomes:
            if b.startswith("?"):
                values.append({"id": b[1:], "required": False})
            else:
                values.append(b)
        write(data(M, f"tags/worldgen/biome/spawns/{group}.json"), {"replace": False, "values": values})

    for t in TREES:
        leaves = ns(t.leaves)
        entries = [{"weight": w, "data": {"Name": leaves, "Properties": {
            "age": str(age), "distance": "7", "persistent": "false", "waterlogged": "false"}}}
            for age, w in ((0, 4), (1, 2), (2, 2), (3, 3))]
        base, ra, rb = t.trunk_height
        if t.foliage == "palm":
            foliage = {"type": "minecraft:acacia_foliage_placer", "radius": 2, "offset": 0}
        else:
            foliage = {"type": "minecraft:blob_foliage_placer", "radius": 2, "offset": 0, "height": 3}
        write(data(M, f"worldgen/configured_feature/fruit_tree/{t.id}.json"), {"type": "minecraft:tree", "config": {
            "decorators": [],
            "dirt_provider": {"type": "minecraft:simple_state_provider", "state": {"Name": "minecraft:dirt"}},
            "foliage_placer": foliage,
            "foliage_provider": {"type": "minecraft:weighted_state_provider", "entries": entries},
            "force_dirt": False, "ignore_vines": True,
            "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 1, "lower_size": 0, "upper_size": 1},
            "trunk_placer": {"type": "minecraft:straight_trunk_placer", "base_height": base, "height_rand_a": ra,
                             "height_rand_b": rb},
            "trunk_provider": {"type": "minecraft:simple_state_provider",
                               "state": {"Name": t.log, "Properties": {"axis": "y"}}}}})
        write(data(M, f"worldgen/placed_feature/fruit_tree/{t.id}.json"), {
            "feature": f"{M}:fruit_tree/{t.id}", "placement": [
                {"type": "minecraft:rarity_filter", "chance": 48},
                {"type": "minecraft:in_square"},
                {"type": "minecraft:surface_water_depth_filter", "max_water_depth": 0},
                {"type": "minecraft:heightmap", "heightmap": "OCEAN_FLOOR"},
                {"type": "minecraft:block_predicate_filter", "predicate": {
                    "type": "minecraft:would_survive", "state": {"Name": ns(t.sapling), "Properties": {"stage": "0"}}}},
                {"type": "minecraft:biome"}]})
        write(data(M, f"neoforge/biome_modifier/fruit_tree/{t.id}.json"), {
            "type": "neoforge:add_features", "biomes": f"#{M}:spawns/{t.biomes}",
            "features": f"{M}:fruit_tree/{t.id}", "step": "vegetal_decoration"})

    for g in GARDENS:
        block = ns(g.id)
        write(data(M, f"worldgen/configured_feature/wild_garden/{g.id}.json"), {"type": "minecraft:random_patch", "config": {
            "tries": 8, "xz_spread": 4, "y_spread": 2,
            "feature": {"feature": {"type": "minecraft:simple_block", "config": {
                "to_place": {"type": "minecraft:simple_state_provider", "state": {"Name": block}}}},
                "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:all_of", "predicates": [
                    {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
                    {"type": "minecraft:would_survive", "state": {"Name": block}}]}}]}}})
        write(data(M, f"worldgen/placed_feature/wild_garden/{g.id}.json"), {
            "feature": f"{M}:wild_garden/{g.id}", "placement": [
                {"type": "minecraft:rarity_filter", "chance": 24},
                {"type": "minecraft:in_square"},
                {"type": "minecraft:heightmap", "heightmap": "MOTION_BLOCKING"},
                {"type": "minecraft:biome"}]})
        write(data(M, f"neoforge/biome_modifier/wild_garden/{g.id}.json"), {
            "type": "neoforge:add_features", "biomes": f"#{M}:spawns/{g.biomes[0]}",
            "features": f"{M}:wild_garden/{g.id}", "step": "vegetal_decoration"})

    manifest = build_manifest()
    write(data("neoforge", "data_maps/item/compostables.json"),
          {"values": {k: {"chance": v} for k, v in manifest["compost"].items()}})


# =========================================================================== advancements


def gen_advancements() -> None:
    def adv(name, icon, frame, parent, criteria, requirements=None, hidden=False, xp=None):
        body = {"display": {"icon": {"id": ns(icon)}, "title": {"translate": f"advancements.{M}.{name}.title"},
                            "description": {"translate": f"advancements.{M}.{name}.description"},
                            "frame": frame, "show_toast": True, "announce_to_chat": frame != "task" or name != "root",
                            "hidden": hidden},
                "criteria": criteria,
                "requirements": requirements or [list(criteria)]}
        if name == "root":
            body["display"]["background"] = "minecraft:textures/block/farmland_moist.png"
            body["display"]["show_toast"] = False
            body["display"]["announce_to_chat"] = False
        if parent:
            body["parent"] = f"{M}:{parent}"
        if xp:
            body["rewards"] = {"experience": xp}
        write(data(M, f"advancement/{name}.json"), body)

    has = lambda *ids: {"trigger": "minecraft:inventory_changed", "conditions": {"items": [{"items": [ns(i) for i in ids]}]}}  # noqa: E731
    eat = lambda *ids: {"trigger": "minecraft:consume_item", "conditions": {"item": {"items": [ns(i) for i in ids]}}}  # noqa: E731
    effect = lambda e: {"trigger": "minecraft:effects_changed", "conditions": {"effects": {f"{M}:{e}": {}}}}  # noqa: E731

    seeds = [c.planting_item.id for c in CROPS]
    produce = [c.produce.id for c in CROPS]
    adv("root", "tomato", "task", None, {"seeds": has(*seeds)})
    adv("harvest", "lettuce", "task", "root", {"produce": has(*produce)})
    adv("master_gardener", "corn", "challenge", "harvest", {c.produce.id: has(c.produce.id) for c in CROPS}, xp=200)
    adv("watering_can", "watering_can", "task", "harvest", {"can": has("watering_can")})
    adv("sprinkler", "sprinkler", "goal", "watering_can", {"sprinkler": has("sprinkler")})
    adv("scarecrow", "scarecrow", "task", "harvest", {"scarecrow": has("scarecrow")})
    adv("sickle", "iron_sickle", "task", "harvest", {"sickle": has(*[t.id for t in TOOLS if "sickle" in t.id])})
    adv("orchard", "orange_sapling", "task", "root", {"sapling": has(*[t.sapling for t in TREES])})
    adv("fruit_basket", "mango", "challenge", "orchard",
        {i.id: has(i.id) for i in spec.fruit_items()}, xp=150)
    adv("wild_garden", "meadow_garden", "task", "root", {"garden": has(*[g.id for g in GARDENS])}, hidden=False)
    adv("cooking_pot", "cooking_pot", "task", "root", {"pot": has("cooking_pot")})
    adv("first_meal", "vegetable_soup", "task", "cooking_pot", {"meal": eat(*[d.id for d in spec.SOUPS])})
    adv("well_fed", "beef_stew", "goal", "first_meal", {"well_fed": effect("well_fed")})
    adv("gourmet", "steak_dinner", "challenge", "well_fed", {d.id: eat(d.id) for d in spec.PLATES}, xp=250)
    adv("cutting_board", "iron_knife", "task", "cooking_pot", {"knife": has(*[t.id for t in TOOLS if "knife" in t.id])})
    adv("coffee", "coffee", "task", "cooking_pot", {"caffeinated": effect("caffeinated")})
    adv("cozy", "hot_cocoa", "task", "cooking_pot", {"cozy": effect("cozy")})
    adv("pie", "apple_pie", "goal", "cooking_pot", {"pie": has(*[f.id for f in FEASTS if f.kind == "pie"])})


# =========================================================================== lang


ADV_TEXT = {
    "root": ("Sprout & Soil", "Find seeds in a wild garden or from a farmer"),
    "harvest": ("Fruits of Your Labor", "Harvest your first crop - right-click it when ripe"),
    "master_gardener": ("Master Gardener", "Harvest every one of the 40 crops"),
    "watering_can": ("Rain Maker", "Craft a watering can and give your crops a drink"),
    "sprinkler": ("Let It Pour", "Automate watering with a sprinkler"),
    "scarecrow": ("Field Guardian", "Protect your farmland with a scarecrow"),
    "sickle": ("Reap What You Sow", "Harvest a whole patch at once with a sickle"),
    "orchard": ("Branching Out", "Get a fruit tree sapling"),
    "fruit_basket": ("Fruit Basket", "Collect every kind of tree fruit"),
    "wild_garden": ("Foraging", "Find a wild garden"),
    "cooking_pot": ("Something's Cooking", "Craft a cooking pot and set it over a fire"),
    "first_meal": ("Soup's On", "Eat a bowl of something warm"),
    "well_fed": ("Well Fed", "Eat a hearty meal and feel Well Fed"),
    "gourmet": ("Gourmet", "Eat every plated meal"),
    "cutting_board": ("Sharp Skills", "Craft a knife for the cutting board"),
    "coffee": ("Wired", "Drink coffee and get Caffeinated"),
    "cozy": ("Hygge", "Warm up with a hot drink"),
    "pie": ("Easy as Pie", "Bake a pie"),
}


def gen_lang() -> dict:
    lang: dict[str, str] = {}
    for i in spec.all_item_defs():
        key = "block" if i in WORKSTATIONS else "item"
        lang[f"{key}.{M}.{i.id}"] = i.display
        if i.tooltip and i.desc:
            lang[f"{key}.{M}.{i.id}.desc"] = i.desc
    for c in CROPS:
        lang[f"block.{M}.{c.block}"] = f"{title(c.id)} Plant"
    for t in TREES:
        lang[f"block.{M}.{t.sapling}"] = f"{t.display} Sapling"
        lang[f"block.{M}.{t.leaves}"] = f"{t.display} Leaves"
    for g in GARDENS:
        lang[f"block.{M}.{g.id}"] = g.display
    for crate, item in spec.crate_sources().items():
        lang[f"block.{M}.{crate}"] = title(crate)
    for f in FEASTS:
        lang[f"block.{M}.{f.id}"] = f.display
    lang.update({
        f"itemGroup.{M}.farm": "Sprout & Soil: Farm",
        f"itemGroup.{M}.kitchen": "Sprout & Soil: Kitchen",
        f"effect.{M}.well_fed": "Well Fed",
        f"effect.{M}.cozy": "Cozy",
        f"effect.{M}.caffeinated": "Caffeinated",
        f"container.{M}.cooking_pot": "Cooking Pot",
        f"container.{M}.cooking_pot.heated": "Heated - ready to cook",
        f"container.{M}.cooking_pot.not_heated": "Needs heat below: a lit campfire, fire, magma block or lava",
        f"message.{M}.cutting_board.no_recipe": "That can't be cut on a board",
        f"tooltip.{M}.chance": "%s (%s%% chance)",
        f"tooltip.{M}.water": "Water: %s / %s",
        f"tooltip.{M}.sickle": "Right-click a ripe crop to harvest a %sx%s area",
        f"gui.{M}.jei.cooking_time": "%ss",
        f"gui.{M}.jei.chance": "%s%% chance",
    })
    lang.update(TAG_NAMES)
    for key, (t, d) in ADV_TEXT.items():
        lang[f"advancements.{M}.{key}.title"] = t
        lang[f"advancements.{M}.{key}.description"] = d
    lang = dict(sorted(lang.items()))
    write(asset("lang/en_us.json"), lang)
    return lang


# =========================================================================== gametest structure


def _nbt(tag_type: int, name: str | None, value) -> bytes:
    import struct

    def payload(t, v):
        if t == 3:
            return struct.pack(">i", v)
        if t == 8:
            raw = v.encode("utf-8")
            return struct.pack(">H", len(raw)) + raw
        if t == 9:
            elem_type, items = v
            return struct.pack(">bi", elem_type if items else 0, len(items)) + b"".join(payload(elem_type, i) for i in items)
        if t == 10:
            return b"".join(_nbt(ct, cn, cv) for cn, (ct, cv) in v.items()) + b"\x00"
        raise ValueError(t)

    head = struct.pack(">b", tag_type)
    if name is not None:
        raw = name.encode("utf-8")
        head += struct.pack(">H", len(raw)) + raw
    return head + payload(tag_type, value)


def gen_test_structure(size=(9, 4, 9)) -> None:
    """An empty GameTest arena with a stone floor: data/sprout_and_soil/structure/empty.nbt."""
    import gzip

    sx, sy, sz = size
    blocks = [(10, {"pos": (9, (3, [x, 0, z])), "state": (3, 1)}) for x in range(sx) for z in range(sz)]
    root = {
        "DataVersion": (3, 3955),
        "size": (9, (3, [sx, sy, sz])),
        "palette": (9, (10, [{"Name": (8, "minecraft:air")}, {"Name": (8, "minecraft:stone")}])),
        "blocks": (9, (10, [b[1] for b in blocks])),
        "entities": (9, (10, [])),
    }
    path = data(M, "structure/empty.nbt")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_nbt(10, "", root), mtime=0))
    WRITTEN.append(path)


# =========================================================================== driver


def clean_generated() -> None:
    """Remove previously generated JSON (textures are left to the art generators)."""
    for root in (ASSETS / "models", ASSETS / "blockstates", ASSETS / "lang", DATA, GENERATED / M):
        if root.exists():
            for p in root.rglob("*.json"):
                # hand-authored 3D models from the hardware lane are art, keep them
                if p.parent == ASSETS / "models" / "block" and _is_art_model(p.stem):
                    continue
                p.unlink()


def _is_art_model(stem: str) -> bool:
    art = {w.id for w in WORKSTATIONS} | {f"template_{k}_{n}" for k in ("pie", "pizza") for n in range(4)}
    return stem in art


def generate() -> list[Path]:
    WRITTEN.clear()
    clean_generated()
    manifest = build_manifest()
    write(GENERATED / M / "content" / "manifest.json", manifest)
    gen_models()
    gen_recipe_advancements(gen_recipes())
    gen_loot()
    gen_tags()
    gen_worldgen()
    gen_advancements()
    gen_lang()
    gen_test_structure()
    return list(WRITTEN)
