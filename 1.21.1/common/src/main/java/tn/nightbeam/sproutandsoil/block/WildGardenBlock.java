package tn.nightbeam.sproutandsoil.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.BushBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** A wild tangle of crops found in the world; its loot table drops seeds suited to its climate. */
public class WildGardenBlock extends BushBlock {
    public static final MapCodec<WildGardenBlock> CODEC = simpleCodec(WildGardenBlock::new);
    private static final VoxelShape SHAPE = box(2, 0, 2, 14, 13, 14);

    public WildGardenBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected MapCodec<? extends BushBlock> codec() {
        return CODEC;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        Vec3 offset = state.getOffset(level, pos);
        return SHAPE.move(offset.x, offset.y, offset.z);
    }
}
