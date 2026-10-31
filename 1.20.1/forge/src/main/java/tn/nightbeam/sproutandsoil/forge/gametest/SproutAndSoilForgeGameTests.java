package tn.nightbeam.sproutandsoil.forge.gametest;

import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.gametest.SproutAndSoilTests;

/** Runs with {@code ./gradlew :forge:runGameTestServer}. */
@GameTestHolder(SproutAndSoil.MOD_ID)
@PrefixGameTestTemplate(false)
public class SproutAndSoilForgeGameTests {

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

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void knivesTakeWeaponEnchantments(GameTestHelper helper) {
        SproutAndSoilTests.knivesTakeWeaponEnchantments(helper);
    }

    @GameTest(template = SproutAndSoilTests.TEMPLATE, timeoutTicks = 100)
    public static void caffeineSpeedsUpMining(GameTestHelper helper) {
        SproutAndSoilTests.caffeineSpeedsUpMining(helper);
    }
}
