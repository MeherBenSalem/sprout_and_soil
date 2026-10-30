package tn.nightbeam.sproutandsoil.item;

import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffectUtil;
import net.minecraft.world.entity.LivingEntity;
import tn.nightbeam.sproutandsoil.content.ContentManifest;

import java.util.List;
import java.util.Optional;

/**
 * Food effects from the content manifest. They are resolved lazily (by id) when eaten, so food items
 * can reference effects that register after them.
 */
public final class FoodEffects {
    private FoodEffects() {
    }

    public static void apply(LivingEntity entity, List<ContentManifest.Effect> effects) {
        for (ContentManifest.Effect effect : effects) {
            if (effect.chance() < 1.0F && entity.getRandom().nextFloat() >= effect.chance()) {
                continue;
            }
            resolve(effect).ifPresent(holder -> entity.addEffect(new MobEffectInstance(holder, effect.duration(), effect.amplifier())));
        }
    }

    public static void appendTooltip(List<ContentManifest.Effect> effects, List<Component> tooltip, float tickRate) {
        for (ContentManifest.Effect effect : effects) {
            resolve(effect).ifPresent(holder -> {
                MobEffectInstance instance = new MobEffectInstance(holder, effect.duration(), effect.amplifier());
                MutableComponent line = Component.translatable(holder.value().getDescriptionId());
                if (effect.amplifier() > 0) {
                    line = Component.translatable("potion.withAmplifier", line,
                            Component.translatable("potion.potency." + effect.amplifier()));
                }
                line = Component.translatable("potion.withDuration", line, MobEffectUtil.formatDuration(instance, 1.0F, tickRate));
                if (effect.chance() < 1.0F) {
                    line = Component.translatable("tooltip.sprout_and_soil.chance", line, Math.round(effect.chance() * 100));
                }
                tooltip.add(line.withStyle(holder.value().getCategory().getTooltipFormatting()));
            });
        }
    }

    private static Optional<Holder.Reference<MobEffect>> resolve(ContentManifest.Effect effect) {
        return BuiltInRegistries.MOB_EFFECT.getHolder(effect.effect());
    }
}
