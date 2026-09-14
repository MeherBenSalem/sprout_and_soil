package tn.nightbeam.sproutandsoil.block.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import tn.nightbeam.sproutandsoil.crop.CropType;
import tn.nightbeam.sproutandsoil.registry.ModBlockEntities;

public class CropStageBlockEntity extends BlockEntity {
    private int growthTime;
    private int growthStage;
    private String cropType = "";

    public CropStageBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.CROP_STAGE.get(), pos, state);
    }

    public int getGrowthTime() {
        return growthTime;
    }

    public void setGrowthTime(int growthTime) {
        this.growthTime = growthTime;
        setChanged();
    }

    public int getGrowthStage() {
        return growthStage;
    }

    public void setGrowthStage(int growthStage) {
        this.growthStage = growthStage;
        setChanged();
    }

    public CropType getCropType() {
        if (cropType.isEmpty()) {
            return null;
        }
        return CropType.valueOf(cropType.toUpperCase());
    }

    public void setCropType(CropType type) {
        this.cropType = type.name().toLowerCase();
        setChanged();
    }

    @Override
    protected void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.putInt("GrowthTime", growthTime);
        output.putInt("GrowthStage", growthStage);
        output.putString("type", cropType);
    }

    @Override
    protected void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        growthTime = input.getIntOr("GrowthTime", 0);
        growthStage = input.getIntOr("GrowthStage", 0);
        cropType = input.getStringOr("type", "");
    }

    @Override
    public ClientboundBlockEntityDataPacket getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        return saveWithoutMetadata(registries);
    }
}
