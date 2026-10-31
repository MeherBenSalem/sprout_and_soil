package tn.nightbeam.sproutandsoil.forge;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ComposterBlock;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootTableReference;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.LootTableLoadEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.village.VillagerTradesEvent;
import net.minecraftforge.event.village.WandererTradesEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.farming.CropHarvesting;
import tn.nightbeam.sproutandsoil.farming.ScarecrowTracker;
import tn.nightbeam.sproutandsoil.forge.platform.ForgeRegistrar;
import tn.nightbeam.sproutandsoil.registry.ModEffects;
import tn.nightbeam.sproutandsoil.world.ModTrades;

/**
 * Worldgen (biome modifiers) is data-driven on Forge and lives in the generated resources; everything
 * else is wired here.
 */
@Mod(SproutAndSoil.MOD_ID)
public class SproutAndSoilForge {
    private static final ResourceLocation GRASS_SEEDS = SproutAndSoil.id("gameplay/grass_seeds");

    public SproutAndSoilForge() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        SproutAndSoil.init();
        ForgeRegistrar.registerAll(modBus);
        modBus.addListener(SproutAndSoilForge::onCommonSetup);
        if (FMLEnvironment.dist.isClient()) {
            SproutAndSoilForgeClient.init(modBus);
        }
        MinecraftForge.EVENT_BUS.addListener(SproutAndSoilForge::onVillagerTrades);
        MinecraftForge.EVENT_BUS.addListener(SproutAndSoilForge::onWandererTrades);
        MinecraftForge.EVENT_BUS.addListener(SproutAndSoilForge::onRightClickBlock);
        MinecraftForge.EVENT_BUS.addListener(SproutAndSoilForge::onFarmlandTrample);
        MinecraftForge.EVENT_BUS.addListener(SproutAndSoilForge::onBreakSpeed);
        MinecraftForge.EVENT_BUS.addListener(SproutAndSoilForge::onLootTableLoad);
    }

    private static void onCommonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> Content.manifest().compost().forEach((id, chance) -> {
            Item item = BuiltInRegistries.ITEM.get(id);
            if (item != Items.AIR) {
                ComposterBlock.COMPOSTABLES.put(item, chance.floatValue());
            }
        }));
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

    /** Farmland near a scarecrow is never trampled (the fall still hurts). */
    private static void onFarmlandTrample(BlockEvent.FarmlandTrampleEvent event) {
        if (!event.getLevel().isClientSide() && ScarecrowTracker.protects(event.getLevel(), event.getPos())) {
            event.setCanceled(true);
        }
    }

    private static void onBreakSpeed(PlayerEvent.BreakSpeed event) {
        event.setNewSpeed(ModEffects.breakSpeed(event.getEntity(), event.getNewSpeed()));
    }

    /** Grass has a small chance to drop temperate seeds (Fabric adds the same table through its loot event). */
    private static void onLootTableLoad(LootTableLoadEvent event) {
        if (Blocks.GRASS.getLootTable().equals(event.getName())) {
            event.getTable().addPool(LootPool.lootPool().name(SproutAndSoil.MOD_ID + ":grass_seeds")
                    .add(LootTableReference.lootTableReference(GRASS_SEEDS)).build());
        }
    }
}
