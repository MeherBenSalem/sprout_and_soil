package tn.nightbeam.sproutandsoil.block.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.WorldlyContainer;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import tn.nightbeam.sproutandsoil.farming.HeatSources;
import tn.nightbeam.sproutandsoil.menu.CookingPotMenu;
import tn.nightbeam.sproutandsoil.recipe.CookingPotInput;
import tn.nightbeam.sproutandsoil.recipe.CookingPotRecipe;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;
import tn.nightbeam.sproutandsoil.registry.ModTags;

import java.util.Optional;

/**
 * Slots 0-5 hold ingredients, 6 the serving container and 7 the finished dish. Cooking needs heat
 * below; progress cools down slowly when heat or ingredients go away. Hoppers feed ingredients from
 * the top, containers from the sides and pull dishes (and emptied buckets/bowls) from the bottom.
 */
public class CookingPotBlockEntity extends BaseContainerBlockEntity implements WorldlyContainer {
    public static final int INGREDIENT_SLOTS = 6;
    public static final int CONTAINER_SLOT = 6;
    public static final int OUTPUT_SLOT = 7;
    public static final int SIZE = 8;
    public static final int DATA_PROGRESS = 0;
    public static final int DATA_TOTAL = 1;
    public static final int DATA_HEATED = 2;

    private static final int[] TOP_SLOTS = {0, 1, 2, 3, 4, 5};
    private static final int[] SIDE_SLOTS = {CONTAINER_SLOT};
    private static final int[] BOTTOM_SLOTS = {OUTPUT_SLOT, 0, 1, 2, 3, 4, 5};

    private NonNullList<ItemStack> items = NonNullList.withSize(SIZE, ItemStack.EMPTY);
    private int cookTime;
    private int cookTimeTotal = CookingPotRecipe.DEFAULT_COOKING_TIME;
    private boolean heated;
    private float storedExperience;
    private final RecipeManager.CachedCheck<Container, CookingPotRecipe> recipeCheck =
            RecipeManager.createCheck(ModRecipes.COOKING_TYPE.get());

    private final ContainerData data = new ContainerData() {
        @Override
        public int get(int index) {
            return switch (index) {
                case DATA_PROGRESS -> cookTime;
                case DATA_TOTAL -> cookTimeTotal;
                case DATA_HEATED -> heated ? 1 : 0;
                default -> 0;
            };
        }

        @Override
        public void set(int index, int value) {
            switch (index) {
                case DATA_PROGRESS -> cookTime = value;
                case DATA_TOTAL -> cookTimeTotal = value;
                case DATA_HEATED -> heated = value != 0;
                default -> {
                }
            }
        }

        @Override
        public int getCount() {
            return 3;
        }
    };

    public CookingPotBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.COOKING_POT.get(), pos, state);
    }

    // ------------------------------------------------------------------------------------ ticking

    public static void serverTick(Level level, BlockPos pos, BlockState state, CookingPotBlockEntity pot) {
        boolean dirty = false;
        boolean heatedNow = HeatSources.isHeated(level, pos);
        if (heatedNow != pot.heated) {
            pot.heated = heatedNow;
            dirty = true;
        }

        Optional<CookingPotRecipe> recipe = pot.heated && pot.hasIngredients()
                ? pot.recipeCheck.getRecipeFor(pot.input(), level) : Optional.empty();
        if (recipe.isPresent() && pot.canCook(recipe.get(), level)) {
            CookingPotRecipe value = recipe.get();
            pot.cookTimeTotal = value.getCookingTime();
            if (++pot.cookTime >= pot.cookTimeTotal) {
                pot.cookTime = 0;
                pot.cook(value, level, pos);
            }
            dirty = true;
        } else if (pot.cookTime > 0) {
            pot.cookTime = Math.max(0, pot.cookTime - 2);
            dirty = true;
        }

        if (dirty) {
            setChanged(level, pos, state);
        }
    }

    private boolean hasIngredients() {
        for (int i = 0; i < INGREDIENT_SLOTS; i++) {
            if (!items.get(i).isEmpty()) {
                return true;
            }
        }
        return false;
    }

    private CookingPotInput input() {
        return new CookingPotInput(items.subList(0, INGREDIENT_SLOTS));
    }

    private boolean canCook(CookingPotRecipe recipe, Level level) {
        if (recipe.needsContainer() && !recipe.getContainer().test(items.get(CONTAINER_SLOT))) {
            return false;
        }
        ItemStack result = recipe.getResultItem(level.registryAccess());
        ItemStack output = items.get(OUTPUT_SLOT);
        if (output.isEmpty()) {
            return true;
        }
        return ItemStack.isSameItemSameTags(output, result)
                && output.getCount() + result.getCount() <= output.getMaxStackSize();
    }

    private void cook(CookingPotRecipe recipe, Level level, BlockPos pos) {
        ItemStack result = recipe.assemble(input(), level.registryAccess());
        ItemStack output = items.get(OUTPUT_SLOT);
        if (output.isEmpty()) {
            items.set(OUTPUT_SLOT, result);
        } else {
            output.grow(result.getCount());
        }
        for (int i = 0; i < INGREDIENT_SLOTS; i++) {
            ItemStack stack = items.get(i);
            if (stack.isEmpty()) {
                continue;
            }
            Item remainder = stack.getItem().getCraftingRemainingItem();
            stack.shrink(1);
            if (remainder != null) {
                ItemStack leftover = new ItemStack(remainder);
                if (stack.isEmpty()) {
                    items.set(i, leftover);
                } else {
                    Vec3 spot = Vec3.atCenterOf(pos).add(0, 0.6, 0);
                    Block.popResource(level, BlockPos.containing(spot), leftover);
                }
            }
        }
        if (recipe.needsContainer()) {
            items.get(CONTAINER_SLOT).shrink(1);
        }
        storedExperience += recipe.getExperience();
        level.playSound(null, pos, SoundEvents.BREWING_STAND_BREW, SoundSource.BLOCKS, 0.5F, 1.2F + level.random.nextFloat() * 0.2F);
    }

    /** Pays out experience stored from finished dishes, furnace-style. */
    public void awardExperience(Player player) {
        if (!(player.level() instanceof ServerLevel level) || storedExperience <= 0) {
            return;
        }
        int whole = Mth.floor(storedExperience);
        float fraction = Mth.frac(storedExperience);
        if (fraction > 0 && level.random.nextFloat() < fraction) {
            whole++;
        }
        storedExperience = 0;
        ExperienceOrb.award(level, player.position(), whole);
        setChanged();
    }

    public boolean isHeated() {
        return heated;
    }

    // ------------------------------------------------------------------------------------ container

    @Override
    protected Component getDefaultName() {
        return Component.translatable("container.sprout_and_soil.cooking_pot");
    }

    @Override
    public int getContainerSize() {
        return SIZE;
    }

    @Override
    public boolean isEmpty() {
        for (ItemStack stack : items) {
            if (!stack.isEmpty()) {
                return false;
            }
        }
        return true;
    }

    @Override
    public ItemStack getItem(int slot) {
        return items.get(slot);
    }

    @Override
    public ItemStack removeItem(int slot, int amount) {
        ItemStack removed = ContainerHelper.removeItem(items, slot, amount);
        if (!removed.isEmpty()) {
            setChanged();
        }
        return removed;
    }

    @Override
    public ItemStack removeItemNoUpdate(int slot) {
        return ContainerHelper.takeItem(items, slot);
    }

    @Override
    public void setItem(int slot, ItemStack stack) {
        items.set(slot, stack);
        if (stack.getCount() > getMaxStackSize()) {
            stack.setCount(getMaxStackSize());
        }
        setChanged();
    }

    @Override
    public boolean stillValid(Player player) {
        return Container.stillValidBlockEntity(this, player);
    }

    @Override
    public void clearContent() {
        items.clear();
    }

    @Override
    protected AbstractContainerMenu createMenu(int containerId, Inventory inventory) {
        return new CookingPotMenu(containerId, inventory, this, data);
    }

    @Override
    public boolean canPlaceItem(int slot, ItemStack stack) {
        return slot != OUTPUT_SLOT;
    }

    @Override
    public int[] getSlotsForFace(Direction side) {
        return switch (side) {
            case UP -> TOP_SLOTS;
            case DOWN -> BOTTOM_SLOTS;
            default -> SIDE_SLOTS;
        };
    }

    @Override
    public boolean canPlaceItemThroughFace(int slot, ItemStack stack, @Nullable Direction side) {
        if (side == Direction.UP) {
            return slot < INGREDIENT_SLOTS;
        }
        return slot == CONTAINER_SLOT && side != Direction.DOWN && stack.is(ModTags.SERVING_CONTAINERS);
    }

    @Override
    public boolean canTakeItemThroughFace(int slot, ItemStack stack, Direction side) {
        if (side != Direction.DOWN) {
            return false;
        }
        // emptied buckets, bowls and bottles left behind by ingredients can be drained too
        return slot == OUTPUT_SLOT || stack.is(Items.BUCKET) || stack.is(ModTags.SERVING_CONTAINERS);
    }

    // ------------------------------------------------------------------------------------ persistence

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        items = NonNullList.withSize(SIZE, ItemStack.EMPTY);
        ContainerHelper.loadAllItems(tag, items);
        cookTime = tag.getInt("CookTime");
        cookTimeTotal = tag.contains("CookTimeTotal") ? tag.getInt("CookTimeTotal") : CookingPotRecipe.DEFAULT_COOKING_TIME;
        storedExperience = tag.getFloat("StoredExperience");
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        ContainerHelper.saveAllItems(tag, items);
        tag.putInt("CookTime", cookTime);
        tag.putInt("CookTimeTotal", cookTimeTotal);
        tag.putFloat("StoredExperience", storedExperience);
    }
}
