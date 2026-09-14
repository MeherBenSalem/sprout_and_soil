package tn.nightbeam.sproutandsoil.crop;

import net.minecraft.core.BlockPos;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import tn.nightbeam.sproutandsoil.block.entity.CropStageBlockEntity;
import tn.nightbeam.sproutandsoil.registry.ModBlocks;

public final class CropLogic {
    private static final TagKey<Block> FARMLAND_TAG = TagKey.create(Registries.BLOCK, Identifier.fromNamespaceAndPath("crops", "farmland"));
    private static final TagKey<Item> FERTILIZER_TAG = TagKey.create(Registries.ITEM, Identifier.fromNamespaceAndPath("crops", "fertilizer"));

    private CropLogic() {
    }

    public static boolean canSurvive(LevelReader level, BlockPos pos) {
        return level.getMaxLocalRawBrightness(pos) >= 8
                && level.getBlockState(pos.below()).is(FARMLAND_TAG);
    }

    public static boolean tryPlant(Level level, BlockPos farmlandPos, CropType cropType) {
        BlockPos plantPos = farmlandPos.above();
        BlockState stage0 = ModBlocks.stageBlock(cropType, 0).defaultBlockState();
        if (!level.getBlockState(farmlandPos).is(FARMLAND_TAG)) {
            return false;
        }
        if (!level.getBlockState(plantPos).isAir()) {
            return false;
        }
        if (!stage0.canSurvive(level, plantPos)) {
            return false;
        }
        level.setBlock(plantPos, stage0, 3);
        initializeBlockEntity(level, plantPos, cropType, 0);
        return true;
    }

    public static void initializeBlockEntity(Level level, BlockPos pos, CropType cropType, int stage) {
        if (level.isClientSide()) {
            return;
        }
        BlockEntity blockEntity = level.getBlockEntity(pos);
        if (blockEntity instanceof CropStageBlockEntity crop) {
            crop.setCropType(cropType);
            crop.setGrowthStage(stage);
            crop.setGrowthTime(randomGrowthDelay(level.getRandom()));
            blockEntity.setChanged();
            level.sendBlockUpdated(pos, level.getBlockState(pos), level.getBlockState(pos), 3);
        }
    }

    public static void onRandomTick(ServerLevel level, BlockPos pos, BlockState state, RandomSource random) {
        BlockEntity blockEntity = level.getBlockEntity(pos);
        if (!(blockEntity instanceof CropStageBlockEntity crop)) {
            return;
        }
        CropType type = crop.getCropType();
        if (type == null) {
            return;
        }
        int stage = crop.getGrowthStage();
        if (type.isMature(stage)) {
            return;
        }
        if (crop.getGrowthTime() > 0) {
            crop.setGrowthTime(crop.getGrowthTime() - 1);
            return;
        }
        advanceStage(level, pos, type, stage);
    }

    public static void tryFertilize(Level level, BlockPos pos, Player player) {
        ItemStack held = player.getMainHandItem();
        if (!held.is(FERTILIZER_TAG)) {
            return;
        }
        BlockEntity blockEntity = level.getBlockEntity(pos);
        if (!(blockEntity instanceof CropStageBlockEntity crop)) {
            return;
        }
        CropType type = crop.getCropType();
        if (type == null || type.isMature(crop.getGrowthStage())) {
            return;
        }
        if (level.isClientSide()) {
            return;
        }
        if (level instanceof ServerLevel serverLevel) {
            advanceStage(serverLevel, pos, type, crop.getGrowthStage());
        }
        if (!player.getAbilities().instabuild) {
            held.shrink(1);
        }
    }

    private static void advanceStage(ServerLevel level, BlockPos pos, CropType type, int currentStage) {
        int nextStage = currentStage + 1;
        if (nextStage > type.maxStage) {
            return;
        }
        BlockState nextState = ModBlocks.stageBlock(type, nextStage).defaultBlockState();
        if (!nextState.canSurvive(level, pos)) {
            return;
        }
        BlockEntity existing = level.getBlockEntity(pos);
        CropStageBlockEntity snapshot = existing instanceof CropStageBlockEntity crop ? crop : null;
        level.setBlock(pos, nextState, 3);
        BlockEntity newEntity = level.getBlockEntity(pos);
        if (newEntity instanceof CropStageBlockEntity crop) {
            crop.setCropType(type);
            crop.setGrowthStage(nextStage);
            crop.setGrowthTime(randomGrowthDelay(level.getRandom()));
            if (snapshot != null) {
                crop.setChanged();
            }
        }
        level.sendBlockUpdated(pos, nextState, nextState, 3);
    }

    private static int randomGrowthDelay(RandomSource random) {
        return 3 + random.nextInt(6);
    }
}
