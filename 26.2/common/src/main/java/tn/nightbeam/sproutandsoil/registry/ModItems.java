package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.component.Consumable;
import net.minecraft.world.item.component.Consumables;
import net.minecraft.world.level.block.Block;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.content.ContentManifest;
import tn.nightbeam.sproutandsoil.item.DescribedItem;
import tn.nightbeam.sproutandsoil.item.FertilizerItem;
import tn.nightbeam.sproutandsoil.item.KnifeItem;
import tn.nightbeam.sproutandsoil.item.ModTiers;
import tn.nightbeam.sproutandsoil.item.MortarItem;
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
    public static RegistryEntry<MortarItem> MORTAR_AND_PESTLE;
    public static RegistryEntry<FertilizerItem> FERTILIZER;

    private ModItems() {
    }

    public static void init() {
        ContentManifest manifest = Content.manifest();

        // Manifest order puts serving containers (plate, mug) before the dishes that return them.
        for (ContentManifest.ItemEntry entry : manifest.items()) {
            register(entry.id(), () -> createItem(entry));
        }

        ModBlocks.SAPLINGS.forEach(block -> blockItem(block.id().getPath(), block, 64));
        ModBlocks.FRUIT_LEAVES.forEach(block -> blockItem(block.id().getPath(), block, 64));
        ModBlocks.GARDENS.forEach(block -> blockItem(block.id().getPath(), block, 64));
        ModBlocks.CRATES.forEach(block -> blockItem(block.id().getPath(), block, 64));
        ModBlocks.FEASTS.forEach(block -> blockItem(block.id().getPath(), block, 1));

        COOKING_POT = register("cooking_pot", () -> new DescribedItem.ForBlock(ModBlocks.COOKING_POT.get(),
                Keys.item("cooking_pot").useBlockDescriptionPrefix()));
        CUTTING_BOARD = register("cutting_board", () -> new DescribedItem.ForBlock(ModBlocks.CUTTING_BOARD.get(),
                Keys.item("cutting_board").useBlockDescriptionPrefix()));
        SCARECROW = register("scarecrow", () -> new DescribedItem.ForBlock(ModBlocks.SCARECROW.get(),
                Keys.item("scarecrow").useBlockDescriptionPrefix()));
        SPRINKLER = register("sprinkler", () -> new DescribedItem.ForBlock(ModBlocks.SPRINKLER.get(),
                Keys.item("sprinkler").useBlockDescriptionPrefix()));

        knife("flint_knife", ModTiers.FLINT, false);
        knife("iron_knife", ToolMaterial.IRON, false);
        knife("golden_knife", ToolMaterial.GOLD, false);
        knife("diamond_knife", ToolMaterial.DIAMOND, false);
        knife("netherite_knife", ToolMaterial.NETHERITE, true);
        sickle("iron_sickle", ToolMaterial.IRON, 1, false);
        sickle("golden_sickle", ToolMaterial.GOLD, 1, false);
        sickle("diamond_sickle", ToolMaterial.DIAMOND, 2, false);
        sickle("netherite_sickle", ToolMaterial.NETHERITE, 2, true);

        WATERING_CAN = register("watering_can", () -> new WateringCanItem(Keys.item("watering_can").stacksTo(1)));
        MORTAR_AND_PESTLE = register("mortar_and_pestle", () -> new MortarItem(Keys.item("mortar_and_pestle").durability(160)));
        FERTILIZER = register("fertilizer", () -> new FertilizerItem(Keys.item("fertilizer")));
    }

    private static Item createItem(ContentManifest.ItemEntry entry) {
        Item.Properties properties = Keys.item(entry.id()).stacksTo(entry.stackSize());
        ContentManifest.Food food = entry.food();
        if (food != null) {
            properties.food(food(food), consumable(entry));
            if (entry.container() != null) {
                properties.usingConvertsTo(resolve(entry.container(), entry.id()));
            }
        }
        // The crafting remainder (bottles, bowls) is returned by SoilFoodItem / SoilSeedItem.
        Item remainder = entry.remainder() != null ? resolve(entry.remainder(), entry.id()) : null;
        if (entry.plants() != null) {
            return new SoilSeedItem(ModBlocks.get(entry.plants()), properties.useItemDescriptionPrefix(), entry, remainder);
        }
        return new SoilFoodItem(properties, entry, remainder);
    }

    private static FoodProperties food(ContentManifest.Food food) {
        FoodProperties.Builder builder = new FoodProperties.Builder()
                .nutrition(food.nutrition())
                .saturationModifier(food.saturation());
        if (food.alwaysEdible()) {
            builder.alwaysEdible();
        }
        return builder.build();
    }

    /** Eating or drinking; fast foods take 0.8 s. Manifest effects are applied when eaten (see SoilFoodItem). */
    private static Consumable consumable(ContentManifest.ItemEntry entry) {
        Consumable.Builder builder = entry.drink() ? Consumables.defaultDrink() : Consumables.defaultFood();
        if (entry.food() != null && entry.food().fast()) {
            builder.consumeSeconds(0.8F);
        }
        return builder.build();
    }

    /** Containers must already be registered: the manifest lists them before the foods that use them. */
    private static Item resolve(Identifier id, String user) {
        Item item = BuiltInRegistries.ITEM.getValue(id);
        if (item == Items.AIR) {
            throw new IllegalStateException("Item " + user + " references " + id + " before it is registered");
        }
        return item;
    }

    private static void knife(String name, ToolMaterial material, boolean fireResistant) {
        Item.Properties properties = Keys.item(name);
        if (fireResistant) {
            properties.fireResistant();
        }
        register(name, () -> new KnifeItem(material, properties));
    }

    private static void sickle(String name, ToolMaterial material, int radius, boolean fireResistant) {
        Item.Properties properties = Keys.item(name);
        if (fireResistant) {
            properties.fireResistant();
        }
        register(name, () -> new SickleItem(material, radius, properties));
    }

    private static void blockItem(String name, RegistryEntry<? extends Block> block, int stackSize) {
        register(name, () -> new BlockItem(block.get(), Keys.item(name).stacksTo(stackSize).useBlockDescriptionPrefix()));
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
