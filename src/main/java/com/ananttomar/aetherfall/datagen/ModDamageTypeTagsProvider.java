package com.ananttomar.aetherfall.datagen;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.damage.ModDamageTypes;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.PackOutput;
import net.minecraft.data.tags.TagsProvider;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageType;
import net.minecraftforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

/**
 * Vanilla behaviour tags for the mod's damage types:
 * Erosion pierces armor and never knocks back; the beam doesn't knock back (it would juggle players);
 * meteors count as explosions (Blast Protection works); shockwaves count as explosions too.
 */
public class ModDamageTypeTagsProvider extends TagsProvider<DamageType> {
    public ModDamageTypeTagsProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> lookup, ExistingFileHelper files) {
        super(output, Registries.DAMAGE_TYPE, lookup, AetherfallMod.MOD_ID, files);
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        tag(DamageTypeTags.BYPASSES_ARMOR).add(ModDamageTypes.EROSION);
        tag(DamageTypeTags.NO_IMPACT).add(ModDamageTypes.EROSION, ModDamageTypes.VOID_BREATH);
        tag(DamageTypeTags.IS_EXPLOSION).add(ModDamageTypes.VOID_METEOR, ModDamageTypes.VOID_SHOCKWAVE);
    }
}
