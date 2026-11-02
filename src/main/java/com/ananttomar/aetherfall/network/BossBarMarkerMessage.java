package com.ananttomar.aetherfall.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.UUID;
import java.util.function.Supplier;

/** Tells a client that a boss bar belongs to the World Eater, so it is drawn with the ornate overlay. */
public record BossBarMarkerMessage(UUID barId, boolean add) {
    public void encode(FriendlyByteBuf buf) {
        buf.writeUUID(barId);
        buf.writeBoolean(add);
    }

    public static BossBarMarkerMessage decode(FriendlyByteBuf buf) {
        return new BossBarMarkerMessage(buf.readUUID(), buf.readBoolean());
    }

    public void handle(Supplier<NetworkEvent.Context> context) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                com.ananttomar.aetherfall.client.hud.WorldEaterBossBar.mark(barId, add));
        context.get().setPacketHandled(true);
    }
}
