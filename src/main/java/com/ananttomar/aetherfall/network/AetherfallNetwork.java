package com.ananttomar.aetherfall.network;

import com.ananttomar.aetherfall.AetherfallMod;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

/** The mod's network channel. Both messages flow server -> client and only drive presentation. */
public final class AetherfallNetwork {
    private static final String PROTOCOL = "1";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            AetherfallMod.id("main"), () -> PROTOCOL, PROTOCOL::equals, PROTOCOL::equals);

    private AetherfallNetwork() {
    }

    public static void register() {
        int id = 0;
        CHANNEL.messageBuilder(BossBarMarkerMessage.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(BossBarMarkerMessage::encode)
                .decoder(BossBarMarkerMessage::decode)
                .consumerMainThread(BossBarMarkerMessage::handle)
                .add();
        CHANNEL.messageBuilder(ScreenShakeMessage.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(ScreenShakeMessage::encode)
                .decoder(ScreenShakeMessage::decode)
                .consumerMainThread(ScreenShakeMessage::handle)
                .add();
    }

    public static void sendTo(ServerPlayer player, Object message) {
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), message);
    }

    /** Shakes the camera of every player within {@code radius}, fading with distance. */
    public static void shake(ServerLevel level, Vec3 origin, double radius, float intensity, int ticks) {
        for (ServerPlayer player : level.players()) {
            double distance = player.position().distanceTo(origin);
            if (distance < radius) {
                float scaled = (float) (intensity * (1.0D - distance / radius));
                if (scaled > 0.02F) {
                    sendTo(player, new ScreenShakeMessage(scaled, ticks));
                }
            }
        }
    }
}
