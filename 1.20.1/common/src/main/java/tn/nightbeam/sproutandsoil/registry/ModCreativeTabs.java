package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.platform.Services;

import java.util.List;

/** Two tabs, "Farm" and "Kitchen", in the order the content spec lists items. */
public final class ModCreativeTabs {
    public static RegistryEntry<CreativeModeTab> FARM;
    public static RegistryEntry<CreativeModeTab> KITCHEN;

    private ModCreativeTabs() {
    }

    public static void init() {
        FARM = tab("farm", "tomato");
        KITCHEN = tab("kitchen", "cooking_pot");
    }

    private static RegistryEntry<CreativeModeTab> tab(String name, String icon) {
        return Services.REGISTRAR.register(Registries.CREATIVE_MODE_TAB, name, () -> Services.PLATFORM.creativeTabBuilder()
                .title(Component.translatable("itemGroup.sprout_and_soil." + name))
                .icon(() -> new ItemStack(ModItems.get(icon)))
                .displayItems((parameters, output) -> {
                    List<ResourceLocation> ids = Content.manifest().tabs().getOrDefault(name, List.of());
                    for (ResourceLocation id : ids) {
                        Item item = BuiltInRegistries.ITEM.get(id);
                        if (item != Items.AIR) {
                            output.accept(item);
                        }
                    }
                })
                .build());
    }
}
