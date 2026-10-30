"""Hand-coded blocks and tools (registered in Java) plus data-driven crates and wild gardens."""
from .model import Art, GardenDef, ItemDef, shaped, shapeless

# --------------------------------------------------------------------------- biome groups
# Each group becomes a biome tag ``sprout_and_soil:<kind>/<group>``. Optional convention
# tags keep modded biomes covered.

BIOME_GROUPS = {
    # wild gardens
    "meadow": ["minecraft:plains", "minecraft:sunflower_plains", "minecraft:meadow", "minecraft:flower_forest",
               "?#c:is_plains"],
    "woodland": ["minecraft:forest", "minecraft:birch_forest", "minecraft:old_growth_birch_forest",
                 "minecraft:dark_forest", "?#c:is_birch_forest"],
    "highland": ["#minecraft:is_taiga", "minecraft:windswept_hills", "minecraft:windswept_forest",
                 "minecraft:windswept_gravelly_hills", "minecraft:grove"],
    "arid": ["#minecraft:is_savanna", "minecraft:desert", "minecraft:wooded_badlands", "?#c:is_desert"],
    "tropical": ["#minecraft:is_jungle"],
    "marsh": ["minecraft:swamp", "minecraft:mangrove_swamp", "#minecraft:is_river", "?#c:is_swamp"],
    # fruit trees
    "orchard": ["minecraft:forest", "minecraft:flower_forest", "minecraft:birch_forest", "minecraft:meadow",
                "minecraft:plains"],
    "citrus": ["minecraft:savanna", "minecraft:savanna_plateau", "minecraft:sparse_jungle"],
    "cherry": ["minecraft:cherry_grove", "minecraft:flower_forest", "minecraft:meadow"],
    "mediterranean": ["minecraft:savanna_plateau", "minecraft:windswept_savanna", "minecraft:wooded_badlands"],
}

GARDENS = [
    GardenDef("meadow_garden", ["meadow"], [],
              art=Art("garden", ["#5a9a3a", "#d8322a", "#f2c63a"],
                      "wild tangle of grass, a tomato vine with two red fruits, yellow corn tassel, small white flowers")),
    GardenDef("woodland_garden", ["woodland"], [],
              art=Art("garden", ["#3f7a30", "#d02a4a", "#f1ead2"],
                      "shady forest-floor bramble with raspberries, a radish top and a pale cauliflower leaf")),
    GardenDef("highland_garden", ["highland"], [],
              art=Art("garden", ["#3a6a4a", "#3a4aa0", "#e8d8a0"],
                      "hardy cold-climate shrub: blue-green leaves, blueberries, pale oat spikelets")),
    GardenDef("arid_garden", ["arid"], [],
              art=Art("garden", ["#7a8a3a", "#d7261e", "#f6f4f0"],
                      "dry dusty shrub with red chilies, a cotton boll and olive-grey leaves")),
    GardenDef("tropical_garden", ["tropical"], [],
              art=Art("garden", ["#2a7a2a", "#e0a830", "#c02a2a"],
                      "lush broad tropical leaves, a small pineapple top and red coffee cherries")),
    GardenDef("marsh_garden", ["marsh"], [],
              art=Art("garden", ["#4a8a5a", "#e8d8a0", "#b81a2a"],
                      "reedy wetland tuft with drooping rice grains, mint sprigs and cranberries")),
]

# --------------------------------------------------------------------------- tools

TOOLS = [
    ItemDef("flint_knife", recipes=[shaped([" F", "S "], {"F": "minecraft:flint", "S": "minecraft:stick"})],
            art=Art("knife", ["#4a4a4a", "#8a6a3a"], "knife with chipped dark flint blade lashed to a stick"),
            tab="kitchen", category="tool", stack=1, tags=["c:tools/knife", "sprout_and_soil:knives"]),
    ItemDef("iron_knife", recipes=[shaped([" I", "S "], {"I": "minecraft:iron_ingot", "S": "minecraft:stick"})],
            art=Art("knife", ["#d8d8d8", "#6a4a2a"], "kitchen knife with polished steel blade and dark wood handle"),
            tab="kitchen", category="tool", stack=1, tags=["c:tools/knife", "sprout_and_soil:knives"]),
    ItemDef("golden_knife", recipes=[shaped([" I", "S "], {"I": "minecraft:gold_ingot", "S": "minecraft:stick"})],
            art=Art("knife", ["#f8d838", "#6a4a2a"], "knife with shiny gold blade"),
            tab="kitchen", category="tool", stack=1, tags=["c:tools/knife", "sprout_and_soil:knives"]),
    ItemDef("diamond_knife", recipes=[shaped([" I", "S "], {"I": "minecraft:diamond", "S": "minecraft:stick"})],
            art=Art("knife", ["#4ae0d0", "#6a4a2a"], "knife with cyan diamond blade"),
            tab="kitchen", category="tool", stack=1, tags=["c:tools/knife", "sprout_and_soil:knives"]),
    ItemDef("netherite_knife", recipes=[],  # smithing upgrade, emitted by the data generator
            art=Art("knife", ["#4a3a3a", "#2a2020"], "knife with dark netherite blade, gold-ish edge highlights"),
            tab="kitchen", category="tool", stack=1, tags=["c:tools/knife", "sprout_and_soil:knives"]),
    ItemDef("iron_sickle", recipes=[shaped([" I ", "  I", "SI "], {"I": "minecraft:iron_ingot", "S": "minecraft:stick"})],
            art=Art("sickle", ["#d8d8d8", "#6a4a2a"], "crescent-bladed iron sickle with wooden handle"),
            tab="farm", category="tool", stack=1, tags=["sprout_and_soil:sickles"]),
    ItemDef("golden_sickle", recipes=[shaped([" I ", "  I", "SI "], {"I": "minecraft:gold_ingot", "S": "minecraft:stick"})],
            art=Art("sickle", ["#f8d838", "#6a4a2a"], "crescent-bladed golden sickle"),
            tab="farm", category="tool", stack=1, tags=["sprout_and_soil:sickles"]),
    ItemDef("diamond_sickle", recipes=[shaped([" I ", "  I", "SI "], {"I": "minecraft:diamond", "S": "minecraft:stick"})],
            art=Art("sickle", ["#4ae0d0", "#6a4a2a"], "crescent-bladed diamond sickle"),
            tab="farm", category="tool", stack=1, tags=["sprout_and_soil:sickles"]),
    ItemDef("netherite_sickle", recipes=[],
            art=Art("sickle", ["#4a3a3a", "#2a2020"], "crescent-bladed netherite sickle"),
            tab="farm", category="tool", stack=1, tags=["sprout_and_soil:sickles"]),
    ItemDef("watering_can",
            recipes=[shaped(["C  ", "CBC", " CC"], {"C": "minecraft:copper_ingot", "B": "minecraft:bucket"})],
            art=Art("watering_can", ["#d87a4a", "#4a9ac8"],
                    "copper watering can with long spout pointing up-right and arched handle; slight teal patina"),
            tab="farm", category="tool", stack=1, tooltip=True,
            desc="Hold use to water crops and farmland. Refill at any water source."),
    ItemDef("mortar_and_pestle",
            recipes=[shaped(["  T", "S S", " S "], {"S": "minecraft:stone", "T": "minecraft:stick"})],
            art=Art("mortar", ["#9a9a9a", "#6a4a2a"], "grey stone mortar bowl with wooden pestle leaning in it"),
            tab="kitchen", category="tool", stack=1, tooltip=True,
            desc="Grinds ingredients in the crafting grid. Loses durability instead of being consumed."),
    ItemDef("fertilizer",
            recipes=[shapeless("minecraft:bone_meal", "minecraft:bone_meal", "minecraft:rotten_flesh", "minecraft:dirt",
                               count=4)],
            art=Art("fertilizer", ["#8a6a3a", "#f0ece0", "#4a8a2a"], "small burlap pouch tied with string, spilling dark compost and white granules"),
            tab="farm", category="tool", tooltip=True, desc="Applies bone meal to every plant in a 5x5 area."),
]

# --------------------------------------------------------------------------- workstations

WORKSTATIONS = [
    ItemDef("cooking_pot",
            recipes=[shaped(["I I", "IBI", "III"], {"I": "minecraft:iron_ingot", "B": "minecraft:bowl"})],
            art=Art("model", ["#4a4e56", "#c8643a"],
                    "3D: dark cast-iron pot with copper rim band, two side handles, lid with knob slightly ajar"),
            tab="kitchen", category="workstation", tooltip=True,
            desc="Cook up to six ingredients. Needs a heat source below (fire, campfire, magma...)."),
    ItemDef("cutting_board",
            recipes=[shaped(["SPP"], {"S": "minecraft:stick", "P": "#minecraft:planks"})],
            art=Art("model", ["#b8844a", "#8a5a2a"], "3D: low wooden chopping board with rounded handle"),
            tab="kitchen", category="workstation", tooltip=True,
            desc="Place an ingredient on it, then use a knife."),
    ItemDef("scarecrow",
            recipes=[shaped([" P ", "SHS", " S "], {"P": "minecraft:carved_pumpkin", "H": "minecraft:hay_block",
                                                   "S": "minecraft:stick"})],
            art=Art("model", ["#d8b85a", "#e8901a", "#6a4a2a"],
                    "3D: wooden post cross with straw-stuffed burlap shirt, carved pumpkin head, straw hat"),
            tab="farm", category="workstation", tooltip=True,
            desc="Stops farmland within 8 blocks from being trampled."),
    ItemDef("sprinkler",
            recipes=[shaped([" C ", "CBC", " C "], {"C": "minecraft:copper_ingot", "B": "minecraft:bucket"})],
            art=Art("model", ["#d87a4a", "#4ab8a0"], "3D: copper sprinkler: small tank base, pipe and rotating 4-nozzle head"),
            tab="farm", category="workstation", tooltip=True,
            desc="Next to water, it hydrates farmland and speeds crop growth in a 9x9 area."),
]

# --------------------------------------------------------------------------- crates

VANILLA_CRATES = {"carrot": "minecraft:carrot", "potato": "minecraft:potato", "beetroot": "minecraft:beetroot",
                  "apple": "minecraft:apple"}
