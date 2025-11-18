/*
*	MCreator note: This file will be REGENERATED on each build.
*/
package tn.nightbeam.sproutandsoil.init;

import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.event.village.VillagerTradesEvent;
import net.minecraftforge.common.BasicItemListing;

import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.npc.VillagerProfession;

@Mod.EventBusSubscriber(bus = Mod.EventBusSubscriber.Bus.FORGE)
public class SproutAndSoilModTrades {
	@SubscribeEvent
	public static void registerTrades(VillagerTradesEvent event) {
		if (event.getType() == VillagerProfession.FARMER) {
			event.getTrades().get(1).add(new BasicItemListing(new ItemStack(Items.WHEAT, 8),

					new ItemStack(SproutAndSoilModItems.TOMATO_SEEDS.get()), 10, 5, 0.05f));
			event.getTrades().get(2).add(new BasicItemListing(new ItemStack(SproutAndSoilModItems.TOMATO.get(), 8),

					new ItemStack(SproutAndSoilModItems.GARLIC.get()), 10, 5, 0.05f));
			event.getTrades().get(3).add(new BasicItemListing(new ItemStack(SproutAndSoilModItems.GARLIC.get(), 8),

					new ItemStack(SproutAndSoilModItems.LETUCE.get()), 10, 5, 0.05f));
		}
	}
}