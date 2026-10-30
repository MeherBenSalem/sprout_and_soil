package tn.nightbeam.sproutandsoil.platform;

import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.platform.services.IPlatformHelper;
import tn.nightbeam.sproutandsoil.platform.services.IRegistrar;

import java.util.ServiceLoader;

/** Loads the loader-specific implementations declared in {@code META-INF/services}. */
public final class Services {
    public static final IPlatformHelper PLATFORM = load(IPlatformHelper.class);
    public static final IRegistrar REGISTRAR = load(IRegistrar.class);

    private Services() {
    }

    public static <T> T load(Class<T> clazz) {
        T service = ServiceLoader.load(clazz, Services.class.getClassLoader())
                .findFirst()
                .orElseThrow(() -> new NullPointerException("Failed to load service for " + clazz.getName()));
        SproutAndSoil.LOGGER.debug("Loaded {} for service {}", service, clazz);
        return service;
    }
}
