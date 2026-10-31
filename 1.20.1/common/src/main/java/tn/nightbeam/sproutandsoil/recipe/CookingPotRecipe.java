package tn.nightbeam.sproutandsoil.recipe;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import net.minecraft.core.NonNullList;
import net.minecraft.core.RegistryAccess;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraft.world.Container;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.item.crafting.ShapedRecipe;
import net.minecraft.world.level.Level;
import tn.nightbeam.sproutandsoil.registry.ModItems;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;

import java.util.ArrayList;
import java.util.List;

/**
 * Up to six shapeless ingredients cooked over heat, optionally served into a container
 * (bowl, plate, mug, bottle) that must sit in the pot's container slot.
 */
public class CookingPotRecipe implements Recipe<Container> {
    public static final int MAX_INGREDIENTS = 6;
    public static final int DEFAULT_COOKING_TIME = 200;

    private final ResourceLocation id;
    private final String group;
    private final NonNullList<Ingredient> ingredients;
    private final Ingredient container;
    private final ItemStack result;
    private final float experience;
    private final int cookingTime;

    public CookingPotRecipe(ResourceLocation id, String group, NonNullList<Ingredient> ingredients, Ingredient container,
                            ItemStack result, float experience, int cookingTime) {
        this.id = id;
        this.group = group;
        this.ingredients = ingredients;
        this.container = container;
        this.result = result;
        this.experience = experience;
        this.cookingTime = cookingTime;
    }

    @Override
    public boolean matches(Container input, Level level) {
        List<ItemStack> stacks = new ArrayList<>(MAX_INGREDIENTS);
        for (int i = 0; i < Math.min(MAX_INGREDIENTS, input.getContainerSize()); i++) {
            ItemStack stack = input.getItem(i);
            if (!stack.isEmpty()) {
                stacks.add(stack);
            }
        }
        return IngredientMatcher.matches(stacks, ingredients);
    }

    @Override
    public ItemStack assemble(Container input, RegistryAccess registries) {
        return result.copy();
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return width * height >= ingredients.size();
    }

    @Override
    public ItemStack getResultItem(RegistryAccess registries) {
        return result;
    }

    @Override
    public ResourceLocation getId() {
        return id;
    }

    @Override
    public NonNullList<Ingredient> getIngredients() {
        return ingredients;
    }

    @Override
    public String getGroup() {
        return group;
    }

    /** {@link Ingredient#EMPTY} when the dish needs no container. */
    public Ingredient getContainer() {
        return container;
    }

    public boolean needsContainer() {
        return !container.isEmpty();
    }

    public float getExperience() {
        return experience;
    }

    public int getCookingTime() {
        return cookingTime;
    }

    @Override
    public ItemStack getToastSymbol() {
        return new ItemStack(ModItems.COOKING_POT.get());
    }

    /** Keeps these out of the vanilla recipe book, which has no category for them (JEI shows them instead). */
    @Override
    public boolean isSpecial() {
        return true;
    }

    @Override
    public RecipeSerializer<?> getSerializer() {
        return ModRecipes.COOKING_SERIALIZER.get();
    }

    @Override
    public RecipeType<?> getType() {
        return ModRecipes.COOKING_TYPE.get();
    }

    public static class Serializer implements RecipeSerializer<CookingPotRecipe> {

        @Override
        public CookingPotRecipe fromJson(ResourceLocation id, JsonObject json) {
            JsonArray array = GsonHelper.getAsJsonArray(json, "ingredients");
            if (array.isEmpty()) {
                throw new JsonParseException("No ingredients for cooking pot recipe");
            }
            if (array.size() > MAX_INGREDIENTS) {
                throw new JsonParseException("Too many ingredients for cooking pot recipe, max " + MAX_INGREDIENTS);
            }
            NonNullList<Ingredient> ingredients = NonNullList.withSize(array.size(), Ingredient.EMPTY);
            for (int i = 0; i < array.size(); i++) {
                ingredients.set(i, Ingredient.fromJson(array.get(i), false));
            }
            Ingredient container = json.has("container") ? Ingredient.fromJson(json.get("container"), false) : Ingredient.EMPTY;
            ItemStack result = ShapedRecipe.itemStackFromJson(GsonHelper.getAsJsonObject(json, "result"));
            return new CookingPotRecipe(id, GsonHelper.getAsString(json, "group", ""), ingredients, container, result,
                    GsonHelper.getAsFloat(json, "experience", 0.0F), GsonHelper.getAsInt(json, "cookingtime", DEFAULT_COOKING_TIME));
        }

        @Override
        public CookingPotRecipe fromNetwork(ResourceLocation id, FriendlyByteBuf buf) {
            String group = buf.readUtf();
            int count = buf.readVarInt();
            NonNullList<Ingredient> ingredients = NonNullList.withSize(count, Ingredient.EMPTY);
            ingredients.replaceAll(ignored -> Ingredient.fromNetwork(buf));
            Ingredient container = Ingredient.fromNetwork(buf);
            ItemStack result = buf.readItem();
            return new CookingPotRecipe(id, group, ingredients, container, result, buf.readFloat(), buf.readVarInt());
        }

        @Override
        public void toNetwork(FriendlyByteBuf buf, CookingPotRecipe recipe) {
            buf.writeUtf(recipe.group);
            buf.writeVarInt(recipe.ingredients.size());
            for (Ingredient ingredient : recipe.ingredients) {
                ingredient.toNetwork(buf);
            }
            recipe.container.toNetwork(buf);
            buf.writeItem(recipe.result);
            buf.writeFloat(recipe.experience);
            buf.writeVarInt(recipe.cookingTime);
        }
    }
}
