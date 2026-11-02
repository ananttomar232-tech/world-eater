package com.ananttomar.aetherfall.client.sound;

import com.ananttomar.aetherfall.client.hud.WorldEaterBossBar;
import com.ananttomar.aetherfall.config.AetherfallConfig;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraftforge.client.event.sound.PlaySoundEvent;

/**
 * Plays "Aetherfall - The World Eater" while a World Eater boss bar is shown. Fades in over 2.5 s, loops, fades out
 * over 4 s when the fight ends, and keeps vanilla music from starting on top of it.
 */
public final class BossMusic {
    private static Theme current;

    private BossMusic() {
    }

    public static void tick() {
        Minecraft mc = Minecraft.getInstance();
        boolean wanted = mc.level != null && AetherfallConfig.CLIENT.bossMusic.get() && WorldEaterBossBar.anyActive();
        if (wanted) {
            if (current == null || current.isStopped()) {
                mc.getMusicManager().stopPlaying();
                current = new Theme();
                mc.getSoundManager().play(current);
            } else {
                current.fadingOut = false;
            }
        } else if (current != null) {
            current.fadingOut = true;
            if (current.isStopped()) {
                current = null;
            }
        }
    }

    public static void stopNow() {
        if (current != null) {
            Minecraft.getInstance().getSoundManager().stop(current);
            current = null;
        }
    }

    /** While the theme plays, other music tracks are suppressed (records are a separate category and unaffected). */
    public static void onPlaySound(PlaySoundEvent event) {
        SoundInstance sound = event.getSound();
        if (current != null && !current.fadingOut && sound != null && sound != current && sound.getSource() == SoundSource.MUSIC) {
            event.setSound(null);
        }
    }

    private static final class Theme extends AbstractTickableSoundInstance {
        boolean fadingOut;

        Theme() {
            super(ModSounds.MUSIC_WORLD_EATER.get(), SoundSource.MUSIC, RandomSource.create());
            this.looping = true;
            this.delay = 0;
            this.relative = true;
            this.attenuation = Attenuation.NONE;
            this.volume = 0.02F;
        }

        @Override
        public boolean canStartSilent() {
            return true;
        }

        @Override
        public void tick() {
            if (fadingOut) {
                volume -= 0.0125F;
                if (volume <= 0.0F) {
                    volume = 0.0F;
                    stop();
                }
            } else {
                volume = Math.min(1.0F, volume + 0.02F);
            }
        }
    }
}
