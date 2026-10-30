package tn.nightbeam.sproutandsoil.compat.jei;

import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.gui.widgets.IRecipeExtrasBuilder;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.recipe.category.IRecipeCategory;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeHolder;
import tn.nightbeam.sproutandsoil.client.CookingPotScreen;
import tn.nightbeam.sproutandsoil.recipe.CookingPotRecipe;
import tn.nightbeam.sproutandsoil.registry.ModItems;

import java.util.List;

public class CookingPotCategory implements IRecipeCategory<RecipeHolder<CookingPotRecipe>> {
    private static final int WIDTH = 120;
    private static final int HEIGHT = 60;

    private final IDrawable icon;
    private final IDrawable flame;

    public CookingPotCategory(IGuiHelper gui) {
        this.icon = gui.createDrawableItemLike(ModItems.COOKING_POT.get());
        this.flame = gui.createDrawable(CookingPotScreen.TEXTURE, 176, 0, 14, 14);
    }

    @Override
    public RecipeType<RecipeHolder<CookingPotRecipe>> getRecipeType() {
        return SproutAndSoilJeiPlugin.COOKING;
    }

    @Override
    public Component getTitle() {
        return Component.translatable("block.sprout_and_soil.cooking_pot");
    }

    @Override
    public int getWidth() {
        return WIDTH;
    }

    @Override
    public int getHeight() {
        return HEIGHT;
    }

    @Override
    public IDrawable getIcon() {
        return icon;
    }

    @Override
    public void setRecipe(IRecipeLayoutBuilder builder, RecipeHolder<CookingPotRecipe> holder, IFocusGroup focuses) {
        CookingPotRecipe recipe = holder.value();
        List<Ingredient> ingredients = recipe.getIngredients();
        for (int i = 0; i < CookingPotRecipe.MAX_INGREDIENTS; i++) {
            var slot = builder.addInputSlot(1 + (i % 3) * 18, 1 + (i / 3) * 18).setStandardSlotBackground();
            if (i < ingredients.size()) {
                slot.addIngredients(ingredients.get(i));
            }
        }
        var container = builder.addInputSlot(64, 38).setStandardSlotBackground();
        if (recipe.needsContainer()) {
            container.addIngredients(recipe.getContainer());
        }
        builder.addOutputSlot(98, 10).setOutputSlotBackground().addItemStack(recipe.getResultItem(registryAccess()));
    }

    @Override
    public void createRecipeExtras(IRecipeExtrasBuilder builder, RecipeHolder<CookingPotRecipe> holder, IFocusGroup focuses) {
        builder.addAnimatedRecipeArrow(holder.value().getCookingTime()).setPosition(62, 10);
    }

    @Override
    public void draw(RecipeHolder<CookingPotRecipe> holder, IRecipeSlotsView slots, GuiGraphics graphics, double mouseX, double mouseY) {
        flame.draw(graphics, 21, 41);
        CookingPotRecipe recipe = holder.value();
        Component time = Component.translatable("gui.sprout_and_soil.jei.cooking_time", recipe.getCookingTime() / 20);
        graphics.drawString(Minecraft.getInstance().font, time, WIDTH - Minecraft.getInstance().font.width(time),
                HEIGHT - 9, 0xFF808080, false);
    }

    private static net.minecraft.core.RegistryAccess registryAccess() {
        var level = Minecraft.getInstance().level;
        return level == null ? net.minecraft.core.RegistryAccess.EMPTY : level.registryAccess();
    }
}
