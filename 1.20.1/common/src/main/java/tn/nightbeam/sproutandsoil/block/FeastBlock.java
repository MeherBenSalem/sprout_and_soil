package tn.nightbeam.sproutandsoil.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** A placed pie or pizza that hands out four slices before it is gone. */
public class FeastBlock extends Block {
    public static final IntegerProperty SERVINGS_TAKEN = IntegerProperty.create("servings_taken", 0, 3);

    private final ResourceLocation sliceId;
    private final double height;
    private final VoxelShape[] shapes = new VoxelShape[4];

    public FeastBlock(Properties properties, ResourceLocation sliceId, double height) {
        super(properties);
        this.sliceId = sliceId;
        this.height = height;
        VoxelShape nw = box(1, 0, 1, 8, height, 8);
        VoxelShape sw = box(1, 0, 8, 8, height, 15);
        VoxelShape se = box(8, 0, 8, 15, height, 15);
        VoxelShape ne = box(8, 0, 1, 15, height, 8);
        shapes[0] = Shapes.or(nw, ne, se, sw);
        shapes[1] = Shapes.or(nw, se, sw);
        shapes[2] = Shapes.or(nw, sw);
        shapes[3] = nw;
        registerDefaultState(stateDefinition.any().setValue(SERVINGS_TAKEN, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(SERVINGS_TAKEN);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return shapes[state.getValue(SERVINGS_TAKEN)];
    }

    @Override
    @SuppressWarnings("deprecation")
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (!level.isClientSide()) {
            ItemStack slice = new ItemStack(BuiltInRegistries.ITEM.get(sliceId));
            if (!player.getInventory().add(slice)) {
                player.drop(slice, false);
            }
            int taken = state.getValue(SERVINGS_TAKEN);
            if (taken >= 3) {
                level.removeBlock(pos, false);
                level.gameEvent(player, GameEvent.BLOCK_DESTROY, pos);
            } else {
                level.setBlock(pos, state.setValue(SERVINGS_TAKEN, taken + 1), Block.UPDATE_ALL);
                level.gameEvent(player, GameEvent.BLOCK_CHANGE, pos);
            }
            level.playSound(null, pos, SoundEvents.WOOL_BREAK, SoundSource.BLOCKS, 0.8F, 0.8F + level.random.nextFloat() * 0.3F);
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }

    @Override
    public BlockState updateShape(BlockState state, Direction direction, BlockState neighborState, LevelAccessor level,
                                     BlockPos pos, BlockPos neighborPos) {
        return direction == Direction.DOWN && !state.canSurvive(level, pos)
                ? Blocks.AIR.defaultBlockState()
                : super.updateShape(state, direction, neighborState, level, pos, neighborPos);
    }

    @Override
    public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        return level.getBlockState(pos.below()).isSolid();
    }

    @Override
    public boolean hasAnalogOutputSignal(BlockState state) {
        return true;
    }

    @Override
    public int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        return (4 - state.getValue(SERVINGS_TAKEN)) * 3;
    }

    @Override
    public boolean isPathfindable(BlockState state, BlockGetter level, BlockPos pos, PathComputationType type) {
        return false;
    }
}
