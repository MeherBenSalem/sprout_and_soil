package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.platform.Services;
import tn.nightbeam.sproutandsoil.recipe.CookingPotRecipe;
import tn.nightbeam.sproutandsoil.recipe.CuttingBoardRecipe;
import tn.nightbeam.sproutandsoil.recipe.ToolShapelessRecipe;

public final class ModRecipes {
    public static RegistryEntry<RecipeType<CookingPotRecipe>> COOKING_TYPE;
    public static RegistryEntry<RecipeType<CuttingBoardRecipe>> CUTTING_TYPE;
    public static RegistryEntry<RecipeSerializer<CookingPotRecipe>> COOKING_SERIALIZER;
    public static RegistryEntry<RecipeSerializer<CuttingBoardRecipe>> CUTTING_SERIALIZER;
    public static RegistryEntry<RecipeSerializer<ToolShapelessRecipe>> TOOL_SHAPELESS_SERIALIZER;

    private ModRecipes() {
    }

    public static void init() {
        COOKING_TYPE = type("cooking");
        CUTTING_TYPE = type("cutting");
        COOKING_SERIALIZER = Services.REGISTRAR.register(Registries.RECIPE_SERIALIZER, "cooking", CookingPotRecipe.Serializer::new);
        CUTTING_SERIALIZER = Services.REGISTRAR.register(Registries.RECIPE_SERIALIZER, "cutting", CuttingBoardRecipe.Serializer::new);
        TOOL_SHAPELESS_SERIALIZER = Services.REGISTRAR.register(Registries.RECIPE_SERIALIZER, "tool_shapeless",
                ToolShapelessRecipe.Serializer::new);
    }

    private static <T extends Recipe<?>> RegistryEntry<RecipeType<T>> type(String name) {
        String id = SproutAndSoil.id(name).toString();
        return Services.REGISTRAR.register(Registries.RECIPE_TYPE, name, () -> new RecipeType<T>() {
            @Override
            public String toString() {
                return id;
            }
        });
    }
}
