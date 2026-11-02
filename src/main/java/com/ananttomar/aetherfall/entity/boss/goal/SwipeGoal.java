package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/** Claw rake across a 130 degree front arc. Heavy knockback, disables shields. Hit frame at tick 14. */
public class SwipeGoal extends BossAttackGoal {
    private static final double REACH = 6.0D;
    private static final double ARC_COS = Math.cos(Math.toRadians(65.0D));

    public SwipeGoal(AetherfallEntity boss) {
        super(boss, AttackType.SWIPE);
    }

    @Override
    protected void onTick() {
        holdStill();
        if (before(12)) {
            faceTarget(18.0F);
        }
        if (at(8)) {
            boss.playBossSound(ModSounds.WORLD_EATER_SWIPE.get(), 2.5F, 0.9F + boss.getRandom().nextFloat() * 0.2F);
        }
        if (at(14)) {
            strike();
        }
    }

    private void strike() {
        double reach = boss.getBbWidth() / 2.0D + REACH;
        Vec3 forward = boss.forward();
        float damage = (float) boss.getAttributeValue(Attributes.ATTACK_DAMAGE);
        for (LivingEntity victim : boss.victimsIn(boss.getBoundingBox().inflate(reach, 1.5D, reach))) {
            Vec3 to = victim.position().subtract(boss.position());
            Vec3 flat = new Vec3(to.x, 0.0D, to.z);
            double distance = flat.length() - victim.getBbWidth() / 2.0D;
            if (distance > reach) {
                continue;
            }
            boolean inArc = flat.lengthSqr() < 1.0E-4D || flat.normalize().dot(forward) >= ARC_COS;
            boolean pressedAgainst = distance < boss.getBbWidth() / 2.0D + 1.5D;
            if (!inArc && !pressedAgainst) {
                continue;
            }
            if (boss.dealDamage(victim, ModDamageTypes.WORLD_EATER, damage)) {
                AetherfallEntity.launch(victim, flat, 2.4D, 0.55D);
                if (victim instanceof Player player && player.isBlocking()) {
                    player.disableShield(true);
                }
            }
        }
    }
}
