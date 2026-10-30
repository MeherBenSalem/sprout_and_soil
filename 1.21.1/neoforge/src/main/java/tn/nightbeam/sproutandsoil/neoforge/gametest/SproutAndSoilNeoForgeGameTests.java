package tn.nightbeam.sproutandsoil.neoforge.gametest;

import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.gametest.SproutAndSoilTests;

/** Runs with {@code ./gradlew :neoforge:runGameTestServer}. */
@GameTestHolder(SproutAndSoil.MOD_ID)
@PrefixGameTestTemplate(false)
public class SproutAndSoilNeoForgeGameTests {

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void contentIsRegistered(GameTestHelper helper) {
        SproutAndSoilTests.contentIsRegistered(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void perennialRegrowsAfterHarvest(GameTestHelper helper) {
        SproutAndSoilTests.perennialRegrowsAfterHarvest(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void annualReplantsAfterHarvest(GameTestHelper helper) {
        SproutAndSoilTests.annualReplantsAfterHarvest(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void vanillaCropsHarvestWithEmptyHand(GameTestHelper helper) {
        SproutAndSoilTests.vanillaCropsHarvestWithEmptyHand(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 400)
    public static void cookingPotCooksOverFire(GameTestHelper helper) {
        SproutAndSoilTests.cookingPotCooksOverFire(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 300)
    public static void cookingPotNeedsHeat(GameTestHelper helper) {
        SproutAndSoilTests.cookingPotNeedsHeat(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void cuttingBoardSlicesWithKnife(GameTestHelper helper) {
        SproutAndSoilTests.cuttingBoardSlicesWithKnife(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void mortarIsDamagedNotConsumed(GameTestHelper helper) {
        SproutAndSoilTests.mortarIsDamagedNotConsumed(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void ripeFruitCanBePicked(GameTestHelper helper) {
        SproutAndSoilTests.ripeFruitCanBePicked(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void pieServesFourSlices(GameTestHelper helper) {
        SproutAndSoilTests.pieServesFourSlices(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 200)
    public static void sprinklerHydratesFarmland(GameTestHelper helper) {
        SproutAndSoilTests.sprinklerHydratesFarmland(helper);
    }
}
