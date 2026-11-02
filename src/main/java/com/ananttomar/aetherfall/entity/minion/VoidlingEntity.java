package com.ananttomar.aetherfall.entity.minion;

import com.ananttomar.aetherfall.effect.ErosionEffect;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import com.ananttomar.aetherfall.registry.ModEffects;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.UUID;

/**
 * A Voidling: a scuttling shard of the void torn loose by the World Eater.
 * <ul>
 *     <li>Fast melee; every bite adds an Erosion stack.</li>
 *     <li>Blinks to its target when it falls behind, so kiting is not enough.</li>
 *     <li>Bound to its summoner: when the World Eater dies or is gone for 3 seconds, its brood dissolves.</li>
 * </ul>
 * A Voidling with no owner (spawn egg) lives on like a normal monster.
 */
public class VoidlingEntity extends Monster implements GeoEntity {
    public static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.voidling.idle");
    public static final RawAnimation RUN = RawAnimation.begin().thenLoop("animation.voidling.run");
    public static final RawAnimation ATTACK = RawAnimation.begin().thenPlay("animation.voidling.attack");

    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    @Nullable
    private UUID ownerId;
    private int orphanTicks;
    private int blinkCooldown = 60;

    public VoidlingEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 6;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 24.0D)
                .add(Attributes.ARMOR, 4.0D)
                .add(Attributes.ATTACK_DAMAGE, 5.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.36D)
                .add(Attributes.FOLLOW_RANGE, 32.0D);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.25D, false));
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 12.0F));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this, AetherfallEntity.class, VoidlingEntity.class));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    public void setOwner(AetherfallEntity owner) {
        this.ownerId = owner.getUUID();
        setPersistenceRequired();
    }

    public boolean isOwnedBy(AetherfallEntity boss) {
        return ownerId != null && ownerId.equals(boss.getUUID());
    }

    /** Unravels into the void (no drops). */
    public void dissolve() {
        if (isRemoved()) {
            return;
        }
        level().playSound(null, getX(), getY(), getZ(), ModSounds.VOIDLING_DEATH.get(), SoundSource.HOSTILE, 1.0F, 1.2F);
        level().broadcastEntityEvent(this, (byte) 60);
        discard();
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide) {
            return;
        }
        if (ownerId != null && tickCount % 20 == 0 && level() instanceof ServerLevel server) {
            Entity owner = server.getEntity(ownerId);
            orphanTicks = owner != null && owner.isAlive() ? 0 : orphanTicks + 20;
            if (orphanTicks >= 60) {
                dissolve();
                return;
            }
        }
        LivingEntity target = getTarget();
        if (blinkCooldown > 0) {
            blinkCooldown--;
        } else if (target != null && target.isAlive() && distanceToSqr(target) > 49.0D) {
            blinkTo(target);
        }
    }

    private void blinkTo(LivingEntity target) {
        for (int attempt = 0; attempt < 12; attempt++) {
            double x = target.getX() + (random.nextDouble() - 0.5D) * 6.0D;
            double z = target.getZ() + (random.nextDouble() - 0.5D) * 6.0D;
            double y = target.getY() + random.nextInt(3) - 1;
            double fromX = getX();
            double fromY = getY();
            double fromZ = getZ();
            if (randomTeleport(x, y, z, true)) {
                level().playSound(null, fromX, fromY, fromZ, ModSounds.VOID_BLINK.get(), SoundSource.HOSTILE, 0.8F, 1.4F);
                playSound(ModSounds.VOID_BLINK.get(), 0.8F, 1.6F);
                blinkCooldown = 80 + random.nextInt(60);
                return;
            }
        }
        blinkCooldown = 20;
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity living) {
            ErosionEffect.addStack(living, 1, 120, this);
        }
        return hit;
    }

    @Override
    public boolean isAlliedTo(Entity other) {
        return other instanceof AetherfallEntity || other instanceof VoidlingEntity || other instanceof VoidMeteorEntity
                || super.isAlliedTo(other);
    }

    @Override
    public boolean canBeAffected(MobEffectInstance effect) {
        return effect.getEffect() != ModEffects.EROSION.get() && super.canBeAffected(effect);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.VOIDLING_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.VOIDLING_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.VOIDLING_DEATH.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (ownerId != null) {
            tag.putUUID("Owner", ownerId);
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        ownerId = tag.hasUUID("Owner") ? tag.getUUID("Owner") : null;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 4, this::animate));
    }

    private PlayState animate(AnimationState<VoidlingEntity> state) {
        if (swinging) {
            return state.setAndContinue(ATTACK);
        }
        return state.setAndContinue(state.isMoving() ? RUN : IDLE);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }
}
