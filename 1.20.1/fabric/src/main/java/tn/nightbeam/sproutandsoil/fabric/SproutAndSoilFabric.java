package tn.nightbeam.sproutandsoil.fabric;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.loot.v2.LootTableEvents;
import net.fabricmc.fabric.api.object.builder.v1.trade.TradeOfferHelper;
import net.fabricmc.fabric.api.registry.CompostingChanceRegistry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.storage.loot.entries.LootTableReference;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.content.ContentManifest;
import tn.nightbeam.sproutandsoil.farming.CropHarvesting;
import tn.nightbeam.sproutandsoil.world.ModTrades;

public class SproutAndSoilFabric implements ModInitializer {

    @Override
    public void onInitialize() {
        SproutAndSoil.init();
        registerTrades();
        registerWorldgen();
        registerCompostables();
        registerLootInjections();
        UseBlockCallback.EVENT.register(CropHarvesting::onUseBlock);
    }

    /** Grass has a small chance to drop temperate seeds (Forge adds the same table from LootTableLoadEvent). */
    private static void registerLootInjections() {
        ResourceLocation grassSeeds = SproutAndSoil.id("gameplay/grass_seeds");
        LootTableEvents.MODIFY.register((resourceManager, lootManager, id, builder, source) -> {
            if (source.isBuiltin() && Blocks.GRASS.getLootTable().equals(id)) {
                builder.withPool(LootPool.lootPool().add(LootTableReference.lootTableReference(grassSeeds)));
            }
        });
    }

    private static void registerTrades() {
        ModTrades.farmer().forEach((level, listings) ->
                TradeOfferHelper.registerVillagerOffers(VillagerProfession.FARMER, level, factories -> factories.addAll(listings)));
        TradeOfferHelper.registerWanderingTraderOffers(1, factories -> factories.addAll(ModTrades.wandererGeneric()));
        TradeOfferHelper.registerWanderingTraderOffers(2, factories -> factories.addAll(ModTrades.wandererRare()));
    }

    /** Same placements Forge gets from data/sprout_and_soil/forge/biome_modifier. */
    private static void registerWorldgen() {
        for (ContentManifest.Worldgen entry : Content.manifest().worldgen()) {
            BiomeModifications.addFeature(BiomeSelectors.tag(TagKey.create(Registries.BIOME, entry.biomes())),
                    GenerationStep.Decoration.VEGETAL_DECORATION,
                    ResourceKey.create(Registries.PLACED_FEATURE, entry.feature()));
        }
    }

    private static void registerCompostables() {
        Content.manifest().compost().forEach((id, chance) -> {
            Item item = BuiltInRegistries.ITEM.get(id);
            if (item != Items.AIR) {
                CompostingChanceRegistry.INSTANCE.add(item, chance);
            }
        });
    }
}
