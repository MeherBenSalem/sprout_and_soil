package tn.nightbeam.sproutandsoil.item;

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TieredItem;

/** Light, fast blade used on the cutting board; also a decent backup weapon. */
public class KnifeItem extends TieredItem {

    public KnifeItem(Tier tier, Properties properties) {
        super(tier, properties.attributes(DiggerItem.createAttributes(tier, 0.5F, -2.0F)));
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        return true;
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        stack.hurtAndBreak(1, attacker, EquipmentSlot.MAINHAND);
    }
}
