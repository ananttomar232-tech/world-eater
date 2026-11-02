package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.effect.ErosionEffect;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/**
 * <b>Gravity Well</b> (phase 2+). A singularity forms in the World Eater's jaws and drags everything within 26 blocks
 * toward it for three seconds (stronger the closer you are); standing in the core erodes you. Then it implodes.
 * Counterplay: sprint away, or dig in behind a pillar so the pull pins you to stone instead of the jaws.
 */
public class GravityWellGoal extends BossAttackGoal {
    private static final double PULL_RADIUS = 26.0D;
    private static final double IMPLOSION_RADIUS = 8.0D;

    public GravityWellGoal(AetherfallEntity boss) {
        super(boss, AttackType.GRAVITY_WELL);
    }

    @Override
    protected void onStart() {
        boss.playBossSound(ModSounds.WORLD_EATER_GRAVITY_WELL.get(), 4.0F, 1.0F);
    }

    @Override
    protected void onTick() {
        holdStill();
        faceTarget(6.0F);
        Vec3 well = boss.mouthPosition();
        if (between(10, 62)) {
            for (LivingEntity victim : boss.victimsIn(boss.getBoundingBox().inflate(PULL_RADIUS))) {
                Vec3 to = well.subtract(victim.position());
                double distance = to.length();
                if (distance > PULL_RADIUS || distance < 0.5D) {
                    continue;
                }
                double strength = 0.06D + 0.12D * (1.0D - distance / PULL_RADIUS);
                AetherfallEntity.launch(victim, to, strength, to.y / distance * strength * 0.5D, 0.5D);
                if (distance < 5.0D && tick % 20 == 0) {
                    ErosionEffect.addStack(victim, 1, 120, boss);
                }
            }
        }
        if (at(62)) {
            boss.playBossSound(ModSounds.VOID_METEOR_IMPACT.get(), 4.0F, 0.7F);
            for (LivingEntity victim : boss.victimsIn(boss.getBoundingBox().inflate(IMPLOSION_RADIUS + boss.getBbWidth()))) {
                Vec3 out = victim.position().subtract(well);
                if (out.length() > IMPLOSION_RADIUS) {
                    continue;
                }
                if (boss.dealDamage(victim, ModDamageTypes.VOID_SHOCKWAVE, 16.0F)) {
                    AetherfallEntity.launch(victim, new Vec3(out.x, 0.0D, out.z), 2.2D, 0.8D);
                }
            }
        }
    }
}
