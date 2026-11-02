package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.network.AetherfallNetwork;
import com.ananttomar.aetherfall.registry.ModParticles;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.phys.Vec3;

/** Glides down (drifting toward its target) until it touches ground, then lands with a heavy impact. */
public class LandGoal extends BossAttackGoal {
    private boolean landed;
    private int landTick;

    public LandGoal(AetherfallEntity boss) {
        super(boss, AttackType.LAND);
    }

    @Override
    protected void onStart() {
        landed = false;
    }

    @Override
    protected void onTick() {
        faceTarget(6.0F);
        if (landed) {
            holdStill();
            if (tick - landTick >= boss.scaled(18)) {
                finish();
            }
            return;
        }
        if (boss.onGround()) {
            landed = true;
            landTick = tick;
            boss.setFlying(false);
            boss.triggerAnim(AetherfallEntity.ATTACK_CONTROLLER, "land_impact");
            boss.playBossSound(ModSounds.WORLD_EATER_LAND.get(), 4.0F, 1.0F);
            if (boss.level() instanceof ServerLevel server) {
                AetherfallNetwork.shake(server, boss.position(), 32.0D, 0.5F, 12);
                server.sendParticles(ModParticles.SHOCKWAVE.get(), boss.getX(), boss.getY() + 0.1D, boss.getZ(), 0, 6.0D, 0.0D, 0.0D, 1.0D);
            }
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
