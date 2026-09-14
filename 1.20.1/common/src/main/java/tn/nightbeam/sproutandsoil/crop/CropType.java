package tn.nightbeam.sproutandsoil.crop;

public enum CropType {
    TOMATO(7, new double[]{3, 6, 9, 12, 15, 15, 15, 15}),
    GARLIC(3, new double[]{3, 6, 6, 15}),
    LETUCE(3, new double[]{3, 6, 6, 15});

    public final int maxStage;
    public final double[] heights;

    CropType(int maxStage, double[] heights) {
        this.maxStage = maxStage;
        this.heights = heights;
    }

    public String idPrefix() {
        return switch (this) {
            case TOMATO -> "tomato_plant_stage_";
            case GARLIC -> "garlic_plant_stage_";
            case LETUCE -> "letuce_plant_stage_";
        };
    }

    public boolean isMature(int stage) {
        return stage >= maxStage;
    }
}
