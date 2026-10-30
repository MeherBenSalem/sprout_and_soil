"""Aggregated Sprout & Soil content spec with cross-reference validation."""
from __future__ import annotations

from .blocks import BIOME_GROUPS, GARDENS, TOOLS, VANILLA_CRATES, WORKSTATIONS
from .crops import CROPS, CROPS_BY_ID
from .foods import BAKED, CONTAINERS, DRINKS, FEASTS, HANDHELDS, INGREDIENTS, PLATES, SOUPS
from .model import MOD_ID, CropDef, ItemDef, Recipe, TreeDef, ns, title
from .trees import TREES, TREES_BY_ID

# Garden crop pools are derived from each crop's ``gardens`` list.
for _g in GARDENS:
    _g.crops = [c.id for c in CROPS if _g.id in c.gardens]

DISHES = SOUPS + PLATES + HANDHELDS + BAKED
FOOD_ITEMS = CONTAINERS + INGREDIENTS + DISHES + DRINKS


def crop_items() -> list[ItemDef]:
    out = []
    for c in CROPS:
        c.produce.plants = c.block if c.seed is None else None
        out.append(c.produce)
        if c.seed is not None:
            c.seed.plants = c.block
            out.append(c.seed)
    return out


def fruit_items() -> list[ItemDef]:
    return [t.fruit for t in TREES if isinstance(t.fruit, ItemDef)]


def slice_items() -> list[ItemDef]:
    return [f.slice for f in FEASTS if f.slice is not None]


def crate_sources() -> dict[str, str]:
    """crate id -> stored item id (namespaced)."""
    out = {}
    for c in CROPS:
        if c.crate:
            out[f"{c.produce.id}_crate"] = ns(c.produce.id)
    for t in TREES:
        if t.crate:
            out[f"{t.fruit_id.split(':')[1]}_crate"] = t.fruit_id
    for name, item in VANILLA_CRATES.items():
        out[f"{name}_crate"] = item
    return dict(sorted(out.items()))


def manifest_items() -> list[ItemDef]:
    """Items the Java side registers from the manifest (everything except hand-coded tools/workstations)."""
    return crop_items() + fruit_items() + FOOD_ITEMS + slice_items()


def all_item_defs() -> list[ItemDef]:
    return manifest_items() + TOOLS + WORKSTATIONS


def all_recipes() -> list[tuple[str, Recipe]]:
    out = []
    for item in all_item_defs():
        for r in item.recipes:
            out.append((item.id, r))
    for f in FEASTS:
        if f.recipe:
            out.append((f.id, f.recipe))
    return out


def known_ids() -> set[str]:
    ids = {ns(i.id) for i in all_item_defs()}
    ids |= {ns(c.block) for c in CROPS}
    ids |= {ns(t.sapling) for t in TREES} | {ns(t.leaves) for t in TREES}
    ids |= {ns(f.id) for f in FEASTS}
    ids |= {ns(c) for c in crate_sources()}
    ids |= {ns(g.id) for g in GARDENS}
    return ids


def validate() -> list[str]:
    errors = []
    seen = {}
    for i in all_item_defs():
        if i.id in seen:
            errors.append(f"duplicate item id {i.id}")
        seen[i.id] = i
    ids = known_ids()

    def check(ref, ctx):
        if isinstance(ref, (list, tuple)):
            ref = ref[0]
        if ref.startswith("#") or ref.startswith("minecraft:"):
            return
        if ns(ref) not in ids:
            errors.append(f"{ctx}: unknown reference '{ref}'")

    for owner, r in all_recipes():
        ings = r.ingredients.values() if isinstance(r.ingredients, dict) else r.ingredients
        for ing in ings:
            check(ing, f"recipe for {owner}")
        if r.container:
            check(r.container, f"container for {owner}")
        if r.kind in ("cooking_pot",) and len(r.ingredients) > 6:
            errors.append(f"{owner}: cooking pot recipes take at most 6 ingredients")
        if r.kind in ("crafting_shapeless", "tool_shapeless") and len(r.ingredients) > 9:
            errors.append(f"{owner}: too many ingredients")
        for res in r.results or []:
            check(res[0], f"cutting result for {owner}")
    for i in all_item_defs():
        for ref in (i.container, i.remainder):
            if ref:
                check(ref, f"{i.id} container/remainder")
        if i.art is None:
            errors.append(f"{i.id}: missing art hints")
    for g in GARDENS:
        if not g.crops:
            errors.append(f"{g.id}: no crops assigned")
    for c in CROPS:
        for g in c.gardens:
            if g not in {x.id for x in GARDENS}:
                errors.append(f"{c.id}: unknown garden {g}")
    return errors


__all__ = [
    "MOD_ID", "BIOME_GROUPS", "CROPS", "CROPS_BY_ID", "TREES", "TREES_BY_ID", "GARDENS", "TOOLS",
    "WORKSTATIONS", "FEASTS", "CONTAINERS", "INGREDIENTS", "DISHES", "DRINKS", "SOUPS", "PLATES",
    "HANDHELDS", "BAKED", "FOOD_ITEMS", "crop_items", "fruit_items", "slice_items", "crate_sources",
    "manifest_items", "all_item_defs", "all_recipes", "validate", "ns", "title",
]
