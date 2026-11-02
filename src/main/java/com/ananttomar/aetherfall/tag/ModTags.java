package com.ananttomar.aetherfall.tag;

import com.ananttomar.aetherfall.AetherfallMod;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;

public final class ModTags {
    public static final class Blocks {
        /** Blocks the World Eater never destroys while {@code protectArenaBlocks} is enabled. */
        public static final TagKey<Block> ARENA_PROTECTED = BlockTags.create(AetherfallMod.id("arena_protected"));
        /** Blocks that wake when the altar is lit (they carry the {@code awakened} state). */
        public static final TagKey<Block> AWAKENING_RUNES = BlockTags.create(AetherfallMod.id("awakening_runes"));

        private Blocks() {
        }
    }

    public static final class Items {
        public static final TagKey<Item> VOID_TEMPLE_STONE = ItemTags.create(AetherfallMod.id("void_temple_stone"));

        private Items() {
        }
    }

    private ModTags() {
    }
}
