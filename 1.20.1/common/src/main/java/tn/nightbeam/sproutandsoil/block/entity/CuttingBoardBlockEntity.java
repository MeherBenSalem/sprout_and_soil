package tn.nightbeam.sproutandsoil.block.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import tn.nightbeam.sproutandsoil.recipe.CuttingBoardRecipe;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;
import tn.nightbeam.sproutandsoil.registry.ModRecipes;

import java.util.Optional;

/** Holds the single ingredient lying on a cutting board. */
public class CuttingBoardBlockEntity extends BlockEntity {
    private ItemStack item = ItemStack.EMPTY;
    private final RecipeManager.CachedCheck<Container, CuttingBoardRecipe> recipeCheck =
            RecipeManager.createCheck(ModRecipes.CUTTING_TYPE.get());

    public CuttingBoardBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.CUTTING_BOARD.get(), pos, state);
    }

    public ItemStack getItem() {
        return item;
    }

    public boolean isEmpty() {
        return item.isEmpty();
    }

    /** Puts one item from {@code stack} on the board. */
    public boolean place(ItemStack stack, Player player) {
        if (!item.isEmpty() || stack.isEmpty()) {
            return false;
        }
        item = stack.copyWithCount(1);
        if (!player.getAbilities().instabuild) {
            stack.shrink(1);
        }
        changed();
        return true;
    }

    public ItemStack take() {
        ItemStack out = item;
        item = ItemStack.EMPTY;
        changed();
        return out;
    }

    public Optional<CuttingBoardRecipe> findRecipe(Level level) {
        return item.isEmpty() ? Optional.empty() : recipeCheck.getRecipeFor(new SimpleContainer(item), level);
    }

    /** Processes the ingredient with {@code tool}; returns false when the tool does not fit the recipe. */
    public boolean process(ServerLevel level, Player player, ItemStack tool) {
        Optional<CuttingBoardRecipe> recipe = findRecipe(level);
        if (recipe.isEmpty() || !recipe.get().isTool(tool)) {
            return false;
        }
        ItemStack ingredient = item;
        for (ItemStack result : recipe.get().rollResults(level.random)) {
            Block.popResourceFromFace(level, worldPosition, net.minecraft.core.Direction.UP, result);
        }
        level.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, ingredient), worldPosition.getX() + 0.5D,
                worldPosition.getY() + 0.15D, worldPosition.getZ() + 0.5D, 8, 0.15D, 0.05D, 0.15D, 0.05D);
        level.playSound(null, worldPosition, SoundEvents.SHEEP_SHEAR, SoundSource.BLOCKS, 0.8F, 0.9F + level.random.nextFloat() * 0.2F);
        level.playSound(null, worldPosition, SoundEvents.WOOD_HIT, SoundSource.BLOCKS, 0.6F, 1.2F);
        if (tool.isDamageableItem()) {
            tool.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(EquipmentSlot.MAINHAND));
        }
        item = ItemStack.EMPTY;
        changed();
        return true;
    }

    private void changed() {
        setChanged();
        if (level != null) {
            BlockState state = getBlockState();
            level.sendBlockUpdated(worldPosition, state, state, Block.UPDATE_CLIENTS);
        }
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        item = tag.contains("Item") ? ItemStack.of(tag.getCompound("Item")) : ItemStack.EMPTY;
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        if (!item.isEmpty()) {
            tag.put("Item", item.save(new CompoundTag()));
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    @Override
    public CompoundTag getUpdateTag() {
        CompoundTag tag = new CompoundTag();
        saveAdditional(tag);
        return tag;
    }
}
