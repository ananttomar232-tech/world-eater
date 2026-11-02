package com.ananttomar.aetherfall.client.renderer;

import com.ananttomar.aetherfall.client.model.VoidlingModel;
import com.ananttomar.aetherfall.entity.minion.VoidlingEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public class VoidlingRenderer extends GeoEntityRenderer<VoidlingEntity> {
    public VoidlingRenderer(EntityRendererProvider.Context context) {
        super(context, new VoidlingModel());
        addRenderLayer(new EmissiveGlowLayer<>(this));
        this.shadowRadius = 0.45F;
    }
}
