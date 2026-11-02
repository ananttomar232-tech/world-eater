package com.ananttomar.aetherfall.datagen;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.block.RunicVoidStoneBlock;
import com.ananttomar.aetherfall.registry.ModBlocks;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraftforge.client.model.generators.BlockModelBuilder;
import net.minecraftforge.client.model.generators.BlockStateProvider;
import net.minecraftforge.client.model.generators.ConfiguredModel;
import net.minecraftforge.client.model.generators.ModelFile;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModBlockStateProvider extends BlockStateProvider {
    public ModBlockStateProvider(PackOutput output, ExistingFileHelper files) {
        super(output, AetherfallMod.MOD_ID, files);
    }

    @Override
    protected void registerStatesAndModels() {
        cubeWithItem(ModBlocks.VOID_STONE_BRICKS);
        cubeWithItem(ModBlocks.CRACKED_VOID_STONE_BRICKS);
        cubeWithItem(ModBlocks.CHISELED_VOID_STONE_BRICKS);
        cubeWithItem(ModBlocks.GILDED_VOID_BRICKS);
        cubeWithItem(ModBlocks.VOID_CRYSTAL_BLOCK);
        cubeWithItem(ModBlocks.VOID_SCALE_BLOCK);

        ResourceLocation bricks = blockTexture(ModBlocks.VOID_STONE_BRICKS.get());
        stairsBlock(ModBlocks.VOID_STONE_BRICK_STAIRS.get(), bricks);
        slabBlock(ModBlocks.VOID_STONE_BRICK_SLAB.get(), bricks, bricks);
        wallBlock(ModBlocks.VOID_STONE_BRICK_WALL.get(), bricks);
        models().wallInventory("void_stone_brick_wall_inventory", bricks);

        axisBlock(ModBlocks.VOID_STONE_PILLAR.get(), modLoc("block/void_stone_pillar"), modLoc("block/void_stone_pillar_top"));

        runicVoidStone();
        crystalCluster();
    }

    private void cubeWithItem(RegistryObject<? extends Block> block) {
        simpleBlockWithItem(block.get(), cubeAll(block.get()));
    }

    /**
     * Two stacked full cubes: lit stone below, and a cut-out glyph layer above with Forge per-element emissivity.
     * Only the rune strokes glow; the stone keeps normal lighting and ambient occlusion.
     */
    private void runicVoidStone() {
        ResourceLocation base = modLoc("block/runic_void_stone");
        getVariantBuilder(ModBlocks.RUNIC_VOID_STONE.get()).forAllStates(state -> {
            int glyph = state.getValue(RunicVoidStoneBlock.GLYPH);
            boolean awakened = state.getValue(RunicVoidStoneBlock.AWAKENED);
            String name = "runic_void_stone_glyph_" + glyph + (awakened ? "_awakened" : "");
            return ConfiguredModel.builder().modelFile(runicModel(name, base, modLoc("block/" + name))).build();
        });
    }

    private BlockModelBuilder runicModel(String name, ResourceLocation base, ResourceLocation overlay) {
        return models().withExistingParent(name, mcLoc("block/block"))
                .renderType("cutout")
                .texture("particle", base)
                .texture("base", base)
                .texture("overlay", overlay)
                .element()
                    .from(0, 0, 0).to(16, 16, 16)
                    .allFaces((dir, face) -> face.texture("#base").cullface(dir))
                .end()
                .element()
                    .from(0, 0, 0).to(16, 16, 16)
                    .shade(false)
                    .emissivity(15, 15)
                    .ao(false)
                    .allFaces((dir, face) -> face.texture("#overlay").cullface(dir))
                .end();
    }

    private void crystalCluster() {
        Block block = ModBlocks.VOID_CRYSTAL_CLUSTER.get();
        ModelFile model = models().cross(name(block), blockTexture(block)).renderType("cutout");
        directionalBlock(block, model);
    }

    private static String name(Block block) {
        ResourceLocation key = ForgeRegistries.BLOCKS.getKey(block);
        if (key == null) {
            throw new IllegalStateException("Unregistered block " + block);
        }
        return key.getPath();
    }
}
