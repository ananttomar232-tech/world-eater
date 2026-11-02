package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/** Glides down (drifting toward its target) until it touches ground, then lands with a heavy impact. */
public class LandGoal extends BossAttackGoal {
    public LandGoal(AetherfallEntity boss) {
        super(boss, AttackType.LAND);
    }

    @Override
    protected void onTick() {
        faceTarget(6.0F);
        if (boss.onGround()) {
            boss.setFlying(false);
            boss.playBossSound(ModSounds.WORLD_EATER_LAND.get(), 4.0F, 1.0F);
            finish();
            return;
        }
        Vec3 drift = Vec3.ZERO;
        if (hasTarget()) {
            Vec3 to = target.position().subtract(boss.position());
            Vec3 flat = new Vec3(to.x, 0.0D, to.z);
            if (flat.length() > 10.0D) {
                drift = flat.normalize().scale(0.25D);
            }
        }
        Vec3 v = boss.getDeltaMovement();
        boss.setDeltaMovement(v.x * 0.7D + drift.x, -0.45D, v.z * 0.7D + drift.z);
        if (tick % boss.scaled(14) == 0) {
            boss.playBossSound(ModSounds.WORLD_EATER_WING_FLAP.get(), 2.5F, 1.1F);
        }
    }

    @Override
    protected void onStop() {
        if (boss.isFlying()) {
            boss.setFlying(false);
        }
    }
}
