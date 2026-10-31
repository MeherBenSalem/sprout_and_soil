package tn.nightbeam.sproutandsoil.fabric;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.blockrenderlayer.v1.BlockRenderLayerMap;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderers;
import tn.nightbeam.sproutandsoil.client.CookingPotScreen;
import tn.nightbeam.sproutandsoil.client.CuttingBoardRenderer;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;
import tn.nightbeam.sproutandsoil.registry.ModBlocks;
import tn.nightbeam.sproutandsoil.registry.ModMenus;

public class SproutAndSoilFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        ModBlocks.cutoutBlocks().forEach(block -> BlockRenderLayerMap.INSTANCE.putBlock(block, RenderType.cutout()));
        ModBlocks.cutoutMippedBlocks().forEach(block -> BlockRenderLayerMap.INSTANCE.putBlock(block, RenderType.cutoutMipped()));
        MenuScreens.register(ModMenus.COOKING_POT.get(), CookingPotScreen::new);
        BlockEntityRenderers.register(ModBlockEntities.CUTTING_BOARD.get(), CuttingBoardRenderer::new);
    }
}
