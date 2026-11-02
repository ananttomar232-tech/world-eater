package com.ananttomar.aetherfall.client;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.client.fx.ScreenShake;
import com.ananttomar.aetherfall.client.hud.WorldEaterBossBar;
import com.ananttomar.aetherfall.client.sound.BossMusic;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.CustomizeGuiOverlayEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.client.event.sound.PlaySoundEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Client gameplay hooks on the Forge bus: boss bar, camera shake, battle music. */
@Mod.EventBusSubscriber(modid = AetherfallMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class ClientForgeEvents {
    private ClientForgeEvents() {
    }

    @SubscribeEvent
    public static void onBossBar(CustomizeGuiOverlayEvent.BossEventProgress event) {
        WorldEaterBossBar.onBossEventProgress(event);
    }

    @SubscribeEvent
    public static void onCamera(ViewportEvent.ComputeCameraAngles event) {
        ScreenShake.apply(event);
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase == TickEvent.Phase.END) {
            ScreenShake.tick();
            WorldEaterBossBar.tick();
            BossMusic.tick();
        }
    }

    @SubscribeEvent
    public static void onPlaySound(PlaySoundEvent event) {
        BossMusic.onPlaySound(event);
    }

    @SubscribeEvent
    public static void onLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        WorldEaterBossBar.clear();
        ScreenShake.reset();
        BossMusic.stopNow();
    }
}
