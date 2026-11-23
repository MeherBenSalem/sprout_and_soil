package tn.nightbeam.sproutandsoil.recipe;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.PlacementInfo;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeBookCategories;
import net.minecraft.world.item.crafting.RecipeBookCategory;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.item.crafting.SingleRecipeInput;
import net.minecraft.world.level.Level;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;

import java.util.ArrayList;
import java.util.List;

/** One ingredient on the cutting board, processed with a tool (usually a knife) into one or more results. */
public record CuttingBoardRecipe(String group, Ingredient input, Ingredient tool, List<ChanceResult> results)
        implements Recipe<SingleRecipeInput> {

    public static final MapCodec<CuttingBoardRecipe> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            Codec.STRING.optionalFieldOf("group", "").forGetter(CuttingBoardRecipe::group),
            Ingredient.CODEC.fieldOf("ingredient").forGetter(CuttingBoardRecipe::input),
            Ingredient.CODEC.fieldOf("tool").forGetter(CuttingBoardRecipe::tool),
            ChanceResult.CODEC.listOf(1, 4).fieldOf("results").forGetter(CuttingBoardRecipe::results)
    ).apply(i, CuttingBoardRecipe::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, CuttingBoardRecipe> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.STRING_UTF8, CuttingBoardRecipe::group,
            Ingredient.CONTENTS_STREAM_CODEC, CuttingBoardRecipe::input,
            Ingredient.CONTENTS_STREAM_CODEC, CuttingBoardRecipe::tool,
            ChanceResult.STREAM_CODEC.apply(ByteBufCodecs.list(4)), CuttingBoardRecipe::results,
            CuttingBoardRecipe::new);

    @Override
    public boolean matches(SingleRecipeInput input, Level level) {
        return this.input.test(input.item());
    }

    public boolean isTool(ItemStack stack) {
        return tool.test(stack);
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
    public ItemStack assemble(SingleRecipeInput input) {
        return results.isEmpty() ? ItemStack.EMPTY : results.getFirst().item().create();
    }

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
    public RecipeSerializer<CuttingBoardRecipe> getSerializer() {
        return ModRecipes.CUTTING_SERIALIZER.get();
    }

    @Override
    public RecipeType<CuttingBoardRecipe> getType() {
        return ModRecipes.CUTTING_TYPE.get();
    }

    public static RecipeSerializer<CuttingBoardRecipe> serializer() {
        return new RecipeSerializer<>(CODEC, STREAM_CODEC);
    }

    public record ChanceResult(ItemStackTemplate item, float chance) {
        public static final Codec<ChanceResult> CODEC = RecordCodecBuilder.create(i -> i.group(
                ItemStackTemplate.CODEC.fieldOf("item").forGetter(ChanceResult::item),
                Codec.floatRange(0.0F, 1.0F).optionalFieldOf("chance", 1.0F).forGetter(ChanceResult::chance)
        ).apply(i, ChanceResult::new));
        public static final StreamCodec<RegistryFriendlyByteBuf, ChanceResult> STREAM_CODEC = StreamCodec.composite(
                ItemStackTemplate.STREAM_CODEC, ChanceResult::item,
                ByteBufCodecs.FLOAT, ChanceResult::chance,
                ChanceResult::new);

        public ItemStack roll(RandomSource random) {
            return chance >= 1.0F || random.nextFloat() < chance ? item.create() : ItemStack.EMPTY;
        }
    }
}
