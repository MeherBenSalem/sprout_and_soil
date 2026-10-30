package tn.nightbeam.sproutandsoil.compat.jei;

import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.registration.IGuiHandlerRegistration;
import mezz.jei.api.registration.IRecipeCatalystRegistration;
import mezz.jei.api.registration.IRecipeCategoryRegistration;
import mezz.jei.api.registration.IRecipeRegistration;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeManager;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.client.CookingPotScreen;
import tn.nightbeam.sproutandsoil.recipe.CookingPotRecipe;
import tn.nightbeam.sproutandsoil.recipe.CuttingBoardRecipe;
import tn.nightbeam.sproutandsoil.registry.ModItems;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;

@JeiPlugin
public class SproutAndSoilJeiPlugin implements IModPlugin {
    public static final RecipeType<RecipeHolder<CookingPotRecipe>> COOKING =
            RecipeType.createRecipeHolderType(SproutAndSoil.id("cooking"));
    public static final RecipeType<RecipeHolder<CuttingBoardRecipe>> CUTTING =
            RecipeType.createRecipeHolderType(SproutAndSoil.id("cutting"));

    @Override
    public ResourceLocation getPluginUid() {
        return SproutAndSoil.id("jei_plugin");
    }

    @Override
    public void registerCategories(IRecipeCategoryRegistration registration) {
        IGuiHelper gui = registration.getJeiHelpers().getGuiHelper();
        registration.addRecipeCategories(new CookingPotCategory(gui), new CuttingBoardCategory(gui));
    }

    @Override
    public void registerRecipes(IRecipeRegistration registration) {
        if (Minecraft.getInstance().level == null) {
            return;
        }
        RecipeManager recipes = Minecraft.getInstance().level.getRecipeManager();
        registration.addRecipes(COOKING, recipes.getAllRecipesFor(ModRecipes.COOKING_TYPE.get()));
        registration.addRecipes(CUTTING, recipes.getAllRecipesFor(ModRecipes.CUTTING_TYPE.get()));
    }

    @Override
    public void registerRecipeCatalysts(IRecipeCatalystRegistration registration) {
        registration.addRecipeCatalyst(ModItems.COOKING_POT.get(), COOKING);
        registration.addRecipeCatalyst(ModItems.CUTTING_BOARD.get(), CUTTING);
    }

    @Override
    public void registerGuiHandlers(IGuiHandlerRegistration registration) {
        registration.addRecipeClickArea(CookingPotScreen.class, CookingPotScreen.ARROW_X, CookingPotScreen.ARROW_Y, 24, 17, COOKING);
    }
}
