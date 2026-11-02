package com.ananttomar.aetherfall.gametest;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.effect.ErosionEffect;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.entity.minion.VoidlingEntity;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import com.ananttomar.aetherfall.registry.ModEffects;
import com.ananttomar.aetherfall.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Server-side game tests for the World Eater's systems. Run with {@code ./gradlew runGameTestServer}.
 * <p>
 * Every test runs the real entity, goals and damage code in a live world. The boss fights an iron golem dummy
 * (no AI, 5000 HP) because game tests have no real players. Each test is its own batch so the boss's area attacks
 * never leak into a neighbouring test.
 */
@GameTestHolder(AetherfallMod.MOD_ID)
@PrefixGameTestTemplate(false)
public final class AetherfallGameTests {
    private static final String ARENA = "gametest/arena";
    /** Helper coordinates: the arena structure sits one block above the test origin, so its floor is y = 1. */
    private static final BlockPos BOSS_POS = new BlockPos(20, 2, 20);

    private AetherfallGameTests() {
    }

    // ------------------------------------------------------------------------------------------------------------
    // Spawning, scaling, phases, damage rules
    // ------------------------------------------------------------------------------------------------------------

    @GameTest(template = ARENA, batch = "scaling", timeoutTicks = 100)
    public static void bossAppliesConfigScalingOnFirstTick(GameTestHelper helper) {
        AetherfallEntity boss = helper.spawn(ModEntities.WORLD_EATER.get(), BOSS_POS);
        helper.runAfterDelay(5, () -> {
            helper.assertTrue(boss.getMaxHealth() >= 900.0F, "Max health should come from config, was " + boss.getMaxHealth());
            helper.assertTrue(Math.abs(boss.getHealth() - boss.getMaxHealth()) < 0.01F, "Boss should start at full health");
            helper.assertTrue(boss.getPhase() == 1, "Boss should start in phase 1");
            helper.succeed();
        });
    }

    @GameTest(template = ARENA, batch = "phase", timeoutTicks = 200)
    public static void crossingThresholdTriggersInvulnerablePhaseRoar(GameTestHelper helper) {
        AetherfallEntity boss = helper.spawn(ModEntities.WORLD_EATER.get(), BOSS_POS);
        helper.startSequence()
                .thenIdle(3)
                .thenExecute(() -> {
                    boss.setHealth(boss.getMaxHealth() * 0.67F);
                    boss.hurt(helper.getLevel().damageSources().generic(), 20.0F);
                })
                .thenWaitUntil(() -> helper.assertTrue(boss.getAttack() == AttackType.PHASE_ROAR, "Phase roar should start"))
                .thenExecute(() -> {
                    helper.assertTrue(boss.getPhase() == 2, "Boss should be in phase 2, was " + boss.getPhase());
                    float before = boss.getHealth();
                    boss.hurt(helper.getLevel().damageSources().generic(), 50.0F);
                    helper.assertTrue(boss.getHealth() == before, "Boss must be invulnerable during the phase roar");
                })
                .thenWaitUntil(() -> helper.assertTrue(boss.getAttack() == AttackType.NONE, "Phase roar should finish"))
                .thenSucceed();
    }

    @GameTest(template = ARENA, batch = "cap", timeoutTicks = 100)
    public static void singleHitIsCappedAtFivePercent(GameTestHelper helper) {
        AetherfallEntity boss = helper.spawn(ModEntities.WORLD_EATER.get(), BOSS_POS);
        helper.runAfterDelay(5, () -> {
            float before = boss.getHealth();
            boss.hurt(helper.getLevel().damageSources().generic(), 100000.0F);
            float lost = before - boss.getHealth();
            helper.assertTrue(lost > 0.0F && lost <= boss.getMaxHealth() * AetherfallEntity.MAX_HIT_FRACTION + 0.01F,
                    "Hit should be capped at 5% of max health, lost " + lost);
            helper.succeed();
        });
    }

    @GameTest(template = ARENA, batch = "death", timeoutTicks = 300)
    public static void deathSequenceRemovesBossAndDissolvesBrood(GameTestHelper helper) {
        AetherfallEntity boss = helper.spawn(ModEntities.WORLD_EATER.get(), BOSS_POS);
        VoidlingEntity voidling = helper.spawn(ModEntities.VOIDLING.get(), new BlockPos(5, 2, 5));
        voidling.setOwner(boss);
        helper.startSequence()
                .thenIdle(3)
                .thenExecute(boss::kill)
                .thenWaitUntil(() -> helper.assertTrue(voidling.isRemoved(), "Voidlings should dissolve when their summoner dies"))
                .thenExecute(() -> helper.assertFalse(boss.isRemoved(), "The death sequence should still be playing"))
                .thenWaitUntil(() -> helper.assertTrue(boss.isRemoved(), "Boss should be removed after its death sequence"))
                .thenSucceed();
    }

    // ------------------------------------------------------------------------------------------------------------
    // The attack director
    // ------------------------------------------------------------------------------------------------------------

    @GameTest(template = ARENA, batch = "director", timeoutTicks = 400)
    public static void directorChoosesAttacksOnItsOwn(GameTestHelper helper) {
        AetherfallEntity boss = helper.spawn(ModEntities.WORLD_EATER.get(), BOSS_POS);
        IronGolem dummy = dummy(helper, new BlockPos(20, 2, 30));
        boss.setTarget(dummy);
        helper.succeedWhen(() -> helper.assertTrue(boss.getAttack() != AttackType.NONE, "Boss should start an attack by itself"));
    }

    // ------------------------------------------------------------------------------------------------------------
    // Every attack, run end to end
    // ------------------------------------------------------------------------------------------------------------

    @GameTest(template = ARENA, batch = "swipe", timeoutTicks = 200)
    public static void swipeDamagesAndLaunches(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.SWIPE, 1, false, new BlockPos(20, 2, 25));
        run.then(() -> helper.assertTrue(run.dummy.getHealth() < run.dummy.getMaxHealth(), "Swipe should damage the target"));
    }

    @GameTest(template = ARENA, batch = "tail", timeoutTicks = 200)
    public static void tailSweepHitsAllAroundAndErodes(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.TAIL_SWEEP, 1, false, new BlockPos(14, 2, 20));
        run.then(() -> {
            helper.assertTrue(run.dummy.getHealth() < run.dummy.getMaxHealth(), "Tail sweep should damage the target");
            helper.assertTrue(run.dummy.hasEffect(ModEffects.EROSION.get()), "Tail sweep should apply Erosion");
        });
    }

    @GameTest(template = ARENA, batch = "breath", timeoutTicks = 300)
    public static void voidBreathBurnsAndErodes(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.VOID_BREATH, 1, false, new BlockPos(20, 2, 34));
        AtomicBoolean beamSeen = new AtomicBoolean();
        helper.onEachTick(() -> {
            if (run.boss.isBeamActive()) {
                beamSeen.set(true);
            }
        });
        run.then(() -> {
            helper.assertTrue(beamSeen.get(), "Beam should have been active");
            helper.assertFalse(run.boss.isBeamActive(), "Beam should switch off when the attack ends");
            helper.assertTrue(run.dummy.getHealth() < run.dummy.getMaxHealth(), "Beam should damage the target");
            MobEffectInstance erosion = run.dummy.getEffect(ModEffects.EROSION.get());
            helper.assertTrue(erosion != null && erosion.getAmplifier() >= 1, "Beam should stack Erosion");
        });
    }

    @GameTest(template = ARENA, batch = "meteor", timeoutTicks = 400)
    public static void meteorShowerRainsMeteorsThatSpareTheBoss(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.METEOR_SHOWER, 2, false, new BlockPos(20, 2, 36));
        AtomicInteger maxMeteors = new AtomicInteger();
        helper.onEachTick(() -> {
            int count = helper.getLevel().getEntitiesOfClass(VoidMeteorEntity.class, run.boss.getBoundingBox().inflate(80.0D)).size();
            maxMeteors.accumulateAndGet(count, Math::max);
        });
        run.then(() -> {
            helper.assertTrue(maxMeteors.get() >= 3, "Meteors should fall, saw at most " + maxMeteors.get());
            helper.assertTrue(run.boss.getHealth() == run.boss.getMaxHealth(), "Meteors must never hurt the World Eater");
        });
    }

    @GameTest(template = ARENA, batch = "gust", timeoutTicks = 200)
    public static void wingGustHurlsTargetAway(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.WING_GUST, 1, false, new BlockPos(20, 2, 30));
        run.then(() -> helper.assertTrue(run.dummy.getHealth() < run.dummy.getMaxHealth(), "Wing gust should hit the target"));
    }

    @GameTest(template = ARENA, batch = "dive", timeoutTicks = 300)
    public static void diveSlamEndsOnTheGround(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.DIVE_SLAM, 1, true, new BlockPos(20, 2, 30));
        run.then(() -> {
            helper.assertFalse(run.boss.isFlying(), "Dive slam should end grounded");
            helper.assertTrue(run.dummy.getHealth() < run.dummy.getMaxHealth(), "Dive slam shockwave should hit the target");
        });
    }

    @GameTest(template = ARENA, batch = "well", timeoutTicks = 300)
    public static void gravityWellPullsTargetsIn(GameTestHelper helper) {
        AetherfallEntity boss = helper.spawn(ModEntities.WORLD_EATER.get(), BOSS_POS);
        // A NoAI mob never applies its velocity, so the pull needs a dummy that can move: AI on, every goal removed.
        IronGolem dummy = dummy(helper, new BlockPos(20, 2, 36));
        dummy.setNoAi(false);
        dummy.goalSelector.removeAllGoals(goal -> true);
        dummy.targetSelector.removeAllGoals(goal -> true);
        AttackRun run = new AttackRun(helper, boss, dummy, AttackType.GRAVITY_WELL, 2, false);
        run.then(() -> helper.assertTrue(run.dummy.position().z < run.start.z - 1.0D,
                "Gravity well should drag the target toward the boss (z " + run.start.z + " -> " + run.dummy.position().z + ")"));
    }

    @GameTest(template = ARENA, batch = "summon", timeoutTicks = 200)
    public static void summonCallsBoundVoidlings(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.SUMMON_VOIDLINGS, 2, false, new BlockPos(20, 2, 34));
        run.then(() -> helper.assertTrue(run.boss.countVoidlings() >= 3, "Expected at least 3 Voidlings, got " + run.boss.countVoidlings()));
    }

    @GameTest(template = ARENA, batch = "takeoff", timeoutTicks = 200)
    public static void takeoffLeavesTheGround(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.TAKEOFF, 1, false, new BlockPos(20, 2, 34));
        run.then(() -> {
            helper.assertTrue(run.boss.isFlying(), "Boss should be flying after takeoff");
            helper.assertTrue(run.boss.getY() > run.bossStart.y + 5.0D, "Boss should have climbed, y=" + run.boss.getY());
        });
    }

    @GameTest(template = ARENA, batch = "land", timeoutTicks = 200)
    public static void landReturnsToTheGround(GameTestHelper helper) {
        AttackRun run = attack(helper, AttackType.LAND, 1, true, new BlockPos(20, 2, 34));
        run.then(() -> {
            helper.assertFalse(run.boss.isFlying(), "Boss should be grounded after landing");
            helper.assertTrue(run.boss.onGround(), "Boss should be standing on the floor");
        });
    }

    // ------------------------------------------------------------------------------------------------------------
    // Erosion
    // ------------------------------------------------------------------------------------------------------------

    @GameTest(template = ARENA, batch = "erosion", timeoutTicks = 100)
    public static void erosionStacksToFiveAndStripsArmor(GameTestHelper helper) {
        IronGolem dummy = dummy(helper, new BlockPos(20, 2, 20));
        double armorBefore = dummy.getAttributeValue(Attributes.ARMOR);
        int stacks = 0;
        for (int i = 0; i < 7; i++) {
            stacks = ErosionEffect.addStack(dummy, 1, 200, null);
        }
        helper.assertTrue(stacks == ErosionEffect.MAX_STACKS, "Erosion should cap at 5 stacks, got " + stacks);
        MobEffectInstance instance = dummy.getEffect(ModEffects.EROSION.get());
        helper.assertTrue(instance != null && instance.getAmplifier() == ErosionEffect.MAX_STACKS - 1, "Amplifier should be 4");
        double armorAfter = dummy.getAttributeValue(Attributes.ARMOR);
        helper.assertTrue(armorBefore - armorAfter >= 9.99D || armorAfter == 0.0D,
                "5 stacks should strip 10 armor (" + armorBefore + " -> " + armorAfter + ")");
        helper.assertTrue(ErosionEffect.healingFactor(dummy) == 0.0F, "5 stacks should block all healing");
        float health = dummy.getHealth();
        dummy.heal(10.0F);
        helper.assertTrue(dummy.getHealth() == health, "Healing must be blocked at 5 stacks");
        helper.succeed();
    }

    // ------------------------------------------------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------------------------------------------------

    private static IronGolem dummy(GameTestHelper helper, BlockPos pos) {
        IronGolem golem = helper.spawnWithNoFreeWill(EntityType.IRON_GOLEM, pos);
        golem.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000.0D);
        golem.setHealth(golem.getMaxHealth());
        golem.setPersistenceRequired();
        return golem;
    }

    /** Spawns the boss and a dummy, forces one attack, and waits for it to start and finish. */
    private static AttackRun attack(GameTestHelper helper, AttackType type, int phase, boolean flying, BlockPos dummyPos) {
        AetherfallEntity boss = helper.spawn(ModEntities.WORLD_EATER.get(), BOSS_POS);
        IronGolem dummy = dummy(helper, dummyPos);
        return new AttackRun(helper, boss, dummy, type, phase, flying);
    }

    private static final class AttackRun {
        final GameTestHelper helper;
        final AetherfallEntity boss;
        final LivingEntity dummy;
        final AttackType type;
        final int phase;
        final boolean flying;
        Vec3 start = Vec3.ZERO;
        Vec3 bossStart = Vec3.ZERO;

        AttackRun(GameTestHelper helper, AetherfallEntity boss, LivingEntity dummy, AttackType type, int phase, boolean flying) {
            this.helper = helper;
            this.boss = boss;
            this.dummy = dummy;
            this.type = type;
            this.phase = phase;
            this.flying = flying;
        }

        void then(Runnable assertions) {
            helper.startSequence()
                    .thenIdle(3)
                    .thenExecute(() -> {
                        boss.forcePhase(phase);
                        if (flying) {
                            boss.setFlying(true);
                            boss.setPos(boss.getX(), boss.getY() + 10.0D, boss.getZ());
                        }
                        boss.setTarget(dummy);
                        start = dummy.position();
                        bossStart = boss.position();
                        boss.queueAttack(type);
                    })
                    .thenWaitUntil(() -> helper.assertTrue(boss.getAttack() == type, type + " should start"))
                    .thenWaitUntil(() -> helper.assertTrue(boss.getAttack() != type, type + " should finish"))
                    .thenExecute(assertions)
                    .thenExecute(() -> clearArea(helper, boss))
                    .thenSucceed();
        }
    }

    private static void clearArea(GameTestHelper helper, AetherfallEntity boss) {
        AABB area = boss.getBoundingBox().inflate(96.0D);
        helper.getLevel().getEntitiesOfClass(VoidMeteorEntity.class, area).forEach(VoidMeteorEntity::discard);
        helper.getLevel().getEntitiesOfClass(VoidlingEntity.class, area).forEach(VoidlingEntity::discard);
    }
}
