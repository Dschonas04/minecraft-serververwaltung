package io.github.dschonas04.managr.spawnschutz;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;

/**
 * The contents of {@code config/spawn-guard.properties}.
 *
 * <p>Written with comments on first start, read again on every server start. The area is a
 * square measured in chunks around a block position, so it lines up with how chunks load.
 */
public final class Einstellungen {

    /** Whether the guard does anything at all. */
    public boolean enabled = true;

    /** The world the area sits in. */
    public String dimension = "minecraft:overworld";

    /** Block position the area is centred on. */
    public int centerX = 0;
    public int centerZ = 0;

    /** Half the width of the area, in chunks: 10 covers 21 by 21 chunks. */
    public int radiusChunks = 10;

    /**
     * Also stop mobs that do not come from natural spawning: monster spawners, patrols,
     * mod-added spawners, spawn eggs and {@code /summon}.
     */
    public boolean blockOtherSources = true;

    /** How many monsters may live around the players, as a multiple of vanilla. */
    public double monsterCap = 1.0;

    /** The same for animals such as cows, sheep and pigs. */
    public double animalCap = 1.0;

    /** The same for fish, squid, dolphins and axolotls. */
    public double waterCap = 1.0;

    /** The same for bats and the small fish that fill out a biome. */
    public double ambientCap = 1.0;

    /**
     * How often animals get a chance to spawn, in ticks. Vanilla is 400 and only tries then,
     * which is why animals hardly ever come back. A smaller number means more animals.
     */
    public int animalIntervalTicks = 400;

    /** Log every dropped spawn. Noisy; for checking that the area is where you meant it. */
    public boolean debug = false;

    private static final String VORLAGE = """
            # Spawn Guard — an area where hostile mobs do not spawn.
            #
            # Mobs are not spawned and removed again: the spawn attempt is dropped, so nothing
            # ever appears, nothing dies, and no drops or death sounds happen.

            # Set to no to leave spawning alone.
            enabled = %s

            # The world the area is in.
            dimension = %s

            # Block position the area is centred on, usually your spawn point.
            center_x = %s
            center_z = %s

            # Half the width in chunks. 10 covers 21 by 21 chunks, about 160 blocks in each
            # direction from the centre.
            radius_chunks = %s

            # Natural spawning is always stopped inside the area. With this set to yes, mobs from
            # monster spawners, patrols, mod spawners, spawn eggs and /summon are stopped as well.
            block_other_sources = %s

            # How many mobs may live around the players, as a multiple of vanilla. 1.0 is
            # vanilla, 1.5 is half as many again. Vanilla allows 70 monsters, 10 animals,
            # 5 water creatures and 15 ambient mobs per 289 loaded chunks.
            monster_cap = %s
            animal_cap = %s
            water_cap = %s
            ambient_cap = %s

            # How often animals get a chance to spawn, in ticks. Vanilla is 400 and only tries
            # then, which is why animals barely come back once an area is emptied. 100 gives them
            # four times as many chances; every value of 400 or more leaves vanilla alone.
            animal_interval = %s

            # Write a log line for every dropped spawn.
            debug = %s
            """;

    public static Einstellungen lies(Path pfad) {
        Einstellungen werte = new Einstellungen();
        if (!Files.exists(pfad)) {
            werte.schreibe(pfad);
            return werte;
        }
        try {
            for (String zeile : Files.readAllLines(pfad)) {
                int raute = zeile.indexOf('#');
                if (raute >= 0) {
                    zeile = zeile.substring(0, raute);
                }
                int gleich = zeile.indexOf('=');
                if (gleich < 0) {
                    continue;
                }
                String schluessel = zeile.substring(0, gleich).trim().toLowerCase(Locale.ROOT);
                String wert = zeile.substring(gleich + 1).trim();
                switch (schluessel) {
                    case "enabled" -> werte.enabled = ja(wert);
                    case "dimension" -> werte.dimension = wert;
                    case "center_x" -> werte.centerX = ganz(wert, werte.centerX);
                    case "center_z" -> werte.centerZ = ganz(wert, werte.centerZ);
                    case "radius_chunks" -> werte.radiusChunks = ganz(wert, werte.radiusChunks);
                    case "block_other_sources" -> werte.blockOtherSources = ja(wert);
                    case "monster_cap" -> werte.monsterCap = zahl(wert, werte.monsterCap);
                    case "animal_cap" -> werte.animalCap = zahl(wert, werte.animalCap);
                    case "water_cap" -> werte.waterCap = zahl(wert, werte.waterCap);
                    case "ambient_cap" -> werte.ambientCap = zahl(wert, werte.ambientCap);
                    case "animal_interval" -> werte.animalIntervalTicks =
                            ganz(wert, werte.animalIntervalTicks);
                    case "debug" -> werte.debug = ja(wert);
                    default -> SpawnGuard.LOG.warn("unknown setting '{}' in {}", schluessel, pfad);
                }
            }
        } catch (IOException fehler) {
            SpawnGuard.LOG.error("could not read {}, using defaults: {}", pfad, fehler.getMessage());
        }
        return werte;
    }

    private static boolean ja(String wert) {
        return List.of("true", "yes", "1", "on").contains(wert.toLowerCase(Locale.ROOT));
    }

    private static double zahl(String wert, double ersatz) {
        try {
            double zahl = Double.parseDouble(wert);
            if (zahl <= 0.0 || zahl > 20.0) {
                SpawnGuard.LOG.warn("{} is outside 0.1 … 20.0, keeping {}", zahl, ersatz);
                return ersatz;
            }
            return zahl;
        } catch (NumberFormatException fehler) {
            SpawnGuard.LOG.warn("'{}' is not a number, keeping {}", wert, ersatz);
            return ersatz;
        }
    }

    private static int ganz(String wert, int ersatz) {
        try {
            return Integer.parseInt(wert);
        } catch (NumberFormatException fehler) {
            SpawnGuard.LOG.warn("'{}' is not a whole number, keeping {}", wert, ersatz);
            return ersatz;
        }
    }

    private void schreibe(Path pfad) {
        try {
            Files.createDirectories(pfad.getParent());
            Files.writeString(pfad, VORLAGE.formatted(enabled ? "yes" : "no", dimension,
                    centerX, centerZ, radiusChunks,
                    blockOtherSources ? "yes" : "no",
                    monsterCap, animalCap, waterCap, ambientCap, animalIntervalTicks,
                    debug ? "yes" : "no"));
            SpawnGuard.LOG.info("wrote a fresh {}", pfad);
        } catch (IOException fehler) {
            SpawnGuard.LOG.error("could not write {}: {}", pfad, fehler.getMessage());
        }
    }
}
