package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceLocation;

import java.util.function.Supplier;

/** A registered object that can be resolved lazily, by id, or as a registry {@link Holder}. */
public interface RegistryEntry<T> extends Supplier<T> {

    ResourceLocation id();

    /** The registry holder. Only meaningful when {@code T} is the registry's own type (e.g. {@code MobEffect}). */
    Holder<T> holder();
}
