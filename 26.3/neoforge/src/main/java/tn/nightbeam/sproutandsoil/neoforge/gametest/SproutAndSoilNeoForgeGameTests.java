package tn.nightbeam.sproutandsoil.neoforge.gametest;

import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.FunctionGameTestInstance;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.gametest.framework.TestData;
import net.minecraft.gametest.framework.TestEnvironmentDefinition;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.RegisterGameTestsEvent;
import net.neoforged.neoforge.registries.DeferredRegister;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.gametest.SproutAndSoilTests;

import java.util.function.Consumer;

/**
 * Registers the shared {@link SproutAndSoilTests} with NeoForge: one test function per test and one test instance per
 * function in template {@code sprout_and_soil:empty}. Runs with {@code ./gradlew :neoforge:runGameTestServer}.
 */
public final class SproutAndSoilNeoForgeGameTests {
    private static final DeferredRegister<Consumer<GameTestHelper>> FUNCTIONS =
            DeferredRegister.create(Registries.TEST_FUNCTION, SproutAndSoil.MOD_ID);

    private record TestEntry(String name, int maxTicks, Consumer<GameTestHelper> function) {
    }

    private static final TestEntry[] TESTS = {
            new TestEntry("content_is_registered", 100, SproutAndSoilTests::contentIsRegistered),
            new TestEntry("perennial_regrows_after_harvest", 100, SproutAndSoilTests::perennialRegrowsAfterHarvest),
            new TestEntry("annual_replants_after_harvest", 100, SproutAndSoilTests::annualReplantsAfterHarvest),
            new TestEntry("vanilla_crops_harvest_with_empty_hand", 100, SproutAndSoilTests::vanillaCropsHarvestWithEmptyHand),
            new TestEntry("cooking_pot_cooks_over_fire", 400, SproutAndSoilTests::cookingPotCooksOverFire),
            new TestEntry("cooking_pot_needs_heat", 300, SproutAndSoilTests::cookingPotNeedsHeat),
            new TestEntry("cutting_board_slices_with_knife", 100, SproutAndSoilTests::cuttingBoardSlicesWithKnife),
            new TestEntry("mortar_is_damaged_not_consumed", 100, SproutAndSoilTests::mortarIsDamagedNotConsumed),
            new TestEntry("ripe_fruit_can_be_picked", 100, SproutAndSoilTests::ripeFruitCanBePicked),
            new TestEntry("pie_serves_four_slices", 100, SproutAndSoilTests::pieServesFourSlices),
            new TestEntry("sprinkler_hydrates_farmland", 200, SproutAndSoilTests::sprinklerHydratesFarmland),
    };

    static {
        for (TestEntry test : TESTS) {
            FUNCTIONS.register(test.name(), test::function);
        }
    }

    private SproutAndSoilNeoForgeGameTests() {
    }

    public static void register(IEventBus modBus) {
        FUNCTIONS.register(modBus);
        modBus.addListener(SproutAndSoilNeoForgeGameTests::registerInstances);
    }

    private static void registerInstances(RegisterGameTestsEvent event) {
        Holder<TestEnvironmentDefinition<?>> environment = event.registerEnvironment(SproutAndSoil.id("default"),
                new TestEnvironmentDefinition.AllOf());
        Identifier template = SproutAndSoil.id(SproutAndSoilTests.TEMPLATE);
        for (TestEntry test : TESTS) {
            Identifier id = SproutAndSoil.id(test.name());
            event.registerTest(id, new FunctionGameTestInstance(ResourceKey.create(Registries.TEST_FUNCTION, id),
                    new TestData<>(environment, template, test.maxTicks(), 0, true)));
        }
    }
}
