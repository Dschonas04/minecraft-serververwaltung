// Autor: Dschonas04 (https://github.com/Dschonas04)

package io.github.dschonas04.managr.stumm;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import io.github.dschonas04.managr.mixin.stumm.MinecraftServerAccessor;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.ColumnPosArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ColumnPos;
import net.minecraft.server.level.ServerLevel;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * /sichern <x z> <radius> kopiert die Regionsdateien, die ein Quadrat um x/z berühren, nach
 * {@code sicherungen/<Zeitpunkt>/} neben dem Weltordner – vor jedem Geländeumbau. Gesichert werden
 * Blöcke (region), Wesen (entities) und Orte wie Betten und Arbeitsblöcke (poi) der aktuellen
 * Dimension. Vorher wird die Welt gespeichert, damit die Kopie den Stand von jetzt enthält.
 * Zurückspielen: Server stoppen, die Dateien an ihren alten Platz kopieren. Nur für Operatoren.
 */
final class Sicherung {
    private static final Logger LOG = LogManager.getLogger("Sicherung");
    private static final String[] ORDNER = {"region", "entities", "poi"};
    private static final DateTimeFormatter ZEIT = DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss");

    private Sicherung() {}

    static void register() {
        CommandRegistrationCallback.EVENT.register((dispatcher, registry, environment) ->
                dispatcher.register(Commands.literal("sichern").requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .then(Commands.argument("mitte", ColumnPosArgument.columnPos())
                                .then(Commands.argument("radius", IntegerArgumentType.integer(0, 4096))
                                        .executes(c -> sichern(c.getSource(), ColumnPosArgument.getColumnPos(c, "mitte"),
                                                IntegerArgumentType.getInteger(c, "radius")))))));
    }

    private static int sichern(CommandSourceStack quelle, ColumnPos mitte, int radius) {
        MinecraftServer server = quelle.getServer();
        ServerLevel level = quelle.getLevel();
        server.saveAllChunks(true, true, true);

        Path dimension = ((MinecraftServerAccessor) server).managr$speicher().getDimensionPath(level.dimension());
        String name = level.dimension().identifier().toString().replace(':', '_');
        Path ziel = server.getServerDirectory().resolve("sicherungen").resolve(LocalDateTime.now().format(ZEIT)).resolve(name);
        // Eine Regionsdatei deckt 512 × 512 Blöcke ab: r.<x>.<z>.mca mit x = Block-x / 512, abgerundet.
        int vonX = Math.floorDiv(mitte.x() - radius, 512);
        int bisX = Math.floorDiv(mitte.x() + radius, 512);
        int vonZ = Math.floorDiv(mitte.z() - radius, 512);
        int bisZ = Math.floorDiv(mitte.z() + radius, 512);

        int dateien = 0;
        long bytes = 0;
        try {
            for (String ordner : ORDNER) {
                for (int rx = vonX; rx <= bisX; rx++) {
                    for (int rz = vonZ; rz <= bisZ; rz++) {
                        Path datei = dimension.resolve(ordner).resolve("r." + rx + "." + rz + ".mca");
                        if (!Files.isRegularFile(datei)) {
                            continue;
                        }
                        Path kopie = ziel.resolve(ordner).resolve(datei.getFileName());
                        Files.createDirectories(kopie.getParent());
                        Files.copy(datei, kopie, StandardCopyOption.COPY_ATTRIBUTES);
                        dateien++;
                        bytes += Files.size(kopie);
                    }
                }
            }
        } catch (IOException fehler) {
            LOG.error("Sicherung nach {} fehlgeschlagen", ziel, fehler);
            quelle.sendFailure(Component.literal("Sicherung fehlgeschlagen: " + fehler.getMessage()));
            return 0;
        }
        if (dateien == 0) {
            quelle.sendFailure(Component.literal("Dort gibt es noch keine gespeicherten Regionen."));
            return 0;
        }
        Path relativ = server.getServerDirectory().relativize(ziel);
        int anzahl = dateien;
        String groesse = String.format("%.1f MB", bytes / 1024.0 / 1024.0);
        LOG.info("Sicherung: {} Dateien ({}) um {} {} r={} nach {}", anzahl, groesse, mitte.x(), mitte.z(), radius, relativ);
        quelle.sendSuccess(() -> Component.literal("Gesichert: " + anzahl + " Regionsdateien (" + groesse + ") nach " + relativ), true);
        return anzahl;
    }
}
