package com.ananttomar.aetherfall.block;

import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import org.jetbrains.annotations.Nullable;

/**
 * The glowing rune masonry of the Void Temple.
 * <ul>
 *     <li>{@link #GLYPH}: one of four carved runes. Chosen from the block position on placement, so a wall of runic
 *     stone always reads as script instead of a repeating tile.</li>
 *     <li>{@link #AWAKENED}: set by the Void Altar while the World Eater lives. Awakened runes burn at full light.</li>
 * </ul>
 */
public class RunicVoidStoneBlock extends Block {
    public static final int GLYPH_COUNT = 4;
    public static final IntegerProperty GLYPH = IntegerProperty.create("glyph", 0, GLYPH_COUNT - 1);
    public static final BooleanProperty AWAKENED = BooleanProperty.create("awakened");
    public static final int DORMANT_LIGHT = 9;
    public static final int AWAKENED_LIGHT = 15;

    public RunicVoidStoneBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(GLYPH, 0).setValue(AWAKENED, false));
    }

    /** Light level for a given state; used by the block properties' light function. */
    public static int lightLevel(BlockState state) {
        return state.getValue(AWAKENED) ? AWAKENED_LIGHT : DORMANT_LIGHT;
    }

    /** Deterministic glyph for a position, so structures and hand-placed walls look the same everywhere. */
    public static int glyphFor(BlockPos pos) {
        long seed = Mth.getSeed(pos.getX(), pos.getY(), pos.getZ());
        return (int) Math.floorMod(seed >> 16, GLYPH_COUNT);
    }

    @Override
    public @Nullable BlockState getStateForPlacement(BlockPlaceContext context) {
        return defaultBlockState().setValue(GLYPH, glyphFor(context.getClickedPos()));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(GLYPH, AWAKENED);
    }

    /** Convenience for the altar: same glyph, toggled glow. */
    public static BlockState withAwakened(BlockState state, boolean awakened) {
        return state.hasProperty(AWAKENED) ? state.setValue(AWAKENED, awakened) : state;
    }
}
