package tn.nightbeam.sproutandsoil.recipe;

import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.PlacementInfo;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeBookCategories;
import net.minecraft.world.item.crafting.RecipeBookCategory;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Up to six shapeless ingredients cooked over heat, optionally served into a container
 * (bowl, plate, mug, bottle) that must sit in the pot's container slot.
 */
public record CookingPotRecipe(String group, List<Ingredient> ingredients, Optional<Ingredient> container, ItemStackTemplate result,
                               float experience, int cookingTime) implements Recipe<CookingPotInput> {
    public static final int MAX_INGREDIENTS = 6;
    public static final int DEFAULT_COOKING_TIME = 200;

    public static final MapCodec<CookingPotRecipe> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            Codec.STRING.optionalFieldOf("group", "").forGetter(CookingPotRecipe::group),
            Ingredient.CODEC.listOf()
                    .validate(list -> list.isEmpty() || list.size() > MAX_INGREDIENTS
                            ? DataResult.error(() -> "Cooking pot recipes need 1 to " + MAX_INGREDIENTS + " ingredients")
                            : DataResult.success(list))
                    .fieldOf("ingredients").forGetter(CookingPotRecipe::ingredients),
            Ingredient.CODEC.optionalFieldOf("container").forGetter(CookingPotRecipe::container),
            ItemStackTemplate.CODEC.fieldOf("result").forGetter(CookingPotRecipe::result),
            Codec.FLOAT.optionalFieldOf("experience", 0.0F).forGetter(CookingPotRecipe::experience),
            Codec.INT.optionalFieldOf("cookingtime", DEFAULT_COOKING_TIME).forGetter(CookingPotRecipe::cookingTime)
    ).apply(i, CookingPotRecipe::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, CookingPotRecipe> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.STRING_UTF8, CookingPotRecipe::group,
            Ingredient.CONTENTS_STREAM_CODEC.apply(ByteBufCodecs.list(MAX_INGREDIENTS)), CookingPotRecipe::ingredients,
            ByteBufCodecs.optional(Ingredient.CONTENTS_STREAM_CODEC), CookingPotRecipe::container,
            ItemStackTemplate.STREAM_CODEC, CookingPotRecipe::result,
            ByteBufCodecs.FLOAT, CookingPotRecipe::experience,
            ByteBufCodecs.VAR_INT, CookingPotRecipe::cookingTime,
            CookingPotRecipe::new);

    @Override
    public boolean matches(CookingPotInput input, Level level) {
        List<ItemStack> stacks = new ArrayList<>(MAX_INGREDIENTS);
        for (ItemStack stack : input.items()) {
            if (!stack.isEmpty()) {
                stacks.add(stack);
            }
        }
        return IngredientMatcher.matches(stacks, ingredients);
    }

    @Override
    public ItemStack assemble(CookingPotInput input) {
        return result.create();
    }

    public boolean needsContainer() {
        return container.isPresent();
    }

    /** True when the dish needs no container, or {@code stack} is the right one. */
    public boolean acceptsContainer(ItemStack stack) {
        return container.map(c -> c.test(stack)).orElse(true);
    }

    /** Cooking pot recipes have their own block, so the recipe book skips them. */
    @Override
    public boolean isSpecial() {
        return true;
    }

    @Override
    public boolean showNotification() {
        return false;
    }

    @Override
    public PlacementInfo placementInfo() {
        return PlacementInfo.NOT_PLACEABLE;
    }

    @Override
    public RecipeBookCategory recipeBookCategory() {
        return RecipeBookCategories.CRAFTING_MISC;
    }

    @Override
    public RecipeSerializer<CookingPotRecipe> getSerializer() {
        return ModRecipes.COOKING_SERIALIZER.get();
    }

    @Override
    public RecipeType<CookingPotRecipe> getType() {
        return ModRecipes.COOKING_TYPE.get();
    }

    public static RecipeSerializer<CookingPotRecipe> serializer() {
        return new RecipeSerializer<>(CODEC, STREAM_CODEC);
    }
}
