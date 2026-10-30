package tn.nightbeam.sproutandsoil.block.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import tn.nightbeam.sproutandsoil.farming.Watering;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;

/**
 * Every two seconds a sprinkler next to water hydrates farmland and gives extra growth ticks to
 * plants in a 9x9 area (two blocks down to one block up).
 */
public class SprinklerBlockEntity extends BlockEntity {
    public static final int RADIUS = 4;
    private static final int INTERVAL = 40;
    private static final int GROWTH_ROLLS = 7;

    private int timer;

    public SprinklerBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.SPRINKLER.get(), pos, state);
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, SprinklerBlockEntity sprinkler) {
        if (++sprinkler.timer < INTERVAL || !(level instanceof ServerLevel serverLevel)) {
            return;
        }
        sprinkler.timer = serverLevel.random.nextInt(8);
        if (!hasWater(serverLevel, pos)) {
            return;
        }
        RandomSource random = serverLevel.random;
        for (BlockPos target : BlockPos.betweenClosed(pos.offset(-RADIUS, -2, -RADIUS), pos.offset(RADIUS, 1, RADIUS))) {
            Watering.hydrate(serverLevel, target);
        }
        for (int i = 0; i < GROWTH_ROLLS; i++) {
            BlockPos target = pos.offset(random.nextInt(RADIUS * 2 + 1) - RADIUS, random.nextInt(4) - 2,
                    random.nextInt(RADIUS * 2 + 1) - RADIUS);
            Watering.boostGrowth(serverLevel, target, random);
        }
        for (int i = 0; i < 4; i++) {
            double angle = (serverLevel.getGameTime() / 8.0D + i * Math.PI / 2.0D) % (Math.PI * 2.0D);
            double x = pos.getX() + 0.5D + Math.cos(angle) * 0.35D;
            double z = pos.getZ() + 0.5D + Math.sin(angle) * 0.35D;
            serverLevel.sendParticles(ParticleTypes.SPLASH, x, pos.getY() + 0.6D, z, 6,
                    Math.cos(angle) * 0.6D, 0.1D, Math.sin(angle) * 0.6D, 0.4D);
        }
        if (random.nextInt(3) == 0) {
            serverLevel.playSound(null, pos, SoundEvents.WEATHER_RAIN, SoundSource.BLOCKS, 0.08F, 1.6F);
        }
    }

    /** Water source, flowing water, a water cauldron or a waterlogged block on any side. */
    public static boolean hasWater(Level level, BlockPos pos) {
        for (Direction direction : Direction.values()) {
            if (direction == Direction.UP) {
                continue;
            }
            BlockPos side = pos.relative(direction);
            if (level.getFluidState(side).is(FluidTags.WATER) || level.getBlockState(side).is(Blocks.WATER_CAULDRON)) {
                return true;
            }
        }
        return false;
    }
}
