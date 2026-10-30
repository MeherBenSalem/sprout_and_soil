package tn.nightbeam.sproutandsoil.neoforge;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import tn.nightbeam.sproutandsoil.client.CookingPotScreen;
import tn.nightbeam.sproutandsoil.client.CuttingBoardRenderer;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;
import tn.nightbeam.sproutandsoil.registry.ModMenus;

/** Client-only wiring. Render layers come from the block models' {@code render_type} on NeoForge. */
public final class SproutAndSoilNeoForgeClient {
    private SproutAndSoilNeoForgeClient() {
    }

    static void init(IEventBus modBus) {
        modBus.addListener(SproutAndSoilNeoForgeClient::onRegisterScreens);
        modBus.addListener(SproutAndSoilNeoForgeClient::onRegisterRenderers);
    }

    private static void onRegisterScreens(RegisterMenuScreensEvent event) {
        event.register(ModMenus.COOKING_POT.get(), CookingPotScreen::new);
    }

    private static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerBlockEntityRenderer(ModBlockEntities.CUTTING_BOARD.get(), CuttingBoardRenderer::new);
    }
}
