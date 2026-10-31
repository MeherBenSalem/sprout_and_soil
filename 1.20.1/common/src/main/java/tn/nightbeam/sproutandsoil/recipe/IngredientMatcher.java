package tn.nightbeam.sproutandsoil.recipe;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;

import java.util.List;

/** Shapeless matching: every ingredient must claim a distinct stack (small backtracking search). */
public final class IngredientMatcher {
    private IngredientMatcher() {
    }

    public static boolean matches(List<ItemStack> stacks, List<Ingredient> ingredients) {
        if (stacks.size() != ingredients.size()) {
            return false;
        }
        return assign(0, stacks, ingredients, new boolean[stacks.size()]);
    }

    private static boolean assign(int index, List<ItemStack> stacks, List<Ingredient> ingredients, boolean[] used) {
        if (index == ingredients.size()) {
            return true;
        }
        Ingredient ingredient = ingredients.get(index);
        for (int i = 0; i < stacks.size(); i++) {
            if (!used[i] && ingredient.test(stacks.get(i))) {
                used[i] = true;
                if (assign(index + 1, stacks, ingredients, used)) {
                    return true;
                }
                used[i] = false;
            }
        }
        return false;
    }
}
