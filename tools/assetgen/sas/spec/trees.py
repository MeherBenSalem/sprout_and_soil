"""Fruit trees.

Each tree is a sapling + a fruiting leaves block with an ``age`` property:
0 = leafy, 1 = blossoming, 2 = unripe fruit, 3 = ripe fruit (right-click to pick).
Trunks reuse vanilla logs so trees blend into any build.
"""
from .model import Art, Food, ItemDef, TreeDef


def fruit(id_, food, colors, desc, archetype="round_fruit", kind="fruit", name=None):
    return ItemDef(id=id_, name=name, food=food, compost=0.65, tab="farm", category=f"produce:{kind}",
                   art=Art(archetype, colors, desc))


TREES: list[TreeDef] = [
    TreeDef("apple", "minecraft:apple", log="minecraft:oak_log", biomes="orchard",
            leaf_colors=["#4f8f34", "#78b04a"], blossom="#f6d6e0"),
    TreeDef("orange",
            fruit("orange", Food(4, 0.4), ["#f08a1a", "#3f7a2a"],
                  "round bright-orange citrus with dimpled skin and a small leaf"),
            log="minecraft:oak_log", biomes="citrus", leaf_colors=["#2f6e2a", "#4f9a3a"], blossom="#fbf7ea",
            crate=True),
    TreeDef("lemon",
            fruit("lemon", Food(2, 0.2), ["#f2d83a", "#3f7a2a"],
                  "oval yellow lemon with pointed ends", archetype="oval_fruit"),
            log="minecraft:birch_log", biomes="citrus", leaf_colors=["#2f6e2a", "#4f9a3a"], blossom="#fbf7ea",
            crate=True),
    TreeDef("lime",
            fruit("lime", Food(2, 0.2), ["#6ab83a", "#3f7a2a"],
                  "small round bright-green lime", archetype="oval_fruit"),
            log="minecraft:birch_log", biomes="citrus", leaf_colors=["#2f6e2a", "#4f9a3a"], blossom="#fbf7ea"),
    TreeDef("peach",
            fruit("peach", Food(4, 0.4), ["#f0a070", "#e05a4a"],
                  "fuzzy peach, orange-yellow blushing red, with a crease and a leaf"),
            log="minecraft:oak_log", biomes="orchard", leaf_colors=["#4a8a34", "#72aa48"], blossom="#f4a8c0",
            crate=True),
    TreeDef("pear",
            fruit("pear", Food(4, 0.3), ["#c8d050", "#8a6a2a"],
                  "yellow-green pear with a brown stem and slight russet freckles", archetype="pear"),
            log="minecraft:oak_log", biomes="orchard", leaf_colors=["#4a8a34", "#72aa48"], blossom="#ffffff",
            crate=True),
    TreeDef("plum",
            fruit("plum", Food(3, 0.3), ["#5a2a6a", "#8a5aa0"],
                  "dusky purple plum with a powdery bloom and short stem"),
            log="minecraft:dark_oak_log", biomes="orchard", leaf_colors=["#3f7a30", "#62983e"], blossom="#ffffff"),
    TreeDef("sweet_cherry",
            fruit("cherries", Food(2, 0.3, fast=True), ["#b01a2a", "#4a7a2a"],
                  "pair of dark-red cherries joined by green stems", archetype="cherries"),
            log="minecraft:cherry_log", biomes="cherry", leaf_colors=["#4a8a34", "#72aa48"], blossom="#f7b8d0"),
    TreeDef("mango",
            fruit("mango", Food(4, 0.4), ["#f0a82a", "#d0402a"],
                  "kidney-shaped mango, yellow-orange with red-green blush", archetype="oval_fruit"),
            log="minecraft:jungle_log", biomes="tropical", trunk_height=(5, 2, 1),
            leaf_colors=["#2a6a2a", "#4a8a3a"], blossom="#e8d89a", crate=True),
    TreeDef("avocado",
            fruit("avocado", Food(3, 0.6), ["#3a5a2a", "#b8c86a"],
                  "pear-shaped avocado with bumpy dark-green skin", archetype="pear"),
            log="minecraft:jungle_log", biomes="tropical", trunk_height=(5, 2, 1),
            leaf_colors=["#2a6a2a", "#4a8a3a"], blossom="#d8e09a"),
    TreeDef("banana",
            fruit("banana", Food(3, 0.4), ["#f2d23a", "#6a8a2a"],
                  "curved yellow banana with brown tip", archetype="banana"),
            log="minecraft:jungle_log", biomes="tropical", foliage="palm", trunk_height=(6, 2, 0),
            leaf_colors=["#3a7a2a", "#6aaa3a"], blossom="#c84a6a"),
    TreeDef("olive",
            fruit("olives", Food(1, 0.3, fast=True), ["#5a6a2a", "#2a2a1a"],
                  "a few small green and black olives with a sprig", archetype="cherries", kind="fruit"),
            log="minecraft:acacia_log", biomes="mediterranean", leaf_colors=["#6a8a5a", "#9ab08a"],
            blossom="#f2f0d8"),
]

TREES_BY_ID = {t.id: t for t in TREES}
