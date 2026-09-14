package tn.nightbeam.sproutandsoil.fabric;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.fabricmc.fabric.api.object.builder.v1.block.entity.FabricBlockEntityTypeBuilder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.item.trading.MerchantOffer;
import net.fabricmc.fabric.api.object.builder.v1.trade.TradeOfferHelper;
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
        registerTrades();
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
                FabricBlockEntityTypeBuilder.create(CropStageBlockEntity::new, blocks).build()));
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
        CreativeModeTab tab = FabricItemGroup.builder()
                .title(Component.translatable("itemGroup.sprout_and_soil.sprout_and_soil"))
                .icon(() -> new ItemStack(ModItems.TOMATO_SEEDS.get()))
                .displayItems((params, output) -> {
                    output.accept(ModItems.TOMATO_SEEDS.get());
                    output.accept(ModItems.TOMATO.get());
                    output.accept(ModItems.GARLIC.get());
                    output.accept(ModItems.LETUCE.get());
                })
                .build();
        ResourceKey<CreativeModeTab> key = ResourceKey.create(Registries.CREATIVE_MODE_TAB, id("sprout_and_soil"));
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, key, tab);
        ModCreativeTabs.SPROUT_AND_SOIL = () -> tab;
    }

    private static void registerTrades() {
        TradeOfferHelper.registerVillagerOffers(VillagerProfession.FARMER, 1, factories -> factories.add((entity, random) ->
                new MerchantOffer(new ItemStack(Items.WHEAT, 8), new ItemStack(ModItems.TOMATO_SEEDS.get()), 10, 5, 0.05f)));
        TradeOfferHelper.registerVillagerOffers(VillagerProfession.FARMER, 2, factories -> factories.add((entity, random) ->
                new MerchantOffer(new ItemStack(ModItems.TOMATO.get(), 8), new ItemStack(ModItems.GARLIC.get()), 10, 5, 0.05f)));
        TradeOfferHelper.registerVillagerOffers(VillagerProfession.FARMER, 3, factories -> factories.add((entity, random) ->
                new MerchantOffer(new ItemStack(ModItems.GARLIC.get(), 8), new ItemStack(ModItems.LETUCE.get()), 10, 5, 0.05f)));
    }

    private static <T extends Item> Supplier<T> item(String name, Supplier<T> factory) {
        return register(name, () -> Registry.register(BuiltInRegistries.ITEM, id(name), factory.get()));
    }

    private static <T> Supplier<T> register(String name, Supplier<T> supplier) {
        T value = supplier.get();
        return () -> value;
    }

    private static ResourceLocation id(String path) {
        return new ResourceLocation(SproutAndSoil.MOD_ID, path);
    }
}
