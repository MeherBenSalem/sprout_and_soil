package tn.nightbeam.sproutandsoil.farming;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import tn.nightbeam.sproutandsoil.registry.ModTags;

public final class HeatSources {
    private HeatSources() {
    }

    /** A pot is heated by a {@code sprout_and_soil:heat_sources} block directly below it; campfires must be lit. */
    public static boolean isHeated(BlockGetter level, BlockPos potPos) {
        BlockState below = level.getBlockState(potPos.below());
        if (!below.is(ModTags.HEAT_SOURCES)) {
            return false;
        }
        return !below.hasProperty(BlockStateProperties.LIT) || below.getValue(BlockStateProperties.LIT);
    }
}
