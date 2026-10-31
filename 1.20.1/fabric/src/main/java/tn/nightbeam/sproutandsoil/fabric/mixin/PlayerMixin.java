package tn.nightbeam.sproutandsoil.fabric.mixin;

import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import tn.nightbeam.sproutandsoil.registry.ModEffects;

/** Caffeinated mines faster (1.20.1 has no block break speed attribute; Forge uses the BreakSpeed event). */
@Mixin(Player.class)
public abstract class PlayerMixin {

    @Inject(method = "getDestroySpeed", at = @At("RETURN"), cancellable = true)
    private void sproutAndSoil$caffeine(BlockState state, CallbackInfoReturnable<Float> cir) {
        cir.setReturnValue(ModEffects.breakSpeed((Player) (Object) this, cir.getReturnValueF()));
    }
}
