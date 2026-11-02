package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.effect.ErosionEffect;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.network.AetherfallNetwork;
import com.ananttomar.aetherfall.registry.ModParticles;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/**
 * <b>Dive Slam</b> (air only). Rises, roars, locks onto the target's position, then plunges. On impact a shockwave
 * (radius 9) deals heavy falloff damage, launches everyone outward and leaves the boss on the ground. The lock is
 * taken before the dive, so sprinting sideways during the roar dodges it.
 */
public class DiveSlamGoal extends BossAttackGoal {
    private static final double SHOCKWAVE_RADIUS = 9.0D;
    private Vec3 lockPos = Vec3.ZERO;
    private boolean diving;
    private boolean impacted;
    private int impactTick;

    public DiveSlamGoal(AetherfallEntity boss) {
        super(boss, AttackType.DIVE_SLAM);
    }

    @Override
    protected void onStart() {
        diving = false;
        impacted = false;
        boss.playBossSound(ModSounds.WORLD_EATER_WING_FLAP.get(), 3.0F, 0.9F);
    }

    @Override
    protected void onTick() {
        if (impacted) {
            holdStill();
            if (tick - impactTick >= boss.scaled(22)) {
                finish();
            }
            return;
        }
        if (before(18)) {
            boss.flyTowards(boss.position().add(0.0D, 5.0D, 0.0D), 0.6D, 0.2D);
            faceTarget(12.0F);
            return;
        }
        if (at(18)) {
            lockPos = hasTarget() ? target.position() : boss.position().add(boss.forward().scale(10.0D)).add(0.0D, -12.0D, 0.0D);
            boss.playBossSound(ModSounds.WORLD_EATER_ROAR.get(), 4.0F, 1.25F);
            diving = true;
        }
        if (diving) {
            Vec3 to = lockPos.subtract(boss.position());
            double speed = boss.isEnraged() ? 2.1D : 1.7D;
            boss.setDeltaMovement(to.lengthSqr() < 1.0E-4D ? new Vec3(0.0D, -speed, 0.0D) : to.normalize().scale(speed));
            boss.faceTowards(lockPos, 20.0F);
            boolean arrived = boss.position().distanceToSqr(lockPos) < 6.25D;
            if (boss.onGround() || arrived || (boss.verticalCollision && boss.getDeltaMovement().y < 0.0D)) {
                impact();
            } else if (!before(62)) {
                boss.setFlying(false);
                finish();
            }
        }
    }

    private void impact() {
        impacted = true;
        impactTick = tick;
        boss.triggerAnim(AetherfallEntity.ATTACK_CONTROLLER, "dive_impact");
        if (boss.level() instanceof ServerLevel server) {
            AetherfallNetwork.shake(server, boss.position(), 40.0D, 0.9F, 20);
            server.sendParticles(ModParticles.SHOCKWAVE.get(), boss.getX(), boss.getY() + 0.1D, boss.getZ(), 0, SHOCKWAVE_RADIUS, 0.0D, 0.0D, 1.0D);
            server.sendParticles(ModParticles.GOLD_SPARK.get(), boss.getX(), boss.getY() + 0.5D, boss.getZ(), 60, 3.0D, 0.3D, 3.0D, 0.4D);
        }
        diving = false;
        boss.setFlying(false);
        boss.setDeltaMovement(0.0D, -0.5D, 0.0D);
        boss.playBossSound(ModSounds.WORLD_EATER_LAND.get(), 5.0F, 0.85F);
        for (LivingEntity victim : boss.victimsIn(boss.getBoundingBox().inflate(SHOCKWAVE_RADIUS, 3.0D, SHOCKWAVE_RADIUS))) {
            Vec3 out = victim.position().subtract(boss.position());
            Vec3 flat = new Vec3(out.x, 0.0D, out.z);
            double distance = Math.max(0.0D, flat.length() - boss.getBbWidth() / 2.0D);
            if (distance > SHOCKWAVE_RADIUS) {
                continue;
            }
            double falloff = 1.0D - distance / SHOCKWAVE_RADIUS;
            if (boss.dealDamage(victim, ModDamageTypes.VOID_SHOCKWAVE, (float) (6.0D + 24.0D * falloff))) {
                AetherfallEntity.launch(victim, flat, 0.4D + 1.6D * falloff, 0.3D + 0.9D * falloff);
                ErosionEffect.addStack(victim, 1, 160, boss);
            }
        }
    }

    @Override
    protected void onStop() {
        if (!impacted && boss.isFlying() && diving) {
            boss.setFlying(false);
        }
    }
}
