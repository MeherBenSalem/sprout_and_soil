package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import tn.nightbeam.sproutandsoil.SproutAndSoil;

/** Since 1.21.2 items and blocks carry their registry key in their properties; these start a property set for a name. */
public final class Keys {
    private Keys() {
    }

    public static Item.Properties item(String name) {
        return new Item.Properties().setId(ResourceKey.create(Registries.ITEM, SproutAndSoil.id(name)));
    }

    public static BlockBehaviour.Properties block(String name) {
        return BlockBehaviour.Properties.of().setId(ResourceKey.create(Registries.BLOCK, SproutAndSoil.id(name)));
    }

    /** All the properties of {@code template}, under this block's own key. */
    public static BlockBehaviour.Properties copy(Block template, String name) {
        return BlockBehaviour.Properties.ofFullCopy(template).setId(ResourceKey.create(Registries.BLOCK, SproutAndSoil.id(name)));
    }
}
