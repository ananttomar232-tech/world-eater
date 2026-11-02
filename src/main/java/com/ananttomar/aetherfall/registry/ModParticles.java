package com.ananttomar.aetherfall.registry;

import com.ananttomar.aetherfall.AetherfallMod;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** Particle types. Client providers and sprites are registered in {@code client.ClientModEvents}. */
public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES =
            DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, AetherfallMod.MOD_ID);

    /** Violet void spark: beam spray, charging, death. */
    public static final RegistryObject<SimpleParticleType> VOID_SPARK = PARTICLES.register("void_spark", () -> new SimpleParticleType(true));
    /** Gold spark: beam core spray, armor glints, impacts. */
    public static final RegistryObject<SimpleParticleType> GOLD_SPARK = PARTICLES.register("gold_spark", () -> new SimpleParticleType(true));
    /** Twinkling star mote shed by the star-wings. */
    public static final RegistryObject<SimpleParticleType> STAR_MOTE = PARTICLES.register("star_mote", () -> new SimpleParticleType(false));
    /** Animated violet-gold void flame: breath plume and meteor trails. */
    public static final RegistryObject<SimpleParticleType> VOID_FLAME = PARTICLES.register("void_flame", () -> new SimpleParticleType(true));
    /** Flat expanding ground ring: meteor impacts, dive slam, roars. */
    public static final RegistryObject<SimpleParticleType> SHOCKWAVE = PARTICLES.register("shockwave", () -> new SimpleParticleType(true));
    /** Slow rising ember from awakened runes and the altar. */
    public static final RegistryObject<SimpleParticleType> VOID_EMBER = PARTICLES.register("void_ember", () -> new SimpleParticleType(false));

    private ModParticles() {
    }
}
