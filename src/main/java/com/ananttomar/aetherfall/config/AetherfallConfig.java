package com.ananttomar.aetherfall.config;

import net.minecraftforge.common.ForgeConfigSpec;
import org.apache.commons.lang3.tuple.Pair;

/**
 * Two config files:
 * <ul>
 *     <li>{@code aetherfall-common.toml}: boss balance and world-interaction rules (synced by the server's copy in
 *     multiplayer because every value is read on the logical server only).</li>
 *     <li>{@code aetherfall-client.toml}: presentation only (music, screen shake, HUD).</li>
 * </ul>
 */
public final class AetherfallConfig {
    public static final Common COMMON;
    public static final ForgeConfigSpec COMMON_SPEC;
    public static final Client CLIENT;
    public static final ForgeConfigSpec CLIENT_SPEC;

    static {
        Pair<Common, ForgeConfigSpec> common = new ForgeConfigSpec.Builder().configure(Common::new);
        COMMON = common.getLeft();
        COMMON_SPEC = common.getRight();

        Pair<Client, ForgeConfigSpec> client = new ForgeConfigSpec.Builder().configure(Client::new);
        CLIENT = client.getLeft();
        CLIENT_SPEC = client.getRight();
    }

    private AetherfallConfig() {
    }

    /**
     * Scales a client-side particle count by {@code particleDensity} (percent). Fractions are rounded
     * probabilistically, so 30% of "1 per tick" still produces a particle about every third tick.
     */
    public static int particles(int base, net.minecraft.util.RandomSource random) {
        double density = CLIENT_SPEC.isLoaded() ? CLIENT.particleDensity.get() / 100.0D : 1.0D;
        double scaled = base * density;
        int whole = (int) scaled;
        return whole + (random.nextDouble() < scaled - whole ? 1 : 0);
    }

    public static final class Common {
        // Boss balance
        public final ForgeConfigSpec.DoubleValue bossMaxHealth;
        public final ForgeConfigSpec.DoubleValue bossArmor;
        public final ForgeConfigSpec.DoubleValue bossArmorToughness;
        public final ForgeConfigSpec.DoubleValue bossDamageMultiplier;
        public final ForgeConfigSpec.DoubleValue healthPerExtraPlayer;
        public final ForgeConfigSpec.DoubleValue damagePerExtraPlayer;
        public final ForgeConfigSpec.IntValue playerScalingRadius;
        public final ForgeConfigSpec.BooleanValue scaleWithDifficulty;

        // World interaction
        public final ForgeConfigSpec.BooleanValue respectMobGriefing;
        public final ForgeConfigSpec.BooleanValue meteorsBreakBlocks;
        public final ForgeConfigSpec.BooleanValue breathBreaksBlocks;
        public final ForgeConfigSpec.BooleanValue protectArenaBlocks;
        public final ForgeConfigSpec.DoubleValue meteorExplosionPower;

        // Arena / summoning
        public final ForgeConfigSpec.IntValue altarCooldownTicks;
        public final ForgeConfigSpec.IntValue arenaLeashRadius;
        public final ForgeConfigSpec.BooleanValue templeGenerationEnabled;

        Common(ForgeConfigSpec.Builder builder) {
            builder.comment("Aetherfall, the World Eater: balance values. All values are read on the server.")
                    .push("boss");
            bossMaxHealth = builder
                    .comment("Base maximum health before player-count scaling. Wither = 300, Ender Dragon = 200.")
                    .defineInRange("maxHealth", 1200.0D, 100.0D, 100000.0D);
            bossArmor = builder
                    .comment("Base armor points (vanilla cap is 30).")
                    .defineInRange("armor", 20.0D, 0.0D, 30.0D);
            bossArmorToughness = builder
                    .comment("Base armor toughness.")
                    .defineInRange("armorToughness", 12.0D, 0.0D, 20.0D);
            bossDamageMultiplier = builder
                    .comment("Multiplies the damage of every Aetherfall attack.")
                    .defineInRange("damageMultiplier", 1.0D, 0.1D, 10.0D);
            healthPerExtraPlayer = builder
                    .comment("Fraction of base health added for every player beyond the first inside the scaling radius.")
                    .defineInRange("healthPerExtraPlayer", 0.5D, 0.0D, 5.0D);
            damagePerExtraPlayer = builder
                    .comment("Fraction of damage added for every player beyond the first inside the scaling radius.")
                    .defineInRange("damagePerExtraPlayer", 0.15D, 0.0D, 5.0D);
            playerScalingRadius = builder
                    .comment("Radius (blocks) in which players count toward scaling when the boss is summoned.")
                    .defineInRange("playerScalingRadius", 64, 8, 256);
            scaleWithDifficulty = builder
                    .comment("Easy = 0.75x, Normal = 1x, Hard = 1.35x damage and health.")
                    .define("scaleWithDifficulty", true);
            builder.pop();

            builder.comment("How the World Eater interacts with terrain.").push("world");
            respectMobGriefing = builder
                    .comment("When true, terrain destruction also requires the mobGriefing game rule.")
                    .define("respectMobGriefing", true);
            meteorsBreakBlocks = builder
                    .comment("Meteor impacts carve craters.")
                    .define("meteorsBreakBlocks", true);
            breathBreaksBlocks = builder
                    .comment("Void Breath erodes soft blocks it touches.")
                    .define("breathBreaksBlocks", false);
            protectArenaBlocks = builder
                    .comment("Void Temple blocks (bricks, runes, pillars, altar) are never destroyed by the boss.")
                    .define("protectArenaBlocks", true);
            meteorExplosionPower = builder
                    .comment("Explosion radius of a standard meteor. Enraged meteors use 1.5x.")
                    .defineInRange("meteorExplosionPower", 2.5D, 0.0D, 8.0D);
            builder.pop();

            builder.comment("Summoning and the Void Temple arena.").push("arena");
            altarCooldownTicks = builder
                    .comment("Ticks a Void Altar must rest after the World Eater is defeated before it can be used again.")
                    .defineInRange("altarCooldownTicks", 6000, 0, 1728000);
            arenaLeashRadius = builder
                    .comment("Distance from its altar the boss may travel before it returns. 0 disables the leash.")
                    .defineInRange("arenaLeashRadius", 56, 0, 512);
            templeGenerationEnabled = builder
                    .comment("Generate Ruined Void Temples in the world.")
                    .define("templeGenerationEnabled", true);
            builder.pop();
        }
    }

    public enum BossBarPosition { TOP, BOTTOM }

    public static final class Client {
        public final ForgeConfigSpec.BooleanValue bossMusic;
        public final ForgeConfigSpec.DoubleValue screenShakeIntensity;
        public final ForgeConfigSpec.BooleanValue ornateBossBar;
        public final ForgeConfigSpec.IntValue particleDensity;
        public final ForgeConfigSpec.EnumValue<BossBarPosition> bossBarPosition;

        Client(ForgeConfigSpec.Builder builder) {
            builder.comment("Presentation settings. These never affect gameplay.").push("presentation");
            bossMusic = builder
                    .comment("Play the World Eater battle theme during the fight.")
                    .define("bossMusic", true);
            screenShakeIntensity = builder
                    .comment("Camera shake from roars, slams and meteor impacts. 0 disables it.")
                    .defineInRange("screenShakeIntensity", 1.0D, 0.0D, 2.0D);
            ornateBossBar = builder
                    .comment("Use the gold-and-void ornate boss bar instead of the vanilla bar.")
                    .define("ornateBossBar", true);
            bossBarPosition = builder
                    .comment("Where the ornate boss bar sits: BOTTOM (above the hotbar, as in the reference art) or TOP.")
                    .defineEnum("bossBarPosition", BossBarPosition.BOTTOM);
            particleDensity = builder
                    .comment("Particle density in percent for breath, meteors and wings.")
                    .defineInRange("particleDensity", 100, 10, 200);
            builder.pop();
        }
    }
}
