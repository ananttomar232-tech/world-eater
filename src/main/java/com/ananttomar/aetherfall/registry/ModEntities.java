package com.ananttomar.aetherfall.registry;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.minion.VoidlingEntity;
import com.ananttomar.aetherfall.entity.projectile.VoidMeteorEntity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod.EventBusSubscriber(modid = AetherfallMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, AetherfallMod.MOD_ID);

    /** Aetherfall, the World Eater. 5.5 x 7 blocks; tracked from 16 chunks away so the fight is visible across the arena. */
    public static final RegistryObject<EntityType<AetherfallEntity>> WORLD_EATER = ENTITY_TYPES.register("world_eater",
            () -> EntityType.Builder.of(AetherfallEntity::new, MobCategory.MONSTER)
                    .sized(5.5F, 7.0F)
                    .fireImmune()
                    .clientTrackingRange(16)
                    .updateInterval(1)
                    .build(AetherfallMod.id("world_eater").toString()));

    public static final RegistryObject<EntityType<VoidlingEntity>> VOIDLING = ENTITY_TYPES.register("voidling",
            () -> EntityType.Builder.of(VoidlingEntity::new, MobCategory.MONSTER)
                    .sized(0.9F, 0.9F)
                    .fireImmune()
                    .clientTrackingRange(10)
                    .build(AetherfallMod.id("voidling").toString()));

    public static final RegistryObject<EntityType<VoidMeteorEntity>> VOID_METEOR = ENTITY_TYPES.register("void_meteor",
            () -> EntityType.Builder.<VoidMeteorEntity>of(VoidMeteorEntity::new, MobCategory.MISC)
                    .sized(1.5F, 1.5F)
                    .fireImmune()
                    .clientTrackingRange(12)
                    .updateInterval(1)
                    .build(AetherfallMod.id("void_meteor").toString()));

    private ModEntities() {
    }

    @SubscribeEvent
    public static void registerAttributes(EntityAttributeCreationEvent event) {
        event.put(WORLD_EATER.get(), AetherfallEntity.createAttributes().build());
        event.put(VOIDLING.get(), VoidlingEntity.createAttributes().build());
    }
}
