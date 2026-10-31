package tn.nightbeam.sproutandsoil.forge;

import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import tn.nightbeam.sproutandsoil.client.CookingPotScreen;
import tn.nightbeam.sproutandsoil.client.CuttingBoardRenderer;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;
import tn.nightbeam.sproutandsoil.registry.ModMenus;

/** Client-only wiring. Render layers come from the block models' {@code render_type} on Forge. */
public final class SproutAndSoilForgeClient {
    private SproutAndSoilForgeClient() {
    }

    static void init(IEventBus modBus) {
        modBus.addListener(SproutAndSoilForgeClient::onClientSetup);
        modBus.addListener(SproutAndSoilForgeClient::onRegisterRenderers);
    }

    private static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> MenuScreens.register(ModMenus.COOKING_POT.get(), CookingPotScreen::new));
    }

    private static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerBlockEntityRenderer(ModBlockEntities.CUTTING_BOARD.get(), CuttingBoardRenderer::new);
    }
}
