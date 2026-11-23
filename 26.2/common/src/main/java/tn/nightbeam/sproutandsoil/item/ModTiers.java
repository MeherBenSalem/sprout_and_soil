package tn.nightbeam.sproutandsoil.item;

import net.minecraft.core.registries.Registries;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ToolMaterial;
import tn.nightbeam.sproutandsoil.SproutAndSoil;

public final class ModTiers {
    /** Repairs the flint knife (data/sprout_and_soil/tags/item/flint_tool_materials.json: flint). */
    public static final TagKey<Item> FLINT_TOOL_MATERIALS = TagKey.create(Registries.ITEM, SproutAndSoil.id("flint_tool_materials"));

    /** Early-game material for the flint knife: a little better than wood, repaired with flint. */
    public static final ToolMaterial FLINT = new ToolMaterial(BlockTags.INCORRECT_FOR_STONE_TOOL, 96, 4.0F, 0.5F, 5, FLINT_TOOL_MATERIALS);

    private ModTiers() {
    }
}
