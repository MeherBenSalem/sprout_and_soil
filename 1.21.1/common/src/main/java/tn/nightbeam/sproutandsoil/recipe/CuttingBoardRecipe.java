package tn.nightbeam.sproutandsoil.recipe;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.item.crafting.SingleRecipeInput;
import net.minecraft.world.level.Level;
import tn.nightbeam.sproutandsoil.registry.ModItems;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;

import java.util.ArrayList;
import java.util.List;

/** One ingredient on the cutting board, processed with a tool (usually a knife) into one or more results. */
public class CuttingBoardRecipe implements Recipe<SingleRecipeInput> {
    private final String group;
    private final Ingredient input;
    private final Ingredient tool;
    private final List<ChanceResult> results;

    public CuttingBoardRecipe(String group, Ingredient input, Ingredient tool, List<ChanceResult> results) {
        this.group = group;
        this.input = input;
        this.tool = tool;
        this.results = List.copyOf(results);
    }

    @Override
    public boolean matches(SingleRecipeInput input, Level level) {
        return this.input.test(input.item());
    }

    public boolean isTool(ItemStack stack) {
        return tool.test(stack);
    }

    public Ingredient getInput() {
        return input;
    }

    public Ingredient getTool() {
        return tool;
    }

    public List<ChanceResult> getResults() {
        return results;
    }

    /** Rolls every result against its chance. */
    public List<ItemStack> rollResults(RandomSource random) {
        List<ItemStack> out = new ArrayList<>();
        for (ChanceResult result : results) {
            ItemStack rolled = result.roll(random);
            if (!rolled.isEmpty()) {
                out.add(rolled);
            }
        }
        return out;
    }

    @Override
    public ItemStack assemble(SingleRecipeInput input, HolderLookup.Provider registries) {
        return results.isEmpty() ? ItemStack.EMPTY : results.getFirst().stack().copy();
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return true;
    }

    @Override
    public ItemStack getResultItem(HolderLookup.Provider registries) {
        return results.isEmpty() ? ItemStack.EMPTY : results.getFirst().stack();
    }

    @Override
    public NonNullList<Ingredient> getIngredients() {
        return NonNullList.of(Ingredient.EMPTY, input);
    }

    @Override
    public String getGroup() {
        return group;
    }

    @Override
    public ItemStack getToastSymbol() {
        return new ItemStack(ModItems.CUTTING_BOARD.get());
    }

    @Override
    public boolean isSpecial() {
        return true;
    }

    @Override
    public RecipeSerializer<?> getSerializer() {
        return ModRecipes.CUTTING_SERIALIZER.get();
    }

    @Override
    public RecipeType<?> getType() {
        return ModRecipes.CUTTING_TYPE.get();
    }

    public record ChanceResult(ItemStack stack, float chance) {
        public static final Codec<ChanceResult> CODEC = RecordCodecBuilder.create(i -> i.group(
                ItemStack.STRICT_CODEC.fieldOf("item").forGetter(ChanceResult::stack),
                Codec.floatRange(0.0F, 1.0F).optionalFieldOf("chance", 1.0F).forGetter(ChanceResult::chance)
        ).apply(i, ChanceResult::new));
        public static final StreamCodec<RegistryFriendlyByteBuf, ChanceResult> STREAM_CODEC = StreamCodec.composite(
                ItemStack.STREAM_CODEC, ChanceResult::stack,
                ByteBufCodecs.FLOAT, ChanceResult::chance,
                ChanceResult::new);

        public ItemStack roll(RandomSource random) {
            return chance >= 1.0F || random.nextFloat() < chance ? stack.copy() : ItemStack.EMPTY;
        }
    }

    public static class Serializer implements RecipeSerializer<CuttingBoardRecipe> {
        private static final MapCodec<CuttingBoardRecipe> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
                Codec.STRING.optionalFieldOf("group", "").forGetter(r -> r.group),
                Ingredient.CODEC_NONEMPTY.fieldOf("ingredient").forGetter(r -> r.input),
                Ingredient.CODEC_NONEMPTY.fieldOf("tool").forGetter(r -> r.tool),
                ChanceResult.CODEC.listOf(1, 4).fieldOf("results").forGetter(r -> r.results)
        ).apply(i, CuttingBoardRecipe::new));

        private static final StreamCodec<RegistryFriendlyByteBuf, CuttingBoardRecipe> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.STRING_UTF8, r -> r.group,
                Ingredient.CONTENTS_STREAM_CODEC, r -> r.input,
                Ingredient.CONTENTS_STREAM_CODEC, r -> r.tool,
                ChanceResult.STREAM_CODEC.apply(ByteBufCodecs.list()), r -> r.results,
                CuttingBoardRecipe::new);

        @Override
        public MapCodec<CuttingBoardRecipe> codec() {
            return CODEC;
        }

        @Override
        public StreamCodec<RegistryFriendlyByteBuf, CuttingBoardRecipe> streamCodec() {
            return STREAM_CODEC;
        }
    }
}
