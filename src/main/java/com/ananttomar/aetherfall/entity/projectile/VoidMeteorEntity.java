package com.ananttomar.aetherfall.entity.projectile;

import com.ananttomar.aetherfall.config.AetherfallConfig;
import com.ananttomar.aetherfall.damage.ModDamageTypes;
import com.ananttomar.aetherfall.effect.ErosionEffect;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.network.AetherfallNetwork;
import com.ananttomar.aetherfall.registry.ModEntities;
import com.ananttomar.aetherfall.registry.ModParticles;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.ForgeEventFactory;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * A flaming void meteor called down by the World Eater's Meteor Shower.
 * <p>
 * It falls under its own gravity, bursts on the first block or creature it touches, carves a crater (if terrain
 * damage is allowed and the block is not protected Void Temple masonry), and erodes everything near the impact.
 * The explosion is run server-side only and announced with the mod's own impact sound, so no vanilla explosion
 * sound or particle plays; the impact visuals are the mod's own particles (client side, Phase 3).
 */
public class VoidMeteorEntity extends Projectile implements GeoEntity {
    private static final EntityDataAccessor<Boolean> DATA_ENRAGED = SynchedEntityData.defineId(VoidMeteorEntity.class, EntityDataSerializers.BOOLEAN);
    public static final RawAnimation SPIN = RawAnimation.begin().thenLoop("animation.void_meteor.spin");
    private static final double GRAVITY = 0.04D;
    private static final int MAX_LIFE = 300;

    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);

    public VoidMeteorEntity(EntityType<? extends VoidMeteorEntity> type, Level level) {
        super(type, level);
        this.noCulling = true;
    }

    public static VoidMeteorEntity create(Level level, LivingEntity owner, Vec3 start, Vec3 velocity, boolean enraged) {
        VoidMeteorEntity meteor = new VoidMeteorEntity(ModEntities.VOID_METEOR.get(), level);
        meteor.setOwner(owner);
        meteor.setPos(start);
        meteor.setDeltaMovement(velocity);
        meteor.setEnraged(enraged);
        ProjectileUtil.rotateTowardsMovement(meteor, 1.0F);
        return meteor;
    }

    @Override
    protected void defineSynchedData() {
        entityData.define(DATA_ENRAGED, false);
    }

    public boolean isEnraged() {
        return entityData.get(DATA_ENRAGED);
    }

    public void setEnraged(boolean enraged) {
        entityData.set(DATA_ENRAGED, enraged);
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide && tickCount == 1) {
            level().playSound(null, getX(), getY(), getZ(), ModSounds.VOID_METEOR_FALL.get(), SoundSource.HOSTILE, 4.0F,
                    0.9F + random.nextFloat() * 0.2F);
        }
        HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
        if (hit.getType() != HitResult.Type.MISS && !ForgeEventFactory.onProjectileImpact(this, hit)) {
            onHit(hit);
            if (isRemoved()) {
                return;
            }
        }
        Vec3 velocity = getDeltaMovement();
        if (level().isClientSide) {
            trail(velocity);
        }
        setPos(getX() + velocity.x, getY() + velocity.y, getZ() + velocity.z);
        setDeltaMovement(velocity.add(0.0D, -GRAVITY, 0.0D));
        ProjectileUtil.rotateTowardsMovement(this, 0.3F);
        if (!level().isClientSide && (tickCount > MAX_LIFE || getY() < level().getMinBuildHeight() - 16)) {
            discard();
        }
    }

    @Override
    protected boolean canHitEntity(Entity entity) {
        if (!super.canHitEntity(entity) || entity instanceof VoidMeteorEntity) {
            return false;
        }
        Entity owner = getOwner();
        return owner == null || !owner.isAlliedTo(entity);
    }

    @Override
    protected void onHit(HitResult result) {
        super.onHit(result);
        if (!level().isClientSide) {
            impact();
        }
    }

    private void impact() {
        Entity owner = getOwner();
        float power = (float) (AetherfallConfig.COMMON.meteorExplosionPower.get() * (isEnraged() ? 1.5D : 1.0D));
        if (power > 0.0F) {
            boolean grief = owner instanceof AetherfallEntity boss
                    ? boss.canGrief(AetherfallConfig.COMMON.meteorsBreakBlocks.get())
                    : AetherfallConfig.COMMON.meteorsBreakBlocks.get()
                    && (!AetherfallConfig.COMMON.respectMobGriefing.get() || level().getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING));
            DamageSource source = ModDamageTypes.source(level(), ModDamageTypes.VOID_METEOR, this, owner);
            Explosion explosion = new Explosion(level(), this, source, ArenaSafeExplosionCalculator.INSTANCE,
                    getX(), getY(), getZ(), power, false,
                    grief ? Explosion.BlockInteraction.DESTROY_WITH_DECAY : Explosion.BlockInteraction.KEEP);
            if (!ForgeEventFactory.onExplosionStart(level(), explosion)) {
                explosion.explode();
                explosion.finalizeExplosion(false);
            }
        }
        double radius = 4.0D + (isEnraged() ? 1.5D : 0.0D);
        for (LivingEntity victim : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(radius),
                e -> e.isAlive() && (owner == null || !owner.isAlliedTo(e)) && !(e instanceof Player p && (p.isCreative() || p.isSpectator())))) {
            ErosionEffect.addStack(victim, 1, 160, owner);
        }
        level().playSound(null, getX(), getY(), getZ(), ModSounds.VOID_METEOR_IMPACT.get(), SoundSource.HOSTILE, 5.0F,
                0.85F + random.nextFloat() * 0.3F);
        if (level() instanceof ServerLevel server) {
            AetherfallNetwork.shake(server, position(), 24.0D, isEnraged() ? 0.7F : 0.5F, 10);
        }
        level().broadcastEntityEvent(this, (byte) 3);
        discard();
    }

    private void trail(Vec3 velocity) {
        RandomSource r = random;
        int count = AetherfallConfig.particles(isEnraged() ? 5 : 3, r);
        for (int i = 0; i < count; i++) {
            double back = r.nextDouble();
            level().addParticle(ModParticles.VOID_FLAME.get(),
                    getX() - velocity.x * back + (r.nextDouble() - 0.5D) * 0.9D,
                    getY() + 0.6D - velocity.y * back + (r.nextDouble() - 0.5D) * 0.9D,
                    getZ() - velocity.z * back + (r.nextDouble() - 0.5D) * 0.9D,
                    -velocity.x * 0.05D, -velocity.y * 0.05D, -velocity.z * 0.05D);
        }
        if (r.nextInt(2) < AetherfallConfig.particles(1, r)) {
            level().addParticle(ModParticles.GOLD_SPARK.get(), getX(), getY() + 0.6D, getZ(),
                    (r.nextDouble() - 0.5D) * 0.2D, 0.05D, (r.nextDouble() - 0.5D) * 0.2D);
        }
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id != 3) {
            super.handleEntityEvent(id);
            return;
        }
        RandomSource r = random;
        float scale = isEnraged() ? 1.5F : 1.0F;
        level().addParticle(ModParticles.SHOCKWAVE.get(), getX(), getY() + 0.05D, getZ(), 5.0D * scale, 0.0D, 0.0D);
        for (int i = 0, n = AetherfallConfig.particles((int) (60 * scale), r); i < n; i++) {
            double angle = r.nextDouble() * Math.PI * 2.0D;
            double speed = 0.2D + r.nextDouble() * 0.6D * scale;
            level().addParticle(i % 3 == 0 ? ModParticles.GOLD_SPARK.get() : ModParticles.VOID_SPARK.get(), getX(), getY() + 0.4D, getZ(),
                    Math.cos(angle) * speed, 0.2D + r.nextDouble() * 0.6D, Math.sin(angle) * speed);
        }
        for (int i = 0, n = AetherfallConfig.particles((int) (24 * scale), r); i < n; i++) {
            level().addParticle(ModParticles.VOID_FLAME.get(), getX() + (r.nextDouble() - 0.5D) * 3.0D, getY() + r.nextDouble(),
                    getZ() + (r.nextDouble() - 0.5D) * 3.0D, 0.0D, 0.08D + r.nextDouble() * 0.12D, 0.0D);
        }
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distance) {
        return distance < 256.0D * 256.0D;
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Enraged", isEnraged());
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        setEnraged(tag.getBoolean("Enraged"));
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "spin", 0, state -> state.setAndContinue(SPIN)));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return animationCache;
    }
}
