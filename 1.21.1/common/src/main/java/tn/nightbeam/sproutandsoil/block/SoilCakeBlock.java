package tn.nightbeam.sproutandsoil.block;

import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CakeBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.phys.BlockHitResult;

/** A richer cake: each bite restores more than vanilla cake and candles are not accepted. */
public class SoilCakeBlock extends CakeBlock {
    public SoilCakeBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                              InteractionHand hand, BlockHitResult hit) {
        if (stack.is(ItemTags.CANDLES)) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        return super.useItemOn(stack, state, level, pos, player, hand, hit);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!player.canEat(false)) {
            return InteractionResult.PASS;
        }
        if (!level.isClientSide()) {
            player.awardStat(Stats.EAT_CAKE_SLICE);
            player.getFoodData().eat(3, 0.3F);
            level.playSound(null, pos, SoundEvents.GENERIC_EAT, SoundSource.PLAYERS, 0.8F, 1.0F);
            int bites = state.getValue(BITES);
            level.gameEvent(player, GameEvent.EAT, pos);
            if (bites < MAX_BITES) {
                level.setBlock(pos, state.setValue(BITES, bites + 1), Block.UPDATE_ALL);
            } else {
                level.removeBlock(pos, false);
                level.gameEvent(player, GameEvent.BLOCK_DESTROY, pos);
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }
}
