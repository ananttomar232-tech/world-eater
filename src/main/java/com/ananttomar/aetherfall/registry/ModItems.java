package com.ananttomar.aetherfall.registry;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.item.AetherfallLoreItem;
import com.ananttomar.aetherfall.item.AetherfallRarities;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.RecordItem;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Materials, the summoning sigil, the music disc and every block item.
 * Armor and weapons are added with the progression content (Phase 4).
 */
public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, AetherfallMod.MOD_ID);

    /** Length of {@code sounds/music/world_eater.ogg} in ticks (3 min 12 s). Keep in sync with the audio file. */
    public static final int WORLD_EATER_THEME_TICKS = 192 * 20;

    // Materials
    public static final RegistryObject<Item> VOID_CRYSTAL_SHARD = ITEMS.register("void_crystal_shard",
            () -> new AetherfallLoreItem(new Item.Properties(), 1, false));
    public static final RegistryObject<Item> VOID_SCALE = ITEMS.register("void_scale",
            () -> new AetherfallLoreItem(new Item.Properties().rarity(Rarity.RARE).fireResistant(), 2, false));
    public static final RegistryObject<Item> WORLD_EATERS_CORE = ITEMS.register("world_eaters_core",
            () -> new AetherfallLoreItem(new Item.Properties().rarity(AetherfallRarities.MYTHIC).fireResistant().stacksTo(16), 2, true));

    // Summoning
    public static final RegistryObject<Item> VOID_SIGIL = ITEMS.register("void_sigil",
            () -> new AetherfallLoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(1), 3, true));

    // Score
    public static final RegistryObject<Item> MUSIC_DISC_WORLD_EATER = ITEMS.register("music_disc_world_eater",
            () -> new RecordItem(15, ModSounds.MUSIC_DISC_WORLD_EATER,
                    new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), WORLD_EATER_THEME_TICKS));

    // Spawn eggs
    public static final RegistryObject<Item> WORLD_EATER_SPAWN_EGG = ITEMS.register("world_eater_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.WORLD_EATER, 0x1A0B2E, 0xF2C14E, new Item.Properties().rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> VOIDLING_SPAWN_EGG = ITEMS.register("voidling_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.VOIDLING, 0x120624, 0xB45CFF, new Item.Properties()));

    // Block items
    static {
        ModBlocks.BLOCKS.getEntries().forEach(block -> {
            Item.Properties properties = new Item.Properties();
            if (block.getId().equals(ModBlocks.VOID_SCALE_BLOCK.getId())) {
                properties.rarity(Rarity.RARE).fireResistant();
            } else if (block.getId().equals(ModBlocks.RUNIC_VOID_STONE.getId())) {
                properties.rarity(Rarity.UNCOMMON);
            }
            ITEMS.register(block.getId().getPath(), () -> new BlockItem(block.get(), properties));
        });
    }

    private ModItems() {
    }
}
