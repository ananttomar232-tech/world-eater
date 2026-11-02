package com.ananttomar.aetherfall.client.particle;

import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

/**
 * A flat ring of light that races outward along the ground. The first velocity argument is the final radius in
 * blocks (default 4), which is how the server picks small meteor rings or a huge phase-roar wave.
 */
public class ShockwaveParticle extends TextureSheetParticle {
    private final float maxRadius;

    protected ShockwaveParticle(ClientLevel level, double x, double y, double z, double radius, SpriteSet sprites) {
        super(level, x, y, z);
        this.maxRadius = radius > 0.0D ? (float) radius : 4.0F;
        this.lifetime = 16 + (int) (maxRadius * 0.6F);
        this.gravity = 0.0F;
        this.hasPhysics = false;
        this.xd = 0.0D;
        this.yd = 0.0D;
        this.zd = 0.0D;
        pickSprite(sprites);
    }

    @Override
    public void render(VertexConsumer buffer, Camera camera, float partialTick) {
        Vec3 cam = camera.getPosition();
        float x = (float) (Mth.lerp(partialTick, xo, this.x) - cam.x());
        float y = (float) (Mth.lerp(partialTick, yo, this.y) - cam.y());
        float z = (float) (Mth.lerp(partialTick, zo, this.z) - cam.z());
        float t = Mth.clamp((age + partialTick) / lifetime, 0.0F, 1.0F);
        float eased = 1.0F - (1.0F - t) * (1.0F - t) * (1.0F - t);
        float r = 0.3F + maxRadius * eased;
        float a = (1.0F - t) * 0.9F;
        float u0 = getU0();
        float u1 = getU1();
        float v0 = getV0();
        float v1 = getV1();
        int light = 0xF000F0;
        // Upward-facing and downward-facing quads so the ring is visible from above and below.
        quad(buffer, x, y, z, r, u0, u1, v0, v1, a, light, false);
        quad(buffer, x, y, z, r, u0, u1, v0, v1, a, light, true);
    }

    private void quad(VertexConsumer b, float x, float y, float z, float r, float u0, float u1, float v0, float v1, float a, int light,
                      boolean flip) {
        float[][] corners = flip
                ? new float[][]{{-r, -r, u0, v0}, {r, -r, u1, v0}, {r, r, u1, v1}, {-r, r, u0, v1}}
                : new float[][]{{-r, -r, u0, v0}, {-r, r, u0, v1}, {r, r, u1, v1}, {r, -r, u1, v0}};
        for (float[] c : corners) {
            b.vertex(x + c[0], y, z + c[1]).uv(c[2], c[3]).color(rCol, gCol, bCol, a).uv2(light).endVertex();
        }
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
    }

    public static class Provider implements ParticleProvider<SimpleParticleType> {
        private final SpriteSet sprites;

        public Provider(SpriteSet sprites) {
            this.sprites = sprites;
        }

        @Override
        public @Nullable Particle createParticle(SimpleParticleType type, ClientLevel level, double x, double y, double z,
                                                 double vx, double vy, double vz) {
            return new ShockwaveParticle(level, x, y, z, vx, sprites);
        }
    }
}
