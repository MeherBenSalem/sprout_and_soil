package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.inventory.MenuType;
import tn.nightbeam.sproutandsoil.menu.CookingPotMenu;
import tn.nightbeam.sproutandsoil.platform.Services;

public final class ModMenus {
    public static RegistryEntry<MenuType<CookingPotMenu>> COOKING_POT;

    private ModMenus() {
    }

    public static void init() {
        COOKING_POT = Services.REGISTRAR.register(Registries.MENU, "cooking_pot",
                () -> Services.PLATFORM.createMenuType(CookingPotMenu::new));
    }
}
