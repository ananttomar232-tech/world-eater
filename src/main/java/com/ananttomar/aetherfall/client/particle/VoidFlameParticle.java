package com.ananttomar.aetherfall.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;
import org.jetbrains.annotations.Nullable;

/** Animated void flame (4 frames): swells, licks upward, then gutters out. Full-bright. */
public class VoidFlameParticle extends TextureSheetParticle {
    private final SpriteSet sprites;
    private final float peakSize;

    protected VoidFlameParticle(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
        super(level, x, y, z);
        this.sprites = sprites;
        this.xd = vx + (random.nextDouble() - 0.5D) * 0.02D;
        this.yd = vy + 0.01D;
        this.zd = vz + (random.nextDouble() - 0.5D) * 0.02D;
        this.lifetime = 14 + random.nextInt(12);
        this.peakSize = 0.16F + random.nextFloat() * 0.22F;
        this.quadSize = peakSize * 0.4F;
        this.gravity = -0.012F;
        this.friction = 0.93F;
        this.hasPhysics = false;
        this.roll = random.nextFloat() * Mth.TWO_PI;
        this.oRoll = roll;
        setSpriteFromAge(sprites);
    }

    @Override
    public void tick() {
        super.tick();
        if (!removed) {
            setSpriteFromAge(sprites);
            float t = (float) age / lifetime;
            this.quadSize = peakSize * (t < 0.3F ? 0.4F + 2.0F * t : 1.0F - (t - 0.3F) * 0.9F);
            this.alpha = Mth.clamp(1.2F - t * 1.2F, 0.0F, 1.0F);
            this.oRoll = roll;
            this.roll += 0.05F;
        }
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
    }

    @Override
    protected int getLightColor(float partialTick) {
        return 0xF000F0;
    }

    public static class Provider implements ParticleProvider<SimpleParticleType> {
        private final SpriteSet sprites;

        public Provider(SpriteSet sprites) {
            this.sprites = sprites;
        }

        @Override
        public @Nullable Particle createParticle(SimpleParticleType type, ClientLevel level, double x, double y, double z,
                                                 double vx, double vy, double vz) {
            return new VoidFlameParticle(level, x, y, z, vx, vy, vz, sprites);
        }
    }
}
