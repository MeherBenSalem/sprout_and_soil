/*
 *    MCreator note: This file will be REGENERATED on each build.
 */
package tn.nightbeam.sproutandsoil.init;

import tn.nightbeam.sproutandsoil.SproutAndSoilMod;

import net.minecraftforge.registries.RegistryObject;
import net.minecraftforge.registries.DeferredRegister;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.network.chat.Component;
import net.minecraft.core.registries.Registries;

public class SproutAndSoilModTabs {
	public static final DeferredRegister<CreativeModeTab> REGISTRY = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, SproutAndSoilMod.MODID);
	public static final RegistryObject<CreativeModeTab> SPROUT_AND_SOIL = REGISTRY.register("sprout_and_soil",
			() -> CreativeModeTab.builder().title(Component.translatable("item_group.sprout_and_soil.sprout_and_soil")).icon(() -> new ItemStack(SproutAndSoilModItems.TOMATO.get())).displayItems((parameters, tabData) -> {
				tabData.accept(SproutAndSoilModItems.TOMATO_SEEDS.get());
				tabData.accept(SproutAndSoilModItems.TOMATO.get());
				tabData.accept(SproutAndSoilModItems.GARLIC.get());
				tabData.accept(SproutAndSoilModItems.LETUCE.get());
			}).build());
}