package tn.nightbeam.sproutandsoil.compat.jei;

import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.gui.widgets.IRecipeExtrasBuilder;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.recipe.category.IRecipeCategory;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import tn.nightbeam.sproutandsoil.recipe.CuttingBoardRecipe;
import tn.nightbeam.sproutandsoil.registry.ModItems;

import java.util.List;

public class CuttingBoardCategory implements IRecipeCategory<CuttingBoardRecipe> {
    private static final int WIDTH = 104;
    private static final int HEIGHT = 40;

    private final IDrawable icon;
    private final IDrawable board;

    public CuttingBoardCategory(IGuiHelper gui) {
        this.icon = gui.createDrawableItemLike(ModItems.CUTTING_BOARD.get());
        this.board = gui.createDrawableItemLike(ModItems.CUTTING_BOARD.get());
    }

    @Override
    public RecipeType<CuttingBoardRecipe> getRecipeType() {
        return SproutAndSoilJeiPlugin.CUTTING;
    }

    @Override
    public Component getTitle() {
        return Component.translatable("block.sprout_and_soil.cutting_board");
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
    public void setRecipe(IRecipeLayoutBuilder builder, CuttingBoardRecipe recipe, IFocusGroup focuses) {
        builder.addInputSlot(1, 1).setStandardSlotBackground().addIngredients(recipe.getTool());
        builder.addInputSlot(21, 1).setStandardSlotBackground().addIngredients(recipe.getInput());
        List<CuttingBoardRecipe.ChanceResult> results = recipe.getResults();
        for (int i = 0; i < results.size(); i++) {
            CuttingBoardRecipe.ChanceResult result = results.get(i);
            builder.addOutputSlot(68 + (i % 2) * 18, 1 + (i / 2) * 18)
                    .setOutputSlotBackground()
                    .addItemStack(result.stack())
                    .addRichTooltipCallback((view, tooltip) -> {
                        if (result.chance() < 1.0F) {
                            tooltip.add(Component.translatable("gui.sprout_and_soil.jei.chance",
                                    Math.round(result.chance() * 100)).withStyle(ChatFormatting.GOLD));
                        }
                    });
        }
    }

    @Override
    public void createRecipeExtras(IRecipeExtrasBuilder builder, CuttingBoardRecipe recipe, IFocusGroup focuses) {
        builder.addRecipeArrow().setPosition(42, 1);
    }

    @Override
    public void draw(CuttingBoardRecipe recipe, IRecipeSlotsView slots, GuiGraphics graphics, double mouseX, double mouseY) {
        board.draw(graphics, 21, 21);
    }
}
