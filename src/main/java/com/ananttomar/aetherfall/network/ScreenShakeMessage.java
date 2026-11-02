package com.ananttomar.aetherfall.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Camera shake: intensity (roughly degrees at 1.0) and duration in ticks. Scaled by the client config. */
public record ScreenShakeMessage(float intensity, int ticks) {
    public void encode(FriendlyByteBuf buf) {
        buf.writeFloat(intensity);
        buf.writeVarInt(ticks);
    }

    public static ScreenShakeMessage decode(FriendlyByteBuf buf) {
        return new ScreenShakeMessage(buf.readFloat(), buf.readVarInt());
    }

    public void handle(Supplier<NetworkEvent.Context> context) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                com.ananttomar.aetherfall.client.fx.ScreenShake.add(intensity, ticks));
        context.get().setPacketHandled(true);
    }
}
