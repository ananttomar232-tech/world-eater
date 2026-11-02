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

/**
 * Full-bright, tinted, animated glow particle shared by sparks, star motes and embers. Velocity is used exactly as
 * given (no vanilla random jitter), so effects like the breath charge can aim particles precisely.
 */
public class GlowParticle extends TextureSheetParticle {
    /** Look and motion of one glow particle family. */
    public record Style(float r, float g, float b, int minLife, int maxLife, float minSize, float maxSize, float gravity,
                        float friction, boolean twinkle, boolean shrink) {
    }

    public static final Style VOID_SPARK = new Style(0.80F, 0.45F, 1.00F, 12, 26, 0.10F, 0.20F, 0.02F, 0.91F, false, true);
    public static final Style GOLD_SPARK = new Style(1.00F, 0.82F, 0.42F, 10, 22, 0.08F, 0.17F, 0.03F, 0.90F, false, true);
    public static final Style STAR_MOTE = new Style(0.95F, 0.90F, 1.00F, 30, 55, 0.06F, 0.13F, -0.002F, 0.96F, true, false);
    public static final Style VOID_EMBER = new Style(0.72F, 0.36F, 1.00F, 40, 80, 0.07F, 0.13F, -0.006F, 0.97F, true, true);

    private final SpriteSet sprites;
    private final Style style;
    private final float baseSize;
    private final float phase;

    protected GlowParticle(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites, Style style) {
        super(level, x, y, z);
        this.sprites = sprites;
        this.style = style;
        this.xd = vx;
        this.yd = vy;
        this.zd = vz;
        this.lifetime = style.minLife() + random.nextInt(Math.max(1, style.maxLife() - style.minLife() + 1));
        this.baseSize = style.minSize() + random.nextFloat() * (style.maxSize() - style.minSize());
        this.quadSize = baseSize;
        this.gravity = style.gravity();
        this.friction = style.friction();
        this.hasPhysics = false;
        this.phase = random.nextFloat() * Mth.TWO_PI;
        float jitter = 0.9F + random.nextFloat() * 0.1F;
        setColor(style.r() * jitter, style.g() * jitter, style.b());
        setSpriteFromAge(sprites);
    }

    @Override
    public void tick() {
        super.tick();
        if (!removed) {
            setSpriteFromAge(sprites);
            float t = (float) age / lifetime;
            float fade = 1.0F - t * t;
            if (style.twinkle()) {
                fade *= 0.55F + 0.45F * Mth.sin(age * 0.6F + phase);
            }
            this.alpha = Mth.clamp(fade, 0.0F, 1.0F);
            this.quadSize = style.shrink() ? baseSize * (1.0F - t * 0.7F) : baseSize;
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
        private final Style style;

        public Provider(SpriteSet sprites, Style style) {
            this.sprites = sprites;
            this.style = style;
        }

        @Override
        public @Nullable Particle createParticle(SimpleParticleType type, ClientLevel level, double x, double y, double z,
                                                 double vx, double vy, double vz) {
            return new GlowParticle(level, x, y, z, vx, vy, vz, sprites, style);
        }
    }
}
