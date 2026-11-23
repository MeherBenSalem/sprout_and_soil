package tn.nightbeam.sproutandsoil.fabric;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.ComposterBlock;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.entries.NestedLootTable;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.content.ContentManifest;
import tn.nightbeam.sproutandsoil.farming.CropHarvesting;

/** Villager and wandering trader trades are not offered on Minecraft 26.x. */
public class SproutAndSoilFabric implements ModInitializer {
    private static final Identifier SHORT_GRASS = Identifier.withDefaultNamespace("blocks/short_grass");

    @Override
    public void onInitialize() {
        SproutAndSoil.init();
        registerWorldgen();
        registerCompostables();
        registerLootInjections();
        UseBlockCallback.EVENT.register(CropHarvesting::onUseBlock);
    }

    /** Grass has a small chance to drop temperate seeds (NeoForge uses a global loot modifier for the same table). */
    private static void registerLootInjections() {
        ResourceKey<LootTable> grassSeeds = ResourceKey.create(Registries.LOOT_TABLE, SproutAndSoil.id("gameplay/grass_seeds"));
        LootTableEvents.MODIFY.register((key, builder, source, registries) -> {
            if (source.isBuiltin() && SHORT_GRASS.equals(key.identifier())) {
                builder.withPool(LootPool.lootPool().add(NestedLootTable.lootTableReference(grassSeeds)));
            }
        });
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
            Item item = BuiltInRegistries.ITEM.getValue(id);
            if (item != Items.AIR) {
                ComposterBlock.COMPOSTABLES.put(item, chance.floatValue());
            }
        });
    }
}
