package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;

/**
 * Base for every World Eater action.
 * <p>
 * A goal runs only when the boss's attack director has queued its {@link AttackType}. It owns movement, look and
 * jump while active (so locomotion pauses), and reports start/end back to the boss, which syncs the attack id to
 * clients for animation. Timings are authored at tempo 1.0 and converted with {@link #at}/{@link #between}, so the
 * whole attack, including its animation, speeds up in later phases.
 */
public abstract class BossAttackGoal extends Goal {
    protected final AetherfallEntity boss;
    protected final AttackType type;
    protected int tick;
    protected int duration;
    @Nullable
    protected LivingEntity target;
    private boolean finished;

    protected BossAttackGoal(AetherfallEntity boss, AttackType type) {
        this.boss = boss;
        this.type = type;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        return boss.getQueuedAttack() == type && boss.isAlive();
    }

    @Override
    public boolean canContinueToUse() {
        if (finished || tick >= duration || !boss.isAlive() || boss.getAttack() != type) {
            return false;
        }
        return type == AttackType.PHASE_ROAR || boss.getQueuedAttack() != AttackType.PHASE_ROAR;
    }

    @Override
    public boolean isInterruptable() {
        return true;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public final void start() {
        tick = 0;
        finished = false;
        duration = boss.scaled(type.duration);
        target = boss.getTarget();
        boss.getNavigation().stop();
        boss.beginAttack(type);
        onStart();
    }

    @Override
    public final void tick() {
        tick++;
        LivingEntity current = boss.getTarget();
        if (current != null && current.isAlive()) {
            target = current;
        }
        onTick();
    }

    @Override
    public final void stop() {
        onStop();
        boss.endAttack(type);
    }

    protected void onStart() {
    }

    protected abstract void onTick();

    protected void onStop() {
    }

    /** True exactly once, on the tick matching {@code baseTick} at the current tempo. */
    protected boolean at(int baseTick) {
        return tick == boss.scaled(baseTick);
    }

    /** True while the current tick lies in [{@code from}, {@code to}) at the current tempo. */
    protected boolean between(int from, int to) {
        return tick >= boss.scaled(from) && tick < boss.scaled(to);
    }

    protected boolean before(int baseTick) {
        return tick < boss.scaled(baseTick);
    }

    protected void finish() {
        finished = true;
    }

    protected boolean hasTarget() {
        return target != null && target.isAlive();
    }

    /** Plants the boss in place on the ground, or bleeds off speed in the air. */
    protected void holdStill() {
        if (boss.isFlying()) {
            boss.setDeltaMovement(boss.getDeltaMovement().scale(0.75D));
        } else {
            boss.getMoveControl().setWantedPosition(boss.getX(), boss.getY(), boss.getZ(), 0.0D);
            boss.setZza(0.0F);
            boss.setXxa(0.0F);
        }
    }

    protected void faceTarget(float maxTurn) {
        if (hasTarget()) {
            boss.faceTowards(target.position().add(0.0D, target.getBbHeight() * 0.5D, 0.0D), maxTurn);
        }
    }
}
