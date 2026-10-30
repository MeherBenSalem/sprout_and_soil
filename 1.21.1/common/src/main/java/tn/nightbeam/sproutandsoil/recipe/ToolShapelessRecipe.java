package tn.nightbeam.sproutandsoil.recipe;

import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.NonNullList;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingBookCategory;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.ShapelessRecipe;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;
import tn.nightbeam.sproutandsoil.registry.ModTags;

/**
 * Shapeless crafting where kitchen tools (tag {@code sprout_and_soil:crafting_tools}, e.g. the mortar
 * and pestle) stay in the grid and lose one point of durability instead of being consumed.
 */
public class ToolShapelessRecipe extends ShapelessRecipe {

    public ToolShapelessRecipe(String group, CraftingBookCategory category, ItemStack result, NonNullList<Ingredient> ingredients) {
        super(group, category, result, ingredients);
    }

    @Override
    public NonNullList<ItemStack> getRemainingItems(CraftingInput input) {
        NonNullList<ItemStack> remaining = super.getRemainingItems(input);
        for (int i = 0; i < input.size(); i++) {
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
        private static final MapCodec<ToolShapelessRecipe> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
                Codec.STRING.optionalFieldOf("group", "").forGetter(ShapelessRecipe::getGroup),
                CraftingBookCategory.CODEC.fieldOf("category").orElse(CraftingBookCategory.MISC).forGetter(ShapelessRecipe::category),
                ItemStack.STRICT_CODEC.fieldOf("result").forGetter(r -> r.getResultItem(null)),
                Ingredient.CODEC_NONEMPTY.listOf().fieldOf("ingredients").flatXmap(list -> {
                    if (list.isEmpty() || list.size() > 9) {
                        return DataResult.error(() -> "Shapeless tool recipes need 1-9 ingredients");
                    }
                    return DataResult.success(NonNullList.of(Ingredient.EMPTY, list.toArray(Ingredient[]::new)));
                }, DataResult::success).forGetter(ShapelessRecipe::getIngredients)
        ).apply(i, ToolShapelessRecipe::new));

        private static final StreamCodec<RegistryFriendlyByteBuf, ToolShapelessRecipe> STREAM_CODEC =
                StreamCodec.of(Serializer::toNetwork, Serializer::fromNetwork);

        @Override
        public MapCodec<ToolShapelessRecipe> codec() {
            return CODEC;
        }

        @Override
        public StreamCodec<RegistryFriendlyByteBuf, ToolShapelessRecipe> streamCodec() {
            return STREAM_CODEC;
        }

        private static ToolShapelessRecipe fromNetwork(RegistryFriendlyByteBuf buf) {
            String group = buf.readUtf();
            CraftingBookCategory category = buf.readEnum(CraftingBookCategory.class);
            NonNullList<Ingredient> ingredients = NonNullList.withSize(buf.readVarInt(), Ingredient.EMPTY);
            ingredients.replaceAll(ignored -> Ingredient.CONTENTS_STREAM_CODEC.decode(buf));
            return new ToolShapelessRecipe(group, category, ItemStack.STREAM_CODEC.decode(buf), ingredients);
        }

        private static void toNetwork(RegistryFriendlyByteBuf buf, ToolShapelessRecipe recipe) {
            buf.writeUtf(recipe.getGroup());
            buf.writeEnum(recipe.category());
            buf.writeVarInt(recipe.getIngredients().size());
            for (Ingredient ingredient : recipe.getIngredients()) {
                Ingredient.CONTENTS_STREAM_CODEC.encode(buf, ingredient);
            }
            ItemStack.STREAM_CODEC.encode(buf, recipe.getResultItem(null));
        }
    }
}
