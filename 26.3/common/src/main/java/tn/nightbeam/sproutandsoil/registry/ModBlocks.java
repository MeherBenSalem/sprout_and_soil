package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.random.WeightedList;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.grower.TreeGrower;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.NoteBlockInstrument;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.block.CookingPotBlock;
import tn.nightbeam.sproutandsoil.block.CuttingBoardBlock;
import tn.nightbeam.sproutandsoil.block.FeastBlock;
import tn.nightbeam.sproutandsoil.block.FruitLeavesBlock;
import tn.nightbeam.sproutandsoil.block.FruitSaplingBlock;
import tn.nightbeam.sproutandsoil.block.ScarecrowBlock;
import tn.nightbeam.sproutandsoil.block.SoilCakeBlock;
import tn.nightbeam.sproutandsoil.block.SoilCropBlock;
import tn.nightbeam.sproutandsoil.block.SprinklerBlock;
import tn.nightbeam.sproutandsoil.block.WildGardenBlock;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.content.ContentManifest;
import tn.nightbeam.sproutandsoil.platform.Services;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Supplier;

public final class ModBlocks {
    private static final Map<String, RegistryEntry<? extends Block>> BY_ID = new LinkedHashMap<>();

    public static final List<RegistryEntry<SoilCropBlock>> CROPS = new ArrayList<>();
    public static final List<RegistryEntry<FruitSaplingBlock>> SAPLINGS = new ArrayList<>();
    public static final List<RegistryEntry<FruitLeavesBlock>> FRUIT_LEAVES = new ArrayList<>();
    public static final List<RegistryEntry<WildGardenBlock>> GARDENS = new ArrayList<>();
    public static final List<RegistryEntry<Block>> CRATES = new ArrayList<>();
    public static final List<RegistryEntry<? extends Block>> FEASTS = new ArrayList<>();

    public static RegistryEntry<CookingPotBlock> COOKING_POT;
    public static RegistryEntry<CuttingBoardBlock> CUTTING_BOARD;
    public static RegistryEntry<ScarecrowBlock> SCARECROW;
    public static RegistryEntry<SprinklerBlock> SPRINKLER;

    private ModBlocks() {
    }

    public static void init() {
        ContentManifest manifest = Content.manifest();

        // Every block's properties carry its registry key (Keys), which 26.x requires before construction.
        for (ContentManifest.Crop crop : manifest.crops()) {
            CROPS.add(register(crop.block(), () -> new SoilCropBlock(Keys.copy(Blocks.WHEAT, crop.block()),
                    SproutAndSoil.id(crop.plantingItem()), crop.regrowAge(), crop.model() == ContentManifest.CropModel.TALL)));
        }

        for (ContentManifest.Tree tree : manifest.trees()) {
            // 26.3 folds configured features into Registries.FEATURE (net.minecraft...feature.Feature).
            ResourceKey<net.minecraft.world.level.levelgen.feature.Feature> feature =
                    ResourceKey.create(Registries.FEATURE, tree.feature());
            SAPLINGS.add(register(tree.sapling(), () -> new FruitSaplingBlock(
                    new TreeGrower(SproutAndSoil.MOD_ID + ":" + tree.id(), WeightedList.of(feature), WeightedList.of(), WeightedList.of(), feature),
                    Keys.copy(Blocks.OAK_SAPLING, tree.sapling()))));
            FRUIT_LEAVES.add(register(tree.leaves(), () -> new FruitLeavesBlock(
                    Keys.copy(Blocks.OAK_LEAVES, tree.leaves()), tree.fruit())));
        }

        for (String garden : manifest.gardens()) {
            GARDENS.add(register(garden, () -> new WildGardenBlock(Keys.block(garden)
                    .mapColor(MapColor.PLANT).noCollision().instabreak().sound(SoundType.SWEET_BERRY_BUSH)
                    .offsetType(BlockBehaviour.OffsetType.XZ).ignitedByLava().pushReaction(PushReaction.POPPED))));
        }

        for (String crate : manifest.crates()) {
            CRATES.add(register(crate, () -> new Block(Keys.block(crate).mapColor(MapColor.WOOD)
                    .instrument(NoteBlockInstrument.BASS).strength(2.0F, 3.0F).sound(SoundType.WOOD).ignitedByLava())));
        }

        for (ContentManifest.Feast feast : manifest.feasts()) {
            FEASTS.add(switch (feast.kind()) {
                case CAKE -> register(feast.id(), () -> new SoilCakeBlock(Keys.copy(Blocks.CAKE, feast.id())));
                case PIE -> register(feast.id(), () -> new FeastBlock(Keys.copy(Blocks.CAKE, feast.id()),
                        SproutAndSoil.id(feast.slice()), 4.0D));
                case PIZZA -> register(feast.id(), () -> new FeastBlock(Keys.copy(Blocks.CAKE, feast.id()),
                        SproutAndSoil.id(feast.slice()), 1.5D));
            });
        }

        COOKING_POT = register("cooking_pot", () -> new CookingPotBlock(Keys.block("cooking_pot")
                .mapColor(MapColor.METAL).strength(1.5F, 6.0F).sound(SoundType.LANTERN).noOcclusion().forceSolidOn()
                .pushReaction(PushReaction.IMMOVEABLE)));
        CUTTING_BOARD = register("cutting_board", () -> new CuttingBoardBlock(Keys.block("cutting_board")
                .mapColor(MapColor.WOOD).strength(0.8F).sound(SoundType.WOOD).noOcclusion().forceSolidOn().ignitedByLava()));
        SCARECROW = register("scarecrow", () -> new ScarecrowBlock(Keys.block("scarecrow")
                .mapColor(MapColor.WOOD).strength(1.0F).sound(SoundType.WOOD).noOcclusion().ignitedByLava()
                .pushReaction(PushReaction.POPPED)));
        SPRINKLER = register("sprinkler", () -> new SprinklerBlock(Keys.block("sprinkler")
                .mapColor(MapColor.COLOR_ORANGE).strength(1.5F, 6.0F).sound(SoundType.COPPER).noOcclusion().forceSolidOn()));
    }

    private static <T extends Block> RegistryEntry<T> register(String name, Supplier<T> factory) {
        RegistryEntry<T> entry = Services.REGISTRAR.register(Registries.BLOCK, name, factory);
        BY_ID.put(name, entry);
        return entry;
    }

    public static Block get(String id) {
        RegistryEntry<? extends Block> entry = BY_ID.get(id);
        if (entry == null) {
            throw new IllegalArgumentException("Unknown Sprout & Soil block " + id);
        }
        return entry.get();
    }
}
