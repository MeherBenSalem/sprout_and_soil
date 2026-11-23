package tn.nightbeam.sproutandsoil.block;

import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.grower.TreeGrower;

/** Grows into a fruit tree whose leaves blossom and bear fruit. */
public class FruitSaplingBlock extends SaplingBlock {

    public FruitSaplingBlock(TreeGrower treeGrower, Properties properties) {
        super(treeGrower, properties);
    }
}
