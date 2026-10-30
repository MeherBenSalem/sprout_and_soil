"""The 40 field crops of Sprout & Soil.

Visuals: every crop has four growth textures (stage0..3). Vanilla ``CropBlock``
age 0-7 maps onto them as 0-1 / 2-3 / 4-6 / 7, so stage3 always means "ripe".
Perennials (``regrow_age`` >= 0) drop back to that age when harvested by hand
instead of being destroyed.
"""
from .model import Art, CropDef, Food, ItemDef

VEG, FRUIT, BERRY, GRAIN, HERB, SPICE, NUT, FIBER = (
    "vegetable", "fruit", "berry", "grain", "herb", "spice", "nut", "fiber")


def produce(id_, kind, food, colors, desc, archetype, name=None, compost=0.65, tooltip=None):
    return ItemDef(
        id=id_, name=name, food=food, compost=compost, tab="farm", category=f"produce:{kind}",
        art=Art(archetype, colors, desc), tooltip=tooltip is not None, desc=tooltip,
    )


def seeds(crop, colors, desc="", name=None, archetype="seeds"):
    return ItemDef(
        id=f"{crop}_seeds", name=name, compost=0.3, tab="farm", category="seeds",
        art=Art(archetype, colors, desc or f"small {crop} seeds"),
    )


def F(n, s, **kw):
    return Food(n, s, **kw)


CROPS: list[CropDef] = [
    # ------------------------------------------------------------------ fruiting vegetables
    CropDef(
        "tomato",
        produce("tomato", VEG, F(3, 0.3), ["#d8322a", "#3f8a2a"],
                "plump glossy red tomato with a green star-shaped calyx on top", "round_fruit"),
        seeds("tomato", ["#e7d39a"], "flat pale-cream tomato seeds"),
        model="crop", regrow_age=4, drops=(2, 4), gardens=["meadow_garden"], crate=True,
        stage_art="vine tied to a wooden stake; stage2 yellow flowers + small green fruit; stage3 several red tomatoes",
    ),
    CropDef(
        "bell_pepper",
        produce("bell_pepper", VEG, F(3, 0.4), ["#c8281e", "#3c7a26"],
                "blocky red bell pepper with a short green stem", "bell_pepper"),
        seeds("bell_pepper", ["#efe0a8"]),
        regrow_age=4, drops=(1, 3), gardens=["arid_garden"], crate=True,
        stage_art="bushy pepper plant; stage2 white flowers + green peppers; stage3 hanging red peppers",
    ),
    CropDef(
        "chili_pepper",
        produce("chili_pepper", SPICE, F(2, 0.2), ["#d7261e", "#3c7a26"],
                "slender curved red chili with green cap", "chili"),
        seeds("chili_pepper", ["#f0d890"], name="Chili Seeds"),
        regrow_age=4, drops=(2, 4), gardens=["arid_garden"], crate=True,
        stage_art="small bush; stage3 many slim red chilies pointing down",
    ),
    CropDef(
        "eggplant",
        produce("eggplant", VEG, F(2, 0.3), ["#4a2160", "#4a7a2a"],
                "glossy deep-purple teardrop eggplant with a green leafy cap", "eggplant"),
        seeds("eggplant", ["#d9c48c"]),
        regrow_age=4, drops=(1, 3), gardens=["arid_garden"], crate=True,
        stage_art="broad-leaf bush; stage2 lavender flowers; stage3 hanging purple eggplants",
    ),
    CropDef(
        "cucumber",
        produce("cucumber", VEG, F(2, 0.4), ["#3e7d2e", "#a7d06a"],
                "long dark-green cucumber with pale bumps/stripes", "long_veg"),
        seeds("cucumber", ["#f2ecc8"]),
        regrow_age=4, drops=(1, 3), gardens=["meadow_garden", "marsh_garden"], crate=True,
        stage_art="climbing vine on a stake; stage2 yellow flowers; stage3 green cucumbers hanging",
    ),
    CropDef(
        "zucchini",
        produce("zucchini", VEG, F(2, 0.4), ["#2f6a26", "#8fbf5a"],
                "dark green zucchini, speckled, straight with a stem stub", "long_veg"),
        seeds("zucchini", ["#efe6c0"]),
        regrow_age=4, drops=(1, 2), gardens=["meadow_garden", "arid_garden"],
        stage_art="low sprawling squash plant with big leaves; stage2 big yellow flower; stage3 zucchinis on ground",
    ),
    CropDef(
        "green_bean",
        produce("green_beans", VEG, F(2, 0.3), ["#5a9a32", "#9acb5c"],
                "a small bundle of 3 slim green bean pods", "pods"),
        seeds("green_bean", ["#f1ead2"], name="Green Bean Seeds", archetype="beans"),
        regrow_age=4, drops=(2, 4), gardens=["marsh_garden", "woodland_garden"],
        stage_art="pole bean vine on tall stake; stage2 white flowers; stage3 hanging green pods",
    ),
    # ------------------------------------------------------------------ leafy & brassicas
    CropDef(
        "lettuce",
        produce("lettuce", VEG, F(2, 0.4), ["#7cc04a", "#c9e88a"],
                "round head of bright green butterhead lettuce, frilly edges", "leafy_head"),
        seeds("lettuce", ["#c9c2a0"]),
        drops=(1, 1), gardens=["meadow_garden"], crate=True,
        stage_art="low rosette of ruffled light-green leaves growing into a full head",
    ),
    CropDef(
        "cabbage",
        produce("cabbage", VEG, F(3, 0.4), ["#7fae5a", "#c8e0a2"],
                "dense round cabbage, pale green with visible leaf veins", "leafy_head"),
        seeds("cabbage", ["#5b3f2a"], "tiny round dark-brown cabbage seeds"),
        drops=(1, 1), gardens=["highland_garden", "meadow_garden"], crate=True,
        stage_art="broad blue-green outer leaves; stage3 a big pale cabbage head in the middle",
    ),
    CropDef(
        "spinach",
        produce("spinach", VEG, F(2, 0.4), ["#2e7a2a", "#5aa844"],
                "bunch of dark-green smooth spinach leaves", "leaf_bunch"),
        seeds("spinach", ["#8a7a52"]),
        drops=(1, 2), gardens=["woodland_garden", "highland_garden"],
        stage_art="low clump of dark glossy spoon-shaped leaves",
    ),
    CropDef(
        "broccoli",
        produce("broccoli", VEG, F(3, 0.5), ["#2f6e2c", "#7fb04a"],
                "broccoli crown: knobbly dark-green florets on a pale stalk", "florets"),
        seeds("broccoli", ["#5b3f2a"]),
        drops=(1, 1), gardens=["woodland_garden"],
        stage_art="blue-green broad leaves; stage3 a dark-green floret head in the centre",
    ),
    CropDef(
        "cauliflower",
        produce("cauliflower", VEG, F(3, 0.5), ["#f1ead2", "#5e9a3e"],
                "creamy white cauliflower curd cupped by green leaves", "florets"),
        seeds("cauliflower", ["#5b3f2a"]),
        drops=(1, 1), gardens=["woodland_garden"],
        stage_art="leafy rosette; stage3 creamy white head peeking out of leaves",
    ),
    CropDef(
        "celery",
        produce("celery", VEG, F(2, 0.3), ["#9cc86a", "#5c9a3a"],
                "bunch of pale-green ribbed celery stalks with leafy tops", "stalks"),
        seeds("celery", ["#a8956a"]),
        drops=(1, 1), gardens=["marsh_garden", "meadow_garden"],
        stage_art="upright pale stalks with frilly leaves at top",
    ),
    CropDef(
        "asparagus",
        produce("asparagus", VEG, F(2, 0.4), ["#6a9a3a", "#8a5a8a"],
                "bundle of green asparagus spears with purple-tinged tips", "spears"),
        seeds("asparagus", ["#2a2420"], "small black asparagus seeds"),
        regrow_age=4, drops=(1, 2), gardens=["meadow_garden"],
        stage_art="thin spears poking up from soil; stage2 feathery fronds; stage3 many tall spears",
    ),
    # ------------------------------------------------------------------ roots & bulbs
    CropDef(
        "garlic",
        produce("garlic", SPICE, F(1, 0.3), ["#efe6d6", "#b89ab0"],
                "plump white garlic bulb with faint purple streaks and papery top", "bulb"),
        None, drops=(1, 3), gardens=["meadow_garden"], crate=True,
        stage_art="flat strap leaves, slightly blue-green; stage3 leaves yellowing at tips, white bulb tops visible",
    ),
    CropDef(
        "onion",
        produce("onion", VEG, F(2, 0.4), ["#c88a3a", "#f0d6a0"],
                "round golden-brown onion with dry papery skin and a tuft on top", "bulb"),
        None, drops=(1, 3), gardens=["meadow_garden", "highland_garden"], crate=True,
        stage_art="hollow tubular green leaves; stage3 golden onion bulbs showing at soil",
    ),
    CropDef(
        "leek",
        produce("leek", VEG, F(2, 0.4), ["#f0f0d8", "#3f7a3a"],
                "long leek: white shaft fading into dark-green fan of leaves", "long_veg"),
        seeds("leek", ["#2a2420"]),
        drops=(1, 2), gardens=["highland_garden", "woodland_garden"],
        stage_art="fan of flat blue-green leaves on a white shaft",
    ),
    CropDef(
        "radish",
        produce("radish", VEG, F(2, 0.4), ["#d23a5a", "#5e9a3e"],
                "small round magenta-red radish with white tip and green leaves", "root"),
        seeds("radish", ["#8a5a3a"]),
        drops=(1, 2), gardens=["woodland_garden", "highland_garden"], crate=True,
        stage_art="small leafy rosette; stage3 red radish shoulders visible",
    ),
    CropDef(
        "turnip",
        produce("turnip", VEG, F(3, 0.4), ["#ece4d6", "#9a4a8a"],
                "round white turnip with a purple top half and green leaf stems", "root"),
        seeds("turnip", ["#5b3f2a"]),
        drops=(1, 2), gardens=["highland_garden", "woodland_garden"], crate=True,
        stage_art="leafy tops; stage3 purple-white turnip crowns",
    ),
    CropDef(
        "sweet_potato",
        produce("sweet_potato", VEG, F(2, 0.3), ["#b8503a", "#e8964a"],
                "elongated reddish-purple sweet potato tapering at both ends", "tuber"),
        None, drops=(1, 3), gardens=["arid_garden", "tropical_garden"], crate=True,
        stage_art="low trailing vines with heart-shaped leaves, some purple tint",
    ),
    CropDef(
        "ginger",
        produce("ginger", SPICE, F(1, 0.2), ["#d8b06a", "#a8783a"],
                "knobbly tan ginger root with branching fingers", "rhizome"),
        None, drops=(1, 2), gardens=["tropical_garden"],
        stage_art="tall reed-like stems with long narrow leaves",
    ),
    CropDef(
        "peanut",
        produce("peanuts", NUT, F(2, 0.3), ["#c8a06a", "#8a6a3a"],
                "two or three tan wrinkled peanut shells, figure-eight shaped", "pods"),
        None, drops=(2, 4), gardens=["arid_garden"],
        stage_art="clover-like low bushy leaves; stage2 small yellow flowers",
    ),
    # ------------------------------------------------------------------ grains
    CropDef(
        "corn",
        produce("corn", GRAIN, F(3, 0.4), ["#f2c63a", "#a8c86a"],
                "corn cob with bright yellow kernels, husk peeled back", "corn"),
        seeds("corn", ["#f0c03a"], "a few yellow corn kernels", name="Corn Kernels", archetype="kernels"),
        model="tall", drops=(1, 3), gardens=["meadow_garden"], crate=True,
        stage_art="TWO BLOCKS TALL from stage2: lower = stalk with long arching leaves, upper = tassel and cobs",
    ),
    CropDef(
        "rice",
        produce("rice", GRAIN, None, ["#f2ecd8", "#c8b88a"],
                "small pile of raw white rice grains", "grains", compost=0.3),
        None, drops=(2, 4), gardens=["marsh_garden", "tropical_garden"], crate=True,
        stage_art="dense grassy tufts; stage3 drooping golden panicles of grain",
    ),
    CropDef(
        "barley",
        produce("barley", GRAIN, None, ["#e0c070", "#b8963a"],
                "sheaf of golden barley with long whiskery awns", "sheaf"),
        seeds("barley", ["#d8b868"]),
        drops=(1, 2), gardens=["meadow_garden", "highland_garden"],
        stage_art="like wheat but with long bristly awns; stage3 golden",
    ),
    CropDef(
        "oat",
        produce("oats", GRAIN, None, ["#e8d8a0", "#b8a060"],
                "sheaf of pale oats with dangling spikelets", "sheaf"),
        seeds("oat", ["#e0d098"], name="Oat Seeds"),
        drops=(1, 2), gardens=["highland_garden"],
        stage_art="loose open panicles with dangling oat spikelets; stage3 pale straw colour",
    ),
    CropDef(
        "soybean",
        produce("soybeans", NUT, None, ["#e8d898", "#7a9a3a"],
                "handful of round cream soybeans next to a fuzzy green pod", "beans"),
        None, drops=(2, 4), gardens=["tropical_garden", "marsh_garden"],
        stage_art="bushy trifoliate leaves; stage3 yellowing leaves with fuzzy pods",
    ),
    # ------------------------------------------------------------------ berries & fruit
    CropDef(
        "strawberry",
        produce("strawberry", BERRY, F(2, 0.3, fast=True), ["#e0303a", "#4a8a2a"],
                "heart-shaped red strawberry with yellow seed dots and green leafy cap", "strawberry"),
        seeds("strawberry", ["#e8c04a"]),
        regrow_age=4, drops=(2, 3), gardens=["meadow_garden"],
        stage_art="low clump of serrated trifoliate leaves; stage2 white flowers; stage3 red berries",
    ),
    CropDef(
        "blueberry",
        produce("blueberries", BERRY, F(2, 0.2, fast=True), ["#3a4aa0", "#7a8ac8"],
                "cluster of dusty indigo blueberries with crown tips", "berry_cluster"),
        seeds("blueberry", ["#6a5a7a"]),
        model="cross", regrow_age=4, drops=(2, 4), gardens=["highland_garden"],
        stage_art="woody shrub; stage2 white bell flowers; stage3 clusters of blue berries",
    ),
    CropDef(
        "raspberry",
        produce("raspberries", BERRY, F(2, 0.2, fast=True), ["#d02a4a", "#f06a7a"],
                "a few bumpy red raspberries", "berry_cluster"),
        seeds("raspberry", ["#c89a6a"]),
        model="cross", regrow_age=4, drops=(2, 4), gardens=["woodland_garden"],
        stage_art="thorny cane bush; stage3 red raspberries",
    ),
    CropDef(
        "blackberry",
        produce("blackberries", BERRY, F(2, 0.2, fast=True), ["#2a1a3a", "#5a3a7a"],
                "glossy black-purple bumpy blackberries", "berry_cluster"),
        seeds("blackberry", ["#7a5a4a"]),
        model="cross", regrow_age=4, drops=(2, 4), gardens=["woodland_garden"],
        stage_art="bramble bush; stage2 red unripe berries; stage3 black berries",
    ),
    CropDef(
        "cranberry",
        produce("cranberries", BERRY, F(1, 0.2, fast=True), ["#b81a2a", "#e05a5a"],
                "handful of small shiny crimson cranberries", "berry_cluster"),
        seeds("cranberry", ["#c8a07a"]),
        model="cross", regrow_age=4, drops=(2, 4), gardens=["marsh_garden", "highland_garden"],
        stage_art="low trailing evergreen bush; stage3 dotted with crimson berries",
    ),
    CropDef(
        "grape",
        produce("grapes", FRUIT, F(2, 0.3, fast=True), ["#6a2a6a", "#9a4a9a"],
                "bunch of purple grapes with a curly tendril and leaf", "grape_bunch"),
        seeds("grape", ["#8a6a3a"]),
        regrow_age=4, drops=(1, 3), gardens=["arid_garden"],
        stage_art="vine on a wooden trellis frame; stage2 green grape bunches; stage3 purple bunches",
    ),
    CropDef(
        "pineapple",
        produce("pineapple", FRUIT, F(4, 0.4), ["#e0a830", "#3a7a3a"],
                "golden pineapple with diamond pattern and spiky green crown", "pineapple"),
        seeds("pineapple", ["#3a7a3a"], "a small spiky pineapple crown cutting", name="Pineapple Crown",
              archetype="crown"),
        drops=(1, 1), gardens=["tropical_garden"],
        stage_art="spiky rosette of stiff leaves; stage3 golden pineapple fruit in the centre",
    ),
    # ------------------------------------------------------------------ cash crops & herbs
    CropDef(
        "coffee",
        produce("coffee_beans", SPICE, None, ["#c02a2a", "#6a3a1a"],
                "a few red coffee cherries and green-tan raw beans", "coffee_beans",
                tooltip="Roast in a furnace before brewing."),
        None, model="cross", regrow_age=4, drops=(2, 4), gardens=["tropical_garden"],
        stage_art="glossy dark-green shrub; stage2 white blossoms; stage3 clusters of red coffee cherries",
    ),
    CropDef(
        "tea",
        produce("tea_leaves", HERB, None, ["#3a7a2a", "#7ab04a"],
                "small pile of fresh bright-green tea leaves", "leaf_bunch"),
        seeds("tea", ["#6a4a2a"]),
        model="cross", regrow_age=4, drops=(2, 4), gardens=["tropical_garden"],
        stage_art="compact rounded tea bush, glossy leaves, new pale shoots on top at stage3",
    ),
    CropDef(
        "cotton",
        produce("cotton", FIBER, None, ["#f6f4f0", "#8a6a4a"],
                "fluffy white cotton boll in a brown husk", "cotton", compost=0.3),
        seeds("cotton", ["#4a3a2a"]),
        drops=(1, 3), gardens=["arid_garden"],
        stage_art="shrubby plant; stage2 cream flowers; stage3 white fluffy bolls",
    ),
    CropDef(
        "basil",
        produce("basil", HERB, None, ["#3a8a2a", "#6ab84a"],
                "sprig of glossy cupped basil leaves", "herb_sprig"),
        seeds("basil", ["#2a2420"]),
        model="cross", regrow_age=4, drops=(1, 3), gardens=["meadow_garden"],
        stage_art="bushy herb with glossy rounded leaves",
    ),
    CropDef(
        "mint",
        produce("mint", HERB, None, ["#4aa84a", "#9ad87a"],
                "sprig of serrated fresh mint leaves", "herb_sprig"),
        seeds("mint", ["#5a4a3a"]),
        model="cross", regrow_age=4, drops=(1, 3), gardens=["marsh_garden"],
        stage_art="upright square stems with paired serrated leaves",
    ),
    CropDef(
        "peppercorn",
        produce("peppercorns", SPICE, None, ["#2a2420", "#7a3a2a"],
                "small heap of wrinkly black peppercorns", "beans"),
        None, model="cross", regrow_age=4, drops=(2, 4), gardens=["tropical_garden"],
        stage_art="climbing vine on a stake with hanging spikes of green then red berries",
    ),
]

CROPS_BY_ID = {c.id: c for c in CROPS}
