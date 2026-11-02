package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.network.AetherfallNetwork;
import com.ananttomar.aetherfall.registry.ModParticles;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * Phase transition. The World Eater is invulnerable while it ascends: a choir swell, then a roar that plunges
 * everyone within 40 blocks into Darkness, slows them and blasts back anyone within 12.
 */
public class PhaseRoarGoal extends BossAttackGoal {
    private static final double SHOCK_RADIUS = 12.0D;
    private static final double FEAR_RADIUS = 40.0D;

    public PhaseRoarGoal(AetherfallEntity boss) {
        super(boss, AttackType.PHASE_ROAR);
    }

    @Override
    protected void onStart() {
        boss.playBossSound(ModSounds.WORLD_EATER_PHASE_SHIFT.get(), 6.0F, 1.0F);
    }

    @Override
    protected void onTick() {
        holdStill();
        faceTarget(5.0F);
        if (at(22)) {
            boss.playBossSound(ModSounds.WORLD_EATER_ROAR.get(), 6.0F, boss.isEnraged() ? 0.8F : 0.95F);
            if (boss.level() instanceof ServerLevel server) {
                AetherfallNetwork.shake(server, boss.position(), 48.0D, 1.0F, 30);
                server.sendParticles(ModParticles.SHOCKWAVE.get(), boss.getX(), boss.getY() + 0.1D, boss.getZ(), 0, SHOCK_RADIUS + 4.0D, 0.0D, 0.0D, 1.0D);
            }
            for (LivingEntity victim : boss.victimsIn(boss.getBoundingBox().inflate(FEAR_RADIUS))) {
                if (victim instanceof Player) {
                    victim.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 120, 0, false, false, true), boss);
                    victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1, false, true, true), boss);
                }
                Vec3 out = victim.position().subtract(boss.position());
                Vec3 flat = new Vec3(out.x, 0.0D, out.z);
                if (flat.length() - boss.getBbWidth() / 2.0D < SHOCK_RADIUS && boss.dealDamage(victim, ModDamageTypes.VOID_SHOCKWAVE, 8.0F)) {
                    AetherfallEntity.launch(victim, flat, 1.8D, 0.6D);
                }
            }
        }
    }
}
