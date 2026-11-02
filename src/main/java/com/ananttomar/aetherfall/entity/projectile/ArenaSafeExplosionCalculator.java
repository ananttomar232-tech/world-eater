package com.ananttomar.aetherfall.entity.projectile;

import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.ExplosionDamageCalculator;
import net.minecraft.world.level.block.state.BlockState;

/** Explosion rules for the World Eater: everything breaks except the Void Temple itself (when protection is on). */
public class ArenaSafeExplosionCalculator extends ExplosionDamageCalculator {
    public static final ArenaSafeExplosionCalculator INSTANCE = new ArenaSafeExplosionCalculator();

    @Override
    public boolean shouldBlockExplode(Explosion explosion, BlockGetter level, BlockPos pos, BlockState state, float power) {
        return !AetherfallEntity.isProtected(state) && super.shouldBlockExplode(explosion, level, pos, state, power);
    }
}
