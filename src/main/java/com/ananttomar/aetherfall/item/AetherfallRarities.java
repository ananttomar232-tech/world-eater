package com.ananttomar.aetherfall.item;

import net.minecraft.ChatFormatting;
import net.minecraft.world.item.Rarity;

/** Extra rarities (Forge lets {@link Rarity} be extended). */
public final class AetherfallRarities {
    /** Gold names for drops from the World Eater itself. */
    public static final Rarity MYTHIC = Rarity.create("AETHERFALL_MYTHIC", ChatFormatting.GOLD);

    private AetherfallRarities() {
    }
}
