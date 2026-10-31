package tn.nightbeam.sproutandsoil.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemNameBlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import org.jetbrains.annotations.Nullable;
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
        return SoilFoodItem.finishEating(entry, super.finishUsingItem(stack, level, entity), level, entity);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        ItemTooltips.append(this, entry, tooltip);
    }
}
