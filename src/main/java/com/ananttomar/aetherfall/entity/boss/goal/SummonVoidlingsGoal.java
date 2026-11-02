package com.ananttomar.aetherfall.entity.boss.goal;

import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.ananttomar.aetherfall.entity.minion.VoidlingEntity;
import com.ananttomar.aetherfall.registry.ModEntities;
import com.ananttomar.aetherfall.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.ForgeEventFactory;

/** Tears 3 Voidlings (4 when enraged) out of the dark around the boss, up to {@link AetherfallEntity#MAX_VOIDLINGS}. */
public class SummonVoidlingsGoal extends BossAttackGoal {
    public SummonVoidlingsGoal(AetherfallEntity boss) {
        super(boss, AttackType.SUMMON_VOIDLINGS);
    }

    @Override
    protected void onTick() {
        holdStill();
        faceTarget(8.0F);
        if (at(8)) {
            boss.playBossSound(ModSounds.WORLD_EATER_ROAR.get(), 3.0F, 1.4F);
        }
        if (at(26) && boss.level() instanceof ServerLevel level) {
            int count = Math.min((boss.isEnraged() ? 4 : 3), AetherfallEntity.MAX_VOIDLINGS - boss.countVoidlings());
            float offset = boss.getRandom().nextFloat() * (float) Math.PI * 2.0F;
            for (int i = 0; i < count; i++) {
                double angle = offset + i * Math.PI * 2.0D / Math.max(1, count);
                double radius = boss.getBbWidth() / 2.0D + 2.5D;
                Vec3 spot = boss.position().add(Math.cos(angle) * radius, 0.0D, Math.sin(angle) * radius);
                spawn(level, spot);
            }
        }
    }

    private void spawn(ServerLevel level, Vec3 spot) {
        VoidlingEntity voidling = ModEntities.VOIDLING.get().create(level);
        if (voidling == null) {
            return;
        }
        BlockPos base = BlockPos.containing(spot);
        // Settle on the nearest floor within a few blocks.
        BlockPos pos = base.above(3);
        for (int i = 0; i < 8 && !level.getBlockState(pos.below()).isFaceSturdy(level, pos.below(), Direction.UP); i++) {
            pos = pos.below();
        }
        voidling.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, boss.getRandom().nextFloat() * 360.0F, 0.0F);
        if (!level.noCollision(voidling)) {
            voidling.moveTo(spot.x, boss.getY(), spot.z);
        }
        ForgeEventFactory.onFinalizeSpawn(voidling, level, level.getCurrentDifficultyAt(pos), MobSpawnType.MOB_SUMMONED, null, null);
        voidling.setOwner(boss);
        if (hasTarget()) {
            voidling.setTarget(target);
        }
        level.addFreshEntity(voidling);
        level.playSound(null, voidling.getX(), voidling.getY(), voidling.getZ(), ModSounds.RUNIC_STONE_AWAKEN.get(),
                SoundSource.HOSTILE, 1.2F, 1.3F);
    }
}
