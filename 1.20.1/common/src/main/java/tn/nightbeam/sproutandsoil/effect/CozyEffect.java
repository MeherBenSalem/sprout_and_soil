package tn.nightbeam.sproutandsoil.effect;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;

/** Warm drinks: no freezing in powder snow, and a gentle heal every ten seconds. */
public class CozyEffect extends MobEffect {
    private static final int HEAL_INTERVAL = 200;

    public CozyEffect() {
        super(MobEffectCategory.BENEFICIAL, 0xD9824B);
    }

    @Override
    public boolean isDurationEffectTick(int duration, int amplifier) {
        return true;
    }

    @Override
    public void applyEffectTick(LivingEntity entity, int amplifier) {
        if (entity.getTicksFrozen() > 0) {
            entity.setTicksFrozen(0);
        }
        if (entity.tickCount % HEAL_INTERVAL == 0 && entity.getHealth() < entity.getMaxHealth()) {
            entity.heal(1.0F + amplifier);
        }
    }
}
