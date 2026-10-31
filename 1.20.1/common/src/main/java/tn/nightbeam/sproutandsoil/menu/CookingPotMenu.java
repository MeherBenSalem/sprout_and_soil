package tn.nightbeam.sproutandsoil.menu;

import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import tn.nightbeam.sproutandsoil.block.entity.CookingPotBlockEntity;
import tn.nightbeam.sproutandsoil.registry.ModMenus;
import tn.nightbeam.sproutandsoil.registry.ModTags;

/** Slot layout matches textures/gui/container/cooking_pot.png (see tools/assetgen/STYLE.md). */
public class CookingPotMenu extends AbstractContainerMenu {
    public static final int[] INPUT_X = {30, 48, 66};
    public static final int[] INPUT_Y = {17, 35};
    public static final int CONTAINER_X = 92;
    public static final int CONTAINER_Y = 54;
    public static final int OUTPUT_X = 124;
    public static final int OUTPUT_Y = 30;

    private static final int PLAYER_START = CookingPotBlockEntity.SIZE;
    private static final int PLAYER_END = PLAYER_START + 36;

    private final Container pot;
    private final ContainerData data;

    public CookingPotMenu(int containerId, Inventory inventory) {
        this(containerId, inventory, new SimpleContainer(CookingPotBlockEntity.SIZE), new SimpleContainerData(3));
    }

    public CookingPotMenu(int containerId, Inventory inventory, Container pot, ContainerData data) {
        super(ModMenus.COOKING_POT.get(), containerId);
        checkContainerSize(pot, CookingPotBlockEntity.SIZE);
        checkContainerDataCount(data, 3);
        this.pot = pot;
        this.data = data;
        pot.startOpen(inventory.player);

        for (int row = 0; row < 2; row++) {
            for (int col = 0; col < 3; col++) {
                addSlot(new Slot(pot, row * 3 + col, INPUT_X[col], INPUT_Y[row]));
            }
        }
        addSlot(new Slot(pot, CookingPotBlockEntity.CONTAINER_SLOT, CONTAINER_X, CONTAINER_Y));
        addSlot(new ResultSlot(inventory.player, pot, CookingPotBlockEntity.OUTPUT_SLOT, OUTPUT_X, OUTPUT_Y));

        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 9; col++) {
                addSlot(new Slot(inventory, col + row * 9 + 9, 8 + col * 18, 84 + row * 18));
            }
        }
        for (int col = 0; col < 9; col++) {
            addSlot(new Slot(inventory, col, 8 + col * 18, 142));
        }
        addDataSlots(data);
    }

    public boolean isHeated() {
        return data.get(CookingPotBlockEntity.DATA_HEATED) != 0;
    }

    /** Arrow fill in pixels, 0..{@code width}. */
    public int progress(int width) {
        int total = data.get(CookingPotBlockEntity.DATA_TOTAL);
        int done = data.get(CookingPotBlockEntity.DATA_PROGRESS);
        return total > 0 && done > 0 ? Math.min(width, done * width / total) : 0;
    }

    @Override
    public boolean stillValid(Player player) {
        return pot.stillValid(player);
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        pot.stopOpen(player);
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        Slot slot = slots.get(index);
        if (!slot.hasItem()) {
            return ItemStack.EMPTY;
        }
        ItemStack stack = slot.getItem();
        ItemStack original = stack.copy();
        if (index == CookingPotBlockEntity.OUTPUT_SLOT) {
            if (!moveItemStackTo(stack, PLAYER_START, PLAYER_END, true)) {
                return ItemStack.EMPTY;
            }
            slot.onQuickCraft(stack, original);
        } else if (index < PLAYER_START) {
            if (!moveItemStackTo(stack, PLAYER_START, PLAYER_END, false)) {
                return ItemStack.EMPTY;
            }
        } else if (stack.is(ModTags.SERVING_CONTAINERS)) {
            if (!moveItemStackTo(stack, CookingPotBlockEntity.CONTAINER_SLOT, CookingPotBlockEntity.CONTAINER_SLOT + 1, false)
                    && !moveItemStackTo(stack, 0, CookingPotBlockEntity.INGREDIENT_SLOTS, false)) {
                return ItemStack.EMPTY;
            }
        } else if (!moveItemStackTo(stack, 0, CookingPotBlockEntity.INGREDIENT_SLOTS, false)) {
            return ItemStack.EMPTY;
        }

        if (stack.isEmpty()) {
            slot.setByPlayer(ItemStack.EMPTY);
        } else {
            slot.setChanged();
        }
        if (stack.getCount() == original.getCount()) {
            return ItemStack.EMPTY;
        }
        slot.onTake(player, stack);
        return original;
    }

    /** Output slot: take-only, pays out stored experience like a furnace. */
    private static class ResultSlot extends Slot {
        private final Player player;
        private int removeCount;

        ResultSlot(Player player, Container container, int slot, int x, int y) {
            super(container, slot, x, y);
            this.player = player;
        }

        @Override
        public boolean mayPlace(ItemStack stack) {
            return false;
        }

        @Override
        public ItemStack remove(int amount) {
            if (hasItem()) {
                removeCount += Math.min(amount, getItem().getCount());
            }
            return super.remove(amount);
        }

        @Override
        public void onTake(Player player, ItemStack stack) {
            checkTakeAchievements(stack);
            super.onTake(player, stack);
        }

        @Override
        protected void onQuickCraft(ItemStack stack, int amount) {
            removeCount += amount;
            checkTakeAchievements(stack);
        }

        @Override
        protected void checkTakeAchievements(ItemStack stack) {
            stack.onCraftedBy(player.level(), player, removeCount);
            if (container instanceof CookingPotBlockEntity pot) {
                pot.awardExperience(player);
            }
            removeCount = 0;
        }
    }
}
