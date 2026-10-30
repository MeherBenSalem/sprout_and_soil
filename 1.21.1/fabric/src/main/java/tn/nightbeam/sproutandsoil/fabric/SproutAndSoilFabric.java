package tn.nightbeam.sproutandsoil.fabric;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
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
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.NestedLootTable;
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

    /** Grass has a small chance to drop temperate seeds (NeoForge uses a global loot modifier for the same table). */
    private static void registerLootInjections() {
        ResourceKey<LootTable> grassSeeds = ResourceKey.create(Registries.LOOT_TABLE, SproutAndSoil.id("gameplay/grass_seeds"));
        LootTableEvents.MODIFY.register((key, builder, source, registries) -> {
            if (source.isBuiltin() && Blocks.SHORT_GRASS.getLootTable().equals(key)) {
                builder.withPool(LootPool.lootPool().add(NestedLootTable.lootTableReference(grassSeeds)));
            }
        });
    }

    private static void registerTrades() {
        ModTrades.farmer().forEach((level, listings) ->
                TradeOfferHelper.registerVillagerOffers(VillagerProfession.FARMER, level, factories -> factories.addAll(listings)));
        TradeOfferHelper.registerWanderingTraderOffers(1, factories -> factories.addAll(ModTrades.wandererGeneric()));
        TradeOfferHelper.registerWanderingTraderOffers(2, factories -> factories.addAll(ModTrades.wandererRare()));
    }

    /** Same placements NeoForge gets from data/sprout_and_soil/neoforge/biome_modifier. */
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
