package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import tn.nightbeam.sproutandsoil.effect.CozyEffect;
import tn.nightbeam.sproutandsoil.effect.SimpleEffect;
import tn.nightbeam.sproutandsoil.effect.WellFedEffect;
import tn.nightbeam.sproutandsoil.platform.Services;

public final class ModEffects {
    /** Caffeinated: +15% movement speed (attribute) and +15% mining speed (see {@link #breakSpeed}). */
    public static final float CAFFEINE_BOOST = 0.15F;

    public static RegistryEntry<MobEffect> WELL_FED;
    public static RegistryEntry<MobEffect> COZY;
    public static RegistryEntry<MobEffect> CAFFEINATED;

    private ModEffects() {
    }

    public static void init() {
        WELL_FED = Services.REGISTRAR.register(Registries.MOB_EFFECT, "well_fed", WellFedEffect::new);
        COZY = Services.REGISTRAR.register(Registries.MOB_EFFECT, "cozy", CozyEffect::new);
        CAFFEINATED = Services.REGISTRAR.register(Registries.MOB_EFFECT, "caffeinated", () ->
                new SimpleEffect(MobEffectCategory.BENEFICIAL, 0x6F4E37)
                        .addAttributeModifier(Attributes.MOVEMENT_SPEED, "5f6d8f63-1d1e-4c39-9a0e-3c9a51c0ffee", CAFFEINE_BOOST,
                                AttributeModifier.Operation.MULTIPLY_TOTAL));
    }

    /**
     * 1.20.1 has no block break speed attribute, so each loader applies the Caffeinated mining bonus
     * through its break speed hook (a Forge event, a Fabric mixin).
     */
    public static float breakSpeed(Player player, float speed) {
        if (CAFFEINATED != null && player.hasEffect(CAFFEINATED.get())) {
            return speed * (1.0F + CAFFEINE_BOOST);
        }
        return speed;
    }
}
