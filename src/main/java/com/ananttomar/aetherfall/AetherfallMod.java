package com.ananttomar.aetherfall;

import com.ananttomar.aetherfall.config.AetherfallConfig;
import com.ananttomar.aetherfall.registry.ModBlocks;
import com.ananttomar.aetherfall.registry.ModCreativeTabs;
import com.ananttomar.aetherfall.registry.ModEffects;
import com.ananttomar.aetherfall.registry.ModEntities;
import com.ananttomar.aetherfall.registry.ModItems;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Entry point for Aetherfall: The World Eater.
 * <p>
 * Every registry is a {@link net.minecraftforge.registries.DeferredRegister} attached to the mod event bus here,
 * so registration order is owned by Forge and never by class-loading order.
 */
@Mod(AetherfallMod.MOD_ID)
public final class AetherfallMod {
    public static final String MOD_ID = "aetherfall";
    public static final Logger LOGGER = LoggerFactory.getLogger("Aetherfall");

    public AetherfallMod(FMLJavaModLoadingContext context) {
        IEventBus modBus = context.getModEventBus();

        // Order matters only for readability: blocks before items so block items can reference them.
        ModSounds.SOUND_EVENTS.register(modBus);
        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModEntities.ENTITY_TYPES.register(modBus);
        ModEffects.EFFECTS.register(modBus);
        ModCreativeTabs.CREATIVE_TABS.register(modBus);

        context.registerConfig(ModConfig.Type.COMMON, AetherfallConfig.COMMON_SPEC, MOD_ID + "-common.toml");
        context.registerConfig(ModConfig.Type.CLIENT, AetherfallConfig.CLIENT_SPEC, MOD_ID + "-client.toml");

        modBus.addListener(this::commonSetup);
        MinecraftForge.EVENT_BUS.register(this);
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        LOGGER.info("Aetherfall stirs beyond the stars. {} blocks, {} items, {} entities and {} sound events registered.",
                ModBlocks.BLOCKS.getEntries().size(),
                ModItems.ITEMS.getEntries().size(),
                ModEntities.ENTITY_TYPES.getEntries().size(),
                ModSounds.SOUND_EVENTS.getEntries().size());
    }

    /** Builds a {@link ResourceLocation} in the {@code aetherfall} namespace. */
    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }
}
