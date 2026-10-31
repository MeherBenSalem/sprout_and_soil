package tn.nightbeam.sproutandsoil.farming;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;
import tn.nightbeam.sproutandsoil.block.SoilCropBlock;

import java.util.List;

/** Shared harvest-and-replant logic for right-click harvesting and sickles. */
public final class CropHarvesting {
    private CropHarvesting() {
    }

    public static boolean isHarvestable(BlockState state) {
        return state.getBlock() instanceof CropBlock crop && crop.isMaxAge(state);
    }

    /**
     * Harvests a ripe crop in place: rolls its loot table with {@code tool} (so Fortune applies),
     * keeps one planting item back as the replanting cost and resets the plant.
     */
    public static boolean harvest(ServerLevel level, BlockPos pos, BlockState state, @Nullable Player player, ItemStack tool) {
        if (!(state.getBlock() instanceof CropBlock crop) || !crop.isMaxAge(state)) {
            return false;
        }
        List<ItemStack> drops = Block.getDrops(state, level, pos, level.getBlockEntity(pos), player, tool);
        ItemStack planting = crop.getCloneItemStack(level, pos, state);
        for (ItemStack drop : drops) {
            if (!planting.isEmpty() && ItemStack.isSameItem(drop, planting)) {
                drop.shrink(1);
                break;
            }
        }
        BlockState replanted = crop instanceof SoilCropBlock soil ? soil.getStateForAge(soil.harvestAge()) : crop.getStateForAge(0);
        level.setBlock(pos, replanted, Block.UPDATE_ALL);
        for (ItemStack drop : drops) {
            if (!drop.isEmpty()) {
                Block.popResource(level, pos, drop);
            }
        }
        level.playSound(null, pos, SoundEvents.CROP_BREAK, SoundSource.BLOCKS, 1.0F, 0.8F + level.random.nextFloat() * 0.4F);
        level.levelEvent(2001, pos, Block.getId(state));
        level.gameEvent(GameEvent.BLOCK_CHANGE, pos, GameEvent.Context.of(player, replanted));
        return true;
    }

    /**
     * Right-click harvesting for crops from vanilla and other mods (ours handle it in the block).
     * Only fires with an empty main hand so it never steals item interactions.
     */
    public static InteractionResult onUseBlock(Player player, Level level, InteractionHand hand, BlockHitResult hit) {
        if (hand != InteractionHand.MAIN_HAND || player.isSpectator() || player.isSecondaryUseActive()
                || !player.getMainHandItem().isEmpty()) {
            return InteractionResult.PASS;
        }
        BlockPos pos = hit.getBlockPos();
        BlockState state = level.getBlockState(pos);
        if (state.getBlock() instanceof SoilCropBlock || !isHarvestable(state)) {
            return InteractionResult.PASS;
        }
        if (level instanceof ServerLevel serverLevel) {
            harvest(serverLevel, pos, state, player, ItemStack.EMPTY);
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }
}
