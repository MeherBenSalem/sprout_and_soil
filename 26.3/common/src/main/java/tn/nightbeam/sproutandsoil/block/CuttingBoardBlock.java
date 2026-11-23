package tn.nightbeam.sproutandsoil.block;

import net.minecraft.util.Prediction;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jspecify.annotations.Nullable;
import tn.nightbeam.sproutandsoil.block.entity.CuttingBoardBlockEntity;
import tn.nightbeam.sproutandsoil.registry.ModTags;

import java.util.Map;

/**
 * Place an ingredient with right-click, then use a knife on it. Empty-handed right-click takes the
 * ingredient back.
 */
public class CuttingBoardBlock extends BaseEntityBlock {
    public static final EnumProperty<Direction> FACING = HorizontalDirectionalBlock.FACING;
    private static final Map<Direction, VoxelShape> SHAPES = ShapeUtil.horizontal(box(1, 0, 3, 15, 1, 13));

    public CuttingBoardBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return defaultBlockState().setValue(FACING, context.getHorizontalDirection().getOpposite());
    }

    @Override
    protected BlockState rotate(BlockState state, Rotation rotation) {
        return state.setValue(FACING, rotation.rotate(state.getValue(FACING)));
    }

    @Override
    protected BlockState mirror(BlockState state, Mirror mirror) {
        return state.rotate(mirror.getRotation(state.getValue(FACING)));
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPES.get(state.getValue(FACING));
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                         InteractionHand hand, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof CuttingBoardBlockEntity board)) {
            return InteractionResult.TRY_WITH_EMPTY_HAND;
        }
        if (board.isEmpty()) {
            if (stack.is(ModTags.KNIVES) || stack.is(ModTags.C_KNIVES)) {
                return InteractionResult.TRY_WITH_EMPTY_HAND;
            }
            if (!level.isClientSide()) {
                board.place(stack, player);
                level.playSound(null, pos, SoundEvents.WOOD_PLACE, SoundSource.BLOCKS, 0.7F, 1.3F);
            }
            return InteractionResult.SUCCESS;
        }
        if (level instanceof ServerLevel serverLevel) {
            if (board.process(serverLevel, player, stack)) {
                return InteractionResult.SUCCESS;
            }
            if (stack.is(ModTags.KNIVES) || stack.is(ModTags.C_KNIVES)) {
                if (player instanceof ServerPlayer serverPlayer) {
                    serverPlayer.sendOverlayMessage(Component.translatable("message.sprout_and_soil.cutting_board.no_recipe"));
                }
                return InteractionResult.CONSUME;
            }
            return InteractionResult.TRY_WITH_EMPTY_HAND;
        }
        boolean couldCut = board.findRecipe(level).map(r -> r.value().isTool(stack)).orElse(false);
        return couldCut || stack.is(ModTags.KNIVES) ? InteractionResult.SUCCESS
                : InteractionResult.TRY_WITH_EMPTY_HAND;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof CuttingBoardBlockEntity board) || board.isEmpty()) {
            return InteractionResult.PASS;
        }
        if (!level.isClientSide()) {
            ItemStack taken = board.take();
            if (!player.getInventory().add(taken)) {
                player.drop(taken, false, Prediction.SERVER_ONLY);
            }
            level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.3F, 1.0F);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    protected void affectNeighborsAfterRemoval(BlockState state, ServerLevel level, BlockPos pos, boolean movedByPiston) {
        // The block entity drops the ingredient on it itself (CuttingBoardBlockEntity#preRemoveSideEffects).
        Containers.updateNeighboursAfterDestroy(state, level, pos);
    }

    @Override
    public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new CuttingBoardBlockEntity(pos, state);
    }
}
