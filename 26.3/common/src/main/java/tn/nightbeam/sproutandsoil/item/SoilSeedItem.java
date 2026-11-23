package tn.nightbeam.sproutandsoil.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemInstance;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import org.jspecify.annotations.Nullable;
import tn.nightbeam.sproutandsoil.content.ContentManifest;

import java.util.function.Consumer;

/**
 * Seeds, and produce that is planted directly (garlic, onions, coffee beans...). Named after the item, not the crop
 * block ({@code useItemDescriptionPrefix} in ModItems).
 */
public class SoilSeedItem extends BlockItem {
    private final ContentManifest.ItemEntry entry;
    private final @Nullable Item remainder;

    public SoilSeedItem(Block crop, Properties properties, ContentManifest.ItemEntry entry, @Nullable Item remainder) {
        super(crop, properties);
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

    /** NeoForge (IItemExtension). */
    public @Nullable ItemStackTemplate getCraftingRemainder(ItemInstance instance) {
        return SoilFoodItem.remainderTemplate(remainder);
    }

    /** Fabric (FabricItem). */
    public @Nullable ItemStackTemplate getCraftingRemainder(ItemStack stack) {
        return SoilFoodItem.remainderTemplate(remainder);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, TooltipDisplay display, Consumer<Component> tooltip, TooltipFlag flag) {
        ItemTooltips.append(this, entry, context, tooltip);
    }
}
