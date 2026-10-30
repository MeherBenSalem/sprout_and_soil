package tn.nightbeam.sproutandsoil.block;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.grower.TreeGrower;

/** Grows into a fruit tree whose leaves blossom and bear fruit. */
public class FruitSaplingBlock extends SaplingBlock {
    public static final MapCodec<FruitSaplingBlock> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            TreeGrower.CODEC.fieldOf("tree").forGetter(b -> b.treeGrower),
            propertiesCodec()
    ).apply(i, FruitSaplingBlock::new));

    public FruitSaplingBlock(TreeGrower treeGrower, Properties properties) {
        super(treeGrower, properties);
    }

    @Override
    public MapCodec<? extends SaplingBlock> codec() {
        return CODEC;
    }
}
