package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.effect.ErosionEffect;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/** The boss spins a full turn; the crystal tail hits everything around it and applies one Erosion stack. */
public class TailSweepGoal extends BossAttackGoal {
    private static final double REACH = 7.0D;

    public TailSweepGoal(AetherfallEntity boss) {
        super(boss, AttackType.TAIL_SWEEP);
    }

    @Override
    protected void onTick() {
        holdStill();
        if (at(8)) {
            boss.playBossSound(ModSounds.WORLD_EATER_TAIL_SWEEP.get(), 2.5F, 0.95F);
        }
        if (between(10, 26)) {
            // 360 degrees over 16 tempo ticks
            float step = 360.0F / Math.max(1, boss.scaled(26) - boss.scaled(10));
            boss.setYRot(boss.getYRot() + step);
            boss.yBodyRot = boss.getYRot();
        }
        if (at(18)) {
            strike();
        }
    }

    private void strike() {
        double reach = boss.getBbWidth() / 2.0D + REACH;
        for (LivingEntity victim : boss.victimsIn(boss.getBoundingBox().inflate(reach, 1.0D, reach))) {
            Vec3 to = victim.position().subtract(boss.position());
            Vec3 out = new Vec3(to.x, 0.0D, to.z);
            if (out.length() - victim.getBbWidth() / 2.0D > reach) {
                continue;
            }
            out = out.lengthSqr() < 1.0E-4D ? boss.forward() : out.normalize();
            Vec3 tangent = new Vec3(-out.z, 0.0D, out.x);
            if (boss.dealDamage(victim, ModDamageTypes.WORLD_EATER, 14.0F)) {
                AetherfallEntity.launch(victim, out.scale(0.6D).add(tangent.scale(0.8D)), 2.0D, 0.4D);
                ErosionEffect.addStack(victim, 1, 140, boss);
            }
        }
    }
}
