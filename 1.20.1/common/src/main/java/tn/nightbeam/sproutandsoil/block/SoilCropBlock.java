package tn.nightbeam.sproutandsoil.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import tn.nightbeam.sproutandsoil.farming.CropHarvesting;

/**
 * A vanilla-compatible crop (age 0-7) planted from a seed or from its own produce.
 *
 * <p>Ripe crops can be harvested with right-click: one planting item is kept back to replant, and
 * perennials (berries, peppers, tea...) fall back to {@link #regrowAge} instead of starting over.
 * Tall crops render two blocks high once past age 3, so they need air above to keep growing.</p>
 */
public class SoilCropBlock extends CropBlock {
    private static final VoxelShape[] SHAPES = {
            box(0, 0, 0, 16, 3, 16), box(0, 0, 0, 16, 5, 16),
            box(0, 0, 0, 16, 7, 16), box(0, 0, 0, 16, 9, 16),
            box(0, 0, 0, 16, 11, 16), box(0, 0, 0, 16, 12, 16),
            box(0, 0, 0, 16, 14, 16), box(0, 0, 0, 16, 16, 16)};
    private static final int TALL_THRESHOLD = 3;

    private final ResourceLocation seedId;
    private final int regrowAge;
    private final boolean tall;

    public SoilCropBlock(Properties properties, ResourceLocation seedId, int regrowAge, boolean tall) {
        super(properties);
        this.seedId = seedId;
        this.regrowAge = regrowAge;
        this.tall = tall;
    }

    public boolean isPerennial() {
        return regrowAge >= 0;
    }

    /** Age the plant returns to after a hand or sickle harvest. */
    public int harvestAge() {
        return Math.max(0, regrowAge);
    }

    public boolean isTall() {
        return tall;
    }

    @Override
    protected ItemLike getBaseSeedId() {
        return BuiltInRegistries.ITEM.get(seedId);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPES[Math.min(SHAPES.length - 1, getAge(state))];
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (tall && getAge(state) >= TALL_THRESHOLD && !hasHeadroom(level, pos)) {
            return;
        }
        super.randomTick(state, level, pos, random);
    }

    @Override
    public void growCrops(Level level, BlockPos pos, BlockState state) {
        if (tall && !hasHeadroom(level, pos)) {
            int capped = Math.min(getMaxAge(), Math.max(getAge(state), TALL_THRESHOLD));
            if (capped != getAge(state)) {
                level.setBlock(pos, getStateForAge(capped), Block.UPDATE_CLIENTS);
            }
            return;
        }
        super.growCrops(level, pos, state);
    }

    @Override
    public boolean isValidBonemealTarget(LevelReader level, BlockPos pos, BlockState state, boolean isClient) {
        if (tall && getAge(state) >= TALL_THRESHOLD && !hasHeadroom(level, pos)) {
            return false;
        }
        return super.isValidBonemealTarget(level, pos, state, isClient);
    }

    private static boolean hasHeadroom(LevelReader level, BlockPos pos) {
        return level.getBlockState(pos.above()).canBeReplaced();
    }

    @Override
    @SuppressWarnings("deprecation")
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (hand != InteractionHand.MAIN_HAND || !isMaxAge(state)) {
            return InteractionResult.PASS;
        }
        if (level instanceof ServerLevel serverLevel) {
            CropHarvesting.harvest(serverLevel, pos, state, player, player.getMainHandItem());
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }
}
