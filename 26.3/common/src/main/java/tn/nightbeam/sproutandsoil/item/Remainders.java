package tn.nightbeam.sproutandsoil.item;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import org.jspecify.annotations.Nullable;

/**
 * What an ingredient leaves behind when used outside the crafting grid (the cooking pot): Sprout &amp; Soil's own
 * remainders (bottles, bowls, the mortar) come from their loader hooks, everything else from vanilla's.
 */
public final class Remainders {
    private Remainders() {
    }

    public static ItemStack of(ItemStack stack) {
        @Nullable ItemStackTemplate template;
        if (stack.getItem() instanceof SoilFoodItem food) {
            template = food.getCraftingRemainder(stack);
        } else if (stack.getItem() instanceof SoilSeedItem seed) {
            template = seed.getCraftingRemainder(stack);
        } else if (stack.getItem() instanceof MortarItem mortar) {
            template = mortar.getCraftingRemainder(stack);
        } else {
            template = stack.getItem().getCraftingRemainder();
        }
        return template == null ? ItemStack.EMPTY : template.create();
    }
}
