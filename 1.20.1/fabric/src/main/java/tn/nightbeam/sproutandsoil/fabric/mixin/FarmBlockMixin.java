package tn.nightbeam.sproutandsoil.fabric.mixin;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import tn.nightbeam.sproutandsoil.farming.ScarecrowTracker;

/** Farmland near a scarecrow takes normal fall damage but is never trampled back to dirt. */
@Mixin(FarmBlock.class)
public abstract class FarmBlockMixin {

    @Inject(method = "fallOn", at = @At("HEAD"), cancellable = true)
    private void sproutAndSoil$protectFarmland(Level level, BlockState state, BlockPos pos, Entity entity, float fallDistance,
                                               CallbackInfo ci) {
        if (!level.isClientSide() && ScarecrowTracker.protects(level, pos)) {
            entity.causeFallDamage(fallDistance, 1.0F, entity.damageSources().fall());
            ci.cancel();
        }
    }
}
