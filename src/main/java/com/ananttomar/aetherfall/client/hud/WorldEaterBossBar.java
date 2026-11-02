package com.ananttomar.aetherfall.client.hud;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.config.AetherfallConfig;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.LerpingBossEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.client.event.CustomizeGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * The World Eater's ornate boss bar (gold frame, void fill, title plate), drawn at the bottom of the screen like the
 * reference art, or at the top (client config {@code bossBarPosition}).
 * <p>
 * The server tags World Eater bars with {@link com.ananttomar.aetherfall.network.BossBarMarkerMessage}. For tagged
 * bars the vanilla bar is cancelled in {@link CustomizeGuiOverlayEvent.BossEventProgress} and collected; this overlay
 * (registered above the vanilla boss overlay, so it runs right after it) then draws them.
 */
public final class WorldEaterBossBar {
    private static final ResourceLocation TEXTURE = AetherfallMod.id("textures/gui/world_eater_bar.png");
    private static final int TEX_W = 256;
    private static final int TEX_H = 64;
    private static final int FRAME_W = 240;
    private static final int FRAME_H = 24;
    private static final int BAR_X = 12;
    private static final int BAR_Y = 8;
    private static final int BAR_W = 216;
    private static final int BAR_H = 8;
    private static final int PLATE_W = 176;
    private static final int PLATE_H = 16;

    private static final Set<UUID> MARKED = new HashSet<>();
    private static final List<LerpingBossEvent> THIS_FRAME = new ArrayList<>();
    private static final Map<UUID, Float> TRAIL = new HashMap<>();
    private static final Map<UUID, Float> LAST = new HashMap<>();
    private static final Map<UUID, Integer> TRAIL_DELAY = new HashMap<>();

    public static final IGuiOverlay OVERLAY = (gui, graphics, partialTick, width, height) -> render(graphics, partialTick, width, height);

    private WorldEaterBossBar() {
    }

    public static void mark(UUID id, boolean add) {
        if (add) {
            MARKED.add(id);
        } else {
            MARKED.remove(id);
            TRAIL.remove(id);
            LAST.remove(id);
            TRAIL_DELAY.remove(id);
        }
    }

    public static boolean anyActive() {
        return !MARKED.isEmpty();
    }

    public static void clear() {
        MARKED.clear();
        TRAIL.clear();
        LAST.clear();
        TRAIL_DELAY.clear();
        THIS_FRAME.clear();
    }

    /** Vanilla is about to draw a bar: take over ours. */
    public static void onBossEventProgress(CustomizeGuiOverlayEvent.BossEventProgress event) {
        if (!AetherfallConfig.CLIENT.ornateBossBar.get() || !MARKED.contains(event.getBossEvent().getId())) {
            return;
        }
        THIS_FRAME.add(event.getBossEvent());
        event.setIncrement(0);
        event.setCanceled(true);
    }

    /** Client tick: the pale "damage trail" waits half a second, then drains down to the real health. */
    public static void tick() {
        for (Map.Entry<UUID, Float> entry : LAST.entrySet()) {
            UUID id = entry.getKey();
            float progress = entry.getValue();
            float trail = TRAIL.getOrDefault(id, progress);
            if (trail < progress) {
                trail = progress;
            } else if (trail > progress) {
                int delay = TRAIL_DELAY.getOrDefault(id, 10);
                if (delay > 0) {
                    TRAIL_DELAY.put(id, delay - 1);
                } else {
                    trail = Math.max(progress, trail - 0.006F);
                }
            }
            if (trail <= progress) {
                TRAIL_DELAY.put(id, 10);
            }
            TRAIL.put(id, trail);
        }
    }

    private static void render(GuiGraphics graphics, float partialTick, int width, int height) {
        if (THIS_FRAME.isEmpty()) {
            return;
        }
        boolean bottom = AetherfallConfig.CLIENT.bossBarPosition.get() == AetherfallConfig.BossBarPosition.BOTTOM;
        int x = (width - FRAME_W) / 2;
        int y = bottom ? height - 96 : 15;
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        for (LerpingBossEvent event : THIS_FRAME) {
            drawBar(graphics, event, x, y, partialTick);
            y += bottom ? -(FRAME_H + PLATE_H + 4) : (FRAME_H + PLATE_H + 4);
        }
        RenderSystem.disableBlend();
        THIS_FRAME.clear();
    }

    private static void drawBar(GuiGraphics g, LerpingBossEvent event, int x, int y, float partialTick) {
        UUID id = event.getId();
        float progress = Mth.clamp(event.getProgress(), 0.0F, 1.0F);
        LAST.put(id, progress);
        float trail = Math.max(progress, TRAIL.getOrDefault(id, progress));
        boolean enraged = progress <= 0.33F;
        int fillW = Math.round(BAR_W * progress);
        int trailW = Math.round(BAR_W * trail);
        int bx = x + BAR_X;
        int by = y + BAR_Y;

        // Empty well, then the trail, then the live fill.
        g.blit(TEXTURE, bx, by, 0, 56, BAR_W, BAR_H, TEX_W, TEX_H);
        if (trailW > fillW) {
            g.blit(TEXTURE, bx + fillW, by, fillW, 40, trailW - fillW, BAR_H, TEX_W, TEX_H);
        }
        if (fillW > 0) {
            g.blit(TEXTURE, bx, by, 0, enraged ? 32 : 24, fillW, BAR_H, TEX_W, TEX_H);
            // A slow sweep of light across the fill.
            long time = Minecraft.getInstance().level != null ? Minecraft.getInstance().level.getGameTime() : 0L;
            float sweep = ((time % 80L) + partialTick) / 80.0F;
            int shineX = bx + Math.round((BAR_W + 24) * sweep) - 12;
            g.enableScissor(bx, by, bx + fillW, by + BAR_H);
            g.blit(TEXTURE, shineX, by, 232, 24, 12, BAR_H, TEX_W, TEX_H);
            g.disableScissor();
        }
        // Phase notches at 66% and 33%.
        for (float mark : new float[]{0.66F, 0.33F}) {
            int nx = bx + Math.round(BAR_W * mark) - 1;
            g.blit(TEXTURE, nx, by - 2, 224, 24, 3, 12, TEX_W, TEX_H);
        }
        // Frame over everything, then the title plate on top.
        g.blit(TEXTURE, x, y, 0, 0, FRAME_W, FRAME_H, TEX_W, TEX_H);
        int px = x + (FRAME_W - PLATE_W) / 2;
        int py = y - PLATE_H + 5;
        g.blit(TEXTURE, px, py, 0, 48, PLATE_W, PLATE_H, TEX_W, TEX_H);

        Font font = Minecraft.getInstance().font;
        Component title = Component.literal(event.getName().getString().toUpperCase(Locale.ROOT).replace(",", ""));
        int tw = font.width(title);
        int color = enraged ? 0xFFB070 : 0xF2C14E;
        g.drawString(font, title, px + (PLATE_W - tw) / 2, py + 4, color, true);
    }
}
