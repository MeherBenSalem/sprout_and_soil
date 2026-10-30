package tn.nightbeam.sproutandsoil.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.core.Direction;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import tn.nightbeam.sproutandsoil.block.entity.CuttingBoardBlockEntity;

/** Draws the ingredient lying flat on the board (block items stand upright at half size). */
public class CuttingBoardRenderer implements BlockEntityRenderer<CuttingBoardBlockEntity> {
    private final ItemRenderer itemRenderer;

    public CuttingBoardRenderer(BlockEntityRendererProvider.Context context) {
        this.itemRenderer = context.getItemRenderer();
    }

    @Override
    public void render(CuttingBoardBlockEntity board, float partialTick, PoseStack pose, MultiBufferSource buffers,
                       int light, int overlay) {
        ItemStack stack = board.getItem();
        if (stack.isEmpty()) {
            return;
        }
        Direction facing = board.getBlockState().hasProperty(HorizontalDirectionalBlock.FACING)
                ? board.getBlockState().getValue(HorizontalDirectionalBlock.FACING) : Direction.NORTH;
        boolean block = Minecraft.getInstance().getItemRenderer().getModel(stack, board.getLevel(), null, 0).isGui3d();
        pose.pushPose();
        if (block) {
            pose.translate(0.5D, 1.0D / 16.0D + 0.125D, 0.5D);
            pose.mulPose(Axis.YP.rotationDegrees(-facing.toYRot()));
            pose.scale(0.5F, 0.5F, 0.5F);
        } else {
            pose.translate(0.5D, 1.1D / 16.0D, 0.5D);
            pose.mulPose(Axis.YP.rotationDegrees(-facing.toYRot()));
            pose.mulPose(Axis.XP.rotationDegrees(90.0F));
            pose.scale(0.6F, 0.6F, 0.6F);
        }
        itemRenderer.renderStatic(stack, ItemDisplayContext.FIXED, light, overlay, pose, buffers, board.getLevel(),
                (int) board.getBlockPos().asLong());
        pose.popPose();
    }
}
