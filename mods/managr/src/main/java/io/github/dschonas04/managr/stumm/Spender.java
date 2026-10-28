package io.github.dschonas04.managr.stumm;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.scores.PlayerTeam;
import net.minecraft.world.scores.Scoreboard;
import net.minecraft.world.scores.TeamColor;

/**
 * Spender: Operatoren tragen Spenden ein (/spende), die Top 10 stehen auf einer Ehrentafel am Spawn,
 * Spender haben im Spiel einen goldenen Namen (Tab-Liste, Chat, Namensschild). Liste in config/spender.txt.
 * Die Tode-Tafel (Teams platz1..7) bleibt: dort wird nur die Namensfarbe des Teams gesetzt.
 */
final class Spender {
    private static final Path DATEI = FabricLoader.getInstance().getConfigDir().resolve("spender.txt");
    /** Name -> Summe in Euro, Groß-/Kleinschreibung wie eingetragen. */
    private static final Map<String, Integer> SUMME = new LinkedHashMap<>();
    private static final String TEAM = "spender";
    private static final String TAFEL = "spendertafel";
    private static final String ORT = "0.5 66.2 -8.5";
    private static int tafelIn = -1;

    private Spender() {}

    static void register() {
        laden();
        CommandRegistrationCallback.EVENT.register((dispatcher, registry, environment) -> {
            dispatcher.register(Commands.literal("spende").requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                    .then(Commands.literal("setzen").then(Commands.argument("spieler", StringArgumentType.word())
                            .then(Commands.argument("euro", IntegerArgumentType.integer(0)).executes(c -> {
                                String name = name(StringArgumentType.getString(c, "spieler"));
                                SUMME.put(name, IntegerArgumentType.getInteger(c, "euro"));
                                return geaendert(c.getSource().getServer(), c.getSource(), name);
                            }))))
                    .then(Commands.literal("entfernen").then(Commands.argument("spieler", StringArgumentType.word()).executes(c -> {
                        String name = name(StringArgumentType.getString(c, "spieler"));
                        boolean war = SUMME.remove(name) != null;
                        geaendert(c.getSource().getServer(), null, name);
                        c.getSource().sendSuccess(() -> Component.literal(war ? name + " ist kein Spender mehr." : name + " war nicht eingetragen."), true);
                        return war ? 1 : 0;
                    })))
                    .then(Commands.literal("liste").executes(c -> {
                        StringBuilder sb = new StringBuilder(SUMME.isEmpty() ? "Noch keine Spender." : "Spender:");
                        int i = 1;
                        for (Map.Entry<String, Integer> e : rangliste()) sb.append("\n").append(i++).append(". ").append(e.getKey()).append(" - ").append(e.getValue()).append(" €");
                        c.getSource().sendSuccess(() -> Component.literal(sb.toString()), false);
                        return SUMME.size();
                    }))
                    .then(Commands.argument("spieler", StringArgumentType.word())
                            .then(Commands.argument("euro", IntegerArgumentType.integer(1)).executes(c -> {
                                String name = name(StringArgumentType.getString(c, "spieler"));
                                SUMME.merge(name, IntegerArgumentType.getInteger(c, "euro"), Integer::sum);
                                return geaendert(c.getSource().getServer(), c.getSource(), name);
                            }))));
            dispatcher.register(Commands.literal("spender").executes(c -> {
                StringBuilder sb = new StringBuilder(SUMME.isEmpty() ? "Noch keine Spender." : "Danke an unsere Spender:");
                int i = 1;
                for (Map.Entry<String, Integer> e : rangliste()) sb.append("\n").append(i++).append(". ").append(e.getKey());
                c.getSource().sendSuccess(() -> Component.literal(sb.toString()).withStyle(ChatFormatting.GOLD), false);
                return SUMME.size();
            }));
        });
        ServerLifecycleEvents.SERVER_STARTED.register(server -> {
            befehl(server, "forceload add 0 -9");
            tafelIn = 100;
        });
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (tafelIn > 0 && --tafelIn == 0) tafel(server);
            if (server.getTickCount() % 20 == 0) faerben(server);
        });
    }

    /** Ein schon bekannter Name behält seine Schreibweise, sonst die eines Online-Spielers, sonst wie getippt. */
    private static String name(String getippt) {
        for (String n : SUMME.keySet()) if (n.equalsIgnoreCase(getippt)) return n;
        return getippt;
    }

    private static boolean istSpender(String name) {
        for (String n : SUMME.keySet()) if (n.equalsIgnoreCase(name)) return true;
        return false;
    }

    private static List<Map.Entry<String, Integer>> rangliste() {
        List<Map.Entry<String, Integer>> liste = new ArrayList<>(SUMME.entrySet());
        liste.removeIf(e -> e.getValue() <= 0);
        liste.sort((a, b) -> b.getValue() != a.getValue().intValue() ? b.getValue() - a.getValue() : a.getKey().compareToIgnoreCase(b.getKey()));
        return liste;
    }

    private static int geaendert(MinecraftServer server, net.minecraft.commands.CommandSourceStack quelle, String name) {
        speichern();
        tafel(server);
        faerben(server);
        if (quelle != null) {
            Integer summe = SUMME.get(name);
            quelle.sendSuccess(() -> Component.literal(name + ": " + summe + " € insgesamt"), true);
        }
        return 1;
    }

    /** Spender bekommen einen goldenen Namen; wer auf der Tode-Tafel steht, behält sein platz-Team. */
    private static void faerben(MinecraftServer server) {
        Scoreboard board = server.getScoreboard();
        PlayerTeam spender = board.getPlayerTeam(TEAM);
        if (spender == null) {
            spender = board.addPlayerTeam(TEAM);
            spender.setColor(Optional.of(TeamColor.GOLD));
        }
        for (ServerPlayer player : server.getPlayerList().getPlayers()) {
            String name = player.getGameProfile().name();
            boolean gold = istSpender(name);
            PlayerTeam team = board.getPlayersTeam(name);
            if (team != null && team.getName().startsWith("platz")) {
                Optional<TeamColor> farbe = gold ? Optional.of(TeamColor.GOLD) : Optional.empty();
                if (!team.getColor().equals(farbe)) team.setColor(farbe);
            } else if (gold && team == null) {
                board.addPlayerToTeam(name, spender);
            } else if (!gold && team == spender) {
                board.removePlayerFromTeam(name, spender);
            }
        }
    }

    /** Die Ehrentafel: ein schwebender Text über dem Spawnplatz, immer dem Betrachter zugewandt. */
    private static void tafel(MinecraftServer server) {
        StringBuilder text = new StringBuilder("[{text:\"\"},{text:\"\\u2605 Top-Spender \\u2605\\n\",color:\"gold\",bold:true}");
        List<Map.Entry<String, Integer>> liste = rangliste();
        if (liste.isEmpty()) text.append(",{text:\"\\nNoch keine Spender\",color:\"gray\"}");
        for (int i = 0; i < Math.min(10, liste.size()); i++) {
            String farbe = i == 0 ? "gold" : i < 3 ? "yellow" : "white";
            text.append(",{text:\"\\n").append(i + 1).append(". \",color:\"gray\"},{text:\"")
                    .append(liste.get(i).getKey().replaceAll("[^A-Za-z0-9_]", "")).append("\",color:\"").append(farbe).append("\"")
                    .append(i == 0 ? ",bold:true" : "").append("}");
        }
        text.append(",{text:\"\\n\\nDanke f\\u00fcr eure Unterst\\u00fctzung!\",color:\"gray\",italic:true}]");
        befehl(server, "kill @e[type=text_display,tag=" + TAFEL + "]");
        befehl(server, "summon text_display " + ORT + " {Tags:[\"" + TAFEL + "\"],billboard:\"vertical\",alignment:\"center\","
                + "line_width:220,background:1426063360,shadow:1b,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],"
                + "translation:[0f,0f,0f],scale:[1.3f,1.3f,1.3f]},text:" + text + "}");
    }

    private static void befehl(MinecraftServer server, String befehl) {
        server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), befehl);
    }

    private static void laden() {
        try {
            if (!Files.exists(DATEI)) return;
            for (String zeile : Files.readAllLines(DATEI, StandardCharsets.UTF_8)) {
                String[] t = zeile.trim().split("\\s+");
                if (t.length == 2) SUMME.put(t[0], Integer.parseInt(t[1]));
            }
        } catch (IOException | NumberFormatException e) {
            throw new IllegalStateException("config/spender.txt nicht lesbar", e);
        }
    }

    private static void speichern() {
        StringBuilder sb = new StringBuilder();
        SUMME.forEach((name, euro) -> sb.append(name).append(' ').append(euro).append('\n'));
        try {
            Files.writeString(DATEI, sb.toString(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new IllegalStateException("config/spender.txt nicht schreibbar", e);
        }
    }
}
