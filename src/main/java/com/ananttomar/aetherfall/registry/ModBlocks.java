package com.ananttomar.aetherfall.registry;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.block.RunicVoidStoneBlock;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.block.state.properties.NoteBlockInstrument;
import net.minecraft.world.level.material.PushReaction;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Supplier;

/**
 * The Void Temple palette: dark, star-flecked masonry with gold inlay and burning purple runes, plus the crystal
 * growths that erupt around the World Eater's lair. The Void Altar is registered with the arena content in Phase 4.
 * <p>
 * Every block here gets a {@link net.minecraft.world.item.BlockItem} automatically in {@link ModItems}.
 */
public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, AetherfallMod.MOD_ID);

    /** Temple masonry: tougher than deepslate bricks, softer than obsidian. */
    private static BlockBehaviour.Properties templeStone() {
        return BlockBehaviour.Properties.of()
                .mapColor(MapColor.COLOR_BLACK)
                .instrument(NoteBlockInstrument.BASEDRUM)
                .requiresCorrectToolForDrops()
                .strength(4.5F, 9.0F)
                .sound(SoundType.DEEPSLATE_BRICKS);
    }

    // Masonry
    public static final RegistryObject<Block> VOID_STONE_BRICKS = register("void_stone_bricks",
            () -> new Block(templeStone()));
    public static final RegistryObject<Block> CRACKED_VOID_STONE_BRICKS = register("cracked_void_stone_bricks",
            () -> new Block(templeStone()));
    public static final RegistryObject<Block> CHISELED_VOID_STONE_BRICKS = register("chiseled_void_stone_bricks",
            () -> new Block(templeStone()));
    public static final RegistryObject<StairBlock> VOID_STONE_BRICK_STAIRS = register("void_stone_brick_stairs",
            () -> new StairBlock(() -> VOID_STONE_BRICKS.get().defaultBlockState(), templeStone()));
    public static final RegistryObject<SlabBlock> VOID_STONE_BRICK_SLAB = register("void_stone_brick_slab",
            () -> new SlabBlock(templeStone()));
    public static final RegistryObject<WallBlock> VOID_STONE_BRICK_WALL = register("void_stone_brick_wall",
            () -> new WallBlock(templeStone().forceSolidOn()));
    public static final RegistryObject<RotatedPillarBlock> VOID_STONE_PILLAR = register("void_stone_pillar",
            () -> new RotatedPillarBlock(templeStone()));
    public static final RegistryObject<Block> GILDED_VOID_BRICKS = register("gilded_void_bricks",
            () -> new Block(templeStone().mapColor(MapColor.GOLD)));

    // Runes
    public static final RegistryObject<RunicVoidStoneBlock> RUNIC_VOID_STONE = register("runic_void_stone",
            () -> new RunicVoidStoneBlock(templeStone()
                    .mapColor(MapColor.COLOR_PURPLE)
                    .lightLevel(RunicVoidStoneBlock::lightLevel)));

    // Crystal growths
    public static final RegistryObject<Block> VOID_CRYSTAL_BLOCK = register("void_crystal_block",
            () -> new Block(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_PURPLE)
                    .requiresCorrectToolForDrops()
                    .strength(3.0F, 6.0F)
                    .lightLevel(state -> 6)
                    .sound(SoundType.AMETHYST)));
    public static final RegistryObject<AmethystClusterBlock> VOID_CRYSTAL_CLUSTER = register("void_crystal_cluster",
            () -> new AmethystClusterBlock(7, 3, BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_PURPLE)
                    .forceSolidOn()
                    .noOcclusion()
                    .requiresCorrectToolForDrops()
                    .strength(2.0F)
                    .lightLevel(state -> 8)
                    .sound(SoundType.AMETHYST_CLUSTER)
                    .pushReaction(PushReaction.DESTROY)));

    // Storage
    public static final RegistryObject<Block> VOID_SCALE_BLOCK = register("void_scale_block",
            () -> new Block(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.TERRACOTTA_PURPLE)
                    .requiresCorrectToolForDrops()
                    .strength(25.0F, 1200.0F)
                    .sound(SoundType.NETHERITE_BLOCK)));

    private ModBlocks() {
    }

    private static <T extends Block> RegistryObject<T> register(String name, Supplier<T> block) {
        return BLOCKS.register(name, block);
    }
}
