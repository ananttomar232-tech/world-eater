package com.ananttomar.aetherfall.datagen;

import com.ananttomar.aetherfall.registry.ModBlocks;
import com.ananttomar.aetherfall.registry.ModItems;
import net.minecraft.data.loot.BlockLootSubProvider;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.functions.ApplyBonusCount;
import net.minecraft.world.level.storage.loot.functions.SetItemCountFunction;
import net.minecraft.world.level.storage.loot.providers.number.UniformGenerator;
import net.minecraftforge.registries.RegistryObject;

import java.util.Set;

public class ModBlockLootProvider extends BlockLootSubProvider {
    public ModBlockLootProvider() {
        super(Set.of(), FeatureFlags.REGISTRY.allFlags());
    }

    @Override
    protected void generate() {
        dropSelf(ModBlocks.VOID_STONE_BRICKS.get());
        dropSelf(ModBlocks.CRACKED_VOID_STONE_BRICKS.get());
        dropSelf(ModBlocks.CHISELED_VOID_STONE_BRICKS.get());
        dropSelf(ModBlocks.VOID_STONE_BRICK_STAIRS.get());
        add(ModBlocks.VOID_STONE_BRICK_SLAB.get(), createSlabItemTable(ModBlocks.VOID_STONE_BRICK_SLAB.get()));
        dropSelf(ModBlocks.VOID_STONE_BRICK_WALL.get());
        dropSelf(ModBlocks.VOID_STONE_PILLAR.get());
        dropSelf(ModBlocks.GILDED_VOID_BRICKS.get());
        dropSelf(ModBlocks.RUNIC_VOID_STONE.get());
        dropSelf(ModBlocks.VOID_CRYSTAL_BLOCK.get());
        dropSelf(ModBlocks.VOID_SCALE_BLOCK.get());

        // Like amethyst: silk touch keeps the cluster, otherwise it shatters into shards (Fortune applies).
        add(ModBlocks.VOID_CRYSTAL_CLUSTER.get(), block -> createSilkTouchDispatchTable(block,
                applyExplosionDecay(block, LootItem.lootTableItem(ModItems.VOID_CRYSTAL_SHARD.get())
                        .apply(SetItemCountFunction.setCount(UniformGenerator.between(2.0F, 4.0F)))
                        .apply(ApplyBonusCount.addOreBonusCount(Enchantments.BLOCK_FORTUNE)))));
    }

    @Override
    protected Iterable<Block> getKnownBlocks() {
        return ModBlocks.BLOCKS.getEntries().stream().map(RegistryObject::get).map(Block.class::cast)::iterator;
    }
}
