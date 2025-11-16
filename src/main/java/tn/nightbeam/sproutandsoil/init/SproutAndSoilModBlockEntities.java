/*
 *    MCreator note: This file will be REGENERATED on each build.
 */
package tn.nightbeam.sproutandsoil.init;

import tn.nightbeam.sproutandsoil.block.entity.TomatoPlantStage7BlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.TomatoPlantStage6BlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.TomatoPlantStage5BlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.TomatoPlantStage4BlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.TomatoPlantStage3BlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.TomatoPlantStage2BlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.TomatoPlantStage1BlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.TomatoPlantStage0BlockEntity;
import tn.nightbeam.sproutandsoil.SproutAndSoilMod;

import net.minecraftforge.registries.RegistryObject;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.DeferredRegister;

import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.Block;

public class SproutAndSoilModBlockEntities {
	public static final DeferredRegister<BlockEntityType<?>> REGISTRY = DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, SproutAndSoilMod.MODID);
	public static final RegistryObject<BlockEntityType<TomatoPlantStage0BlockEntity>> TOMATO_PLANT_STAGE_0 = register("tomato_plant_stage_0", SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_0, TomatoPlantStage0BlockEntity::new);
	public static final RegistryObject<BlockEntityType<TomatoPlantStage1BlockEntity>> TOMATO_PLANT_STAGE_1 = register("tomato_plant_stage_1", SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_1, TomatoPlantStage1BlockEntity::new);
	public static final RegistryObject<BlockEntityType<TomatoPlantStage2BlockEntity>> TOMATO_PLANT_STAGE_2 = register("tomato_plant_stage_2", SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_2, TomatoPlantStage2BlockEntity::new);
	public static final RegistryObject<BlockEntityType<TomatoPlantStage3BlockEntity>> TOMATO_PLANT_STAGE_3 = register("tomato_plant_stage_3", SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_3, TomatoPlantStage3BlockEntity::new);
	public static final RegistryObject<BlockEntityType<TomatoPlantStage4BlockEntity>> TOMATO_PLANT_STAGE_4 = register("tomato_plant_stage_4", SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_4, TomatoPlantStage4BlockEntity::new);
	public static final RegistryObject<BlockEntityType<TomatoPlantStage5BlockEntity>> TOMATO_PLANT_STAGE_5 = register("tomato_plant_stage_5", SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_5, TomatoPlantStage5BlockEntity::new);
	public static final RegistryObject<BlockEntityType<TomatoPlantStage6BlockEntity>> TOMATO_PLANT_STAGE_6 = register("tomato_plant_stage_6", SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_6, TomatoPlantStage6BlockEntity::new);
	public static final RegistryObject<BlockEntityType<TomatoPlantStage7BlockEntity>> TOMATO_PLANT_STAGE_7 = register("tomato_plant_stage_7", SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_7, TomatoPlantStage7BlockEntity::new);

	// Start of user code block custom block entities
	// End of user code block custom block entities
	private static <T extends BlockEntity> RegistryObject<BlockEntityType<T>> register(String registryname, RegistryObject<Block> block, BlockEntityType.BlockEntitySupplier<T> supplier) {
		return REGISTRY.register(registryname, () -> BlockEntityType.Builder.of(supplier, block.get()).build(null));
	}
}