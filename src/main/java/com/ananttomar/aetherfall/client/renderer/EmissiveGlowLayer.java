package com.ananttomar.aetherfall.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

/**
 * Emissive layer: re-renders the model with a separate {@code <texture>_glow.png} through vanilla's additive,
 * full-bright {@link RenderType#eyes} pipeline (the one Enderman and Spider eyes use).
 * <p>
 * The glow texture is black (adds nothing) everywhere except the parts that emit light: eyes, runes, gold borders,
 * crystals, the starfield and the mouth. Unlike GeckoLib's AutoGlowingGeoLayer, the base texture is left untouched,
 * so emissive parts keep their lit colour underneath and soft glows (nebula haze) are possible.
 */
public class EmissiveGlowLayer<T extends GeoAnimatable> extends GeoRenderLayer<T> {
    public EmissiveGlowLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    protected ResourceLocation glowTexture(T animatable) {
        ResourceLocation base = getTextureResource(animatable);
        String path = base.getPath();
        return base.withPath(path.substring(0, path.length() - ".png".length()) + "_glow.png");
    }

    @Override
    public void render(PoseStack poseStack, T animatable, BakedGeoModel bakedModel, RenderType renderType,
                       MultiBufferSource bufferSource, VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        RenderType glow = RenderType.eyes(glowTexture(animatable));
        getRenderer().reRender(bakedModel, poseStack, bufferSource, animatable, glow, bufferSource.getBuffer(glow), partialTick,
                LightTexture.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, 1.0F, 1.0F, 1.0F, 1.0F);
    }
}
