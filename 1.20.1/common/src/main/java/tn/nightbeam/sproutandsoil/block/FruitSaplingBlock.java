package tn.nightbeam.sproutandsoil.block;

import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.grower.AbstractTreeGrower;

/** Grows into a fruit tree whose leaves blossom and bear fruit. */
public class FruitSaplingBlock extends SaplingBlock {
    public FruitSaplingBlock(AbstractTreeGrower treeGrower, Properties properties) {
        super(treeGrower, properties);
    }
}
