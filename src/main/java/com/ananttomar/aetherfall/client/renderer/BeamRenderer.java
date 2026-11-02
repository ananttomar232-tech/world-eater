package com.ananttomar.aetherfall.client.renderer;

import com.ananttomar.aetherfall.AetherfallMod;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Vector3f;

/**
 * The Void Breath beam: three nested, twisting 8-sided tubes with scrolling textures.
 * <ol>
 *     <li>Core: white-gold, additive ({@code eyes} render type), thin.</li>
 *     <li>Body: violet with gold filaments, additive, twisting the other way.</li>
 *     <li>Haze: soft translucent violet aura, widest, pulsing.</li>
 * </ol>
 * A flaring cap is drawn at the impact point. Everything is full-bright.
 */
public final class BeamRenderer {
    private static final ResourceLocation CORE = AetherfallMod.id("textures/entity/beam/void_breath_core.png");
    private static final ResourceLocation BODY = AetherfallMod.id("textures/entity/beam/void_breath_body.png");
    private static final ResourceLocation HAZE = AetherfallMod.id("textures/entity/beam/void_breath_haze.png");
    private static final int SIDES = 8;

    private BeamRenderer() {
    }

    /** @param from beam origin relative to the pose stack, {@code to} likewise; {@code time} in ticks (with partial). */
    public static void render(PoseStack poseStack, MultiBufferSource buffers, Vec3 from, Vec3 to, float time, float intensity) {
        Vec3 axis = to.subtract(from);
        float length = (float) axis.length();
        if (length < 0.01F) {
            return;
        }
        poseStack.pushPose();
        poseStack.translate(from.x, from.y, from.z);
        // Rotate +Y onto the beam axis.
        Vec3 dir = axis.normalize();
        float yaw = (float) Mth.atan2(dir.x, dir.z);
        float pitch = (float) Math.acos(Mth.clamp(dir.y, -1.0D, 1.0D));
        poseStack.mulPose(com.mojang.math.Axis.YP.rotation(yaw));
        poseStack.mulPose(com.mojang.math.Axis.XP.rotation(pitch));

        float pulse = 0.85F + 0.15F * Mth.sin(time * 0.9F);
        tube(poseStack, buffers.getBuffer(RenderType.entityTranslucentEmissive(HAZE)), length, 1.15F * pulse * intensity,
                time * 0.02F, -time * 0.04F, 0.45F);
        tube(poseStack, buffers.getBuffer(RenderType.eyes(BODY)), length, 0.62F * intensity, -time * 0.09F, -time * 0.12F, 1.0F);
        tube(poseStack, buffers.getBuffer(RenderType.eyes(CORE)), length, 0.26F * intensity, time * 0.14F, -time * 0.25F, 1.0F);
        cap(poseStack, buffers.getBuffer(RenderType.eyes(BODY)), length, 1.6F * pulse * intensity, time);
        poseStack.popPose();
    }

    private static void tube(PoseStack poseStack, VertexConsumer vc, float length, float radius, float twist, float scroll, float alpha) {
        Matrix4f pose = poseStack.last().pose();
        Matrix3f normal = poseStack.last().normal();
        float vEnd = scroll + length / 4.0F;
        for (int i = 0; i < SIDES; i++) {
            float a0 = twist + (float) (i * Math.PI * 2.0D / SIDES);
            float a1 = twist + (float) ((i + 1) * Math.PI * 2.0D / SIDES);
            float x0 = Mth.cos(a0) * radius;
            float z0 = Mth.sin(a0) * radius;
            float x1 = Mth.cos(a1) * radius;
            float z1 = Mth.sin(a1) * radius;
            float u0 = (float) i / SIDES;
            float u1 = (float) (i + 1) / SIDES;
            Vector3f n = new Vector3f((x0 + x1) * 0.5F, 0.0F, (z0 + z1) * 0.5F).normalize();
            vertex(vc, pose, normal, x0, 0.0F, z0, u0, scroll, alpha, n);
            vertex(vc, pose, normal, x0, length, z0, u0, vEnd, alpha, n);
            vertex(vc, pose, normal, x1, length, z1, u1, vEnd, alpha, n);
            vertex(vc, pose, normal, x1, 0.0F, z1, u1, scroll, alpha, n);
        }
    }

    /** A flat, spinning star of light at the impact point. */
    private static void cap(PoseStack poseStack, VertexConsumer vc, float length, float size, float time) {
        Matrix4f pose = poseStack.last().pose();
        Matrix3f normal = poseStack.last().normal();
        Vector3f n = new Vector3f(0.0F, 1.0F, 0.0F);
        for (int k = 0; k < 2; k++) {
            float spin = time * (k == 0 ? 0.2F : -0.15F) + k * 0.785F;
            float c = Mth.cos(spin) * size;
            float s = Mth.sin(spin) * size;
            vertex(vc, pose, normal, -c, length, -s, 0.0F, 0.0F, 1.0F, n);
            vertex(vc, pose, normal, -s, length, c, 0.0F, 1.0F, 1.0F, n);
            vertex(vc, pose, normal, c, length, s, 1.0F, 1.0F, 1.0F, n);
            vertex(vc, pose, normal, s, length, -c, 1.0F, 0.0F, 1.0F, n);
        }
    }

    private static void vertex(VertexConsumer vc, Matrix4f pose, Matrix3f normal, float x, float y, float z, float u, float v,
                               float alpha, Vector3f n) {
        vc.vertex(pose, x, y, z)
                .color(1.0F, 1.0F, 1.0F, alpha)
                .uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY)
                .uv2(LightTexture.FULL_BRIGHT)
                .normal(normal, n.x(), n.y(), n.z())
                .endVertex();
    }
}
