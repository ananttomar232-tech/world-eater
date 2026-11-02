package com.ananttomar.aetherfall.datagen;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.registry.ModBlocks;
import com.ananttomar.aetherfall.tag.ModTags;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.common.data.BlockTagsProvider;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.registries.RegistryObject;

import java.util.concurrent.CompletableFuture;

public class ModBlockTagsProvider extends BlockTagsProvider {
    public ModBlockTagsProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> lookup, ExistingFileHelper files) {
        super(output, lookup, AetherfallMod.MOD_ID, files);
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        for (RegistryObject<Block> block : ModBlocks.BLOCKS.getEntries()) {
            tag(BlockTags.MINEABLE_WITH_PICKAXE).add(block.get());
        }

        tag(BlockTags.NEEDS_IRON_TOOL).add(
                ModBlocks.VOID_STONE_BRICKS.get(),
                ModBlocks.CRACKED_VOID_STONE_BRICKS.get(),
                ModBlocks.CHISELED_VOID_STONE_BRICKS.get(),
                ModBlocks.VOID_STONE_BRICK_STAIRS.get(),
                ModBlocks.VOID_STONE_BRICK_SLAB.get(),
                ModBlocks.VOID_STONE_BRICK_WALL.get(),
                ModBlocks.VOID_STONE_PILLAR.get(),
                ModBlocks.GILDED_VOID_BRICKS.get(),
                ModBlocks.RUNIC_VOID_STONE.get(),
                ModBlocks.VOID_CRYSTAL_BLOCK.get(),
                ModBlocks.VOID_CRYSTAL_CLUSTER.get());
        tag(BlockTags.NEEDS_DIAMOND_TOOL).add(ModBlocks.VOID_SCALE_BLOCK.get());

        tag(BlockTags.STAIRS).add(ModBlocks.VOID_STONE_BRICK_STAIRS.get());
        tag(BlockTags.SLABS).add(ModBlocks.VOID_STONE_BRICK_SLAB.get());
        tag(BlockTags.WALLS).add(ModBlocks.VOID_STONE_BRICK_WALL.get());
        tag(BlockTags.CRYSTAL_SOUND_BLOCKS).add(ModBlocks.VOID_CRYSTAL_BLOCK.get());
        tag(BlockTags.BEACON_BASE_BLOCKS).add(ModBlocks.VOID_SCALE_BLOCK.get());
        tag(BlockTags.DRAGON_IMMUNE).add(ModBlocks.RUNIC_VOID_STONE.get(), ModBlocks.GILDED_VOID_BRICKS.get());
        tag(BlockTags.WITHER_IMMUNE).add(ModBlocks.RUNIC_VOID_STONE.get(), ModBlocks.GILDED_VOID_BRICKS.get());

        tag(ModTags.Blocks.AWAKENING_RUNES).add(ModBlocks.RUNIC_VOID_STONE.get());
        tag(ModTags.Blocks.ARENA_PROTECTED).add(
                ModBlocks.VOID_STONE_BRICKS.get(),
                ModBlocks.CRACKED_VOID_STONE_BRICKS.get(),
                ModBlocks.CHISELED_VOID_STONE_BRICKS.get(),
                ModBlocks.VOID_STONE_BRICK_STAIRS.get(),
                ModBlocks.VOID_STONE_BRICK_SLAB.get(),
                ModBlocks.VOID_STONE_BRICK_WALL.get(),
                ModBlocks.VOID_STONE_PILLAR.get(),
                ModBlocks.GILDED_VOID_BRICKS.get(),
                ModBlocks.RUNIC_VOID_STONE.get());
    }
}
