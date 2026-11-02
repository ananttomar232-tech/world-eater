package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * <b>Wing Gust</b>: one colossal downbeat. A 90 degree cone of wind, 18 blocks long, hurls everything away and
 * reflects incoming projectiles back at their shooters (arrows, tridents and fireballs all count).
 */
public class WingGustGoal extends BossAttackGoal {
    private static final double LENGTH = 18.0D;
    private static final double CONE_COS = Math.cos(Math.toRadians(45.0D));

    public WingGustGoal(AetherfallEntity boss) {
        super(boss, AttackType.WING_GUST);
    }

    @Override
    protected void onTick() {
        holdStill();
        if (before(12)) {
            faceTarget(15.0F);
        }
        if (at(6)) {
            boss.playBossSound(ModSounds.WORLD_EATER_WING_FLAP.get(), 3.0F, 0.85F);
        }
        if (at(14)) {
            boss.playBossSound(ModSounds.WORLD_EATER_WING_GUST.get(), 4.0F, 1.0F);
            blast();
        }
    }

    private void blast() {
        Vec3 origin = boss.position().add(0.0D, boss.getBbHeight() * 0.4D, 0.0D);
        Vec3 forward = boss.forward();
        AABB area = boss.getBoundingBox().inflate(LENGTH, 6.0D, LENGTH);
        for (LivingEntity victim : boss.victimsIn(area)) {
            Vec3 to = victim.position().subtract(origin);
            Vec3 flat = new Vec3(to.x, 0.0D, to.z);
            double distance = flat.length();
            if (distance > LENGTH + boss.getBbWidth() / 2.0D || distance < 1.0E-3D || flat.normalize().dot(forward) < CONE_COS) {
                continue;
            }
            double falloff = 1.0D - Math.min(1.0D, distance / (LENGTH + boss.getBbWidth() / 2.0D)) * 0.6D;
            boss.dealDamage(victim, ModDamageTypes.WORLD_EATER, 6.0F);
            AetherfallEntity.launch(victim, flat, 3.0D * falloff, 0.7D * falloff);
        }
        for (Projectile projectile : boss.level().getEntitiesOfClass(Projectile.class, area,
                p -> !(p instanceof VoidMeteorEntity) && p.getOwner() != boss)) {
            Vec3 to = projectile.position().subtract(origin);
            Vec3 flat = new Vec3(to.x, 0.0D, to.z);
            if (flat.lengthSqr() > 1.0E-3D && flat.normalize().dot(forward) >= CONE_COS) {
                projectile.setDeltaMovement(projectile.getDeltaMovement().scale(-1.3D));
                projectile.setOwner(boss);
                projectile.hasImpulse = true;
            }
        }
        if (boss.isFlying()) {
            boss.setDeltaMovement(boss.getDeltaMovement().add(forward.scale(-0.6D)));
        }
    }
}
