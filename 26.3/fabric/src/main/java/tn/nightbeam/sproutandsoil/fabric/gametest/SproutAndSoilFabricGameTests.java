package tn.nightbeam.sproutandsoil.fabric.gametest;

import net.fabricmc.fabric.api.gametest.v1.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import tn.nightbeam.sproutandsoil.gametest.SproutAndSoilTests;

/** Runs with {@code ./gradlew :fabric:runGametest}. */
public class SproutAndSoilFabricGameTests {
    private static final String TEMPLATE = "sprout_and_soil:" + SproutAndSoilTests.TEMPLATE;

    @GameTest(structure = TEMPLATE, maxTicks = 100)
    public void contentIsRegistered(GameTestHelper helper) {
        SproutAndSoilTests.contentIsRegistered(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 100)
    public void perennialRegrowsAfterHarvest(GameTestHelper helper) {
        SproutAndSoilTests.perennialRegrowsAfterHarvest(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 100)
    public void annualReplantsAfterHarvest(GameTestHelper helper) {
        SproutAndSoilTests.annualReplantsAfterHarvest(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 100)
    public void vanillaCropsHarvestWithEmptyHand(GameTestHelper helper) {
        SproutAndSoilTests.vanillaCropsHarvestWithEmptyHand(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 400)
    public void cookingPotCooksOverFire(GameTestHelper helper) {
        SproutAndSoilTests.cookingPotCooksOverFire(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 300)
    public void cookingPotNeedsHeat(GameTestHelper helper) {
        SproutAndSoilTests.cookingPotNeedsHeat(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 100)
    public void cuttingBoardSlicesWithKnife(GameTestHelper helper) {
        SproutAndSoilTests.cuttingBoardSlicesWithKnife(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 100)
    public void mortarIsDamagedNotConsumed(GameTestHelper helper) {
        SproutAndSoilTests.mortarIsDamagedNotConsumed(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 100)
    public void ripeFruitCanBePicked(GameTestHelper helper) {
        SproutAndSoilTests.ripeFruitCanBePicked(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 100)
    public void pieServesFourSlices(GameTestHelper helper) {
        SproutAndSoilTests.pieServesFourSlices(helper);
    }

    @GameTest(structure = TEMPLATE, maxTicks = 200)
    public void sprinklerHydratesFarmland(GameTestHelper helper) {
        SproutAndSoilTests.sprinklerHydratesFarmland(helper);
    }
}
