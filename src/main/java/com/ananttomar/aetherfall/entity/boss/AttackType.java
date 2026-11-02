package com.ananttomar.aetherfall.entity.boss;

/**
 * Every action the World Eater can take, with its timing and selection rules.
 * <p>
 * Durations and cooldowns are in ticks at tempo 1.0; the boss speeds them up as it grows desperate
 * (see {@link AetherfallEntity#tempo()}). Ranges are measured from the edge of the boss's hitbox.
 * The {@code animation} names match the clips in {@code animations/world_eater.animation.json}.
 */
public enum AttackType {
    NONE(0, 0, 0, 0, Mode.ANY, 0, 0, false, ""),

    /** Heavy claw rake across the front arc. Huge knockback; breaks shields. */
    SWIPE(1, 32, 22, 12, Mode.GROUND, 0.0F, 6.0F, true, "swipe"),
    /** Full spin: the crystal tail clears everything around the boss. */
    TAIL_SWEEP(2, 38, 30, 9, Mode.GROUND, 0.0F, 7.0F, true, "tail_sweep"),
    /** Charged beam of void energy that tracks its target and applies Erosion. */
    VOID_BREATH(3, 110, 60, 9, Mode.ANY, 5.0F, 40.0F, true, "void_breath"),
    /** Ultimate: the sky cracks and meteors rain on every target. */
    METEOR_SHOWER(4, 130, 160, 6, Mode.ANY, 0.0F, 64.0F, true, "meteor_shower", 2),
    /** One mighty wingbeat: a cone of wind that hurls players and deflects projectiles. */
    WING_GUST(5, 40, 36, 7, Mode.ANY, 0.0F, 16.0F, true, "wing_gust"),
    /** From the air: rise, lock on, plunge into the ground with a shockwave. Ends grounded. */
    DIVE_SLAM(6, 72, 50, 10, Mode.AIR, 4.0F, 44.0F, true, "dive_slam"),
    /** A singularity in its jaws drags everyone in, then implodes. */
    GRAVITY_WELL(7, 84, 120, 6, Mode.ANY, 0.0F, 26.0F, true, "gravity_well", 2),
    /** Rips Voidlings out of the dark. */
    SUMMON_VOIDLINGS(8, 52, 200, 5, Mode.ANY, 0.0F, 64.0F, true, "summon", 2),
    /** Phase change: invulnerable roar that blinds and staggers. Never chosen randomly. */
    PHASE_ROAR(9, 80, 20, 0, Mode.ANY, 0.0F, 999.0F, false, "roar"),
    /** Leaves the ground. */
    TAKEOFF(10, 40, 10, 0, Mode.GROUND, 0.0F, 999.0F, true, "takeoff"),
    /** Returns to the ground. */
    LAND(11, 60, 10, 0, Mode.AIR, 0.0F, 999.0F, true, "land");

    public enum Mode { GROUND, AIR, ANY }

    private static final AttackType[] BY_ID = new AttackType[values().length];

    static {
        for (AttackType type : values()) {
            BY_ID[type.id] = type;
        }
    }

    public final int id;
    public final int duration;
    public final int cooldown;
    public final int weight;
    public final Mode mode;
    public final float minRange;
    public final float maxRange;
    public final boolean selectable;
    public final String animation;
    public final int minPhase;

    AttackType(int id, int duration, int cooldown, int weight, Mode mode, float minRange, float maxRange,
               boolean selectable, String animation) {
        this(id, duration, cooldown, weight, mode, minRange, maxRange, selectable, animation, 1);
    }

    AttackType(int id, int duration, int cooldown, int weight, Mode mode, float minRange, float maxRange,
               boolean selectable, String animation, int minPhase) {
        this.id = id;
        this.duration = duration;
        this.cooldown = cooldown;
        this.weight = weight;
        this.mode = mode;
        this.minRange = minRange;
        this.maxRange = maxRange;
        this.selectable = selectable;
        this.animation = animation;
        this.minPhase = minPhase;
    }

    public static AttackType byId(int id) {
        return id >= 0 && id < BY_ID.length ? BY_ID[id] : NONE;
    }

    public boolean allows(boolean flying) {
        return mode == Mode.ANY || (mode == Mode.AIR) == flying;
    }
}
