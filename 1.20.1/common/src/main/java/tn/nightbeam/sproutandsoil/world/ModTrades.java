package tn.nightbeam.sproutandsoil.world;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.npc.VillagerTrades;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.MerchantOffer;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.content.ContentManifest;
import tn.nightbeam.sproutandsoil.registry.ModItems;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

/**
 * Farmers trade seeds, produce and simple meals; wandering traders bring fruit saplings and rare seeds.
 * Each listing picks a random entry from its pool when a villager unlocks it, so every farmer differs.
 */
public final class ModTrades {
    private ModTrades() {
    }

    public static Map<Integer, List<VillagerTrades.ItemListing>> farmer() {
        ContentManifest.TradePools pools = Content.manifest().trades();
        return Map.of(
                1, List.of(sell(pools.seeds(), 1, 4, 16, 1), buy(pools.produce(), 18, 16, 2)),
                2, List.of(buy(pools.produce(), 16, 16, 5), sell(pools.fruits(), 1, 5, 12, 5)),
                3, List.of(buy(pools.fruits(), 12, 16, 10), fixed(() -> new ItemStack(ModItems.FERTILIZER.get(), 4), 2, 12, 10)),
                4, List.of(sell(pools.meals(), 3, 1, 12, 15), fixed(() -> new ItemStack(ModItems.WATERING_CAN.get()), 6, 3, 15)),
                5, List.of(sell(pools.meals(), 4, 2, 12, 30)));
    }

    public static List<VillagerTrades.ItemListing> wandererGeneric() {
        ContentManifest.TradePools pools = Content.manifest().trades();
        List<VillagerTrades.ItemListing> out = new ArrayList<>();
        out.add(sell(pools.saplings(), 5, 1, 8, 1));
        out.add(sell(pools.saplings(), 5, 1, 8, 1));
        out.add(sell(pools.seeds(), 1, 3, 12, 1));
        return out;
    }

    public static List<VillagerTrades.ItemListing> wandererRare() {
        ContentManifest.TradePools pools = Content.manifest().trades();
        return List.of(sell(pools.saplings(), 3, 2, 6, 1));
    }

    /** Emeralds -> a random item from the pool. */
    private static VillagerTrades.ItemListing sell(List<ResourceLocation> pool, int emeralds, int count, int maxUses, int xp) {
        return (trader, random) -> {
            Item item = pick(pool, random);
            return item == Items.AIR ? null
                    : new MerchantOffer(new ItemStack(Items.EMERALD, emeralds), new ItemStack(item, count), maxUses, xp, 0.05F);
        };
    }

    /** A random item from the pool -> one emerald. */
    private static VillagerTrades.ItemListing buy(List<ResourceLocation> pool, int count, int maxUses, int xp) {
        return (trader, random) -> {
            Item item = pick(pool, random);
            return item == Items.AIR ? null
                    : new MerchantOffer(new ItemStack(item, count), new ItemStack(Items.EMERALD), maxUses, xp, 0.05F);
        };
    }

    private static VillagerTrades.ItemListing fixed(Supplier<ItemStack> result, int emeralds, int maxUses, int xp) {
        return (trader, random) -> new MerchantOffer(new ItemStack(Items.EMERALD, emeralds), result.get(), maxUses, xp, 0.05F);
    }

    private static Item pick(List<ResourceLocation> pool, RandomSource random) {
        return pool.isEmpty() ? Items.AIR : BuiltInRegistries.ITEM.get(pool.get(random.nextInt(pool.size())));
    }
}
