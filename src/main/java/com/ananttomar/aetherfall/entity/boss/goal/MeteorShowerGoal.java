package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * <b>Meteor Shower</b> (ultimate, phase 2+). The World Eater rears up and roars at the sky; the heavens crack and
 * flaming void meteors rain around every combatant for four seconds. 40% of meteors lead their target (aimed where
 * it will be in a second), the rest scatter so standing still is never safe. Enraged: denser and heavier.
 */
public class MeteorShowerGoal extends BossAttackGoal {
    private static final double TARGET_RADIUS = 48.0D;

    public MeteorShowerGoal(AetherfallEntity boss) {
        super(boss, AttackType.METEOR_SHOWER);
    }

    @Override
    protected void onStart() {
        boss.playBossSound(ModSounds.WORLD_EATER_ROAR.get(), 5.0F, 0.9F);
    }

    @Override
    protected void onTick() {
        holdStill();
        faceTarget(4.0F);
        if (at(14)) {
            boss.playBossSound(ModSounds.WORLD_EATER_METEOR_SUMMON.get(), 6.0F, 1.0F);
        }
        if (between(30, 118)) {
            int interval = boss.isEnraged() ? 3 : 5;
            if ((tick - boss.scaled(30)) % interval == 0) {
                for (LivingEntity victim : targets()) {
                    rainOn(victim);
                }
            }
        }
    }

    private List<LivingEntity> targets() {
        List<LivingEntity> list = new ArrayList<>();
        for (LivingEntity e : boss.victimsIn(boss.getBoundingBox().inflate(TARGET_RADIUS))) {
            if (e instanceof Player || e == target) {
                list.add(e);
            }
        }
        if (list.isEmpty() && hasTarget()) {
            list.add(target);
        }
        return list;
    }

    private void rainOn(LivingEntity victim) {
        RandomSource random = boss.getRandom();
        Vec3 aimPoint;
        if (random.nextFloat() < 0.4F) {
            aimPoint = victim.position().add(victim.getDeltaMovement().multiply(20.0D, 0.0D, 20.0D));
        } else {
            double angle = random.nextDouble() * Math.PI * 2.0D;
            double radius = 2.0D + random.nextDouble() * 10.0D;
            aimPoint = victim.position().add(Math.cos(angle) * radius, 0.0D, Math.sin(angle) * radius);
        }
        double skew = random.nextDouble() * Math.PI * 2.0D;
        Vec3 start = aimPoint.add(Math.cos(skew) * (8.0D + random.nextDouble() * 6.0D), 30.0D + random.nextDouble() * 8.0D,
                Math.sin(skew) * (8.0D + random.nextDouble() * 6.0D));
        double speed = (boss.isEnraged() ? 1.8D : 1.4D) + random.nextDouble() * 0.3D;
        Vec3 velocity = aimPoint.subtract(start).normalize().scale(speed);
        boss.level().addFreshEntity(VoidMeteorEntity.create(boss.level(), boss, start, velocity, boss.isEnraged()));
    }
}
