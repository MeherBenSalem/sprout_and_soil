package tn.nightbeam.sproutandsoil.fabric.platform;

import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.platform.services.IRegistrar;
import tn.nightbeam.sproutandsoil.registry.RegistryEntry;

import java.util.function.Supplier;

/** Fabric registers straight away, in call order. */
public class FabricRegistrar implements IRegistrar {

    @Override
    @SuppressWarnings("unchecked")
    public <R, T extends R> RegistryEntry<T> register(ResourceKey<? extends Registry<R>> registryKey, String name, Supplier<T> factory) {
        Registry<R> registry = (Registry<R>) BuiltInRegistries.REGISTRY.get(registryKey.location());
        if (registry == null) {
            throw new IllegalStateException("Unknown registry " + registryKey.location());
        }
        ResourceLocation id = SproutAndSoil.id(name);
        T value = factory.get();
        Holder<R> holder = Registry.registerForHolder(registry, id, value);
        return new Entry<>(id, value, (Holder<T>) holder);
    }

    private record Entry<T>(ResourceLocation id, T value, Holder<T> holder) implements RegistryEntry<T> {
        @Override
        public T get() {
            return value;
        }
    }
}
