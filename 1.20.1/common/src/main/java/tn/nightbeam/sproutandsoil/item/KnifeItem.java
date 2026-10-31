package tn.nightbeam.sproutandsoil.item;

import com.google.common.collect.ImmutableMultimap;
import com.google.common.collect.Multimap;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TieredItem;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentCategory;

/** Light, fast blade used on the cutting board; also a decent backup weapon. */
public class KnifeItem extends TieredItem {
    private final Multimap<Attribute, AttributeModifier> attributes;

    public KnifeItem(Tier tier, Properties properties) {
        super(tier, properties);
        this.attributes = ImmutableMultimap.<Attribute, AttributeModifier>builder()
                .put(Attributes.ATTACK_DAMAGE, new AttributeModifier(BASE_ATTACK_DAMAGE_UUID, "Weapon modifier",
                        0.5F + tier.getAttackDamageBonus(), AttributeModifier.Operation.ADDITION))
                .put(Attributes.ATTACK_SPEED, new AttributeModifier(BASE_ATTACK_SPEED_UUID, "Weapon modifier", -2.0F,
                        AttributeModifier.Operation.ADDITION))
                .build();
    }

    @Override
    public Multimap<Attribute, AttributeModifier> getDefaultAttributeModifiers(EquipmentSlot slot) {
        return slot == EquipmentSlot.MAINHAND ? attributes : super.getDefaultAttributeModifiers(slot);
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        stack.hurtAndBreak(1, attacker, entity -> entity.broadcastBreakEvent(EquipmentSlot.MAINHAND));
        return true;
    }

    /** Knives take weapon enchantments (Sharpness, Looting...) as well as Unbreaking and Mending. */
    public static boolean acceptsEnchantment(Item item, EnchantmentCategory category) {
        return item instanceof KnifeItem && category == EnchantmentCategory.WEAPON;
    }

    /** Forge hook (IForgeItem); on Fabric the same rule is applied by a mixin. */
    public boolean canApplyAtEnchantingTable(ItemStack stack, Enchantment enchantment) {
        return acceptsEnchantment(this, enchantment.category) || enchantment.category.canEnchant(stack.getItem());
    }
}
