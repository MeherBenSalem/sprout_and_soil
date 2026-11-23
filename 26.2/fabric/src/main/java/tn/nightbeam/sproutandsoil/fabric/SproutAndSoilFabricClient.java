package tn.nightbeam.sproutandsoil.fabric;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.BlockEntityRendererRegistry;
import net.minecraft.client.gui.screens.MenuScreens;
import tn.nightbeam.sproutandsoil.client.CookingPotScreen;
import tn.nightbeam.sproutandsoil.client.CuttingBoardRenderer;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;
import tn.nightbeam.sproutandsoil.registry.ModMenus;

/** Render layers (cutout leaves, crops and gardens) are picked from the block textures on Minecraft 26.x. */
public class SproutAndSoilFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        MenuScreens.register(ModMenus.COOKING_POT.get(), CookingPotScreen::new);
        BlockEntityRendererRegistry.register(ModBlockEntities.CUTTING_BOARD.get(), CuttingBoardRenderer::new);
    }
}
