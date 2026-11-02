package com.ananttomar.aetherfall.client.model;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.entity.minion.VoidlingEntity;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;

/** Voidling model; GeckoLib turns the {@code head} bone toward the look direction. */
public class VoidlingModel extends DefaultedEntityGeoModel<VoidlingEntity> {
    public VoidlingModel() {
        super(AetherfallMod.id("voidling"), true);
    }
}
