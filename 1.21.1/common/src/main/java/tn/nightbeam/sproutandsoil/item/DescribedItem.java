package tn.nightbeam.sproutandsoil.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.block.Block;

import java.util.List;

/** Items and block items that show an {@code item.<id>.desc} hint line. */
public final class DescribedItem {
    private DescribedItem() {
    }

    public static class Simple extends Item {
        public Simple(Properties properties) {
            super(properties);
        }

        @Override
        public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
            ItemTooltips.description(this, tooltip);
        }
    }

    public static class ForBlock extends BlockItem {
        public ForBlock(Block block, Properties properties) {
            super(block, properties);
        }

        @Override
        public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
            ItemTooltips.description(this, tooltip);
        }
    }
}
