package tn.nightbeam.sproutandsoil.content;

import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.Map;

/**
 * Gameplay data generated from the content spec in {@code tools/assetgen/sas/spec}.
 * The same spec produces textures, models, recipes and loot tables, so ids always line up.
 */
public record ContentManifest(
        List<Crop> crops,
        List<Tree> trees,
        List<ItemEntry> items,
        List<Feast> feasts,
        List<String> crates,
        List<String> gardens,
        Map<ResourceLocation, Float> compost,
        List<Worldgen> worldgen,
        Map<String, List<ResourceLocation>> tabs,
        TradePools trades) {

    public enum CropModel { CROP, CROSS, TALL }

    public record Crop(String id, String block, String plantingItem, String produce, CropModel model, int regrowAge) {
        public boolean perennial() {
            return regrowAge >= 0;
        }
    }

    public record Tree(String id, String sapling, String leaves, ResourceLocation fruit, ResourceLocation feature) {
    }

    public record Effect(ResourceLocation effect, int duration, int amplifier, float chance) {
    }

    public record Food(int nutrition, float saturation, boolean alwaysEdible, boolean fast, List<Effect> effects) {
    }

    public record ItemEntry(String id, int stackSize, @Nullable Food food, @Nullable ResourceLocation container,
                            @Nullable ResourceLocation remainder, boolean drink, @Nullable String plants, boolean tooltip) {
    }

    public enum FeastKind { PIE, PIZZA, CAKE }

    public record Feast(String id, FeastKind kind, @Nullable String slice) {
    }

    public record Worldgen(ResourceLocation feature, ResourceLocation biomes) {
    }

    public record TradePools(List<ResourceLocation> seeds, List<ResourceLocation> produce, List<ResourceLocation> fruits,
                             List<ResourceLocation> saplings, List<ResourceLocation> meals) {
    }
}
