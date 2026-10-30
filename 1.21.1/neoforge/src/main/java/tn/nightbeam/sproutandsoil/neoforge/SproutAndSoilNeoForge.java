package tn.nightbeam.sproutandsoil.neoforge;

import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.village.VillagerTradesEvent;
import net.neoforged.neoforge.event.village.WandererTradesEvent;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.farming.CropHarvesting;
import tn.nightbeam.sproutandsoil.neoforge.platform.NeoForgeRegistrar;
import tn.nightbeam.sproutandsoil.world.ModTrades;

/**
 * Worldgen (biome modifiers) and compostables (data maps) are data-driven on NeoForge and live in the
 * generated resources; everything else is wired here.
 */
@Mod(SproutAndSoil.MOD_ID)
public class SproutAndSoilNeoForge {

    public SproutAndSoilNeoForge(IEventBus modBus) {
        SproutAndSoil.init();
        NeoForgeRegistrar.registerAll(modBus);
        if (FMLEnvironment.dist.isClient()) {
            SproutAndSoilNeoForgeClient.init(modBus);
        }
        NeoForge.EVENT_BUS.addListener(SproutAndSoilNeoForge::onVillagerTrades);
        NeoForge.EVENT_BUS.addListener(SproutAndSoilNeoForge::onWandererTrades);
        NeoForge.EVENT_BUS.addListener(SproutAndSoilNeoForge::onRightClickBlock);
    }

    private static void onVillagerTrades(VillagerTradesEvent event) {
        if (event.getType() == VillagerProfession.FARMER) {
            ModTrades.farmer().forEach((level, listings) -> event.getTrades().get(level.intValue()).addAll(listings));
        }
    }

    private static void onWandererTrades(WandererTradesEvent event) {
        event.getGenericTrades().addAll(ModTrades.wandererGeneric());
        event.getRareTrades().addAll(ModTrades.wandererRare());
    }

    private static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        InteractionResult result = CropHarvesting.onUseBlock(event.getEntity(), event.getLevel(), event.getHand(), event.getHitVec());
        if (result != InteractionResult.PASS) {
            event.setCanceled(true);
            event.setCancellationResult(result);
        }
    }
}
