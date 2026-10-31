package tn.nightbeam.sproutandsoil.recipe;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import net.minecraft.core.NonNullList;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingBookCategory;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.ShapedRecipe;
import net.minecraft.world.item.crafting.ShapelessRecipe;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;
import tn.nightbeam.sproutandsoil.registry.ModTags;

/**
 * Shapeless crafting where kitchen tools (tag {@code sprout_and_soil:crafting_tools}, e.g. the mortar
 * and pestle) stay in the grid and lose one point of durability instead of being consumed.
 */
public class ToolShapelessRecipe extends ShapelessRecipe {
    private final ItemStack result;

    public ToolShapelessRecipe(ResourceLocation id, String group, CraftingBookCategory category, ItemStack result,
                               NonNullList<Ingredient> ingredients) {
        super(id, group, category, result, ingredients);
        this.result = result;
    }

    @Override
    public NonNullList<ItemStack> getRemainingItems(CraftingContainer input) {
        NonNullList<ItemStack> remaining = super.getRemainingItems(input);
        for (int i = 0; i < input.getContainerSize(); i++) {
            ItemStack stack = input.getItem(i);
            if (stack.is(ModTags.CRAFTING_TOOLS)) {
                remaining.set(i, damaged(stack));
            }
        }
        return remaining;
    }

    private static ItemStack damaged(ItemStack tool) {
        ItemStack copy = tool.copyWithCount(1);
        if (!copy.isDamageableItem()) {
            return copy;
        }
        int damage = copy.getDamageValue() + 1;
        if (damage >= copy.getMaxDamage()) {
            return ItemStack.EMPTY;
        }
        copy.setDamageValue(damage);
        return copy;
    }

    @Override
    public RecipeSerializer<?> getSerializer() {
        return ModRecipes.TOOL_SHAPELESS_SERIALIZER.get();
    }

    public static class Serializer implements RecipeSerializer<ToolShapelessRecipe> {

        @Override
        public ToolShapelessRecipe fromJson(ResourceLocation id, JsonObject json) {
            JsonArray array = GsonHelper.getAsJsonArray(json, "ingredients");
            if (array.isEmpty() || array.size() > 9) {
                throw new JsonParseException("Shapeless tool recipes need 1-9 ingredients");
            }
            NonNullList<Ingredient> ingredients = NonNullList.withSize(array.size(), Ingredient.EMPTY);
            for (int i = 0; i < array.size(); i++) {
                ingredients.set(i, Ingredient.fromJson(array.get(i), false));
            }
            CraftingBookCategory category = CraftingBookCategory.CODEC.byName(GsonHelper.getAsString(json, "category", null),
                    CraftingBookCategory.MISC);
            ItemStack result = ShapedRecipe.itemStackFromJson(GsonHelper.getAsJsonObject(json, "result"));
            return new ToolShapelessRecipe(id, GsonHelper.getAsString(json, "group", ""), category, result, ingredients);
        }

        @Override
        public ToolShapelessRecipe fromNetwork(ResourceLocation id, FriendlyByteBuf buf) {
            String group = buf.readUtf();
            CraftingBookCategory category = buf.readEnum(CraftingBookCategory.class);
            NonNullList<Ingredient> ingredients = NonNullList.withSize(buf.readVarInt(), Ingredient.EMPTY);
            ingredients.replaceAll(ignored -> Ingredient.fromNetwork(buf));
            return new ToolShapelessRecipe(id, group, category, buf.readItem(), ingredients);
        }

        @Override
        public void toNetwork(FriendlyByteBuf buf, ToolShapelessRecipe recipe) {
            buf.writeUtf(recipe.getGroup());
            buf.writeEnum(recipe.category());
            buf.writeVarInt(recipe.getIngredients().size());
            for (Ingredient ingredient : recipe.getIngredients()) {
                ingredient.toNetwork(buf);
            }
            buf.writeItem(recipe.result);
        }
    }
}
