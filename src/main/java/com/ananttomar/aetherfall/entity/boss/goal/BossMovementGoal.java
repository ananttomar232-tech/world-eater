package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.config.AetherfallConfig;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Locomotion between attacks.
 * <ul>
 *     <li>Ground: stalk the target into claw range, then stand and watch.</li>
 *     <li>Air: circle the target at 18 blocks, 12 above, bobbing on its wingbeats.</li>
 *     <li>Both: if summoned by an altar and dragged past the leash radius, return to the temple.</li>
 * </ul>
 */
public class BossMovementGoal extends Goal {
    private static final double ORBIT_RADIUS = 18.0D;
    private static final double ORBIT_HEIGHT = 12.0D;
    private final AetherfallEntity boss;
    private double orbitAngle;

    public BossMovementGoal(AetherfallEntity boss) {
        this.boss = boss;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        return boss.isAlive() && boss.getAttack() == AttackType.NONE;
    }

    @Override
    public boolean canContinueToUse() {
        return canUse();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        LivingEntity target = boss.getTarget();
        if (target != null) {
            orbitAngle = Mth.atan2(boss.getZ() - target.getZ(), boss.getX() - target.getX());
        }
    }

    @Override
    public void tick() {
        LivingEntity target = boss.getTarget();
        BlockPos home = boss.getHomePos();
        int leash = AetherfallConfig.COMMON.arenaLeashRadius.get();
        Vec3 homeCentre = home == null ? null : Vec3.atBottomCenterOf(home);
        boolean leashed = homeCentre != null && leash > 0 && boss.position().distanceToSqr(homeCentre) > (double) leash * leash;
        double speed = boss.isEnraged() ? 1.25D : 1.0D;

        if (boss.isFlying()) {
            if (leashed) {
                boss.flyTowards(homeCentre.add(0.0D, ORBIT_HEIGHT, 0.0D), 0.9D, 0.12D);
            } else if (target != null && target.isAlive()) {
                orbitAngle += 0.022D * boss.tempo();
                double bob = Math.sin(boss.tickCount * 0.08D) * 1.5D;
                Vec3 centre = target.position();
                Vec3 destination = centre.add(Math.cos(orbitAngle) * ORBIT_RADIUS, ORBIT_HEIGHT + bob, Math.sin(orbitAngle) * ORBIT_RADIUS);
                boss.flyTowards(destination, 0.75D * speed, 0.1D);
                boss.getLookControl().setLookAt(target, 20.0F, 30.0F);
            } else {
                boss.setDeltaMovement(boss.getDeltaMovement().scale(0.9D));
            }
            return;
        }

        if (leashed) {
            boss.walkTowards(homeCentre, speed);
        } else if (target != null && target.isAlive()) {
            if (boss.edgeDistanceTo(target) > 3.0D) {
                boss.walkTowards(target.position(), speed);
            } else {
                boss.getMoveControl().setWantedPosition(boss.getX(), boss.getY(), boss.getZ(), 0.0D);
            }
            boss.getLookControl().setLookAt(target, 30.0F, 30.0F);
        }
    }
}
