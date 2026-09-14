package tn.nightbeam.sproutandsoil.item;

import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;

public class TomatoItem extends Item {
    public TomatoItem() {
        super(new Item.Properties().stacksTo(64).rarity(Rarity.COMMON)
                .food(new FoodProperties.Builder().nutrition(4).saturationMod(0.5f).build()));
    }
}
