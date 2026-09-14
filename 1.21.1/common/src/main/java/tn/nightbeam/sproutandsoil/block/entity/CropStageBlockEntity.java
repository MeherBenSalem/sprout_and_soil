package tn.nightbeam.sproutandsoil.block.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
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
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.putInt("GrowthTime", growthTime);
        tag.putInt("GrowthStage", growthStage);
        tag.putString("type", cropType);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        growthTime = tag.getInt("GrowthTime");
        growthStage = tag.getInt("GrowthStage");
        cropType = tag.getString("type");
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
