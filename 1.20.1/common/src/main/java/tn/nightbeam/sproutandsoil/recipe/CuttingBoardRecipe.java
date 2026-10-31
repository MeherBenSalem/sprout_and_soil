package tn.nightbeam.sproutandsoil.recipe;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import net.minecraft.core.NonNullList;
import net.minecraft.core.RegistryAccess;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraft.util.RandomSource;
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

/** One ingredient on the cutting board, processed with a tool (usually a knife) into one or more results. */
public class CuttingBoardRecipe implements Recipe<Container> {
    private static final int MAX_RESULTS = 4;

    private final ResourceLocation id;
    private final String group;
    private final Ingredient input;
    private final Ingredient tool;
    private final List<ChanceResult> results;

    public CuttingBoardRecipe(ResourceLocation id, String group, Ingredient input, Ingredient tool, List<ChanceResult> results) {
        this.id = id;
        this.group = group;
        this.input = input;
        this.tool = tool;
        this.results = List.copyOf(results);
    }

    @Override
    public boolean matches(Container container, Level level) {
        return input.test(container.getItem(0));
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
    public ItemStack assemble(Container container, RegistryAccess registries) {
        return results.isEmpty() ? ItemStack.EMPTY : results.get(0).stack().copy();
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return true;
    }

    @Override
    public ItemStack getResultItem(RegistryAccess registries) {
        return results.isEmpty() ? ItemStack.EMPTY : results.get(0).stack();
    }

    @Override
    public ResourceLocation getId() {
        return id;
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
        public ItemStack roll(RandomSource random) {
            return chance >= 1.0F || random.nextFloat() < chance ? stack.copy() : ItemStack.EMPTY;
        }

        static ChanceResult fromJson(JsonElement element) {
            JsonObject json = GsonHelper.convertToJsonObject(element, "result");
            float chance = GsonHelper.getAsFloat(json, "chance", 1.0F);
            if (chance < 0.0F || chance > 1.0F) {
                throw new JsonParseException("Cutting result chance must be between 0 and 1");
            }
            return new ChanceResult(ShapedRecipe.itemStackFromJson(GsonHelper.getAsJsonObject(json, "item")), chance);
        }
    }

    public static class Serializer implements RecipeSerializer<CuttingBoardRecipe> {

        @Override
        public CuttingBoardRecipe fromJson(ResourceLocation id, JsonObject json) {
            JsonArray array = GsonHelper.getAsJsonArray(json, "results");
            if (array.isEmpty() || array.size() > MAX_RESULTS) {
                throw new JsonParseException("Cutting board recipes need 1-" + MAX_RESULTS + " results");
            }
            List<ChanceResult> results = new ArrayList<>(array.size());
            array.forEach(element -> results.add(ChanceResult.fromJson(element)));
            return new CuttingBoardRecipe(id, GsonHelper.getAsString(json, "group", ""),
                    Ingredient.fromJson(json.get("ingredient"), false), Ingredient.fromJson(json.get("tool"), false), results);
        }

        @Override
        public CuttingBoardRecipe fromNetwork(ResourceLocation id, FriendlyByteBuf buf) {
            String group = buf.readUtf();
            Ingredient input = Ingredient.fromNetwork(buf);
            Ingredient tool = Ingredient.fromNetwork(buf);
            List<ChanceResult> results = buf.readList(b -> new ChanceResult(b.readItem(), b.readFloat()));
            return new CuttingBoardRecipe(id, group, input, tool, results);
        }

        @Override
        public void toNetwork(FriendlyByteBuf buf, CuttingBoardRecipe recipe) {
            buf.writeUtf(recipe.group);
            recipe.input.toNetwork(buf);
            recipe.tool.toNetwork(buf);
            buf.writeCollection(recipe.results, (b, result) -> {
                b.writeItem(result.stack());
                b.writeFloat(result.chance());
            });
        }
    }
}
