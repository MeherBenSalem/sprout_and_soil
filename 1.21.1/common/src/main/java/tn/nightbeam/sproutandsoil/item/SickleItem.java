package tn.nightbeam.sproutandsoil.item;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import tn.nightbeam.sproutandsoil.farming.CropHarvesting;
import tn.nightbeam.sproutandsoil.registry.ModTags;

import java.util.List;

/**
 * Right-click a ripe crop to harvest and replant every ripe crop around it. Fortune increases
 * yields; each harvested plant costs one durability.
 */
public class SickleItem extends DiggerItem {
    private final int radius;

    public SickleItem(Tier tier, int radius, Properties properties) {
        super(tier, ModTags.MINEABLE_WITH_SICKLE, properties.attributes(DiggerItem.createAttributes(tier, 1.0F, -2.2F)));
        this.radius = radius;
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos origin = context.getClickedPos();
        if (!CropHarvesting.isHarvestable(level.getBlockState(origin))) {
            return InteractionResult.PASS;
        }
        if (level instanceof ServerLevel serverLevel) {
            Player player = context.getPlayer();
            ItemStack sickle = context.getItemInHand();
            int harvested = 0;
            for (BlockPos pos : BlockPos.betweenClosed(origin.offset(-radius, -1, -radius), origin.offset(radius, 1, radius))) {
                BlockState state = serverLevel.getBlockState(pos);
                if (CropHarvesting.isHarvestable(state) && CropHarvesting.harvest(serverLevel, pos.immutable(), state, player, sickle)) {
                    harvested++;
                }
                if (sickle.isEmpty()) {
                    break;
                }
            }
            if (harvested > 0 && player != null) {
                sickle.hurtAndBreak(harvested, player, context.getHand() == net.minecraft.world.InteractionHand.MAIN_HAND
                        ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND);
                player.sweepAttack();
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        int size = radius * 2 + 1;
        tooltip.add(Component.translatable("tooltip.sprout_and_soil.sickle", size, size).withStyle(net.minecraft.ChatFormatting.GRAY));
    }
}
