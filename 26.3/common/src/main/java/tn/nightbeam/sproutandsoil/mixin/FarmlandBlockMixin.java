package tn.nightbeam.sproutandsoil.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.FarmlandBlock;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import tn.nightbeam.sproutandsoil.farming.ScarecrowTracker;

/** Farmland near a scarecrow takes normal fall damage but is never trampled back to dirt. */
@Mixin(FarmlandBlock.class)
public abstract class FarmlandBlockMixin {

    @WrapOperation(method = "fallOn", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/level/block/FarmlandBlock;turnToBaseBlock(Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/level/block/state/BlockState;Lnet/minecraft/world/level/Level;Lnet/minecraft/core/BlockPos;)V"))
    private void sproutAndSoil$protectFarmland(FarmlandBlock block, Entity entity, BlockState state, Level level, BlockPos pos,
                                               Operation<Void> original) {
        if (level.isClientSide() || !ScarecrowTracker.protects(level, pos)) {
            original.call(block, entity, state, level, pos);
        }
    }
}
