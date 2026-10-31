package tn.nightbeam.sproutandsoil.gametest;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.inventory.TransientCraftingContainer;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import tn.nightbeam.sproutandsoil.block.FeastBlock;
import tn.nightbeam.sproutandsoil.block.FruitLeavesBlock;
import tn.nightbeam.sproutandsoil.block.SoilCropBlock;
import tn.nightbeam.sproutandsoil.block.entity.CookingPotBlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.CuttingBoardBlockEntity;
import tn.nightbeam.sproutandsoil.content.Content;
import tn.nightbeam.sproutandsoil.content.ContentManifest;
import tn.nightbeam.sproutandsoil.farming.CropHarvesting;
import tn.nightbeam.sproutandsoil.registry.ModBlocks;
import tn.nightbeam.sproutandsoil.registry.ModEffects;
import tn.nightbeam.sproutandsoil.registry.ModItems;

import java.util.Optional;

/**
 * In-world tests shared by both loaders. Each loader exposes these through a thin annotated holder
 * (Fabric: {@code fabric-gametest} entrypoint, NeoForge: {@code @GameTestHolder}). The arena is
 * {@code sprout_and_soil:empty}: 9x4x9 with a stone floor at y=0.
 */
public final class SproutAndSoilTests {
    public static final String TEMPLATE = "empty";

    private SproutAndSoilTests() {
    }

    /** Every crop's planting item plants that crop, and every manifest item is registered. */
    public static void contentIsRegistered(GameTestHelper helper) {
        for (ContentManifest.Crop crop : Content.manifest().crops()) {
            Item planting = ModItems.get(crop.plantingItem());
            helper.assertTrue(planting instanceof BlockItem item && item.getBlock() == ModBlocks.get(crop.block()),
                    crop.plantingItem() + " should plant " + crop.block());
        }
        for (ContentManifest.ItemEntry entry : Content.manifest().items()) {
            helper.assertTrue(ModItems.get(entry.id()) != Items.AIR, entry.id() + " is not registered");
        }
        helper.succeed();
    }

    public static void perennialRegrowsAfterHarvest(GameTestHelper helper) {
        SoilCropBlock tomato = (SoilCropBlock) ModBlocks.get("tomato_crop");
        BlockPos crop = plant(helper, tomato.getStateForAge(7));
        harvest(helper, crop);
        helper.assertBlockState(crop, s -> s.is(tomato) && tomato.getAge(s) == tomato.harvestAge(),
                () -> "tomato should fall back to its regrow age");
        helper.assertItemEntityPresent(ModItems.get("tomato"), crop, 2.0D);
        helper.succeed();
    }

    public static void annualReplantsAfterHarvest(GameTestHelper helper) {
        SoilCropBlock lettuce = (SoilCropBlock) ModBlocks.get("lettuce_crop");
        BlockPos crop = plant(helper, lettuce.getStateForAge(7));
        harvest(helper, crop);
        helper.assertBlockState(crop, s -> s.is(lettuce) && lettuce.getAge(s) == 0, () -> "lettuce should be replanted at age 0");
        helper.assertItemEntityPresent(ModItems.get("lettuce"), crop, 2.0D);
        helper.succeed();
    }

    public static void vanillaCropsHarvestWithEmptyHand(GameTestHelper helper) {
        BlockPos crop = plant(helper, ((CropBlock) Blocks.WHEAT).getStateForAge(7));
        Player player = helper.makeMockPlayer();
        BlockPos abs = helper.absolutePos(crop);
        CropHarvesting.onUseBlock(player, helper.getLevel(), InteractionHand.MAIN_HAND,
                new BlockHitResult(Vec3.atCenterOf(abs), Direction.UP, abs, false));
        helper.assertBlockState(crop, s -> s.is(Blocks.WHEAT) && ((CropBlock) Blocks.WHEAT).getAge(s) == 0,
                () -> "wheat should be replanted");
        helper.assertItemEntityPresent(Items.WHEAT, crop, 2.0D);
        helper.succeed();
    }

    public static void cookingPotCooksOverFire(GameTestHelper helper) {
        CookingPotBlockEntity pot = pot(helper, Blocks.CAMPFIRE.defaultBlockState());
        helper.succeedWhen(() -> {
            helper.assertTrue(pot.getItem(CookingPotBlockEntity.OUTPUT_SLOT).is(ModItems.get("tomato_soup")), "no soup yet");
            helper.assertTrue(pot.getItem(0).isEmpty() && pot.getItem(CookingPotBlockEntity.CONTAINER_SLOT).isEmpty(),
                    "ingredients and bowl should be used up");
        });
    }

    public static void cookingPotNeedsHeat(GameTestHelper helper) {
        CookingPotBlockEntity pot = pot(helper, Blocks.STONE.defaultBlockState());
        helper.runAfterDelay(240, () -> {
            helper.assertTrue(pot.getItem(CookingPotBlockEntity.OUTPUT_SLOT).isEmpty(), "pot cooked without heat");
            helper.succeed();
        });
    }

    public static void cuttingBoardSlicesWithKnife(GameTestHelper helper) {
        BlockPos pos = new BlockPos(4, 1, 4);
        helper.setBlock(pos, ModBlocks.CUTTING_BOARD.get().defaultBlockState());
        Player player = helper.makeMockPlayer();
        CuttingBoardBlockEntity board = (CuttingBoardBlockEntity) helper.getBlockEntity(pos);
        helper.assertTrue(board.place(new ItemStack(Items.BEEF), player), "board should accept beef");
        helper.assertFalse(board.process(helper.getLevel(), player, new ItemStack(Items.STICK)), "a stick is not a knife");
        helper.assertTrue(board.process(helper.getLevel(), player, new ItemStack(ModItems.get("iron_knife"))), "knife should cut");
        helper.assertTrue(board.isEmpty(), "board should be empty after cutting");
        helper.assertItemEntityPresent(ModItems.get("minced_beef"), pos, 2.0D);
        helper.succeed();
    }

    public static void mortarIsDamagedNotConsumed(GameTestHelper helper) {
        CraftingContainer input = new TransientCraftingContainer(new AbstractContainerMenu(null, -1) {
            @Override
            public ItemStack quickMoveStack(Player player, int index) {
                return ItemStack.EMPTY;
            }

            @Override
            public boolean stillValid(Player player) {
                return true;
            }
        }, 2, 1);
        input.setItem(0, new ItemStack(ModItems.get("mortar_and_pestle")));
        input.setItem(1, new ItemStack(Items.WHEAT));
        Optional<CraftingRecipe> recipe = helper.getLevel().getRecipeManager()
                .getRecipeFor(RecipeType.CRAFTING, input, helper.getLevel());
        helper.assertTrue(recipe.isPresent(), "mortar + wheat should match a recipe");
        helper.assertTrue(recipe.get().assemble(input, helper.getLevel().registryAccess()).is(ModItems.get("flour")),
                "should make flour");
        ItemStack left = recipe.get().getRemainingItems(input).get(0);
        helper.assertTrue(left.is(ModItems.get("mortar_and_pestle")) && left.getDamageValue() == 1,
                "mortar should stay in the grid with 1 damage");
        helper.succeed();
    }

    public static void ripeFruitCanBePicked(GameTestHelper helper) {
        BlockPos pos = new BlockPos(4, 2, 4);
        Block leavesBlock = ModBlocks.get("orange_leaves");
        helper.setBlock(pos, leavesBlock.defaultBlockState().setValue(FruitLeavesBlock.AGE, 3).setValue(LeavesBlock.PERSISTENT, true));
        use(helper, pos);
        helper.assertBlockState(pos, s -> s.getValue(FruitLeavesBlock.AGE) == 0, () -> "picked leaves should reset");
        helper.assertItemEntityPresent(ModItems.get("orange"), pos, 2.0D);
        helper.succeed();
    }

    public static void pieServesFourSlices(GameTestHelper helper) {
        BlockPos pos = new BlockPos(4, 1, 4);
        helper.setBlock(pos, ModBlocks.get("apple_pie").defaultBlockState());
        Player player = helper.makeMockPlayer();
        for (int i = 0; i < 4; i++) {
            BlockPos abs = helper.absolutePos(pos);
            helper.getBlockState(pos).use(helper.getLevel(), player, InteractionHand.MAIN_HAND,
                    new BlockHitResult(Vec3.atCenterOf(abs), Direction.UP, abs, false));
        }
        helper.assertBlockNotPresent(ModBlocks.get("apple_pie"), pos);
        helper.assertTrue(player.getInventory().countItem(ModItems.get("apple_pie_slice")) == 4, "expected four slices");
        helper.assertTrue(helper.getBlockState(pos).isAir() || !(helper.getBlockState(pos).getBlock() instanceof FeastBlock), "pie should be gone");
        helper.succeed();
    }

    public static void sprinklerHydratesFarmland(GameTestHelper helper) {
        helper.setBlock(new BlockPos(0, 1, 4), Blocks.WATER.defaultBlockState());
        helper.setBlock(new BlockPos(1, 1, 4), ModBlocks.SPRINKLER.get().defaultBlockState());
        BlockPos farmland = new BlockPos(5, 1, 4);
        helper.setBlock(farmland, Blocks.FARMLAND.defaultBlockState().setValue(FarmBlock.MOISTURE, 0));
        helper.setBlock(farmland.above(), Blocks.WHEAT.defaultBlockState());
        helper.succeedWhen(() -> helper.assertBlockState(farmland,
                s -> s.is(Blocks.FARMLAND) && s.getValue(FarmBlock.MOISTURE) == FarmBlock.MAX_MOISTURE,
                () -> "farmland not hydrated yet"));
    }

    /** Knives are offered weapon enchantments (Fabric: mixin, Forge: IForgeItem#canApplyAtEnchantingTable). */
    public static void knivesTakeWeaponEnchantments(GameTestHelper helper) {
        ItemStack knife = new ItemStack(ModItems.get("iron_knife"));
        boolean sharpness = false;
        for (int level = 1; level <= 30 && !sharpness; level++) {
            sharpness = EnchantmentHelper.getAvailableEnchantmentResults(level, knife, false).stream()
                    .anyMatch(e -> e.enchantment == Enchantments.SHARPNESS);
        }
        helper.assertTrue(sharpness, "the enchanting table should offer Sharpness for a knife");
        helper.assertTrue(Enchantments.SHARPNESS.canEnchant(knife), "Sharpness books should apply to knives");
        helper.succeed();
    }

    /** Caffeinated mines 15% faster (Fabric: mixin, Forge: BreakSpeed event). */
    public static void caffeineSpeedsUpMining(GameTestHelper helper) {
        BlockPos pos = new BlockPos(4, 1, 4);
        helper.setBlock(pos, Blocks.STONE);
        BlockPos abs = helper.absolutePos(pos);
        Player player = helper.makeMockPlayer();
        float normal = helper.getBlockState(pos).getDestroyProgress(player, helper.getLevel(), abs);
        player.addEffect(new MobEffectInstance(ModEffects.CAFFEINATED.get(), 200));
        float caffeinated = helper.getBlockState(pos).getDestroyProgress(player, helper.getLevel(), abs);
        helper.assertTrue(caffeinated > normal * 1.1F, "caffeinated mining should be faster: " + normal + " -> " + caffeinated);
        helper.succeed();
    }

    // ------------------------------------------------------------------------------------ helpers

    private static BlockPos plant(GameTestHelper helper, BlockState crop) {
        BlockPos soil = new BlockPos(4, 1, 4);
        helper.setBlock(soil, Blocks.FARMLAND.defaultBlockState().setValue(FarmBlock.MOISTURE, FarmBlock.MAX_MOISTURE));
        helper.setBlock(soil.above(), crop);
        return soil.above();
    }

    private static void harvest(GameTestHelper helper, BlockPos crop) {
        BlockPos abs = helper.absolutePos(crop);
        helper.assertTrue(CropHarvesting.harvest(helper.getLevel(), abs, helper.getLevel().getBlockState(abs), null, ItemStack.EMPTY),
                "crop should be harvestable");
    }

    private static void use(GameTestHelper helper, BlockPos pos) {
        BlockPos abs = helper.absolutePos(pos);
        helper.getBlockState(pos).use(helper.getLevel(), helper.makeMockPlayer(), InteractionHand.MAIN_HAND,
                new BlockHitResult(Vec3.atCenterOf(abs), Direction.UP, abs, false));
    }

    /** Pot over {@code below}, loaded for tomato soup (tomato, tomato, onion, salt + bowl). */
    private static CookingPotBlockEntity pot(GameTestHelper helper, BlockState below) {
        BlockPos heat = new BlockPos(4, 1, 4);
        helper.setBlock(heat, below);
        helper.setBlock(heat.above(), ModBlocks.COOKING_POT.get().defaultBlockState());
        CookingPotBlockEntity pot = (CookingPotBlockEntity) helper.getBlockEntity(heat.above());
        pot.setItem(0, new ItemStack(ModItems.get("tomato")));
        pot.setItem(1, new ItemStack(ModItems.get("tomato")));
        pot.setItem(2, new ItemStack(ModItems.get("onion")));
        pot.setItem(3, new ItemStack(ModItems.get("salt")));
        pot.setItem(CookingPotBlockEntity.CONTAINER_SLOT, new ItemStack(Items.BOWL));
        return pot;
    }
}
