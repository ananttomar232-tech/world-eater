package com.ananttomar.aetherfall.client.model;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;

public class VoidMeteorModel extends DefaultedEntityGeoModel<VoidMeteorEntity> {
    public VoidMeteorModel() {
        super(AetherfallMod.id("void_meteor"), false);
    }
}
