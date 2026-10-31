package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import tn.nightbeam.sproutandsoil.block.entity.CookingPotBlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.CuttingBoardBlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.ScarecrowBlockEntity;
import tn.nightbeam.sproutandsoil.block.entity.SprinklerBlockEntity;
import tn.nightbeam.sproutandsoil.platform.Services;

public final class ModBlockEntities {
    public static RegistryEntry<BlockEntityType<CookingPotBlockEntity>> COOKING_POT;
    public static RegistryEntry<BlockEntityType<CuttingBoardBlockEntity>> CUTTING_BOARD;
    public static RegistryEntry<BlockEntityType<ScarecrowBlockEntity>> SCARECROW;
    public static RegistryEntry<BlockEntityType<SprinklerBlockEntity>> SPRINKLER;

    private ModBlockEntities() {
    }

    public static void init() {
        COOKING_POT = Services.REGISTRAR.register(Registries.BLOCK_ENTITY_TYPE, "cooking_pot",
                () -> Services.PLATFORM.createBlockEntityType(CookingPotBlockEntity::new, ModBlocks.COOKING_POT.get()));
        CUTTING_BOARD = Services.REGISTRAR.register(Registries.BLOCK_ENTITY_TYPE, "cutting_board",
                () -> Services.PLATFORM.createBlockEntityType(CuttingBoardBlockEntity::new, ModBlocks.CUTTING_BOARD.get()));
        SCARECROW = Services.REGISTRAR.register(Registries.BLOCK_ENTITY_TYPE, "scarecrow",
                () -> Services.PLATFORM.createBlockEntityType(ScarecrowBlockEntity::new, ModBlocks.SCARECROW.get()));
        SPRINKLER = Services.REGISTRAR.register(Registries.BLOCK_ENTITY_TYPE, "sprinkler",
                () -> Services.PLATFORM.createBlockEntityType(SprinklerBlockEntity::new, ModBlocks.SPRINKLER.get()));
    }
}
