package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.util.ExtraCodecs;
import tn.nightbeam.sproutandsoil.platform.Services;

public final class ModDataComponents {
    /** Water left in a watering can. */
    public static RegistryEntry<DataComponentType<Integer>> WATER;

    private ModDataComponents() {
    }

    public static void init() {
        WATER = Services.REGISTRAR.register(Registries.DATA_COMPONENT_TYPE, "water", () -> DataComponentType.<Integer>builder()
                .persistent(ExtraCodecs.NON_NEGATIVE_INT)
                .networkSynchronized(ByteBufCodecs.VAR_INT)
                .build());
    }
}
