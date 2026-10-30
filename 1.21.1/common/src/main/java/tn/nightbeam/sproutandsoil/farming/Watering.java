package tn.nightbeam.sproutandsoil.farming;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.BonemealableBlock;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraft.world.level.block.GrassBlock;
import net.minecraft.world.level.block.state.BlockState;

/** Shared effects of watering cans and sprinklers. */
public final class Watering {
    private Watering() {
    }

    /** Fully moisturises farmland. */
    public static boolean hydrate(ServerLevel level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (state.getBlock() instanceof FarmBlock && state.getValue(FarmBlock.MOISTURE) < FarmBlock.MAX_MOISTURE) {
            level.setBlock(pos, state.setValue(FarmBlock.MOISTURE, FarmBlock.MAX_MOISTURE), Block.UPDATE_CLIENTS);
            return true;
        }
        return false;
    }

    /** Gives a growing plant one extra random tick. */
    public static boolean boostGrowth(ServerLevel level, BlockPos pos, RandomSource random) {
        BlockState state = level.getBlockState(pos);
        if (!state.isRandomlyTicking() || !isPlant(state)) {
            return false;
        }
        state.randomTick(level, pos, random);
        return true;
    }

    public static boolean isPlant(BlockState state) {
        Block block = state.getBlock();
        return state.is(BlockTags.CROPS) || state.is(BlockTags.SAPLINGS)
                || (block instanceof BonemealableBlock && !(block instanceof GrassBlock) && !state.is(BlockTags.LEAVES));
    }
}
