package tn.nightbeam.sproutandsoil.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.effect.CozyEffect;
import tn.nightbeam.sproutandsoil.effect.SimpleEffect;
import tn.nightbeam.sproutandsoil.effect.WellFedEffect;
import tn.nightbeam.sproutandsoil.platform.Services;

public final class ModEffects {
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
                        .addAttributeModifier(Attributes.MOVEMENT_SPEED, SproutAndSoil.id("effect.caffeinated.speed"), 0.15D,
                                AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL)
                        .addAttributeModifier(Attributes.BLOCK_BREAK_SPEED, SproutAndSoil.id("effect.caffeinated.mining"), 0.15D,
                                AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
    }
}
