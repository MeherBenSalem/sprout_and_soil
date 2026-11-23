package tn.nightbeam.sproutandsoil.block.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import tn.nightbeam.sproutandsoil.farming.ScarecrowTracker;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;

/** Registers the scarecrow with {@link ScarecrowTracker} while it is loaded. */
public class ScarecrowBlockEntity extends BlockEntity {

    public ScarecrowBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.SCARECROW.get(), pos, state);
    }

    @Override
    public void setLevel(Level level) {
        super.setLevel(level);
        if (!level.isClientSide()) {
            ScarecrowTracker.add(level, worldPosition);
        }
    }

    @Override
    public void clearRemoved() {
        super.clearRemoved();
        if (level != null && !level.isClientSide()) {
            ScarecrowTracker.add(level, worldPosition);
        }
    }

    @Override
    public void setRemoved() {
        super.setRemoved();
        if (level != null && !level.isClientSide()) {
            ScarecrowTracker.remove(level, worldPosition);
        }
    }
}
