package tn.nightbeam.sproutandsoil.recipe;

import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/** The six ingredient slots of a cooking pot, as a container view over the pot's own stacks. */
public class CookingPotInput extends SimpleContainer {

    public CookingPotInput(List<ItemStack> items) {
        super(items.toArray(ItemStack[]::new));
    }

    public List<ItemStack> items() {
        List<ItemStack> out = new ArrayList<>(getContainerSize());
        for (int i = 0; i < getContainerSize(); i++) {
            out.add(getItem(i));
        }
        return out;
    }
}
