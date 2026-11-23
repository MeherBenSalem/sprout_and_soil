package tn.nightbeam.sproutandsoil.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemInstance;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;
import tn.nightbeam.sproutandsoil.content.ContentManifest;

import java.util.function.Consumer;

/**
 * Manifest-driven item: food (with effects and serving container), drink, or plain ingredient. Drinks use the
 * drinking animation through their consumable component (see ModItems).
 */
public class SoilFoodItem extends Item {
    private final ContentManifest.ItemEntry entry;
    private final @Nullable Item remainder;

    public SoilFoodItem(Properties properties, ContentManifest.ItemEntry entry, @Nullable Item remainder) {
        super(properties);
        this.entry = entry;
        this.remainder = remainder;
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (!level.isClientSide() && entry.food() != null) {
            FoodEffects.apply(entity, entry.food().effects());
        }
        return super.finishUsingItem(stack, level, entity);
    }

    // Crafting remainder (bottles, bowls). Loader hooks without @Override: common code compiles against vanilla, and
    // each method overrides the loader's default at runtime.

    /** NeoForge (IItemExtension). */
    public @Nullable ItemStackTemplate getCraftingRemainder(ItemInstance instance) {
        return remainderTemplate(remainder);
    }

    /** Fabric (FabricItem). */
    public @Nullable ItemStackTemplate getCraftingRemainder(ItemStack stack) {
        return remainderTemplate(remainder);
    }

    static @Nullable ItemStackTemplate remainderTemplate(@Nullable Item remainder) {
        return remainder == null ? null : new ItemStackTemplate(remainder);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, TooltipDisplay display, Consumer<Component> tooltip, TooltipFlag flag) {
        ItemTooltips.append(this, entry, context, tooltip);
    }
}
