"""Content model for Sprout & Soil.

Everything the mod ships (crops, trees, dishes, blocks) is declared once in
``sas.spec`` using these dataclasses. The pipeline turns the spec into:

* ``manifest.json``  - gameplay data read by the Java registry at start-up
* textures / models  - via ``sas.art``
* data packs          - recipes, loot tables, tags, worldgen, advancements
* ``en_us.json``      - display names
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

MOD_ID = "sprout_and_soil"


def ns(ref: str) -> str:
    """Resolve a bare id to our namespace; '#tag' and 'ns:id' pass through."""
    if ref.startswith("#"):
        body = ref[1:]
        return "#" + (body if ":" in body else f"{MOD_ID}:{body}")
    return ref if ":" in ref else f"{MOD_ID}:{ref}"


def title(id_: str) -> str:
    small = {"and", "of", "with", "on", "a", "the", "in", "con"}
    words = id_.split("_")
    return " ".join(w if (i and w in small) else w.capitalize() for i, w in enumerate(words))


# --------------------------------------------------------------------------- food


@dataclass
class Effect:
    effect: str          # e.g. "sprout_and_soil:well_fed" or "minecraft:speed"
    seconds: int
    amplifier: int = 0
    chance: float = 1.0

    def to_json(self) -> dict:
        return {
            "effect": ns(self.effect) if ":" in self.effect else f"minecraft:{self.effect}",
            "duration": self.seconds * 20,
            "amplifier": self.amplifier,
            "chance": self.chance,
        }


@dataclass
class Food:
    nutrition: int
    saturation: float              # saturation *modifier* (vanilla semantics)
    always: bool = False           # can eat when full
    fast: bool = False             # 0.8s eat time (like dried kelp)
    effects: list[Effect] = field(default_factory=list)

    def to_json(self) -> dict:
        out = {"nutrition": self.nutrition, "saturation": self.saturation}
        if self.always:
            out["always_edible"] = True
        if self.fast:
            out["fast"] = True
        if self.effects:
            out["effects"] = [e.to_json() for e in self.effects]
        return out


# --------------------------------------------------------------------------- art hints


@dataclass
class Art:
    """Hints for texture artists. ``archetype`` picks a sprite family,
    ``colors`` are base hex colours (main first), ``desc`` is free text."""
    archetype: str
    colors: list[str] = field(default_factory=list)
    desc: str = ""


# --------------------------------------------------------------------------- recipes


@dataclass
class Recipe:
    kind: str                       # crafting_shaped | crafting_shapeless | tool_shapeless |
                                    # cooking_pot | cutting | smelting | smoking | campfire
    ingredients: list = field(default_factory=list)  # list[str] (refs) or for shaped: key dict
    pattern: Optional[list[str]] = None
    count: int = 1
    container: Optional[str] = None  # cooking pot container
    time: int = 200
    xp: float = 0.35
    tool: Optional[str] = None       # cutting board tool ingredient
    results: Optional[list] = None   # cutting: [(item, count, chance)]
    name: Optional[str] = None       # explicit recipe id suffix
    group: Optional[str] = None
    cook_kinds: tuple = ("smelting", "smoking", "campfire")


def shapeless(*ings, count=1, group=None, name=None) -> Recipe:
    return Recipe("crafting_shapeless", list(ings), count=count, group=group, name=name)


def shaped(pattern, key, count=1, group=None, name=None) -> Recipe:
    return Recipe("crafting_shaped", key, pattern=list(pattern), count=count, group=group, name=name)


def grind(*ings, count=1, name=None) -> Recipe:
    """Shapeless crafting that also needs (and damages) the mortar & pestle."""
    return Recipe("tool_shapeless", ["mortar_and_pestle", *ings], count=count, name=name)


def pot(*ings, container=None, count=1, time=200, xp=0.35, name=None) -> Recipe:
    return Recipe("cooking_pot", list(ings), container=container, count=count, time=time, xp=xp, name=name)


def cut(ing, *results, tool="#c:tools/knife", name=None) -> Recipe:
    return Recipe("cutting", [ing], results=list(results), tool=tool, name=name)


def cook(ing, xp=0.35, time=200, kinds=("smelting", "smoking", "campfire"), name=None) -> Recipe:
    return Recipe("cooking", [ing], xp=xp, time=time, cook_kinds=kinds, name=name)


# --------------------------------------------------------------------------- items


@dataclass
class ItemDef:
    id: str
    name: Optional[str] = None
    food: Optional[Food] = None
    container: Optional[str] = None      # returned after eating (bowl, bottle, mug, plate)
    remainder: Optional[str] = None      # left in crafting grid when used as ingredient
    drink: bool = False
    stack: int = 64
    tags: list[str] = field(default_factory=list)   # item tags, e.g. "c:foods/vegetable"
    compost: Optional[float] = None
    recipes: list[Recipe] = field(default_factory=list)
    art: Optional[Art] = None
    plants: Optional[str] = None         # crop block this item plants (seed behaviour)
    tab: str = "kitchen"                 # farm | kitchen
    category: str = "misc"               # used for ordering and advancements
    tooltip: bool = False                # adds item.<id>.desc line
    desc: Optional[str] = None           # tooltip text when tooltip=True

    @property
    def display(self) -> str:
        return self.name or title(self.id)


# --------------------------------------------------------------------------- crops


@dataclass
class CropDef:
    id: str
    produce: ItemDef
    seed: Optional[ItemDef]              # None: produce is planted directly
    model: str = "crop"                  # crop (# planes) | cross | tall
    regrow_age: int = -1                 # >=0: perennial, resets to this age on harvest
    drops: tuple = (1, 3)                # produce count range at maturity
    gardens: list[str] = field(default_factory=list)
    stage_art: str = ""                  # description of plant appearance per stage
    leaf: str = "#4e8a2e"                # foliage base colour hint
    crate: bool = False

    @property
    def block(self) -> str:
        return f"{self.id}_crop"

    @property
    def planting_item(self) -> ItemDef:
        return self.seed or self.produce

    @property
    def perennial(self) -> bool:
        return self.regrow_age >= 0


# --------------------------------------------------------------------------- trees


@dataclass
class TreeDef:
    id: str
    fruit: ItemDef | str                 # ItemDef, or a vanilla id (e.g. minecraft:apple)
    log: str = "minecraft:oak_log"
    foliage: str = "blob"                # blob | tall | palm
    trunk_height: tuple = (4, 2, 0)      # base, rand_a, rand_b (straight trunk placer)
    biomes: str = "temperate"            # biome tag group used by worldgen
    leaf_colors: list[str] = field(default_factory=list)
    blossom: str = "#ffffff"
    crate: bool = False
    name: Optional[str] = None

    @property
    def sapling(self) -> str:
        return f"{self.id}_sapling"

    @property
    def leaves(self) -> str:
        return f"{self.id}_leaves"

    @property
    def fruit_id(self) -> str:
        return self.fruit if isinstance(self.fruit, str) else ns(self.fruit.id)

    @property
    def display(self) -> str:
        return self.name or title(self.id)


# --------------------------------------------------------------------------- blocks


@dataclass
class FeastDef:
    """Placeable food: pies and pizzas hand out slices, cakes are eaten in place."""
    id: str
    kind: str                            # pie | pizza | cake
    slice: Optional[ItemDef] = None
    recipe: Optional[Recipe] = None
    art: Optional[Art] = None
    name: Optional[str] = None

    @property
    def display(self) -> str:
        return self.name or title(self.id)


@dataclass
class GardenDef:
    id: str
    biomes: list[str]
    crops: list[str]
    art: Art = None
    name: Optional[str] = None

    @property
    def display(self) -> str:
        return self.name or title(self.id)
