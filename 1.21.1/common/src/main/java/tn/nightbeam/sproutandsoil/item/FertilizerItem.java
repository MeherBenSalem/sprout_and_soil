package tn.nightbeam.sproutandsoil.item;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BonemealableBlock;
import net.minecraft.world.level.block.GrassBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;

import java.util.List;

/** Bone meal for a whole 5x5 patch of plants (grass blocks excluded so fields don't sprout flowers). */
public class FertilizerItem extends Item {
    private static final int RADIUS = 2;

    public FertilizerItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos origin = context.getClickedPos();
        boolean any = false;
        for (BlockPos pos : BlockPos.betweenClosed(origin.offset(-RADIUS, -1, -RADIUS), origin.offset(RADIUS, 1, RADIUS))) {
            BlockState state = level.getBlockState(pos);
            if (state.getBlock() instanceof BonemealableBlock plant && !(plant instanceof GrassBlock)
                    && plant.isValidBonemealTarget(level, pos, state)) {
                any = true;
                if (level instanceof ServerLevel serverLevel) {
                    BlockPos target = pos.immutable();
                    if (plant.isBonemealSuccess(serverLevel, serverLevel.random, target, state)) {
                        plant.performBonemeal(serverLevel, serverLevel.random, target, state);
                    }
                    serverLevel.levelEvent(1505, target, 15);
                }
            }
        }
        if (!any) {
            return InteractionResult.PASS;
        }
        if (!level.isClientSide()) {
            context.getItemInHand().consume(1, context.getPlayer());
            level.playSound(null, origin, SoundEvents.BONE_MEAL_USE, SoundSource.BLOCKS, 1.0F, 0.9F);
            level.gameEvent(context.getPlayer(), GameEvent.ITEM_INTERACT_FINISH, origin);
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        ItemTooltips.description(this, tooltip);
    }
}
