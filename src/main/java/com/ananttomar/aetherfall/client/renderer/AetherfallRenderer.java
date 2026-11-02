package com.ananttomar.aetherfall.client.renderer;

import com.ananttomar.aetherfall.client.model.AetherfallModel;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3d;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/**
 * Renders the World Eater:
 * <ul>
 *     <li>GeckoLib model with cut-out (star-membrane wings use alpha) and an {@link EmissiveGlowLayer} that adds
 *     {@code world_eater_glow.png} full-bright: eyes, runes, gold edges, crystals and the starfield.</li>
 *     <li>Tracks the {@code mouth} and wing-tip bones each frame so particles and the beam come from the real model.</li>
 *     <li>Draws the Void Breath beam from the jaws to the server-synced impact point.</li>
 * </ul>
 */
public class AetherfallRenderer extends GeoEntityRenderer<AetherfallEntity> {
    private static final String[] TRACKED = {"mouth", "wing_left_tip", "wing_right_tip"};

    public AetherfallRenderer(EntityRendererProvider.Context context) {
        super(context, new AetherfallModel());
        addRenderLayer(new EmissiveGlowLayer<>(this));
        this.shadowRadius = 3.2F;
        this.shadowStrength = 0.9F;
    }

    @Override
    public void preRender(PoseStack poseStack, AetherfallEntity animatable, BakedGeoModel model, MultiBufferSource bufferSource,
                          com.mojang.blaze3d.vertex.VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight,
                          int packedOverlay, float red, float green, float blue, float alpha) {
        if (!isReRender) {
            for (String name : TRACKED) {
                model.getBone(name).ifPresent(bone -> bone.setTrackingMatrices(true));
            }
        }
        super.preRender(poseStack, animatable, model, bufferSource, buffer, isReRender, partialTick, packedLight, packedOverlay,
                red, green, blue, alpha);
    }

    @Override
    public void render(AetherfallEntity entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource,
                       int packedLight) {
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);

        BakedGeoModel baked = getGeoModel().getBakedModel(getGeoModel().getModelResource(entity));
        entity.clientMouth = worldPos(baked, "mouth");
        entity.clientWingTipLeft = worldPos(baked, "wing_left_tip");
        entity.clientWingTipRight = worldPos(baked, "wing_right_tip");

        if (entity.isBeamActive() && entity.clientMouth != null) {
            double ex = Mth.lerp(partialTick, entity.xo, entity.getX());
            double ey = Mth.lerp(partialTick, entity.yo, entity.getY());
            double ez = Mth.lerp(partialTick, entity.zo, entity.getZ());
            Vec3 origin = new Vec3(ex, ey, ez);
            // Bone world positions use the entity's current-tick position; shift into this frame's interpolated space.
            Vec3 mouth = entity.clientMouth.subtract(entity.position()).add(origin);
            Vec3 from = mouth.subtract(origin);
            Vec3 to = entity.getBeamEnd().subtract(origin);
            float time = entity.tickCount + partialTick;
            BeamRenderer.render(poseStack, bufferSource, from, to, time, 1.0F);
        }
    }

    private static Vec3 worldPos(BakedGeoModel model, String bone) {
        GeoBone geoBone = model.getBone(bone).orElse(null);
        if (geoBone == null || !geoBone.isTrackingMatrices()) {
            return null;
        }
        Vector3d p = geoBone.getWorldPosition();
        return new Vec3(p.x, p.y, p.z);
    }

    /** The World Eater sinks and unravels instead of tipping onto its side like a vanilla mob. */
    @Override
    protected float getDeathMaxRotation(AetherfallEntity animatable) {
        return 0.0F;
    }

    @Override
    public boolean shouldShowName(AetherfallEntity animatable) {
        return false;
    }
}
