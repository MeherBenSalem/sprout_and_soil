/*
 *    MCreator note: This file will be REGENERATED on each build.
 */
package tn.nightbeam.sproutandsoil.init;

import tn.nightbeam.sproutandsoil.block.TomatoPlantStage7Block;
import tn.nightbeam.sproutandsoil.block.TomatoPlantStage6Block;
import tn.nightbeam.sproutandsoil.block.TomatoPlantStage5Block;
import tn.nightbeam.sproutandsoil.block.TomatoPlantStage4Block;
import tn.nightbeam.sproutandsoil.block.TomatoPlantStage3Block;
import tn.nightbeam.sproutandsoil.block.TomatoPlantStage2Block;
import tn.nightbeam.sproutandsoil.block.TomatoPlantStage1Block;
import tn.nightbeam.sproutandsoil.block.TomatoPlantStage0Block;
import tn.nightbeam.sproutandsoil.SproutAndSoilMod;

import net.minecraftforge.registries.RegistryObject;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.DeferredRegister;

import net.minecraft.world.level.block.Block;

public class SproutAndSoilModBlocks {
	public static final DeferredRegister<Block> REGISTRY = DeferredRegister.create(ForgeRegistries.BLOCKS, SproutAndSoilMod.MODID);
	public static final RegistryObject<Block> TOMATO_PLANT_STAGE_0 = REGISTRY.register("tomato_plant_stage_0", () -> new TomatoPlantStage0Block());
	public static final RegistryObject<Block> TOMATO_PLANT_STAGE_1 = REGISTRY.register("tomato_plant_stage_1", () -> new TomatoPlantStage1Block());
	public static final RegistryObject<Block> TOMATO_PLANT_STAGE_2 = REGISTRY.register("tomato_plant_stage_2", () -> new TomatoPlantStage2Block());
	public static final RegistryObject<Block> TOMATO_PLANT_STAGE_3 = REGISTRY.register("tomato_plant_stage_3", () -> new TomatoPlantStage3Block());
	public static final RegistryObject<Block> TOMATO_PLANT_STAGE_4 = REGISTRY.register("tomato_plant_stage_4", () -> new TomatoPlantStage4Block());
	public static final RegistryObject<Block> TOMATO_PLANT_STAGE_5 = REGISTRY.register("tomato_plant_stage_5", () -> new TomatoPlantStage5Block());
	public static final RegistryObject<Block> TOMATO_PLANT_STAGE_6 = REGISTRY.register("tomato_plant_stage_6", () -> new TomatoPlantStage6Block());
	public static final RegistryObject<Block> TOMATO_PLANT_STAGE_7 = REGISTRY.register("tomato_plant_stage_7", () -> new TomatoPlantStage7Block());
	// Start of user code block custom blocks
	// End of user code block custom blocks
}