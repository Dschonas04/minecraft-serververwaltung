package io.github.dschonas04.managr.stumm;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.message.v1.ServerMessageEvents;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/**
 * /stumm <Spieler> schaltet Chat, /me, /msg und /say eines Spielers stumm,
 * /laut <Spieler> hebt es auf, /stumm liste zeigt alle. Nur für Operatoren.
 * Die Liste bleibt in config/stumm.txt über Neustarts erhalten.
 */
public final class Stumm implements ModInitializer {
    private static final Path DATEI = FabricLoader.getInstance().getConfigDir().resolve("stumm.txt");
    private static final Map<UUID, String> STUMM = new LinkedHashMap<>();

    @Override
    public void onInitialize() {
        LogFilter.install();
        Werkzeugwache.register();
        Spender.register();
        Hexenhuette.register();
        Tierwache.register();
        laden();
        ServerMessageEvents.ALLOW_CHAT_MESSAGE.register((message, sender, params) -> erlaubt(sender));
        ServerMessageEvents.ALLOW_COMMAND_MESSAGE.register((message, source, params) -> {
            ServerPlayer player = source.getPlayer();
            return player == null || erlaubt(player);
        });
        CommandRegistrationCallback.EVENT.register((dispatcher, registry, environment) -> {
            dispatcher.register(Commands.literal("stumm").requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                    .then(Commands.literal("liste").executes(c -> {
                        c.getSource().sendSuccess(() -> Component.literal(STUMM.isEmpty() ? "Niemand ist stumm." : "Stumm: " + String.join(", ", STUMM.values())), false);
                        return STUMM.size();
                    }))
                    .then(Commands.argument("spieler", EntityArgument.player()).executes(c -> {
                        ServerPlayer p = EntityArgument.getPlayer(c, "spieler");
                        STUMM.put(p.getUUID(), p.getGameProfile().name());
                        speichern();
                        c.getSource().sendSuccess(() -> Component.literal(p.getGameProfile().name() + " ist jetzt stumm."), true);
                        return 1;
                    })));
            dispatcher.register(Commands.literal("laut").requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                    .then(Commands.argument("spieler", EntityArgument.player()).executes(c -> {
                        ServerPlayer p = EntityArgument.getPlayer(c, "spieler");
                        boolean war = STUMM.remove(p.getUUID()) != null;
                        speichern();
                        c.getSource().sendSuccess(() -> Component.literal(p.getGameProfile().name() + (war ? " darf wieder schreiben." : " war nicht stumm.")), true);
                        return war ? 1 : 0;
                    })));
        });
    }

    private static boolean erlaubt(ServerPlayer player) {
        if (!STUMM.containsKey(player.getUUID())) return true;
        player.sendSystemMessage(Component.literal("Du bist stummgeschaltet."));
        return false;
    }

    private static void laden() {
        try {
            if (!Files.exists(DATEI)) return;
            for (String zeile : Files.readAllLines(DATEI, StandardCharsets.UTF_8)) {
                String[] t = zeile.trim().split("\\s+", 2);
                if (t.length == 2) STUMM.put(UUID.fromString(t[0]), t[1]);
            }
        } catch (IOException | IllegalArgumentException e) {
            throw new IllegalStateException("config/stumm.txt nicht lesbar", e);
        }
    }

    private static void speichern() {
        StringBuilder sb = new StringBuilder();
        STUMM.forEach((id, name) -> sb.append(id).append(' ').append(name).append('\n'));
        try {
            Files.writeString(DATEI, sb.toString(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new IllegalStateException("config/stumm.txt nicht schreibbar", e);
        }
    }
}
