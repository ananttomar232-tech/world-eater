package com.ananttomar.aetherfall.entity.boss;

import com.ananttomar.aetherfall.config.AetherfallConfig;
import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.entity.boss.goal.BossMovementGoal;
import com.ananttomar.aetherfall.entity.boss.goal.DiveSlamGoal;
import com.ananttomar.aetherfall.entity.boss.goal.GravityWellGoal;
import com.ananttomar.aetherfall.entity.boss.goal.LandGoal;
import com.ananttomar.aetherfall.entity.boss.goal.MeteorShowerGoal;
import com.ananttomar.aetherfall.entity.boss.goal.PhaseRoarGoal;
import com.ananttomar.aetherfall.entity.boss.goal.SummonVoidlingsGoal;
import com.ananttomar.aetherfall.entity.boss.goal.SwipeGoal;
import com.ananttomar.aetherfall.entity.boss.goal.TailSweepGoal;
import com.ananttomar.aetherfall.entity.boss.goal.TakeoffGoal;
import com.ananttomar.aetherfall.entity.boss.goal.VoidBreathGoal;
import com.ananttomar.aetherfall.entity.boss.goal.WingGustGoal;
import com.ananttomar.aetherfall.entity.minion.VoidlingEntity;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import com.ananttomar.aetherfall.network.AetherfallNetwork;
import com.ananttomar.aetherfall.network.BossBarMarkerMessage;
import com.ananttomar.aetherfall.registry.ModEffects;
import com.ananttomar.aetherfall.registry.ModParticles;
import com.ananttomar.aetherfall.registry.ModSounds;
import com.ananttomar.aetherfall.tag.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.Difficulty;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.ForgeEventFactory;
import org.jetbrains.annotations.Nullable;
import org.joml.Vector3f;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * <h2>Aetherfall, the World Eater</h2>
 * A colossal void dragon that fights on the ground and in the air.
 *
 * <h3>Phases</h3>
 * <ol>
 *     <li>100-66%: claws, tail, breath, wing gust, takeoff and dive.</li>
 *     <li>66-33%: adds Meteor Shower, Gravity Well and Voidlings. Every action is 15% faster.</li>
 *     <li>Below 33%: <b>enraged</b>. 35% faster, faster movement, denser meteor storms.</li>
 * </ol>
 * Crossing a threshold interrupts the current attack with an invulnerable {@link AttackType#PHASE_ROAR}.
 *
 * <h3>AI</h3>
 * An attack director ({@link #chooseAttack}) picks a weighted-random action whenever the boss is free, filtered by
 * phase, ground or air, distance and line of sight. Each action is its own {@link net.minecraft.world.entity.ai.goal.Goal}
 * (package {@code goal}) that runs only when the director queues it, so attacks never overlap. Between attacks
 * {@link BossMovementGoal} walks it into claw range or circles it through the air.
 *
 * <h3>Animation</h3>
 * Two GeckoLib controllers: {@code body} (idle, walk, hover, glide, death) and {@code attack} (one clip per
 * {@link AttackType}), layered so locomotion keeps playing on bones an attack doesn't animate. The current attack and
 * a serial number are synced, so clients restart the clip exactly when the server starts an attack.
 */
public class AetherfallEntity extends Monster implements GeoEntity {
    // Synced state
    private static final EntityDataAccessor<Integer> DATA_ATTACK = SynchedEntityData.defineId(AetherfallEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_ATTACK_SERIAL = SynchedEntityData.defineId(AetherfallEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_FLYING = SynchedEntityData.defineId(AetherfallEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> DATA_PHASE = SynchedEntityData.defineId(AetherfallEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_BEAM_ACTIVE = SynchedEntityData.defineId(AetherfallEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Vector3f> DATA_BEAM_END = SynchedEntityData.defineId(AetherfallEntity.class, EntityDataSerializers.VECTOR3);

    // Animations
    public static final String ANIM_PREFIX = "animation.world_eater.";
    public static final String ATTACK_CONTROLLER = "attack";
    public static final RawAnimation IDLE = RawAnimation.begin().thenLoop(ANIM_PREFIX + "idle");
    public static final RawAnimation WALK = RawAnimation.begin().thenLoop(ANIM_PREFIX + "walk");
    public static final RawAnimation FLY_HOVER = RawAnimation.begin().thenLoop(ANIM_PREFIX + "fly_hover");
    public static final RawAnimation FLY_GLIDE = RawAnimation.begin().thenLoop(ANIM_PREFIX + "fly_glide");
    public static final RawAnimation DEATH = RawAnimation.begin().thenPlayAndHold(ANIM_PREFIX + "death");
    /** Server-triggered the instant the Dive Slam hits the ground. */
    public static final RawAnimation DIVE_IMPACT = RawAnimation.begin().thenPlay(ANIM_PREFIX + "dive_impact");
    /** Server-triggered the instant a landing touches down. */
    public static final RawAnimation LAND_IMPACT = RawAnimation.begin().thenPlay(ANIM_PREFIX + "land_impact");
    private static final RawAnimation[] ATTACK_ANIMATIONS = new RawAnimation[AttackType.values().length];

    static {
        for (AttackType type : AttackType.values()) {
            if (type == AttackType.VOID_BREATH) {
                ATTACK_ANIMATIONS[type.id] = RawAnimation.begin()
                        .thenPlay(ANIM_PREFIX + "breath_charge")
                        .thenLoop(ANIM_PREFIX + "breath");
            } else if (type == AttackType.LAND) {
                ATTACK_ANIMATIONS[type.id] = RawAnimation.begin().thenLoop(ANIM_PREFIX + type.animation);
            } else if (type != AttackType.NONE) {
                ATTACK_ANIMATIONS[type.id] = RawAnimation.begin().thenPlayAndHold(ANIM_PREFIX + type.animation);
            }
        }
    }

    /** One hit can take at most this fraction of max health (stops one-shot exploits). /kill still works. */
    public static final float MAX_HIT_FRACTION = 0.05F;
    public static final int DEATH_DURATION = 120;
    public static final int MAX_VOIDLINGS = 6;
    public static final double BOSS_BAR_RANGE = 96.0D;
    private static final UUID ENRAGE_SPEED_ID = UUID.fromString("b7f1d3a2-6c1e-4c39-9a51-1f9d2c7e8a10");

    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private final ServerBossEvent bossEvent;

    @Nullable
    private AttackType queuedAttack;
    private AttackType lastAttack = AttackType.NONE;
    private int attackCooldown = 60;
    private int groundTicks;
    private int flightTicks;
    private int ticksSinceUltimate = 600;
    private boolean scalingApplied;
    private double damageMultiplier = 1.0D;
    @Nullable
    private BlockPos homePos;
    private int clientAttackSerialSeen = -1;

    // Client only: bone positions captured by the renderer each frame (world space), used for particles.
    @Nullable
    public Vec3 clientMouth;
    @Nullable
    public Vec3 clientWingTipLeft;
    @Nullable
    public Vec3 clientWingTipRight;

    public AetherfallEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 500;
        this.noCulling = true;
        setMaxUpStep(2.5F);
        setPersistenceRequired();
        this.bossEvent = new ServerBossEvent(getDisplayName(), BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.NOTCHED_10);
        this.bossEvent.setDarkenScreen(true);
        this.bossEvent.setCreateWorldFog(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 1200.0D)
                .add(Attributes.ARMOR, 20.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 12.0D)
                .add(Attributes.ATTACK_DAMAGE, 18.0D)
                .add(Attributes.ATTACK_KNOCKBACK, 2.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.28D)
                .add(Attributes.FLYING_SPEED, 0.6D)
                .add(Attributes.FOLLOW_RANGE, 64.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(DATA_ATTACK, AttackType.NONE.id);
        entityData.define(DATA_ATTACK_SERIAL, 0);
        entityData.define(DATA_FLYING, false);
        entityData.define(DATA_PHASE, 1);
        entityData.define(DATA_BEAM_ACTIVE, false);
        entityData.define(DATA_BEAM_END, new Vector3f());
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new PhaseRoarGoal(this));
        goalSelector.addGoal(1, new SwipeGoal(this));
        goalSelector.addGoal(1, new TailSweepGoal(this));
        goalSelector.addGoal(1, new VoidBreathGoal(this));
        goalSelector.addGoal(1, new MeteorShowerGoal(this));
        goalSelector.addGoal(1, new WingGustGoal(this));
        goalSelector.addGoal(1, new DiveSlamGoal(this));
        goalSelector.addGoal(1, new GravityWellGoal(this));
        goalSelector.addGoal(1, new SummonVoidlingsGoal(this));
        goalSelector.addGoal(1, new TakeoffGoal(this));
        goalSelector.addGoal(1, new LandGoal(this));
        goalSelector.addGoal(3, new BossMovementGoal(this));

        targetSelector.addGoal(1, new HurtByTargetGoal(this, VoidlingEntity.class, AetherfallEntity.class));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, false, false, null));
    }

    // ------------------------------------------------------------------------------------------------------------
    // Server tick: scaling, phases, attack director, boss bar
    // ------------------------------------------------------------------------------------------------------------

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (!scalingApplied) {
            applyScaling();
        }

        if (attackCooldown > 0) {
            attackCooldown--;
        }
        ticksSinceUltimate++;
        if (isFlying()) {
            flightTicks++;
            groundTicks = 0;
        } else {
            groundTicks++;
            flightTicks = 0;
        }

        LivingEntity target = getTarget();
        if (getAttack() == AttackType.NONE && queuedAttack == null && attackCooldown <= 0) {
            if (target != null && target.isAlive()) {
                queuedAttack = chooseAttack(target);
            } else if (isFlying() && flightTicks > 40) {
                queuedAttack = AttackType.LAND;
            }
        }

        if (isFlying() && getAttack() == AttackType.NONE) {
            Vec3 v = getDeltaMovement();
            if (v.horizontalDistanceSqr() > 0.01D) {
                float yaw = (float) (Mth.atan2(v.z, v.x) * Mth.RAD_TO_DEG) - 90.0F;
                setYRot(Mth.approachDegrees(getYRot(), yaw, 6.0F));
                yBodyRot = getYRot();
            }
        }

        bossEvent.setProgress(getHealth() / getMaxHealth());
        if (tickCount % 10 == 0) {
            updateBossBarPlayers();
        }
    }

    private void updateBossBarPlayers() {
        List<ServerPlayer> keep = new ArrayList<>();
        for (Player player : level().players()) {
            if (player instanceof ServerPlayer sp && sp.isAlive() && distanceToSqr(sp) < BOSS_BAR_RANGE * BOSS_BAR_RANGE) {
                keep.add(sp);
                if (!bossEvent.getPlayers().contains(sp)) {
                    AetherfallNetwork.sendTo(sp, new BossBarMarkerMessage(bossEvent.getId(), true));
                    bossEvent.addPlayer(sp);
                }
            }
        }
        for (ServerPlayer sp : List.copyOf(bossEvent.getPlayers())) {
            if (!keep.contains(sp)) {
                bossEvent.removePlayer(sp);
                AetherfallNetwork.sendTo(sp, new BossBarMarkerMessage(bossEvent.getId(), false));
            }
        }
    }

    /** Applies config values and multiplayer/difficulty scaling once, on the first server tick. */
    private void applyScaling() {
        scalingApplied = true;
        AetherfallConfig.Common config = AetherfallConfig.COMMON;
        double radius = config.playerScalingRadius.get();
        int players = (int) level().players().stream()
                .filter(p -> !p.isSpectator() && p.distanceToSqr(this) < radius * radius)
                .count();
        int extra = Math.max(0, players - 1);
        double difficulty = 1.0D;
        if (config.scaleWithDifficulty.get()) {
            Difficulty d = level().getDifficulty();
            difficulty = d == Difficulty.EASY ? 0.75D : d == Difficulty.HARD ? 1.35D : 1.0D;
        }
        double health = config.bossMaxHealth.get() * (1.0D + config.healthPerExtraPlayer.get() * extra) * difficulty;
        damageMultiplier = config.bossDamageMultiplier.get() * (1.0D + config.damagePerExtraPlayer.get() * extra) * difficulty;
        setBaseAttribute(Attributes.MAX_HEALTH, health);
        setBaseAttribute(Attributes.ARMOR, config.bossArmor.get());
        setBaseAttribute(Attributes.ARMOR_TOUGHNESS, config.bossArmorToughness.get());
        setHealth(getMaxHealth());
    }

    private void setBaseAttribute(net.minecraft.world.entity.ai.attributes.Attribute attribute, double value) {
        AttributeInstance instance = getAttribute(attribute);
        if (instance != null) {
            instance.setBaseValue(value);
        }
    }

    /** Weighted-random pick from every action that is legal right now. Returns null if nothing fits. */
    @Nullable
    public AttackType chooseAttack(LivingEntity target) {
        double edge = edgeDistanceTo(target);
        boolean flying = isFlying();
        int phase = getPhase();
        List<AttackType> pool = new ArrayList<>();
        List<Integer> weights = new ArrayList<>();
        int total = 0;
        for (AttackType type : AttackType.values()) {
            if (!type.selectable || phase < type.minPhase || !type.allows(flying)) {
                continue;
            }
            if (edge < type.minRange || edge > type.maxRange) {
                continue;
            }
            int w = type.weight;
            switch (type) {
                case TAKEOFF -> {
                    boolean outOfReach = target.getY() - getY() > 6.0D || edge > 18.0D;
                    w = groundTicks > 300 ? 10 : outOfReach ? 7 : groundTicks > 140 ? 2 : 0;
                }
                case LAND -> w = flightTicks > 300 ? 14 : flightTicks > 160 ? 4 : 0;
                case DIVE_SLAM -> w = flightTicks < 60 ? 0 : flightTicks > 200 ? w + 6 : w;
                case SUMMON_VOIDLINGS -> w = countVoidlings() >= MAX_VOIDLINGS ? 0 : w;
                case SWIPE, TAIL_SWEEP -> w = edge < 3.0D ? w + 4 : w;
                case VOID_BREATH -> w = hasLineOfSight(target) ? w : 0;
                case METEOR_SHOWER -> w = ticksSinceUltimate < 400 ? 0 : w;
                default -> {
                }
            }
            if (type == lastAttack) {
                w /= 3;
            }
            if (w > 0) {
                pool.add(type);
                weights.add(w);
                total += w;
            }
        }
        if (total <= 0) {
            return null;
        }
        int roll = random.nextInt(total);
        for (int i = 0; i < pool.size(); i++) {
            roll -= weights.get(i);
            if (roll < 0) {
                return pool.get(i);
            }
        }
        return pool.get(pool.size() - 1);
    }

    // ------------------------------------------------------------------------------------------------------------
    // Attack lifecycle (called by the goals)
    // ------------------------------------------------------------------------------------------------------------

    public void beginAttack(AttackType type) {
        entityData.set(DATA_ATTACK, type.id);
        entityData.set(DATA_ATTACK_SERIAL, entityData.get(DATA_ATTACK_SERIAL) + 1);
        if (queuedAttack == type) {
            queuedAttack = null;
        }
        lastAttack = type;
        if (type == AttackType.METEOR_SHOWER) {
            ticksSinceUltimate = 0;
        }
    }

    public void endAttack(AttackType type) {
        if (getAttack() == type) {
            entityData.set(DATA_ATTACK, AttackType.NONE.id);
            attackCooldown = scaled(type.cooldown) + random.nextInt(10);
        }
        if (type == AttackType.VOID_BREATH) {
            setBeamActive(false);
        }
    }

    /** Forces the next action (used by phase changes, the altar, commands and game tests). */
    public void queueAttack(AttackType type) {
        queuedAttack = type;
        attackCooldown = 0;
    }

    @Nullable
    public AttackType getQueuedAttack() {
        return queuedAttack;
    }

    public AttackType getAttack() {
        return AttackType.byId(entityData.get(DATA_ATTACK));
    }

    public int getAttackSerial() {
        return entityData.get(DATA_ATTACK_SERIAL);
    }

    /** Speed multiplier for every action and its animation: 1.0, 1.15, 1.35 by phase. */
    public float tempo() {
        return switch (getPhase()) {
            case 2 -> 1.15F;
            case 3 -> 1.35F;
            default -> 1.0F;
        };
    }

    /** Converts a tempo-1 tick count into the current tempo. */
    public int scaled(int ticks) {
        return Math.max(1, Math.round(ticks / tempo()));
    }

    public boolean isEnraged() {
        return getPhase() >= 3;
    }

    // ------------------------------------------------------------------------------------------------------------
    // Phases and damage
    // ------------------------------------------------------------------------------------------------------------

    public int getPhase() {
        return entityData.get(DATA_PHASE);
    }

    private void setPhase(int phase) {
        entityData.set(DATA_PHASE, phase);
        AttributeInstance speed = getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) {
            speed.removeModifier(ENRAGE_SPEED_ID);
            if (phase >= 3) {
                speed.addTransientModifier(new AttributeModifier(ENRAGE_SPEED_ID, "World Eater enrage", 0.25D,
                        AttributeModifier.Operation.MULTIPLY_BASE));
            }
        }
        bossEvent.setColor(phase >= 3 ? BossEvent.BossBarColor.RED : BossEvent.BossBarColor.PURPLE);
    }

    /** Sets the phase directly (commands, game tests). Does not trigger the phase roar. */
    public void forcePhase(int phase) {
        setPhase(Mth.clamp(phase, 1, 3));
    }

    private void updatePhase() {
        float ratio = getHealth() / getMaxHealth();
        int phase = ratio > 0.66F ? 1 : ratio > 0.33F ? 2 : 3;
        if (phase > getPhase() && isAlive()) {
            setPhase(phase);
            queueAttack(AttackType.PHASE_ROAR);
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (isInvulnerableTo(source) || isDeadOrDying()) {
            return false;
        }
        boolean bypass = source.is(DamageTypeTags.BYPASSES_INVULNERABILITY);
        if (!bypass && (getAttack() == AttackType.PHASE_ROAR || queuedAttack == AttackType.PHASE_ROAR)) {
            return false;
        }
        Entity attacker = source.getEntity();
        if (attacker == this || (attacker != null && isAlliedTo(attacker))) {
            return false;
        }
        if (!bypass) {
            amount = Math.min(amount, getMaxHealth() * MAX_HIT_FRACTION);
        }
        boolean hurt = super.hurt(source, amount);
        if (hurt && !level().isClientSide) {
            updatePhase();
        }
        return hurt;
    }

    @Override
    public boolean isInvulnerableTo(DamageSource source) {
        return source.is(DamageTypes.IN_WALL) || source.is(DamageTypes.CRAMMING) || source.is(DamageTypes.DROWN)
                || source.is(DamageTypeTags.IS_FALL) || source.is(ModDamageTypes.EROSION) || super.isInvulnerableTo(source);
    }

    @Override
    public boolean canBeAffected(MobEffectInstance effect) {
        return effect.getEffect() != ModEffects.EROSION.get()
                && effect.getEffect() != MobEffects.WITHER
                && effect.getEffect() != MobEffects.POISON
                && effect.getEffect() != MobEffects.LEVITATION
                && effect.getEffect() != MobEffects.MOVEMENT_SLOWDOWN
                && super.canBeAffected(effect);
    }

    @Override
    public boolean isAlliedTo(Entity other) {
        return other instanceof VoidlingEntity || other instanceof VoidMeteorEntity || other instanceof AetherfallEntity
                || super.isAlliedTo(other);
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    protected void doPush(Entity entity) {
    }

    @Override
    public boolean canChangeDimensions() {
        return false;
    }

    @Override
    public boolean canBeLeashed(Player player) {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (!level().isClientSide) {
            setFlying(false);
            setBeamActive(false);
            entityData.set(DATA_ATTACK, AttackType.NONE.id);
            for (VoidlingEntity voidling : level().getEntitiesOfClass(VoidlingEntity.class, getBoundingBox().inflate(64.0D),
                    v -> v.isOwnedBy(this))) {
                voidling.dissolve();
            }
            bossEvent.setProgress(0.0F);
        }
    }

    /** A long death: it thrashes, sinks to the ground and its body unravels into the void. */
    @Override
    protected void tickDeath() {
        deathTime++;
        if (!level().isClientSide) {
            Vec3 v = getDeltaMovement();
            setDeltaMovement(v.x * 0.6D, v.y, v.z * 0.6D);
            if (deathTime % 20 == 0 && deathTime < DEATH_DURATION) {
                playSound(ModSounds.VOID_METEOR_IMPACT.get(), 2.0F, 0.6F + deathTime / 200.0F);
            }
            if (deathTime >= DEATH_DURATION && !isRemoved()) {
                if (level() instanceof ServerLevel server) {
                    AetherfallNetwork.shake(server, position(), 64.0D, 1.0F, 40);
                }
                level().broadcastEntityEvent(this, (byte) 60);
                remove(RemovalReason.KILLED);
            }
        }
    }

    @Override
    public void remove(RemovalReason reason) {
        if (!level().isClientSide) {
            for (ServerPlayer sp : List.copyOf(bossEvent.getPlayers())) {
                AetherfallNetwork.sendTo(sp, new BossBarMarkerMessage(bossEvent.getId(), false));
            }
        }
        bossEvent.removeAllPlayers();
        super.remove(reason);
    }

    // ------------------------------------------------------------------------------------------------------------
    // Client-side effects
    // ------------------------------------------------------------------------------------------------------------

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) {
            clientEffects();
        }
    }

    private void clientEffects() {
        RandomSource r = random;
        Level level = level();
        double w = getBbWidth();
        double h = getBbHeight();
        Vec3 mouth = clientMouth != null ? clientMouth : mouthPosition();

        if (r.nextInt(3) < AetherfallConfig.particles(1, r)) {
            level.addParticle(ModParticles.STAR_MOTE.get(), getX() + (r.nextDouble() - 0.5D) * w, getY() + r.nextDouble() * h,
                    getZ() + (r.nextDouble() - 0.5D) * w, 0.0D, 0.015D, 0.0D);
        }
        if (isDeadOrDying()) {
            int count = AetherfallConfig.particles(2 + deathTime / 8, r);
            for (int i = 0; i < count; i++) {
                level.addParticle(i % 3 == 0 ? ModParticles.VOID_EMBER.get() : ModParticles.VOID_SPARK.get(),
                        getX() + (r.nextDouble() - 0.5D) * w * 1.4D, getY() + r.nextDouble() * h * 0.8D,
                        getZ() + (r.nextDouble() - 0.5D) * w * 1.4D,
                        (r.nextDouble() - 0.5D) * 0.05D, 0.08D + r.nextDouble() * 0.2D, (r.nextDouble() - 0.5D) * 0.05D);
            }
            return;
        }
        if (isFlying()) {
            for (Vec3 tip : new Vec3[]{clientWingTipLeft, clientWingTipRight}) {
                if (tip != null && AetherfallConfig.particles(1, r) > 0) {
                    level.addParticle(ModParticles.STAR_MOTE.get(), tip.x, tip.y, tip.z,
                            (r.nextDouble() - 0.5D) * 0.04D, -0.02D, (r.nextDouble() - 0.5D) * 0.04D);
                }
            }
        }
        AttackType attack = getAttack();
        if (attack == AttackType.VOID_BREATH && !isBeamActive()) {
            // Light gathering into the jaws
            for (int i = 0, n = AetherfallConfig.particles(3, r); i < n; i++) {
                Vec3 from = mouth.add((r.nextDouble() - 0.5D) * 6.0D, (r.nextDouble() - 0.5D) * 6.0D, (r.nextDouble() - 0.5D) * 6.0D);
                Vec3 v = mouth.subtract(from).scale(0.12D);
                level.addParticle(i == 0 ? ModParticles.GOLD_SPARK.get() : ModParticles.VOID_SPARK.get(), from.x, from.y, from.z, v.x, v.y, v.z);
            }
        }
        if (isBeamActive()) {
            Vec3 end = getBeamEnd();
            Vec3 along = end.subtract(mouth);
            for (int i = 0, n = AetherfallConfig.particles(4, r); i < n; i++) {
                Vec3 p = mouth.add(along.scale(r.nextDouble()));
                level.addParticle(ModParticles.VOID_FLAME.get(), p.x + (r.nextDouble() - 0.5D) * 0.8D, p.y + (r.nextDouble() - 0.5D) * 0.8D,
                        p.z + (r.nextDouble() - 0.5D) * 0.8D, 0.0D, 0.02D, 0.0D);
            }
            for (int i = 0, n = AetherfallConfig.particles(5, r); i < n; i++) {
                level.addParticle(i % 2 == 0 ? ModParticles.GOLD_SPARK.get() : ModParticles.VOID_SPARK.get(), end.x, end.y, end.z,
                        (r.nextDouble() - 0.5D) * 0.6D, r.nextDouble() * 0.45D, (r.nextDouble() - 0.5D) * 0.6D);
            }
        }
        if (attack == AttackType.GRAVITY_WELL) {
            for (int i = 0, n = AetherfallConfig.particles(4, r); i < n; i++) {
                double angle = r.nextDouble() * Math.PI * 2.0D;
                double radius = 4.0D + r.nextDouble() * 10.0D;
                Vec3 from = mouth.add(Math.cos(angle) * radius, (r.nextDouble() - 0.5D) * 4.0D, Math.sin(angle) * radius);
                Vec3 in = mouth.subtract(from).scale(0.06D);
                Vec3 swirl = new Vec3(-Math.sin(angle), 0.0D, Math.cos(angle)).scale(0.25D);
                level.addParticle(ModParticles.VOID_SPARK.get(), from.x, from.y, from.z, in.x + swirl.x, in.y, in.z + swirl.z);
            }
        }
        if (attack == AttackType.METEOR_SHOWER || attack == AttackType.PHASE_ROAR || attack == AttackType.SUMMON_VOIDLINGS) {
            for (int i = 0, n = AetherfallConfig.particles(3, r); i < n; i++) {
                level.addParticle(ModParticles.VOID_EMBER.get(), getX() + (r.nextDouble() - 0.5D) * w * 3.0D, getY() + 0.2D,
                        getZ() + (r.nextDouble() - 0.5D) * w * 3.0D, 0.0D, 0.05D + r.nextDouble() * 0.1D, 0.0D);
            }
            if (attack == AttackType.METEOR_SHOWER && AetherfallConfig.particles(1, r) > 0) {
                level.addParticle(ModParticles.GOLD_SPARK.get(), mouth.x, mouth.y, mouth.z,
                        (r.nextDouble() - 0.5D) * 0.2D, 0.8D + r.nextDouble() * 0.6D, (r.nextDouble() - 0.5D) * 0.2D);
            }
        }
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id == 60) {
            RandomSource r = random;
            for (int i = 0, n = AetherfallConfig.particles(160, r); i < n; i++) {
                double vx = (r.nextDouble() - 0.5D) * 1.2D;
                double vy = r.nextDouble() * 0.9D;
                double vz = (r.nextDouble() - 0.5D) * 1.2D;
                level().addParticle(i % 4 == 0 ? ModParticles.GOLD_SPARK.get() : i % 4 == 1 ? ModParticles.VOID_FLAME.get()
                                : ModParticles.VOID_SPARK.get(),
                        getX(), getY() + 2.0D + r.nextDouble() * 3.0D, getZ(), vx, vy, vz);
            }
            level().addParticle(ModParticles.SHOCKWAVE.get(), getX(), getY() + 0.1D, getZ(), 14.0D, 0.0D, 0.0D);
            return;
        }
        super.handleEntityEvent(id);
    }

    // ------------------------------------------------------------------------------------------------------------
    // Flight
    // ------------------------------------------------------------------------------------------------------------

    public boolean isFlying() {
        return entityData.get(DATA_FLYING);
    }

    public void setFlying(boolean flying) {
        entityData.set(DATA_FLYING, flying);
        setNoGravity(flying);
        if (!flying) {
            fallDistance = 0.0F;
        }
    }

    /** Steers velocity toward a point (flight only). Smooth: acceleration is a fraction of the velocity error. */
    public void flyTowards(Vec3 destination, double maxSpeed, double acceleration) {
        Vec3 to = destination.subtract(position());
        double distance = to.length();
        Vec3 desired = distance < 1.0E-4D ? Vec3.ZERO : to.scale(Math.min(maxSpeed, distance * 0.2D) / distance);
        Vec3 velocity = getDeltaMovement();
        setDeltaMovement(velocity.add(desired.subtract(velocity).scale(acceleration)));
    }

    /** Ground movement via the move control (the boss steps up 2.5 blocks, so temple stairs and rubble are no obstacle). */
    public void walkTowards(Vec3 destination, double speed) {
        getMoveControl().setWantedPosition(destination.x, destination.y, destination.z, speed);
    }

    // ------------------------------------------------------------------------------------------------------------
    // Combat helpers used by the attack goals
    // ------------------------------------------------------------------------------------------------------------

    /** Distance from the edge of this hitbox to the edge of the other's. */
    public double edgeDistanceTo(Entity other) {
        double dx = other.getX() - getX();
        double dz = other.getZ() - getZ();
        double horizontal = Math.sqrt(dx * dx + dz * dz) - getBbWidth() / 2.0D - other.getBbWidth() / 2.0D;
        double dy = 0.0D;
        if (other.getY() > getY() + getBbHeight()) {
            dy = other.getY() - (getY() + getBbHeight());
        } else if (other.getY() + other.getBbHeight() < getY()) {
            dy = getY() - (other.getY() + other.getBbHeight());
        }
        return Math.sqrt(Math.max(0.0D, horizontal) * Math.max(0.0D, horizontal) + dy * dy);
    }

    /** Unit vector along the body's facing, flattened to the horizontal plane. */
    public Vec3 forward() {
        float yaw = yBodyRot * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(yaw), 0.0D, Mth.cos(yaw));
    }

    /** World position of the jaws, where the Void Breath and Gravity Well originate. */
    public Vec3 mouthPosition() {
        float yaw = getYHeadRot() * Mth.DEG_TO_RAD;
        Vec3 ahead = new Vec3(-Mth.sin(yaw), 0.0D, Mth.cos(yaw)).scale(getBbWidth() * 0.5D + 1.6D);
        double height = isFlying() ? getBbHeight() * 0.62D : getBbHeight() * 0.8D;
        return position().add(ahead).add(0.0D, height, 0.0D);
    }

    /** Snaps body and head toward a point (used on attack wind-ups so the attack lands where it looks). */
    public void faceTowards(Vec3 point, float maxTurn) {
        double dx = point.x - getX();
        double dz = point.z - getZ();
        float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        setYRot(Mth.approachDegrees(getYRot(), yaw, maxTurn));
        yBodyRot = getYRot();
        yHeadRot = getYRot();
        getLookControl().setLookAt(point.x, point.y, point.z, maxTurn, 40.0F);
    }

    /** Everything the boss may hurt inside an area: not itself, not its brood, not creative or spectating players. */
    public List<LivingEntity> victimsIn(AABB area) {
        return level().getEntitiesOfClass(LivingEntity.class, area, e -> e != this && e.isAlive() && !isAlliedTo(e)
                && e.isAttackable() && !(e instanceof Player p && (p.isCreative() || p.isSpectator())));
    }

    public float scaledDamage(float base) {
        return (float) (base * damageMultiplier);
    }

    public boolean dealDamage(LivingEntity victim, ResourceKey<DamageType> type, float base) {
        return victim.hurt(ModDamageTypes.source(level(), type, this), scaledDamage(base));
    }

    /** Knockback that respects knockback resistance and syncs to players immediately. */
    public static void launch(LivingEntity victim, Vec3 horizontalDirection, double strength, double upward) {
        launch(victim, horizontalDirection, strength, upward, 1.0D);
    }

    /**
     * Knockback with a configurable weight for knockback resistance: 1.0 = vanilla rules, 0.5 = resistance only
     * counts half (used for gravity, which should drag even armoured targets), 0.0 = ignores it.
     */
    public static void launch(LivingEntity victim, Vec3 horizontalDirection, double strength, double upward, double resistanceWeight) {
        double resist = Mth.clamp(victim.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE) * resistanceWeight, 0.0D, 1.0D);
        double s = strength * (1.0D - resist);
        Vec3 dir = horizontalDirection.lengthSqr() < 1.0E-6D ? Vec3.ZERO : horizontalDirection.normalize();
        victim.setDeltaMovement(victim.getDeltaMovement().add(dir.x * s, upward * (1.0D - resist * 0.5D), dir.z * s));
        victim.hasImpulse = true;
        victim.hurtMarked = true;
    }

    /** Terrain destruction gate: config flag, optional mobGriefing rule, Forge's griefing event. */
    public boolean canGrief(boolean configFlag) {
        if (!configFlag) {
            return false;
        }
        return !AetherfallConfig.COMMON.respectMobGriefing.get() || ForgeEventFactory.getMobGriefingEvent(level(), this);
    }

    public static boolean isProtected(BlockState state) {
        return AetherfallConfig.COMMON.protectArenaBlocks.get() && state.is(ModTags.Blocks.ARENA_PROTECTED);
    }

    public int countVoidlings() {
        return level().getEntitiesOfClass(VoidlingEntity.class, getBoundingBox().inflate(48.0D), v -> v.isOwnedBy(this)).size();
    }

    public void playBossSound(SoundEvent sound, float volume, float pitch) {
        level().playSound(null, getX(), getY() + getBbHeight() * 0.6D, getZ(), sound, SoundSource.HOSTILE, volume, pitch);
    }

    // ------------------------------------------------------------------------------------------------------------
    // Void Breath beam state (synced for the client-side beam renderer)
    // ------------------------------------------------------------------------------------------------------------

    public boolean isBeamActive() {
        return entityData.get(DATA_BEAM_ACTIVE);
    }

    public void setBeamActive(boolean active) {
        entityData.set(DATA_BEAM_ACTIVE, active);
    }

    public Vec3 getBeamEnd() {
        Vector3f v = entityData.get(DATA_BEAM_END);
        return new Vec3(v.x(), v.y(), v.z());
    }

    public void setBeamEnd(Vec3 end) {
        entityData.set(DATA_BEAM_END, new Vector3f((float) end.x, (float) end.y, (float) end.z));
    }

    // ------------------------------------------------------------------------------------------------------------
    // Home (the Void Altar that summoned it)
    // ------------------------------------------------------------------------------------------------------------

    @Nullable
    public BlockPos getHomePos() {
        return homePos;
    }

    public void setHomePos(@Nullable BlockPos pos) {
        this.homePos = pos;
    }

    // ------------------------------------------------------------------------------------------------------------
    // Vanilla overrides: sounds, size, persistence, boss bar name
    // ------------------------------------------------------------------------------------------------------------

    @Override
    protected float getStandingEyeHeight(Pose pose, EntityDimensions dimensions) {
        return dimensions.height * 0.82F;
    }

    @Override
    public int getMaxHeadXRot() {
        return 40;
    }

    @Override
    public int getMaxHeadYRot() {
        return 60;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 160;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return getAttack() == AttackType.NONE ? ModSounds.WORLD_EATER_AMBIENT.get() : null;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.WORLD_EATER_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.WORLD_EATER_DEATH.get();
    }

    @Override
    protected float getSoundVolume() {
        return 4.0F;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        playSound(ModSounds.WORLD_EATER_STEP.get(), 1.6F, 0.9F + random.nextFloat() * 0.2F);
    }

    @Override
    protected float nextStep() {
        return moveDist + 2.6F;
    }

    @Override
    public void setCustomName(@Nullable Component name) {
        super.setCustomName(name);
        bossEvent.setName(getDisplayName());
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("Phase", getPhase());
        tag.putBoolean("Flying", isFlying());
        tag.putBoolean("ScalingApplied", scalingApplied);
        tag.putDouble("DamageMultiplier", damageMultiplier);
        tag.putInt("AttackCooldown", attackCooldown);
        tag.putInt("TicksSinceUltimate", ticksSinceUltimate);
        if (homePos != null) {
            tag.put("Home", NbtUtils.writeBlockPos(homePos));
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("Phase")) {
            setPhase(Mth.clamp(tag.getInt("Phase"), 1, 3));
        }
        setFlying(tag.getBoolean("Flying"));
        scalingApplied = tag.getBoolean("ScalingApplied");
        if (tag.contains("DamageMultiplier")) {
            damageMultiplier = tag.getDouble("DamageMultiplier");
        }
        attackCooldown = tag.getInt("AttackCooldown");
        ticksSinceUltimate = tag.contains("TicksSinceUltimate") ? tag.getInt("TicksSinceUltimate") : 600;
        homePos = tag.contains("Home") ? NbtUtils.readBlockPos(tag.getCompound("Home")) : null;
        if (hasCustomName()) {
            bossEvent.setName(getDisplayName());
        }
    }

    // ------------------------------------------------------------------------------------------------------------
    // GeckoLib
    // ------------------------------------------------------------------------------------------------------------

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "body", 8, this::bodyAnimation));
        controllers.add(new AnimationController<>(this, ATTACK_CONTROLLER, 3, this::attackAnimation)
                .setAnimationSpeedHandler(boss -> (double) boss.tempo())
                .triggerableAnim("dive_impact", DIVE_IMPACT)
                .triggerableAnim("land_impact", LAND_IMPACT));
    }

    private PlayState bodyAnimation(AnimationState<AetherfallEntity> state) {
        if (isDeadOrDying()) {
            return state.setAndContinue(DEATH);
        }
        if (isFlying()) {
            return state.setAndContinue(getDeltaMovement().horizontalDistanceSqr() > 0.04D ? FLY_GLIDE : FLY_HOVER);
        }
        return state.setAndContinue(state.isMoving() ? WALK : IDLE);
    }

    private PlayState attackAnimation(AnimationState<AetherfallEntity> state) {
        AttackType attack = getAttack();
        int serial = getAttackSerial();
        if (attack == AttackType.NONE || isDeadOrDying()) {
            clientAttackSerialSeen = serial;
            return PlayState.STOP;
        }
        if (serial != clientAttackSerialSeen) {
            clientAttackSerialSeen = serial;
            state.getController().forceAnimationReset();
        }
        return state.setAndContinue(ATTACK_ANIMATIONS[attack.id]);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }
}
