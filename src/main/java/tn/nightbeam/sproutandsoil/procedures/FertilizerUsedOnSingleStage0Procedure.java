package tn.nightbeam.sproutandsoil.procedures;

import tn.nightbeam.sproutandsoil.init.SproutAndSoilModBlocks;

import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Entity;
import net.minecraft.tags.ItemTags;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.core.BlockPos;

public class FertilizerUsedOnSingleStage0Procedure {
	public static void execute(LevelAccessor world, double x, double y, double z, Entity entity) {
		if (entity == null)
			return;
		double random = 0;
		BlockState nextStage1 = Blocks.AIR.defaultBlockState();
		BlockState nextStage2 = Blocks.AIR.defaultBlockState();
		BlockState nextStage3 = Blocks.AIR.defaultBlockState();
		if ((world.getBlockState(BlockPos.containing(x, y, z))).getBlock() == SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_0.get()
				&& (entity instanceof LivingEntity _livEnt ? _livEnt.getMainHandItem() : ItemStack.EMPTY).is(ItemTags.create(ResourceLocation.parse("crops:fertilizer")))) {
			nextStage1 = SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_1.get().defaultBlockState();
			nextStage2 = SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_2.get().defaultBlockState();
			nextStage3 = SproutAndSoilModBlocks.TOMATO_PLANT_STAGE_3.get().defaultBlockState();
			random = Math.random();
			if (random >= 0.8 && nextStage3.canSurvive(world, BlockPos.containing(x, y, z))) {
				world.setBlock(BlockPos.containing(x, y, z), nextStage3, 3);
			} else if (random >= 0.5 && nextStage2.canSurvive(world, BlockPos.containing(x, y, z))) {
				world.setBlock(BlockPos.containing(x, y, z), nextStage2, 3);
			} else if (nextStage1.canSurvive(world, BlockPos.containing(x, y, z))) {
				world.setBlock(BlockPos.containing(x, y, z), nextStage1, 3);
			}
		}
	}
}