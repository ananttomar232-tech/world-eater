package com.ananttomar.aetherfall.registry;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.effect.ErosionEffect;
import net.minecraft.world.effect.MobEffect;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEffects {
    public static final DeferredRegister<MobEffect> EFFECTS = DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, AetherfallMod.MOD_ID);

    public static final RegistryObject<MobEffect> EROSION = EFFECTS.register("erosion", ErosionEffect::new);

    private ModEffects() {
    }
}
