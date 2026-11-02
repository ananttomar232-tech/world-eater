package com.ananttomar.aetherfall.command;

import com.ananttomar.aetherfall.AetherfallMod;
import com.ananttomar.aetherfall.entity.boss.AetherfallEntity;
import com.ananttomar.aetherfall.entity.boss.AttackType;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.BoolArgumentType;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.network.chat.Component;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Optional;

/**
 * Operator tools for map makers and server admins (permission level 2). Each acts on the nearest World Eater within
 * 128 blocks of the command source:
 * <pre>
 * /aetherfall attack &lt;name&gt;   force an attack (swipe, void_breath, meteor_shower, ...)
 * /aetherfall phase &lt;1-3&gt;     set the fight phase (no roar)
 * /aetherfall fly &lt;true|false&gt; put it in the air or on the ground
 * </pre>
 */
@Mod.EventBusSubscriber(modid = AetherfallMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class AetherfallCommands {
    private static final List<String> ATTACKS = Arrays.stream(AttackType.values())
            .filter(a -> a != AttackType.NONE)
            .map(a -> a.name().toLowerCase(Locale.ROOT))
            .toList();

    private AetherfallCommands() {
    }

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        CommandDispatcher<CommandSourceStack> dispatcher = event.getDispatcher();
        dispatcher.register(Commands.literal("aetherfall")
                .requires(source -> source.hasPermission(2))
                .then(Commands.literal("attack")
                        .then(Commands.argument("name", StringArgumentType.word())
                                .suggests((ctx, builder) -> SharedSuggestionProvider.suggest(ATTACKS, builder))
                                .executes(AetherfallCommands::attack)))
                .then(Commands.literal("phase")
                        .then(Commands.argument("phase", IntegerArgumentType.integer(1, 3))
                                .executes(ctx -> withBoss(ctx, boss -> {
                                    int phase = IntegerArgumentType.getInteger(ctx, "phase");
                                    boss.forcePhase(phase);
                                    return "Phase set to " + phase;
                                }))))
                .then(Commands.literal("fly")
                        .then(Commands.argument("flying", BoolArgumentType.bool())
                                .executes(ctx -> withBoss(ctx, boss -> {
                                    boolean flying = BoolArgumentType.getBool(ctx, "flying");
                                    boss.setFlying(flying);
                                    if (flying) {
                                        boss.setPos(boss.getX(), boss.getY() + 8.0D, boss.getZ());
                                    }
                                    return flying ? "Now flying" : "Now grounded";
                                })))));
    }

    private static int attack(CommandContext<CommandSourceStack> ctx) {
        String name = StringArgumentType.getString(ctx, "name").toUpperCase(Locale.ROOT);
        AttackType type;
        try {
            type = AttackType.valueOf(name);
        } catch (IllegalArgumentException e) {
            ctx.getSource().sendFailure(Component.literal("Unknown attack: " + name.toLowerCase(Locale.ROOT)));
            return 0;
        }
        return withBoss(ctx, boss -> {
            boss.queueAttack(type);
            return "Queued " + type.name().toLowerCase(Locale.ROOT);
        });
    }

    private static int withBoss(CommandContext<CommandSourceStack> ctx, java.util.function.Function<AetherfallEntity, String> action) {
        CommandSourceStack source = ctx.getSource();
        Optional<AetherfallEntity> boss = source.getLevel()
                .getEntitiesOfClass(AetherfallEntity.class, new AABB(source.getPosition(), source.getPosition()).inflate(128.0D))
                .stream()
                .filter(AetherfallEntity::isAlive)
                .min(Comparator.comparingDouble(b -> b.distanceToSqr(source.getPosition())));
        if (boss.isEmpty()) {
            source.sendFailure(Component.literal("No World Eater within 128 blocks"));
            return 0;
        }
        String message = action.apply(boss.get());
        source.sendSuccess(() -> Component.literal(message), true);
        return 1;
    }
}
