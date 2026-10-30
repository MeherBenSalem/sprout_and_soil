package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import tn.nightbeam.sproutandsoil.SproutAndSoil;

public final class ModTags {
    /** Blocks that heat a cooking pot placed directly on top (lit campfires, fire, magma, lava...). */
    public static final TagKey<Block> HEAT_SOURCES = block("heat_sources");
    /** Blocks a sickle cuts quickly. */
    public static final TagKey<Block> MINEABLE_WITH_SICKLE = block("mineable/sickle");

    /** Tools that stay in the crafting grid and lose durability (mortar and pestle). */
    public static final TagKey<Item> CRAFTING_TOOLS = item("crafting_tools");
    public static final TagKey<Item> KNIVES = item("knives");
    /** Bowls, plates, mugs and bottles accepted by the cooking pot's container slot. */
    public static final TagKey<Item> SERVING_CONTAINERS = item("serving_containers");
    public static final TagKey<Item> C_KNIVES = TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("c", "tools/knife"));

    private ModTags() {
    }

    private static TagKey<Block> block(String path) {
        return TagKey.create(Registries.BLOCK, SproutAndSoil.id(path));
    }

    private static TagKey<Item> item(String path) {
        return TagKey.create(Registries.ITEM, SproutAndSoil.id(path));
    }
}
