package com.ananttomar.aetherfall.client;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.client.hud.WorldEaterBossBar;
import com.ananttomar.aetherfall.client.particle.GlowParticle;
import com.ananttomar.aetherfall.client.particle.ShockwaveParticle;
import com.ananttomar.aetherfall.client.particle.VoidFlameParticle;
import com.ananttomar.aetherfall.client.renderer.AetherfallRenderer;
import com.ananttomar.aetherfall.client.renderer.VoidMeteorRenderer;
import com.ananttomar.aetherfall.client.renderer.VoidlingRenderer;
import com.ananttomar.aetherfall.registry.ModEntities;
import com.ananttomar.aetherfall.registry.ModParticles;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Client registration on the mod bus: renderers, particle providers, the boss bar overlay. */
@Mod.EventBusSubscriber(modid = AetherfallMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientModEvents {
    private ClientModEvents() {
    }

    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.WORLD_EATER.get(), AetherfallRenderer::new);
        event.registerEntityRenderer(ModEntities.VOIDLING.get(), VoidlingRenderer::new);
        event.registerEntityRenderer(ModEntities.VOID_METEOR.get(), VoidMeteorRenderer::new);
    }

    @SubscribeEvent
    public static void registerParticles(RegisterParticleProvidersEvent event) {
        event.registerSpriteSet(ModParticles.VOID_SPARK.get(), s -> new GlowParticle.Provider(s, GlowParticle.VOID_SPARK));
        event.registerSpriteSet(ModParticles.GOLD_SPARK.get(), s -> new GlowParticle.Provider(s, GlowParticle.GOLD_SPARK));
        event.registerSpriteSet(ModParticles.STAR_MOTE.get(), s -> new GlowParticle.Provider(s, GlowParticle.STAR_MOTE));
        event.registerSpriteSet(ModParticles.VOID_EMBER.get(), s -> new GlowParticle.Provider(s, GlowParticle.VOID_EMBER));
        event.registerSpriteSet(ModParticles.VOID_FLAME.get(), VoidFlameParticle.Provider::new);
        event.registerSpriteSet(ModParticles.SHOCKWAVE.get(), ShockwaveParticle.Provider::new);
    }

    @SubscribeEvent
    public static void registerOverlays(RegisterGuiOverlaysEvent event) {
        event.registerAbove(VanillaGuiOverlay.BOSS_EVENT_PROGRESS.id(), "world_eater_boss_bar", WorldEaterBossBar.OVERLAY);
    }
}
