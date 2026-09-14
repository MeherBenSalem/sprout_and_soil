package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.world.level.block.Block;
import tn.nightbeam.sproutandsoil.crop.CropType;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

public final class ModBlocks {
    public static Supplier<Block> TOMATO_PLANT_STAGE_0;
    public static Supplier<Block> TOMATO_PLANT_STAGE_1;
    public static Supplier<Block> TOMATO_PLANT_STAGE_2;
    public static Supplier<Block> TOMATO_PLANT_STAGE_3;
    public static Supplier<Block> TOMATO_PLANT_STAGE_4;
    public static Supplier<Block> TOMATO_PLANT_STAGE_5;
    public static Supplier<Block> TOMATO_PLANT_STAGE_6;
    public static Supplier<Block> TOMATO_PLANT_STAGE_7;
    public static Supplier<Block> GARLIC_PLANT_STAGE_0;
    public static Supplier<Block> GARLIC_PLANT_STAGE_1;
    public static Supplier<Block> GARLIC_PLANT_STAGE_2;
    public static Supplier<Block> GARLIC_PLANT_STAGE_3;
    public static Supplier<Block> LETUCE_PLANT_STAGE_0;
    public static Supplier<Block> LETUCE_PLANT_STAGE_1;
    public static Supplier<Block> LETUCE_PLANT_STAGE_2;
    public static Supplier<Block> LETUCE_PLANT_STAGE_3;

    private ModBlocks() {
    }

    public static Supplier<Block> stageSupplier(CropType type, int stage) {
        return switch (type) {
            case TOMATO -> tomatoStage(stage);
            case GARLIC -> garlicStage(stage);
            case LETUCE -> letuceStage(stage);
        };
    }

    public static Block stageBlock(CropType type, int stage) {
        return stageSupplier(type, stage).get();
    }

    private static Supplier<Block> tomatoStage(int stage) {
        return switch (stage) {
            case 0 -> TOMATO_PLANT_STAGE_0;
            case 1 -> TOMATO_PLANT_STAGE_1;
            case 2 -> TOMATO_PLANT_STAGE_2;
            case 3 -> TOMATO_PLANT_STAGE_3;
            case 4 -> TOMATO_PLANT_STAGE_4;
            case 5 -> TOMATO_PLANT_STAGE_5;
            case 6 -> TOMATO_PLANT_STAGE_6;
            case 7 -> TOMATO_PLANT_STAGE_7;
            default -> throw new IllegalArgumentException("Invalid tomato stage: " + stage);
        };
    }

    private static Supplier<Block> garlicStage(int stage) {
        return switch (stage) {
            case 0 -> GARLIC_PLANT_STAGE_0;
            case 1 -> GARLIC_PLANT_STAGE_1;
            case 2 -> GARLIC_PLANT_STAGE_2;
            case 3 -> GARLIC_PLANT_STAGE_3;
            default -> throw new IllegalArgumentException("Invalid garlic stage: " + stage);
        };
    }

    private static Supplier<Block> letuceStage(int stage) {
        return switch (stage) {
            case 0 -> LETUCE_PLANT_STAGE_0;
            case 1 -> LETUCE_PLANT_STAGE_1;
            case 2 -> LETUCE_PLANT_STAGE_2;
            case 3 -> LETUCE_PLANT_STAGE_3;
            default -> throw new IllegalArgumentException("Invalid letuce stage: " + stage);
        };
    }

    public static List<Block> allCropBlocks() {
        List<Block> blocks = new ArrayList<>();
        for (int i = 0; i <= CropType.TOMATO.maxStage; i++) {
            blocks.add(tomatoStage(i).get());
        }
        for (int i = 0; i <= CropType.GARLIC.maxStage; i++) {
            blocks.add(garlicStage(i).get());
        }
        for (int i = 0; i <= CropType.LETUCE.maxStage; i++) {
            blocks.add(letuceStage(i).get());
        }
        return blocks;
    }
}
