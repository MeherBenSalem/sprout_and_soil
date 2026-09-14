package tn.nightbeam.sproutandsoil.fabric;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.block.CropStageBlock;
import tn.nightbeam.sproutandsoil.block.entity.CropStageBlockEntity;
import tn.nightbeam.sproutandsoil.crop.CropType;
import tn.nightbeam.sproutandsoil.item.GarlicItem;
import tn.nightbeam.sproutandsoil.item.LetuceItem;
import tn.nightbeam.sproutandsoil.item.TomatoItem;
import tn.nightbeam.sproutandsoil.item.TomatoSeedsItem;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;
import tn.nightbeam.sproutandsoil.registry.ModBlocks;
import tn.nightbeam.sproutandsoil.registry.ModCreativeTabs;
import tn.nightbeam.sproutandsoil.registry.ModItems;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

public class SproutAndSoilFabric implements ModInitializer {
    private static final List<Supplier<Block>> REGISTERED_BLOCKS = new ArrayList<>();

    @Override
    public void onInitialize() {
        SproutAndSoil.init();
        registerBlocks();
        registerBlockEntity();
        registerItems();
        registerCreativeTab();
    }

    private static void registerBlocks() {
        ModBlocks.TOMATO_PLANT_STAGE_0 = registerCropBlock(CropType.TOMATO, 0);
        ModBlocks.TOMATO_PLANT_STAGE_1 = registerCropBlock(CropType.TOMATO, 1);
        ModBlocks.TOMATO_PLANT_STAGE_2 = registerCropBlock(CropType.TOMATO, 2);
        ModBlocks.TOMATO_PLANT_STAGE_3 = registerCropBlock(CropType.TOMATO, 3);
        ModBlocks.TOMATO_PLANT_STAGE_4 = registerCropBlock(CropType.TOMATO, 4);
        ModBlocks.TOMATO_PLANT_STAGE_5 = registerCropBlock(CropType.TOMATO, 5);
        ModBlocks.TOMATO_PLANT_STAGE_6 = registerCropBlock(CropType.TOMATO, 6);
        ModBlocks.TOMATO_PLANT_STAGE_7 = registerCropBlock(CropType.TOMATO, 7);
        ModBlocks.GARLIC_PLANT_STAGE_0 = registerCropBlock(CropType.GARLIC, 0);
        ModBlocks.GARLIC_PLANT_STAGE_1 = registerCropBlock(CropType.GARLIC, 1);
        ModBlocks.GARLIC_PLANT_STAGE_2 = registerCropBlock(CropType.GARLIC, 2);
        ModBlocks.GARLIC_PLANT_STAGE_3 = registerCropBlock(CropType.GARLIC, 3);
        ModBlocks.LETUCE_PLANT_STAGE_0 = registerCropBlock(CropType.LETUCE, 0);
        ModBlocks.LETUCE_PLANT_STAGE_1 = registerCropBlock(CropType.LETUCE, 1);
        ModBlocks.LETUCE_PLANT_STAGE_2 = registerCropBlock(CropType.LETUCE, 2);
        ModBlocks.LETUCE_PLANT_STAGE_3 = registerCropBlock(CropType.LETUCE, 3);
    }

    private static Supplier<Block> registerCropBlock(CropType type, int stage) {
        String name = type.idPrefix() + stage;
        Supplier<Block> supplier = register(name, () -> Registry.register(BuiltInRegistries.BLOCK, id(name), new CropStageBlock(type, stage)));
        REGISTERED_BLOCKS.add(supplier);
        return supplier;
    }

    private static void registerBlockEntity() {
        Block[] blocks = ModBlocks.allCropBlocks().toArray(Block[]::new);
        ModBlockEntities.CROP_STAGE = register("crop_stage", () -> Registry.register(
                BuiltInRegistries.BLOCK_ENTITY_TYPE,
                id("crop_stage"),
                new BlockEntityType<>(CropStageBlockEntity::new, java.util.Set.of(blocks))));
    }

    private static void registerItems() {
        ModItems.TOMATO_SEEDS = item("tomato_seeds", TomatoSeedsItem::new);
        ModItems.TOMATO = item("tomato", TomatoItem::new);
        ModItems.GARLIC = item("garlic", GarlicItem::new);
        ModItems.LETUCE = item("letuce", LetuceItem::new);
        for (Supplier<Block> block : REGISTERED_BLOCKS) {
            String path = BuiltInRegistries.BLOCK.getKey(block.get()).getPath();
            item(path, () -> new BlockItem(block.get(), new Item.Properties()));
        }
    }

    private static void registerCreativeTab() {
        CreativeModeTab tab = FabricCreativeModeTab.builder()
                .title(Component.translatable("itemGroup.sprout_and_soil.sprout_and_soil"))
                .icon(() -> new ItemStack(ModItems.TOMATO_SEEDS.get()))
                .build();
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, id("sprout_and_soil"), tab);
        ModCreativeTabs.SPROUT_AND_SOIL = () -> tab;
        CreativeModeTabEvents.modifyOutputEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, id("sprout_and_soil")))
                .register(content -> {
                    content.accept(ModItems.TOMATO_SEEDS.get());
                    content.accept(ModItems.TOMATO.get());
                    content.accept(ModItems.GARLIC.get());
                    content.accept(ModItems.LETUCE.get());
                });
    }

    private static <T extends Item> Supplier<T> item(String name, Supplier<T> factory) {
        return register(name, () -> Registry.register(BuiltInRegistries.ITEM, id(name), factory.get()));
    }

    private static <T> Supplier<T> register(String name, Supplier<T> supplier) {
        T value = supplier.get();
        return () -> value;
    }

    private static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(SproutAndSoil.MOD_ID, path);
    }
}
