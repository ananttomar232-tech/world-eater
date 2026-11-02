package com.ananttomar.aetherfall.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * An item with italic lore lines read from the language file:
 * {@code item.aetherfall.<name>.lore.0}, {@code .lore.1}, ... and, optionally, a glint.
 */
public class AetherfallLoreItem extends Item {
    private final int loreLines;
    private final boolean foil;

    public AetherfallLoreItem(Properties properties, int loreLines, boolean foil) {
        super(properties);
        this.loreLines = loreLines;
        this.foil = foil;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        for (int i = 0; i < loreLines; i++) {
            tooltip.add(Component.translatable(getDescriptionId() + ".lore." + i)
                    .withStyle(i == 0 ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.DARK_GRAY)
                    .withStyle(ChatFormatting.ITALIC));
        }
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return foil || super.isFoil(stack);
    }
}
