package tn.nightbeam.sproutandsoil.neoforge;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.neoforged.neoforge.event.village.VillagerTradesEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
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

@Mod(SproutAndSoil.MOD_ID)
public class SproutAndSoilNeoForge {
    private static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(BuiltInRegistries.BLOCK, SproutAndSoil.MOD_ID);
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(BuiltInRegistries.ITEM, SproutAndSoil.MOD_ID);
    private static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES = DeferredRegister.create(BuiltInRegistries.BLOCK_ENTITY_TYPE, SproutAndSoil.MOD_ID);
    private static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, SproutAndSoil.MOD_ID);
    private static final List<DeferredHolder<Block, Block>> BLOCK_HOLDERS = new ArrayList<>();

    public SproutAndSoilNeoForge(IEventBus modBus) {
        SproutAndSoil.init();
        registerBlocks();
        registerItems();
        registerBlockEntities();
        registerCreativeTab();
        BLOCKS.register(modBus);
        ITEMS.register(modBus);
        BLOCK_ENTITIES.register(modBus);
        TABS.register(modBus);
        IEventBus neoBus = net.neoforged.neoforge.common.NeoForge.EVENT_BUS;
        neoBus.addListener(SproutAndSoilNeoForge::registerTrades);
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

    private static DeferredHolder<Block, Block> registerCropBlock(CropType type, int stage) {
        DeferredHolder<Block, Block> holder = BLOCKS.register(type.idPrefix() + stage, () -> new CropStageBlock(type, stage));
        BLOCK_HOLDERS.add(holder);
        return holder;
    }

    private static void registerItems() {
        ModItems.TOMATO_SEEDS = ITEMS.register("tomato_seeds", TomatoSeedsItem::new);
        ModItems.TOMATO = ITEMS.register("tomato", TomatoItem::new);
        ModItems.GARLIC = ITEMS.register("garlic", GarlicItem::new);
        ModItems.LETUCE = ITEMS.register("letuce", LetuceItem::new);
        for (DeferredHolder<Block, Block> block : BLOCK_HOLDERS) {
            ITEMS.register(block.getId().getPath(), () -> new BlockItem(block.get(), new Item.Properties()));
        }
    }

    private static void registerBlockEntities() {
        ModBlockEntities.CROP_STAGE = BLOCK_ENTITIES.register("crop_stage",
                () -> BlockEntityType.Builder.of(CropStageBlockEntity::new, ModBlocks.allCropBlocks().toArray(Block[]::new)).build(null));
    }

    private static void registerCreativeTab() {
        ModCreativeTabs.SPROUT_AND_SOIL = TABS.register("sprout_and_soil",
                () -> CreativeModeTab.builder()
                        .title(Component.translatable("itemGroup.sprout_and_soil.sprout_and_soil"))
                        .icon(() -> new ItemStack(ModItems.TOMATO_SEEDS.get()))
                        .displayItems((params, output) -> {
                            output.accept(ModItems.TOMATO_SEEDS.get());
                            output.accept(ModItems.TOMATO.get());
                            output.accept(ModItems.GARLIC.get());
                            output.accept(ModItems.LETUCE.get());
                        })
                        .build());
    }

    @SubscribeEvent
    public static void registerTrades(VillagerTradesEvent event) {
        if (event.getType() != VillagerProfession.FARMER) {
            return;
        }
        event.getTrades().get(1).add((entity, random) -> new MerchantOffer(new ItemCost(Items.WHEAT, 8),
                new ItemStack(ModItems.TOMATO_SEEDS.get()), 10, 5, 0.05f));
        event.getTrades().get(2).add((entity, random) -> new MerchantOffer(new ItemCost(ModItems.TOMATO.get(), 8),
                new ItemStack(ModItems.GARLIC.get()), 10, 5, 0.05f));
        event.getTrades().get(3).add((entity, random) -> new MerchantOffer(new ItemCost(ModItems.GARLIC.get(), 8),
                new ItemStack(ModItems.LETUCE.get()), 10, 5, 0.05f));
    }
}
