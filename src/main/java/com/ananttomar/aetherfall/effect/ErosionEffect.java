package com.ananttomar.aetherfall.effect;

import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.registry.ModEffects;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import org.jetbrains.annotations.Nullable;

/**
 * <b>Erosion</b>: the void eating away at matter. Stacks up to {@value #MAX_STACKS} times (amplifier 0..4).
 * <ul>
 *     <li>Each stack strips 2 armor and 1 armor toughness.</li>
 *     <li>Each stack reduces all healing by 20% (handled in {@code CommonEvents}); 5 stacks stop healing entirely.</li>
 *     <li>From 3 stacks, the void starts to consume the body: armor-piercing damage that ticks faster per stack.</li>
 * </ul>
 * Apply it with {@link #addStack} so stacks accumulate instead of replacing each other.
 */
public class ErosionEffect extends MobEffect {
    public static final int MAX_STACKS = 5;
    public static final int COLOR = 0x6D1FB8;
    private static final String ARMOR_UUID = "5c8a6c1e-6a3a-4a8e-9a4a-0b6e1f0a7e01";
    private static final String TOUGHNESS_UUID = "5c8a6c1e-6a3a-4a8e-9a4a-0b6e1f0a7e02";

    public ErosionEffect() {
        super(MobEffectCategory.HARMFUL, COLOR);
        addAttributeModifier(Attributes.ARMOR, ARMOR_UUID, -2.0D, AttributeModifier.Operation.ADDITION);
        addAttributeModifier(Attributes.ARMOR_TOUGHNESS, TOUGHNESS_UUID, -1.0D, AttributeModifier.Operation.ADDITION);
    }

    @Override
    public boolean isDurationEffectTick(int duration, int amplifier) {
        if (amplifier < 2) {
            return false;
        }
        int interval = Math.max(10, 50 - (amplifier - 2) * 15);
        return duration % interval == 0;
    }

    @Override
    public void applyEffectTick(LivingEntity entity, int amplifier) {
        entity.hurt(ModDamageTypes.source(entity.level(), ModDamageTypes.EROSION, null), 1.0F + (amplifier - 2) * 0.5F);
    }

    /** Fraction of healing that still gets through (1.0 = unaffected, 0.0 = none). */
    public static float healingFactor(LivingEntity entity) {
        MobEffectInstance instance = entity.getEffect(ModEffects.EROSION.get());
        if (instance == null) {
            return 1.0F;
        }
        return Math.max(0.0F, 1.0F - 0.2F * (instance.getAmplifier() + 1));
    }

    /**
     * Adds one Erosion stack (or {@code stacks}), refreshing duration to at least {@code durationTicks}.
     *
     * @return the new stack count, or 0 if the target is immune.
     */
    public static int addStack(LivingEntity target, int stacks, int durationTicks, @Nullable Entity source) {
        MobEffect erosion = ModEffects.EROSION.get();
        if (!target.canBeAffected(new MobEffectInstance(erosion, durationTicks))) {
            return 0;
        }
        MobEffectInstance current = target.getEffect(erosion);
        int amplifier = current == null ? stacks - 1 : Math.min(MAX_STACKS - 1, current.getAmplifier() + stacks);
        amplifier = Math.min(MAX_STACKS - 1, amplifier);
        int duration = current == null ? durationTicks : Math.max(current.getDuration(), durationTicks);
        if (current != null) {
            // Remove first so the attribute modifiers are re-applied at the new amplifier.
            target.removeEffect(erosion);
        }
        target.addEffect(new MobEffectInstance(erosion, duration, amplifier, false, true, true), source);
        if (current == null || amplifier > current.getAmplifier()) {
            target.level().playSound(null, target.getX(), target.getY(), target.getZ(), ModSounds.EROSION_APPLY.get(),
                    SoundSource.HOSTILE, 0.8F, 0.9F + 0.05F * amplifier);
        }
        return amplifier + 1;
    }
}
