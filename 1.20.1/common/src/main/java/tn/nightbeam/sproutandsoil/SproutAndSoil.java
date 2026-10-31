package tn.nightbeam.sproutandsoil;

import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;
import tn.nightbeam.sproutandsoil.registry.ModBlocks;
import tn.nightbeam.sproutandsoil.registry.ModCreativeTabs;
import tn.nightbeam.sproutandsoil.registry.ModEffects;
import tn.nightbeam.sproutandsoil.registry.ModItems;
import tn.nightbeam.sproutandsoil.registry.ModMenus;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;

/**
 * Loader-independent entry point. Each loader calls {@link #init()} once during mod construction;
 * registration order matters on Fabric, where entries are registered immediately.
 */
public final class SproutAndSoil {
    public static final String MOD_ID = "sprout_and_soil";
    public static final Logger LOGGER = LoggerFactory.getLogger("Sprout & Soil");

    private SproutAndSoil() {
    }

    public static void init() {
        Content.load();
        ModEffects.init();
        ModBlocks.init();
        ModItems.init();
        ModBlockEntities.init();
        ModMenus.init();
        ModRecipes.init();
        ModCreativeTabs.init();
        LOGGER.info("Sprout & Soil: {} crops, {} fruit trees, {} items from the content manifest",
                Content.manifest().crops().size(), Content.manifest().trees().size(), Content.manifest().items().size());
    }

    public static ResourceLocation id(String path) {
        return new ResourceLocation(MOD_ID, path);
    }
}
