package tn.nightbeam.sproutandsoil.item;

import net.minecraft.world.item.ItemInstance;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;

/**
 * The mortar and pestle: its grinding recipes are plain shapeless recipes, and it stays in the crafting grid with one
 * more point of damage instead of being used up (it breaks on its last use). On 1.20.1 and 1.21.1 a custom
 * {@code tool_shapeless} recipe type did this.
 */
public class MortarItem extends DescribedItem.Simple {
    public MortarItem(Properties properties) {
        super(properties);
    }

    // Loader hooks without @Override: common code compiles against vanilla, and each method overrides the loader's
    // default at runtime.

    /** NeoForge (IItemExtension). */
    public ItemStackTemplate getCraftingRemainder(ItemInstance instance) {
        if ((Object) instance instanceof ItemStack stack) {
            return damaged(stack);
        }
        return new ItemStackTemplate(this);
    }

    /** Fabric (FabricItem). */
    public ItemStackTemplate getCraftingRemainder(ItemStack stack) {
        return damaged(stack);
    }

    /** One more point of damage, or nothing when that use breaks it. */
    static ItemStackTemplate damaged(ItemStack tool) {
        ItemStack copy = tool.copyWithCount(1);
        if (!copy.isDamageableItem()) {
            return ItemStackTemplate.fromNonEmptyStack(copy);
        }
        int damage = copy.getDamageValue() + 1;
        if (damage >= copy.getMaxDamage()) {
            return null;
        }
        copy.setDamageValue(damage);
        return ItemStackTemplate.fromNonEmptyStack(copy);
    }
}
