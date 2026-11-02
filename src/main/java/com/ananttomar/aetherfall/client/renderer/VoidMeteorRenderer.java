package com.ananttomar.aetherfall.client.renderer;

import com.ananttomar.aetherfall.client.model.VoidMeteorModel;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.core.BlockPos;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/** Full-bright burning meteor; enraged meteors are 50% larger. */
public class VoidMeteorRenderer extends GeoEntityRenderer<VoidMeteorEntity> {
    public VoidMeteorRenderer(EntityRendererProvider.Context context) {
        super(context, new VoidMeteorModel());
        addRenderLayer(new EmissiveGlowLayer<>(this));
        this.shadowRadius = 0.0F;
    }

    @Override
    public void scaleModelForRender(float widthScale, float heightScale, PoseStack poseStack, VoidMeteorEntity animatable,
                                    BakedGeoModel model, boolean isReRender, float partialTick, int packedLight, int packedOverlay) {
        float s = animatable.isEnraged() ? 1.5F : 1.0F;
        super.scaleModelForRender(widthScale * s, heightScale * s, poseStack, animatable, model, isReRender, partialTick,
                packedLight, packedOverlay);
    }

    @Override
    protected int getBlockLightLevel(VoidMeteorEntity entity, BlockPos pos) {
        return 15;
    }

    @Override
    public void preRender(PoseStack poseStack, VoidMeteorEntity animatable, BakedGeoModel model, MultiBufferSource bufferSource,
                          VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay,
                          float red, float green, float blue, float alpha) {
        super.preRender(poseStack, animatable, model, bufferSource, buffer, isReRender, partialTick, LightTexture.FULL_BRIGHT,
                packedOverlay, red, green, blue, alpha);
    }
}
