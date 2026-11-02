package com.ananttomar.aetherfall.datagen;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.registry.ModBlocks;
import com.ananttomar.aetherfall.registry.ModItems;
import net.minecraft.data.PackOutput;
import net.minecraftforge.client.model.generators.ItemModelProvider;
import net.minecraftforge.common.data.ExistingFileHelper;

/** Item models for non-cube block items and every plain item. Cube blocks get theirs from the blockstate provider. */
public class ModItemModelProvider extends ItemModelProvider {
    public ModItemModelProvider(PackOutput output, ExistingFileHelper files) {
        super(output, AetherfallMod.MOD_ID, files);
    }

    @Override
    protected void registerModels() {
        basicItem(ModItems.VOID_CRYSTAL_SHARD.get());
        basicItem(ModItems.VOID_SCALE.get());
        basicItem(ModItems.WORLD_EATERS_CORE.get());
        basicItem(ModItems.VOID_SIGIL.get());
        basicItem(ModItems.MUSIC_DISC_WORLD_EATER.get());
        withExistingParent(ModItems.WORLD_EATER_SPAWN_EGG.getId().getPath(), mcLoc("item/template_spawn_egg"));
        withExistingParent(ModItems.VOIDLING_SPAWN_EGG.getId().getPath(), mcLoc("item/template_spawn_egg"));

        blockParent("void_stone_brick_stairs", "void_stone_brick_stairs");
        blockParent("void_stone_brick_slab", "void_stone_brick_slab");
        blockParent("void_stone_brick_wall", "void_stone_brick_wall_inventory");
        blockParent("void_stone_pillar", "void_stone_pillar");
        blockParent("runic_void_stone", "runic_void_stone_glyph_0");

        withExistingParent(ModBlocks.VOID_CRYSTAL_CLUSTER.getId().getPath(), mcLoc("item/generated"))
                .texture("layer0", modLoc("block/void_crystal_cluster"));
    }

    private void blockParent(String item, String blockModel) {
        withExistingParent(item, modLoc("block/" + blockModel));
    }
}
