package tn.nightbeam.sproutandsoil.fabric.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.enchantment.EnchantmentCategory;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import tn.nightbeam.sproutandsoil.item.KnifeItem;

/** The enchanting table offers weapon enchantments for knives (Forge does this through IForgeItem). */
@Mixin(EnchantmentHelper.class)
public abstract class EnchantmentHelperMixin {

    @WrapOperation(method = "getAvailableEnchantmentResults", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/item/enchantment/EnchantmentCategory;canEnchant(Lnet/minecraft/world/item/Item;)Z"))
    private static boolean sproutAndSoil$knives(EnchantmentCategory category, Item item, Operation<Boolean> original) {
        return original.call(category, item) || KnifeItem.acceptsEnchantment(item, category);
    }
}
