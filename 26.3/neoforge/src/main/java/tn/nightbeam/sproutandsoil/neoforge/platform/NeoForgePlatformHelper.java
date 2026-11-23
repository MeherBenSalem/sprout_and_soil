package tn.nightbeam.sproutandsoil.neoforge.platform;

import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
import tn.nightbeam.sproutandsoil.platform.services.IPlatformHelper;

import java.util.Set;

public class NeoForgePlatformHelper implements IPlatformHelper {

    @Override
    public String getPlatformName() {
        return "NeoForge";
    }

    @Override
    public boolean isModLoaded(String modId) {
        return ModList.get().isLoaded(modId);
    }

    @Override
    public boolean isDevelopmentEnvironment() {
        return !FMLEnvironment.isProduction();
    }

    @Override
    public <T extends BlockEntity> BlockEntityType<T> createBlockEntityType(BlockEntityFactory<T> factory, Block... blocks) {
        return new BlockEntityType<>(factory::create, Set.of(blocks));
    }

    @Override
    public <T extends AbstractContainerMenu> MenuType<T> createMenuType(MenuFactory<T> factory) {
        return new MenuType<>(factory::create, FeatureFlags.VANILLA_SET);
    }

    @Override
    public CreativeModeTab creativeTab(net.minecraft.network.chat.Component title, java.util.function.Supplier<net.minecraft.world.item.ItemStack> icon,
            java.util.function.Consumer<java.util.function.Consumer<net.minecraft.world.item.Item>> fill) {
        return CreativeModeTab.builder().title(title).icon(icon).displayItems((parameters, output) -> fill.accept(output::accept)).build();
    }
}
