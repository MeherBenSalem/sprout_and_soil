package tn.nightbeam.sproutandsoil.fabric.mixin;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentCategory;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import tn.nightbeam.sproutandsoil.item.KnifeItem;

/** Weapon enchantments (books on an anvil, commands) accept knives. */
@Mixin(Enchantment.class)
public abstract class EnchantmentMixin {
    @Shadow
    @Final
    public EnchantmentCategory category;

    @Inject(method = "canEnchant", at = @At("HEAD"), cancellable = true)
    private void sproutAndSoil$knives(ItemStack stack, CallbackInfoReturnable<Boolean> cir) {
        if (KnifeItem.acceptsEnchantment(stack.getItem(), category)) {
            cir.setReturnValue(true);
        }
    }
}
