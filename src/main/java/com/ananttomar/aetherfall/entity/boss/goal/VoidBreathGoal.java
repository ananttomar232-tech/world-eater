package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.config.AetherfallConfig;
import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.effect.ErosionEffect;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * <b>Void Breath</b>: a continuous beam of void energy.
 * <ul>
 *     <li>0-30: the jaws gather light (charge sound); the boss tracks its target.</li>
 *     <li>30-100: the beam fires. It turns toward the target at a limited rate, so players can outrun it by moving
 *     sideways, and it stops at the first solid block, so pillars give cover.</li>
 *     <li>Hits deal damage every 4 ticks and add an Erosion stack at most once per second per victim.</li>
 * </ul>
 * The beam's end point is synced every tick for the client renderer.
 */
public class VoidBreathGoal extends BossAttackGoal {
    public static final double RANGE = 48.0D;
    private static final double BEAM_RADIUS = 1.3D;
    private Vec3 beamDir = Vec3.ZERO;
    private final Map<UUID, Integer> lastErosion = new HashMap<>();

    public VoidBreathGoal(AetherfallEntity boss) {
        super(boss, AttackType.VOID_BREATH);
    }

    @Override
    protected void onStart() {
        lastErosion.clear();
        boss.playBossSound(ModSounds.WORLD_EATER_BREATH_CHARGE.get(), 4.0F, 1.0F);
        beamDir = aim();
    }

    @Override
    protected void onTick() {
        holdStill();
        if (before(30)) {
            faceTarget(10.0F);
            beamDir = aim();
            return;
        }
        if (!before(100)) {
            boss.setBeamActive(false);
            return;
        }
        int firing = tick - boss.scaled(30);
        if (firing % 70 == 0) {
            boss.playBossSound(ModSounds.WORLD_EATER_BREATH_LOOP.get(), 4.0F, 1.0F);
        }
        boss.setBeamActive(true);

        // Turn toward the target at a capped angular speed.
        Vec3 desired = aim();
        double maxStep = 0.045D * boss.tempo();
        double angle = Math.acos(Math.max(-1.0D, Math.min(1.0D, beamDir.dot(desired))));
        if (angle > 1.0E-4D) {
            double t = Math.min(1.0D, maxStep / angle);
            beamDir = beamDir.scale(1.0D - t).add(desired.scale(t)).normalize();
        }

        Vec3 origin = boss.mouthPosition();
        Vec3 end = origin.add(beamDir.scale(RANGE));
        BlockHitResult hit = boss.level().clip(new ClipContext(origin, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, boss));
        if (hit.getType() != HitResult.Type.MISS) {
            end = hit.getLocation();
        }
        boss.setBeamEnd(end);
        boss.faceTowards(end, 6.0F);

        if (firing % 4 == 0) {
            burn(origin, end);
        }
        if (firing % 8 == 0 && hit.getType() == HitResult.Type.BLOCK
                && boss.canGrief(AetherfallConfig.COMMON.breathBreaksBlocks.get())) {
            erode(hit.getBlockPos());
        }
    }

    @Override
    protected void onStop() {
        boss.setBeamActive(false);
    }

    private Vec3 aim() {
        Vec3 origin = boss.mouthPosition();
        if (!hasTarget()) {
            return boss.forward();
        }
        Vec3 to = target.position().add(0.0D, target.getBbHeight() * 0.6D, 0.0D).subtract(origin);
        return to.lengthSqr() < 1.0E-4D ? boss.forward() : to.normalize();
    }

    private void burn(Vec3 from, Vec3 to) {
        AABB area = new AABB(from, to).inflate(BEAM_RADIUS + 1.0D);
        for (LivingEntity victim : boss.victimsIn(area)) {
            Vec3 centre = victim.position().add(0.0D, victim.getBbHeight() * 0.5D, 0.0D);
            if (distanceToSegment(centre, from, to) > BEAM_RADIUS + victim.getBbWidth() * 0.5D) {
                continue;
            }
            if (boss.dealDamage(victim, ModDamageTypes.VOID_BREATH, 5.0F)) {
                int last = lastErosion.getOrDefault(victim.getUUID(), -100);
                if (tick - last >= 20) {
                    lastErosion.put(victim.getUUID(), tick);
                    ErosionEffect.addStack(victim, 1, 160, boss);
                }
            }
        }
    }

    private void erode(BlockPos centre) {
        for (BlockPos pos : BlockPos.betweenClosed(centre.offset(-1, -1, -1), centre.offset(1, 1, 1))) {
            BlockState state = boss.level().getBlockState(pos);
            float hardness = state.getDestroySpeed(boss.level(), pos);
            if (!state.isAir() && hardness >= 0.0F && hardness <= 3.0F && !AetherfallEntity.isProtected(state)) {
                boss.level().destroyBlock(pos, false, boss);
            }
        }
    }

    static double distanceToSegment(Vec3 p, Vec3 a, Vec3 b) {
        Vec3 ab = b.subtract(a);
        double lengthSqr = ab.lengthSqr();
        if (lengthSqr < 1.0E-6D) {
            return p.distanceTo(a);
        }
        double t = Math.max(0.0D, Math.min(1.0D, p.subtract(a).dot(ab) / lengthSqr));
        return p.distanceTo(a.add(ab.scale(t)));
    }
}
