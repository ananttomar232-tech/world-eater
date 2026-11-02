package com.ananttomar.aetherfall.block;

import com.ananttomar.aetherfall.config.AetherfallConfig;
import com.ananttomar.aetherfall.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
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
        long h = (pos.getX() * 3129871L) ^ (pos.getZ() * 116129781L) ^ pos.getY();
        h = h * h * 42317861L + h * 11L;
        return (int) Math.floorMod(h >> 16, (long) GLYPH_COUNT);
    }

    @Override
    public @Nullable BlockState getStateForPlacement(BlockPlaceContext context) {
        return defaultBlockState().setValue(GLYPH, glyphFor(context.getClickedPos()));
    }

    /** Embers drift off the rune face; awakened runes burn with many more. */
    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        boolean awakened = state.getValue(AWAKENED);
        if (random.nextInt(awakened ? 2 : 10) >= AetherfallConfig.particles(1, random)) {
            return;
        }
        Direction face = Direction.getRandom(random);
        BlockPos out = pos.relative(face);
        if (level.getBlockState(out).isSolidRender(level, out)) {
            return;
        }
        double x = pos.getX() + 0.5D + face.getStepX() * 0.52D + (face.getStepX() == 0 ? (random.nextDouble() - 0.5D) * 0.8D : 0.0D);
        double y = pos.getY() + 0.5D + face.getStepY() * 0.52D + (face.getStepY() == 0 ? (random.nextDouble() - 0.5D) * 0.8D : 0.0D);
        double z = pos.getZ() + 0.5D + face.getStepZ() * 0.52D + (face.getStepZ() == 0 ? (random.nextDouble() - 0.5D) * 0.8D : 0.0D);
        level.addParticle(ModParticles.VOID_EMBER.get(), x, y, z, face.getStepX() * 0.01D, 0.02D + random.nextDouble() * 0.02D,
                face.getStepZ() * 0.01D);
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
