package tn.nightbeam.sproutandsoil.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.blockentity.state.BlockEntityRenderState;
import net.minecraft.client.renderer.feature.ModelFeatureRenderer;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.Direction;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;
import tn.nightbeam.sproutandsoil.block.entity.CuttingBoardBlockEntity;

/** Draws the ingredient lying flat on the board (block items stand upright at half size). */
public class CuttingBoardRenderer implements BlockEntityRenderer<CuttingBoardBlockEntity, CuttingBoardRenderer.State> {
    private final ItemModelResolver itemModelResolver;

    public CuttingBoardRenderer(BlockEntityRendererProvider.Context context) {
        this.itemModelResolver = context.itemModelResolver();
    }

    /** What the renderer needs from a board, captured once per frame. */
    public static class State extends BlockEntityRenderState {
        Direction facing = Direction.NORTH;
        boolean block;
        final ItemStackRenderState item = new ItemStackRenderState();
    }

    @Override
    public State createRenderState() {
        return new State();
    }

    @Override
    public void extractRenderState(CuttingBoardBlockEntity board, State state, float partialTicks, Vec3 cameraPosition,
                                   ModelFeatureRenderer.@Nullable CrumblingOverlay breakProgress) {
        BlockEntityRenderer.super.extractRenderState(board, state, partialTicks, cameraPosition, breakProgress);
        state.facing = board.getBlockState().hasProperty(HorizontalDirectionalBlock.FACING)
                ? board.getBlockState().getValue(HorizontalDirectionalBlock.FACING) : Direction.NORTH;
        ItemStack stack = board.getItem();
        state.block = stack.getItem() instanceof BlockItem;
        itemModelResolver.updateForTopItem(state.item, stack, ItemDisplayContext.FIXED, board.getLevel(), null,
                (int) board.getBlockPos().asLong());
    }

    @Override
    public void submit(State state, PoseStack pose, SubmitNodeCollector collector, CameraRenderState camera) {
        if (state.item.isEmpty()) {
            return;
        }
        pose.pushPose();
        if (state.block) {
            pose.translate(0.5D, 1.0D / 16.0D + 0.125D, 0.5D);
            pose.rotate(Axis.YP.rotationDegrees(-state.facing.toYRot()));
            pose.scale(0.5F, 0.5F, 0.5F);
        } else {
            pose.translate(0.5D, 1.1D / 16.0D, 0.5D);
            pose.rotate(Axis.YP.rotationDegrees(-state.facing.toYRot()));
            pose.rotate(Axis.XP.rotationDegrees(90.0F));
            pose.scale(0.6F, 0.6F, 0.6F);
        }
        state.item.submit(pose, collector, state.lightCoords, OverlayTexture.NO_OVERLAY, 0);
        pose.popPose();
    }
}
