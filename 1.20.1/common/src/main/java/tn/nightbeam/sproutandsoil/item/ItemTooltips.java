package tn.nightbeam.sproutandsoil.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import tn.nightbeam.sproutandsoil.content.ContentManifest;

import java.util.List;

public final class ItemTooltips {
    private ItemTooltips() {
    }

    /** Effect lines for foods plus an optional {@code item.<id>.desc} hint line. */
    public static void append(Item item, ContentManifest.ItemEntry entry, List<Component> tooltip) {
        if (entry.food() != null && !entry.food().effects().isEmpty()) {
            FoodEffects.appendTooltip(entry.food().effects(), tooltip);
        }
        if (entry.tooltip()) {
            description(item, tooltip);
        }
    }

    public static void description(Item item, List<Component> tooltip) {
        tooltip.add(Component.translatable(item.getDescriptionId() + ".desc").withStyle(ChatFormatting.GRAY));
    }
}
