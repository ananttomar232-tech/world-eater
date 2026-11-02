package com.ananttomar.aetherfall.client.fx;

import com.ananttomar.aetherfall.config.AetherfallConfig;
import net.minecraft.util.Mth;
import net.minecraftforge.client.event.ViewportEvent;

/** Camera shake from roars, slams and impacts. The strongest active shake wins; it eases out quadratically. */
public final class ScreenShake {
    private static float intensity;
    private static int remaining;
    private static int total;
    private static int ticks;

    private ScreenShake() {
    }

    public static void add(float strength, int duration) {
        float current = remaining > 0 ? intensity * (float) remaining / total : 0.0F;
        if (strength >= current) {
            intensity = strength;
            remaining = duration;
            total = Math.max(1, duration);
        }
    }

    public static void tick() {
        ticks++;
        if (remaining > 0) {
            remaining--;
        }
    }

    public static void reset() {
        remaining = 0;
    }

    public static void apply(ViewportEvent.ComputeCameraAngles event) {
        if (remaining <= 0) {
            return;
        }
        double scale = AetherfallConfig.CLIENT.screenShakeIntensity.get();
        if (scale <= 0.0D) {
            return;
        }
        float t = (remaining - (float) event.getPartialTick()) / total;
        float amp = (float) (intensity * scale * Mth.clamp(t, 0.0F, 1.0F) * Mth.clamp(t, 0.0F, 1.0F) * 2.2F);
        float time = ticks + (float) event.getPartialTick();
        event.setYaw(event.getYaw() + Mth.sin(time * 2.3F) * amp);
        event.setPitch(event.getPitch() + Mth.cos(time * 1.9F) * amp * 0.8F);
        event.setRoll(event.getRoll() + Mth.sin(time * 1.4F) * amp * 0.6F);
    }
}
