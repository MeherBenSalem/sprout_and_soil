package tn.nightbeam.sproutandsoil.effect;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodData;

/** Hearty meals: every five seconds tops saturation back up, so hunger drains far more slowly. */
public class WellFedEffect extends MobEffect {
    private static final int INTERVAL = 100;

    public WellFedEffect() {
        super(MobEffectCategory.BENEFICIAL, 0xE8A33C);
    }

    @Override
    public boolean isDurationEffectTick(int duration, int amplifier) {
        return duration % INTERVAL == 0;
    }

    @Override
    public void applyEffectTick(LivingEntity entity, int amplifier) {
        if (entity instanceof Player player && !player.level().isClientSide()) {
            FoodData food = player.getFoodData();
            float saturation = Math.min(food.getFoodLevel(), food.getSaturationLevel() + 1.0F + amplifier);
            if (saturation > food.getSaturationLevel()) {
                food.setSaturation(saturation);
            }
        }
    }
}
