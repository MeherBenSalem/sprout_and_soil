package tn.nightbeam.sproutandsoil.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemNameBlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import tn.nightbeam.sproutandsoil.content.ContentManifest;

import java.util.List;

/** Seeds, and produce that is planted directly (garlic, onions, coffee beans...). */
public class SoilSeedItem extends ItemNameBlockItem {
    private final ContentManifest.ItemEntry entry;

    public SoilSeedItem(Block crop, Properties properties, ContentManifest.ItemEntry entry) {
        super(crop, properties);
        this.entry = entry;
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (!level.isClientSide() && entry.food() != null) {
            FoodEffects.apply(entity, entry.food().effects());
        }
        return super.finishUsingItem(stack, level, entity);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        ItemTooltips.append(this, entry, context, tooltip);
    }
}
