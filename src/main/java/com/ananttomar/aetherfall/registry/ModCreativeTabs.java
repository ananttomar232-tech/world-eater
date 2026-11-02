package com.ananttomar.aetherfall.registry;

import com.ananttomar.aetherfall.AetherfallMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/** One tab holding everything Aetherfall adds, in registration order (blocks first, then gear and materials). */
public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, AetherfallMod.MOD_ID);

    public static final RegistryObject<CreativeModeTab> AETHERFALL = CREATIVE_TABS.register("aetherfall",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.aetherfall"))
                    .icon(() -> new ItemStack(ModItems.WORLD_EATERS_CORE.get()))
                    .withTabsBefore(CreativeModeTabs.SPAWN_EGGS)
                    .displayItems((parameters, output) -> {
                        // Temple blocks first, then materials, gear and the disc.
                        ModItems.ITEMS.getEntries().stream().map(RegistryObject::get)
                                .filter(item -> item instanceof BlockItem).forEach(output::accept);
                        ModItems.ITEMS.getEntries().stream().map(RegistryObject::get)
                                .filter(item -> !(item instanceof BlockItem)).forEach(output::accept);
                    })
                    .build());

    private ModCreativeTabs() {
    }
}
