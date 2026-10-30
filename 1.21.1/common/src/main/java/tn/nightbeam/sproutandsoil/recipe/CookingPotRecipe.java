package tn.nightbeam.sproutandsoil.recipe;

import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import tn.nightbeam.sproutandsoil.registry.ModItems;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Up to six shapeless ingredients cooked over heat, optionally served into a container
 * (bowl, plate, mug, bottle) that must sit in the pot's container slot.
 */
public class CookingPotRecipe implements Recipe<CookingPotInput> {
    public static final int MAX_INGREDIENTS = 6;
    public static final int DEFAULT_COOKING_TIME = 200;

    private final String group;
    private final NonNullList<Ingredient> ingredients;
    private final Ingredient container;
    private final ItemStack result;
    private final float experience;
    private final int cookingTime;

    public CookingPotRecipe(String group, NonNullList<Ingredient> ingredients, Ingredient container, ItemStack result,
                            float experience, int cookingTime) {
        this.group = group;
        this.ingredients = ingredients;
        this.container = container;
        this.result = result;
        this.experience = experience;
        this.cookingTime = cookingTime;
    }

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
    public ItemStack assemble(CookingPotInput input, HolderLookup.Provider registries) {
        return result.copy();
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return width * height >= ingredients.size();
    }

    @Override
    public ItemStack getResultItem(HolderLookup.Provider registries) {
        return result;
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
        private static final MapCodec<CookingPotRecipe> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
                Codec.STRING.optionalFieldOf("group", "").forGetter(r -> r.group),
                Ingredient.CODEC_NONEMPTY.listOf().fieldOf("ingredients").flatXmap(list -> {
                    if (list.isEmpty()) {
                        return DataResult.error(() -> "No ingredients for cooking pot recipe");
                    }
                    if (list.size() > MAX_INGREDIENTS) {
                        return DataResult.error(() -> "Too many ingredients for cooking pot recipe, max " + MAX_INGREDIENTS);
                    }
                    return DataResult.success(NonNullList.of(Ingredient.EMPTY, list.toArray(Ingredient[]::new)));
                }, DataResult::success).forGetter(r -> r.ingredients),
                Ingredient.CODEC_NONEMPTY.optionalFieldOf("container")
                        .forGetter(r -> r.container.isEmpty() ? Optional.empty() : Optional.of(r.container)),
                ItemStack.STRICT_CODEC.fieldOf("result").forGetter(r -> r.result),
                Codec.FLOAT.optionalFieldOf("experience", 0.0F).forGetter(r -> r.experience),
                Codec.INT.optionalFieldOf("cookingtime", DEFAULT_COOKING_TIME).forGetter(r -> r.cookingTime)
        ).apply(i, (group, ingredients, container, result, xp, time) ->
                new CookingPotRecipe(group, ingredients, container.orElse(Ingredient.EMPTY), result, xp, time)));

        private static final StreamCodec<RegistryFriendlyByteBuf, CookingPotRecipe> STREAM_CODEC =
                StreamCodec.of(Serializer::toNetwork, Serializer::fromNetwork);

        @Override
        public MapCodec<CookingPotRecipe> codec() {
            return CODEC;
        }

        @Override
        public StreamCodec<RegistryFriendlyByteBuf, CookingPotRecipe> streamCodec() {
            return STREAM_CODEC;
        }

        private static CookingPotRecipe fromNetwork(RegistryFriendlyByteBuf buf) {
            String group = buf.readUtf();
            int count = buf.readVarInt();
            NonNullList<Ingredient> ingredients = NonNullList.withSize(count, Ingredient.EMPTY);
            ingredients.replaceAll(ignored -> Ingredient.CONTENTS_STREAM_CODEC.decode(buf));
            Ingredient container = Ingredient.CONTENTS_STREAM_CODEC.decode(buf);
            ItemStack result = ItemStack.STREAM_CODEC.decode(buf);
            return new CookingPotRecipe(group, ingredients, container, result, buf.readFloat(), buf.readVarInt());
        }

        private static void toNetwork(RegistryFriendlyByteBuf buf, CookingPotRecipe recipe) {
            buf.writeUtf(recipe.group);
            buf.writeVarInt(recipe.ingredients.size());
            for (Ingredient ingredient : recipe.ingredients) {
                Ingredient.CONTENTS_STREAM_CODEC.encode(buf, ingredient);
            }
            Ingredient.CONTENTS_STREAM_CODEC.encode(buf, recipe.container);
            ItemStack.STREAM_CODEC.encode(buf, recipe.result);
            buf.writeFloat(recipe.experience);
            buf.writeVarInt(recipe.cookingTime);
        }
    }
}
