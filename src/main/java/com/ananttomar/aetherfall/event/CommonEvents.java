package com.ananttomar.aetherfall.event;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.effect.ErosionEffect;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.minion.VoidlingEntity;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import net.minecraftforge.event.entity.living.LivingHealEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Gameplay hooks on the Forge event bus. */
@Mod.EventBusSubscriber(modid = AetherfallMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class CommonEvents {
    private CommonEvents() {
    }

    /** Erosion: every stack cuts healing by 20%; five stacks stop it entirely. */
    @SubscribeEvent
    public static void onHeal(LivingHealEvent event) {
        float factor = ErosionEffect.healingFactor(event.getEntity());
        if (factor < 1.0F) {
            if (factor <= 0.0F) {
                event.setCanceled(true);
            } else {
                event.setAmount(event.getAmount() * factor);
            }
        }
    }

    /** Meteors never harm the World Eater or its brood, and never break protected Void Temple blocks. */
    @SubscribeEvent
    public static void onDetonate(ExplosionEvent.Detonate event) {
        if (!(event.getExplosion().getDirectSourceEntity() instanceof VoidMeteorEntity)) {
            return;
        }
        event.getAffectedEntities().removeIf(e -> e instanceof AetherfallEntity || e instanceof VoidlingEntity
                || e instanceof VoidMeteorEntity);
        event.getAffectedBlocks().removeIf(pos -> AetherfallEntity.isProtected(event.getLevel().getBlockState(pos)));
    }
}
