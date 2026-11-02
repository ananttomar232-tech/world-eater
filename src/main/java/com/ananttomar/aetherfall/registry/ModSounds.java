package com.ananttomar.aetherfall.registry;

import com.ananttomar.aetherfall.AetherfallMod;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Every sound Aetherfall plays. All audio is original and lives in {@code assets/aetherfall/sounds/}; the mapping
 * from event to files (variants, pitch, streaming) is in {@code assets/aetherfall/sounds.json}.
 */
public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUND_EVENTS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, AetherfallMod.MOD_ID);

    // The World Eater: voice
    public static final RegistryObject<SoundEvent> WORLD_EATER_AMBIENT = register("entity.world_eater.ambient");
    public static final RegistryObject<SoundEvent> WORLD_EATER_HURT = register("entity.world_eater.hurt");
    public static final RegistryObject<SoundEvent> WORLD_EATER_DEATH = register("entity.world_eater.death");
    public static final RegistryObject<SoundEvent> WORLD_EATER_ROAR = register("entity.world_eater.roar");

    // The World Eater: body and movement
    public static final RegistryObject<SoundEvent> WORLD_EATER_STEP = register("entity.world_eater.step");
    public static final RegistryObject<SoundEvent> WORLD_EATER_WING_FLAP = register("entity.world_eater.wing_flap");
    public static final RegistryObject<SoundEvent> WORLD_EATER_TAKEOFF = register("entity.world_eater.takeoff");
    public static final RegistryObject<SoundEvent> WORLD_EATER_LAND = register("entity.world_eater.land");

    // The World Eater: attacks
    public static final RegistryObject<SoundEvent> WORLD_EATER_SWIPE = register("entity.world_eater.swipe");
    public static final RegistryObject<SoundEvent> WORLD_EATER_TAIL_SWEEP = register("entity.world_eater.tail_sweep");
    public static final RegistryObject<SoundEvent> WORLD_EATER_WING_GUST = register("entity.world_eater.wing_gust");
    public static final RegistryObject<SoundEvent> WORLD_EATER_BREATH_CHARGE = register("entity.world_eater.breath_charge");
    public static final RegistryObject<SoundEvent> WORLD_EATER_BREATH_LOOP = register("entity.world_eater.breath_loop");
    public static final RegistryObject<SoundEvent> WORLD_EATER_METEOR_SUMMON = register("entity.world_eater.meteor_summon");
    public static final RegistryObject<SoundEvent> WORLD_EATER_GRAVITY_WELL = register("entity.world_eater.gravity_well");
    public static final RegistryObject<SoundEvent> WORLD_EATER_PHASE_SHIFT = register("entity.world_eater.phase_shift");

    // Meteors
    public static final RegistryObject<SoundEvent> VOID_METEOR_FALL = register("entity.void_meteor.fall");
    public static final RegistryObject<SoundEvent> VOID_METEOR_IMPACT = register("entity.void_meteor.impact");

    // Voidlings (summoned minions)
    public static final RegistryObject<SoundEvent> VOIDLING_AMBIENT = register("entity.voidling.ambient");
    public static final RegistryObject<SoundEvent> VOIDLING_HURT = register("entity.voidling.hurt");
    public static final RegistryObject<SoundEvent> VOIDLING_DEATH = register("entity.voidling.death");

    // Arena
    public static final RegistryObject<SoundEvent> VOID_ALTAR_ACTIVATE = register("block.void_altar.activate");
    public static final RegistryObject<SoundEvent> VOID_ALTAR_AMBIENT = register("block.void_altar.ambient");
    public static final RegistryObject<SoundEvent> RUNIC_STONE_AWAKEN = register("block.runic_void_stone.awaken");

    // Gear
    public static final RegistryObject<SoundEvent> VOID_GREATSWORD_SLASH = register("item.void_greatsword.slash");
    public static final RegistryObject<SoundEvent> CORE_STAFF_FIRE = register("item.world_eater_staff.fire");
    public static final RegistryObject<SoundEvent> VOID_ARMOR_EQUIP = register("item.armor.equip_void_scale");
    public static final RegistryObject<SoundEvent> VOID_BLINK = register("item.void_scale_armor.blink");
    public static final RegistryObject<SoundEvent> EROSION_APPLY = register("effect.erosion.apply");

    // Score
    public static final RegistryObject<SoundEvent> MUSIC_WORLD_EATER = register("music.world_eater");
    public static final RegistryObject<SoundEvent> MUSIC_DISC_WORLD_EATER = register("music_disc.world_eater");

    private ModSounds() {
    }

    private static RegistryObject<SoundEvent> register(String path) {
        return SOUND_EVENTS.register(path, () -> SoundEvent.createVariableRangeEvent(AetherfallMod.id(path)));
    }
}
