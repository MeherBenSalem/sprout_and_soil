package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.grower.AbstractTreeGrower;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.NoteBlockInstrument;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;
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

        for (ContentManifest.Crop crop : manifest.crops()) {
            CROPS.add(register(crop.block(), () -> new SoilCropBlock(BlockBehaviour.Properties.copy(Blocks.WHEAT),
                    SproutAndSoil.id(crop.plantingItem()), crop.regrowAge(), crop.model() == ContentManifest.CropModel.TALL)));
        }

        for (ContentManifest.Tree tree : manifest.trees()) {
            ResourceKey<ConfiguredFeature<?, ?>> feature =
                    ResourceKey.create(Registries.CONFIGURED_FEATURE, tree.feature());
            SAPLINGS.add(register(tree.sapling(), () -> new FruitSaplingBlock(
                    new AbstractTreeGrower() {
                        @Override
                        protected ResourceKey<ConfiguredFeature<?, ?>> getConfiguredFeature(RandomSource random, boolean hasFlowers) {
                            return feature;
                        }
                    },
                    BlockBehaviour.Properties.copy(Blocks.OAK_SAPLING))));
            FRUIT_LEAVES.add(register(tree.leaves(), () -> new FruitLeavesBlock(
                    BlockBehaviour.Properties.copy(Blocks.OAK_LEAVES), tree.fruit())));
        }

        for (String garden : manifest.gardens()) {
            GARDENS.add(register(garden, () -> new WildGardenBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.PLANT).noCollission().instabreak().sound(SoundType.SWEET_BERRY_BUSH)
                    .offsetType(BlockBehaviour.OffsetType.XZ).ignitedByLava().pushReaction(PushReaction.DESTROY))));
        }

        for (String crate : manifest.crates()) {
            CRATES.add(register(crate, () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.WOOD)
                    .instrument(NoteBlockInstrument.BASS).strength(2.0F, 3.0F).sound(SoundType.WOOD).ignitedByLava())));
        }

        for (ContentManifest.Feast feast : manifest.feasts()) {
            FEASTS.add(switch (feast.kind()) {
                case CAKE -> register(feast.id(), () -> new SoilCakeBlock(BlockBehaviour.Properties.copy(Blocks.CAKE)));
                case PIE -> register(feast.id(), () -> new FeastBlock(BlockBehaviour.Properties.copy(Blocks.CAKE),
                        SproutAndSoil.id(feast.slice()), 4.0D));
                case PIZZA -> register(feast.id(), () -> new FeastBlock(BlockBehaviour.Properties.copy(Blocks.CAKE),
                        SproutAndSoil.id(feast.slice()), 1.5D));
            });
        }

        COOKING_POT = register("cooking_pot", () -> new CookingPotBlock(BlockBehaviour.Properties.of()
                .mapColor(MapColor.METAL).strength(1.5F, 6.0F).sound(SoundType.LANTERN).noOcclusion().forceSolidOn()
                .pushReaction(PushReaction.BLOCK)));
        CUTTING_BOARD = register("cutting_board", () -> new CuttingBoardBlock(BlockBehaviour.Properties.of()
                .mapColor(MapColor.WOOD).strength(0.8F).sound(SoundType.WOOD).noOcclusion().forceSolidOn().ignitedByLava()));
        SCARECROW = register("scarecrow", () -> new ScarecrowBlock(BlockBehaviour.Properties.of()
                .mapColor(MapColor.WOOD).strength(1.0F).sound(SoundType.WOOD).noOcclusion().ignitedByLava()
                .pushReaction(PushReaction.DESTROY)));
        SPRINKLER = register("sprinkler", () -> new SprinklerBlock(BlockBehaviour.Properties.of()
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

    /** Every block that renders with a cutout layer (plants, leaves, workstations with holes). */
    public static List<Block> cutoutBlocks() {
        List<Block> out = new ArrayList<>();
        CROPS.forEach(e -> out.add(e.get()));
        SAPLINGS.forEach(e -> out.add(e.get()));
        GARDENS.forEach(e -> out.add(e.get()));
        out.add(COOKING_POT.get());
        out.add(CUTTING_BOARD.get());
        out.add(SCARECROW.get());
        out.add(SPRINKLER.get());
        return out;
    }

    public static List<Block> cutoutMippedBlocks() {
        List<Block> out = new ArrayList<>();
        FRUIT_LEAVES.forEach(e -> out.add(e.get()));
        return out;
    }
}
