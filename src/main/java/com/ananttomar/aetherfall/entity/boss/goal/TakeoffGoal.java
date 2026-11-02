package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/** Crouch, then three mighty wingbeats lift the boss roughly 12 blocks into the air. */
public class TakeoffGoal extends BossAttackGoal {
    public TakeoffGoal(AetherfallEntity boss) {
        super(boss, AttackType.TAKEOFF);
    }

    @Override
    protected void onTick() {
        faceTarget(8.0F);
        if (before(8)) {
            holdStill();
            return;
        }
        if (at(8)) {
            boss.setNoGravity(true);
            boss.playBossSound(ModSounds.WORLD_EATER_TAKEOFF.get(), 4.0F, 1.0F);
        }
        if (before(34)) {
            Vec3 v = boss.getDeltaMovement();
            boss.setDeltaMovement(v.x * 0.8D, 0.45D, v.z * 0.8D);
        } else {
            boss.setFlying(true);
            finish();
        }
    }

    @Override
    protected void onStop() {
        if (!boss.isFlying() && tick >= boss.scaled(8)) {
            boss.setFlying(true);
        }
    }
}
