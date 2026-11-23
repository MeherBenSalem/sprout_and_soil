package tn.nightbeam.sproutandsoil.neoforge;

import net.minecraft.world.InteractionResult;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.farming.CropHarvesting;
import tn.nightbeam.sproutandsoil.neoforge.gametest.SproutAndSoilNeoForgeGameTests;
import tn.nightbeam.sproutandsoil.neoforge.platform.NeoForgeRegistrar;

/**
 * Worldgen (biome modifiers), compostables (data maps) and the grass seed drop (a loot modifier) are data-driven on
 * NeoForge and live in the generated resources; everything else is wired here. Villager and wandering trader trades
 * are not offered on Minecraft 26.x.
 */
@Mod(SproutAndSoil.MOD_ID)
public class SproutAndSoilNeoForge {

    public SproutAndSoilNeoForge(IEventBus modBus) {
        SproutAndSoil.init();
        NeoForgeRegistrar.registerAll(modBus);
        SproutAndSoilNeoForgeGameTests.register(modBus);
        if (FMLEnvironment.getDist().isClient()) {
            SproutAndSoilNeoForgeClient.init(modBus);
        }
        NeoForge.EVENT_BUS.addListener(SproutAndSoilNeoForge::onRightClickBlock);
    }

    private static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        InteractionResult result = CropHarvesting.onUseBlock(event.getEntity(), event.getLevel(), event.getHand(), event.getHitVec());
        if (result != InteractionResult.PASS) {
            event.setCanceled(true);
            event.setCancellationResult(result);
        }
    }
}
