// Autor: Dschonas04 (https://github.com/Dschonas04)

package io.github.dschonas04.managr.spawnschutz;

import net.minecraft.world.entity.MobCategory;

/** How many mobs may live near the players, and how often animals get a chance to spawn. */
public final class Dichte {

    /** Counts the level ticks that ask which categories may spawn. */
    private static int takt;

    /** What the last decision was, so both switches of one call agree. */
    private static boolean tiereJetzt;

    private Dichte() {
    }

    public static int grenze(MobCategory kategorie, int vanilla) {
        Einstellungen werte = SpawnGuard.einstellungen();
        double faktor = switch (kategorie.getName()) {
            case "monster" -> werte.monsterCap;
            case "creature" -> werte.animalCap;
            case "water_creature", "underground_water_creature", "axolotls" -> werte.waterCap;
            case "ambient", "water_ambient" -> werte.ambientCap;
            default -> 1.0;
        };
        if (faktor == 1.0) {
            return vanilla;
        }
        return Math.max(1, (int) Math.round(vanilla * faktor));
    }

    /**
     * Vanilla lets friendly mobs try to spawn once every 400 ticks. A shorter interval means
     * animals come back on their own instead of only appearing when a chunk is generated.
     */
    public static boolean tiereDuerfen(boolean vanilla) {
        int abstand = SpawnGuard.einstellungen().animalIntervalTicks;
        if (vanilla || abstand >= 400) {
            tiereJetzt = vanilla;
            return vanilla;
        }
        takt++;
        tiereJetzt = takt % Math.max(1, abstand) == 0;
        return tiereJetzt;
    }

    /** The second switch of the same call — persistent categories such as animals. */
    public static boolean tiereDuerfenNoch(boolean vanilla) {
        return vanilla || tiereJetzt;
    }
}
