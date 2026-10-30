package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.block.Block;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.content.ContentManifest;
import tn.nightbeam.sproutandsoil.item.DescribedItem;
import tn.nightbeam.sproutandsoil.item.FertilizerItem;
import tn.nightbeam.sproutandsoil.item.KnifeItem;
import tn.nightbeam.sproutandsoil.item.ModTiers;
import tn.nightbeam.sproutandsoil.item.SickleItem;
import tn.nightbeam.sproutandsoil.item.SoilFoodItem;
import tn.nightbeam.sproutandsoil.item.SoilSeedItem;
import tn.nightbeam.sproutandsoil.item.WateringCanItem;
import tn.nightbeam.sproutandsoil.platform.Services;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;

public final class ModItems {
    private static final Map<String, RegistryEntry<? extends Item>> BY_ID = new LinkedHashMap<>();

    public static RegistryEntry<BlockItem> COOKING_POT;
    public static RegistryEntry<BlockItem> CUTTING_BOARD;
    public static RegistryEntry<BlockItem> SCARECROW;
    public static RegistryEntry<BlockItem> SPRINKLER;
    public static RegistryEntry<WateringCanItem> WATERING_CAN;
    public static RegistryEntry<Item> MORTAR_AND_PESTLE;
    public static RegistryEntry<FertilizerItem> FERTILIZER;

    private ModItems() {
    }

    public static void init() {
        ContentManifest manifest = Content.manifest();

        // Manifest order puts serving containers (plate, mug) before the dishes that return them.
        for (ContentManifest.ItemEntry entry : manifest.items()) {
            register(entry.id(), () -> createItem(entry));
        }

        ModBlocks.SAPLINGS.forEach(block -> blockItem(block.id().getPath(), block, new Item.Properties()));
        ModBlocks.FRUIT_LEAVES.forEach(block -> blockItem(block.id().getPath(), block, new Item.Properties()));
        ModBlocks.GARDENS.forEach(block -> blockItem(block.id().getPath(), block, new Item.Properties()));
        ModBlocks.CRATES.forEach(block -> blockItem(block.id().getPath(), block, new Item.Properties()));
        ModBlocks.FEASTS.forEach(block -> blockItem(block.id().getPath(), block, new Item.Properties().stacksTo(1)));

        COOKING_POT = register("cooking_pot", () -> new DescribedItem.ForBlock(ModBlocks.COOKING_POT.get(), new Item.Properties()));
        CUTTING_BOARD = register("cutting_board", () -> new DescribedItem.ForBlock(ModBlocks.CUTTING_BOARD.get(), new Item.Properties()));
        SCARECROW = register("scarecrow", () -> new DescribedItem.ForBlock(ModBlocks.SCARECROW.get(), new Item.Properties()));
        SPRINKLER = register("sprinkler", () -> new DescribedItem.ForBlock(ModBlocks.SPRINKLER.get(), new Item.Properties()));

        knife("flint_knife", ModTiers.FLINT, new Item.Properties());
        knife("iron_knife", Tiers.IRON, new Item.Properties());
        knife("golden_knife", Tiers.GOLD, new Item.Properties());
        knife("diamond_knife", Tiers.DIAMOND, new Item.Properties());
        knife("netherite_knife", Tiers.NETHERITE, new Item.Properties().fireResistant());
        sickle("iron_sickle", Tiers.IRON, 1, new Item.Properties());
        sickle("golden_sickle", Tiers.GOLD, 1, new Item.Properties());
        sickle("diamond_sickle", Tiers.DIAMOND, 2, new Item.Properties());
        sickle("netherite_sickle", Tiers.NETHERITE, 2, new Item.Properties().fireResistant());

        WATERING_CAN = register("watering_can", () -> new WateringCanItem(new Item.Properties().stacksTo(1)));
        MORTAR_AND_PESTLE = register("mortar_and_pestle", () -> new DescribedItem.Simple(new Item.Properties().durability(160)));
        FERTILIZER = register("fertilizer", () -> new FertilizerItem(new Item.Properties()));
    }

    private static Item createItem(ContentManifest.ItemEntry entry) {
        Item.Properties properties = new Item.Properties().stacksTo(entry.stackSize());
        if (entry.food() != null) {
            properties.food(food(entry));
        }
        if (entry.remainder() != null) {
            properties.craftRemainder(resolve(entry.remainder(), entry.id()));
        }
        if (entry.plants() != null) {
            return new SoilSeedItem(ModBlocks.get(entry.plants()), properties, entry);
        }
        return new SoilFoodItem(properties, entry);
    }

    private static FoodProperties food(ContentManifest.ItemEntry entry) {
        ContentManifest.Food food = entry.food();
        FoodProperties.Builder builder = new FoodProperties.Builder()
                .nutrition(food.nutrition())
                .saturationModifier(food.saturation());
        if (food.alwaysEdible()) {
            builder.alwaysEdible();
        }
        if (food.fast()) {
            builder.fast();
        }
        if (entry.container() != null) {
            builder.usingConvertsTo(resolve(entry.container(), entry.id()));
        }
        return builder.build();
    }

    /** Containers must already be registered: the manifest lists them before the foods that use them. */
    private static Item resolve(ResourceLocation id, String user) {
        Item item = BuiltInRegistries.ITEM.get(id);
        if (item == Items.AIR) {
            throw new IllegalStateException("Item " + user + " references " + id + " before it is registered");
        }
        return item;
    }

    private static void knife(String name, Tier tier, Item.Properties properties) {
        register(name, () -> new KnifeItem(tier, properties));
    }

    private static void sickle(String name, Tier tier, int radius, Item.Properties properties) {
        register(name, () -> new SickleItem(tier, radius, properties));
    }

    private static void blockItem(String name, RegistryEntry<? extends Block> block, Item.Properties properties) {
        register(name, () -> new BlockItem(block.get(), properties));
    }

    private static <T extends Item> RegistryEntry<T> register(String name, Supplier<T> factory) {
        RegistryEntry<T> entry = Services.REGISTRAR.register(Registries.ITEM, name, factory);
        BY_ID.put(name, entry);
        return entry;
    }

    public static Item get(String id) {
        RegistryEntry<? extends Item> entry = BY_ID.get(id);
        if (entry == null) {
            throw new IllegalArgumentException("Unknown Sprout & Soil item " + id);
        }
        return entry.get();
    }
}
