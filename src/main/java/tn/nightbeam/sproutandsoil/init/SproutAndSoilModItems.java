/*
 *    MCreator note: This file will be REGENERATED on each build.
 */
package tn.nightbeam.sproutandsoil.init;

import tn.nightbeam.sproutandsoil.item.TomatoSeedsItem;
import tn.nightbeam.sproutandsoil.item.TomatoItem;
import tn.nightbeam.sproutandsoil.item.LetuceItem;
import tn.nightbeam.sproutandsoil.item.GarlicItem;
import tn.nightbeam.sproutandsoil.SproutAndSoilMod;

import net.minecraftforge.registries.RegistryObject;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.DeferredRegister;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.BlockItem;

public class SproutAndSoilModItems {
	public static final DeferredRegister<Item> REGISTRY = DeferredRegister.create(ForgeRegistries.ITEMS, SproutAndSoilMod.MODID);
	public static final RegistryObject<Item> TOMATO_SEEDS = REGISTRY.register("tomato_seeds", () -> new TomatoSeedsItem());
	public static final RegistryObject<Item> TOMATO_PLANT_STAGE_0 = block(SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_0);
	public static final RegistryObject<Item> TOMATO_PLANT_STAGE_1 = block(SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_1);
	public static final RegistryObject<Item> TOMATO_PLANT_STAGE_2 = block(SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_2);
	public static final RegistryObject<Item> TOMATO_PLANT_STAGE_3 = block(SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_3);
	public static final RegistryObject<Item> TOMATO_PLANT_STAGE_4 = block(SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_4);
	public static final RegistryObject<Item> TOMATO_PLANT_STAGE_5 = block(SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_5);
	public static final RegistryObject<Item> TOMATO_PLANT_STAGE_6 = block(SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_6);
	public static final RegistryObject<Item> TOMATO_PLANT_STAGE_7 = block(SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_7);
	public static final RegistryObject<Item> TOMATO = REGISTRY.register("tomato", () -> new TomatoItem());
	public static final RegistryObject<Item> GARLIC = REGISTRY.register("garlic", () -> new GarlicItem());
	public static final RegistryObject<Item> GARLIC_PLANT_STAGE_0 = block(SproutAndSoilModBlocks.GARLIC_PLANT_STAGE_0);
	public static final RegistryObject<Item> GARLIC_PLANT_STAGE_1 = block(SproutAndSoilModBlocks.GARLIC_PLANT_STAGE_1);
	public static final RegistryObject<Item> GARLIC_PLANT_STAGE_2 = block(SproutAndSoilModBlocks.GARLIC_PLANT_STAGE_2);
	public static final RegistryObject<Item> GARLIC_PLANT_STAGE_3 = block(SproutAndSoilModBlocks.GARLIC_PLANT_STAGE_3);
	public static final RegistryObject<Item> LETUCE = REGISTRY.register("letuce", () -> new LetuceItem());
	public static final RegistryObject<Item> LETUCE_PLANT_STAGE_0 = block(SproutAndSoilModBlocks.LETUCE_PLANT_STAGE_0);
	public static final RegistryObject<Item> LETUCE_PLANT_STAGE_1 = block(SproutAndSoilModBlocks.LETUCE_PLANT_STAGE_1);
	public static final RegistryObject<Item> LETUCE_PLANT_STAGE_2 = block(SproutAndSoilModBlocks.LETUCE_PLANT_STAGE_2);
	public static final RegistryObject<Item> LETUCE_PLANT_STAGE_3 = block(SproutAndSoilModBlocks.LETUCE_PLANT_STAGE_3);

	// Start of user code block custom items
	// End of user code block custom items
	private static RegistryObject<Item> block(RegistryObject<Block> block) {
		return block(block, new Item.Properties());
	}

	private static RegistryObject<Item> block(RegistryObject<Block> block, Item.Properties properties) {
		return REGISTRY.register(block.getId().getPath(), () -> new BlockItem(block.get(), properties));
	}
}