package tn.nightbeam.sproutandsoil.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import tn.nightbeam.sproutandsoil.content.ContentManifest;

import java.util.List;

/** Manifest-driven item: food (with effects and serving container), drink, or plain ingredient. */
public class SoilFoodItem extends Item {
    private final ContentManifest.ItemEntry entry;

    public SoilFoodItem(Properties properties, ContentManifest.ItemEntry entry) {
        super(properties);
        this.entry = entry;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return entry.drink() ? UseAnim.DRINK : super.getUseAnimation(stack);
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (!level.isClientSide() && entry.food() != null) {
            FoodEffects.apply(entity, entry.food().effects());
        }
        return super.finishUsingItem(stack, level, entity);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        ItemTooltips.append(this, entry, context, tooltip);
    }
}
