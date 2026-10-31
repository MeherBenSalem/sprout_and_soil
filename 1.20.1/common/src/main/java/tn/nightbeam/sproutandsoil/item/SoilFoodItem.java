package tn.nightbeam.sproutandsoil.item;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;
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
        return finishEating(entry, super.finishUsingItem(stack, level, entity), level, entity);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        ItemTooltips.append(this, entry, tooltip);
    }

    /** Applies the manifest's food effects and hands back the serving container (bowl, plate, mug, bottle). */
    static ItemStack finishEating(ContentManifest.ItemEntry entry, ItemStack result, Level level, LivingEntity entity) {
        if (entry.food() == null) {
            return result;
        }
        if (!level.isClientSide()) {
            FoodEffects.apply(entity, entry.food().effects());
        }
        if (entry.container() == null || (entity instanceof Player player && player.getAbilities().instabuild)) {
            return result;
        }
        ItemStack container = new ItemStack(BuiltInRegistries.ITEM.get(entry.container()));
        if (result.isEmpty()) {
            return container;
        }
        if (entity instanceof Player player && !player.getInventory().add(container)) {
            player.drop(container, false);
        }
        return result;
    }
}
