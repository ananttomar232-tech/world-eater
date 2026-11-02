package com.ananttomar.aetherfall.datagen;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.registry.ModBlocks;
import com.ananttomar.aetherfall.registry.ModItems;
import com.ananttomar.aetherfall.tag.ModTags;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.data.tags.ItemTagsProvider;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

public class ModItemTagsProvider extends ItemTagsProvider {
    public ModItemTagsProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> lookup,
                               CompletableFuture<TagLookup<Block>> blockTags, ExistingFileHelper files) {
        super(output, lookup, blockTags, AetherfallMod.MOD_ID, files);
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        copy(BlockTags.STAIRS, ItemTags.STAIRS);
        copy(BlockTags.SLABS, ItemTags.SLABS);
        copy(BlockTags.WALLS, ItemTags.WALLS);

        tag(ItemTags.MUSIC_DISCS).add(ModItems.MUSIC_DISC_WORLD_EATER.get());
        tag(ItemTags.BEACON_PAYMENT_ITEMS).add(ModItems.VOID_SCALE.get());

        tag(ModTags.Items.VOID_TEMPLE_STONE).add(
                ModBlocks.VOID_STONE_BRICKS.get().asItem(),
                ModBlocks.CRACKED_VOID_STONE_BRICKS.get().asItem(),
                ModBlocks.CHISELED_VOID_STONE_BRICKS.get().asItem(),
                ModBlocks.VOID_STONE_PILLAR.get().asItem());
    }
}
