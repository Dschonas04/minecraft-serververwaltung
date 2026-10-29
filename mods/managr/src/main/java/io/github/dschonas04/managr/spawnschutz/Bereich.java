// Autor: Dschonas04 (https://github.com/Dschonas04)

package io.github.dschonas04.managr.spawnschutz;

import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;

/** Tells whether a chunk or a block position lies inside the guarded area. */
public final class Bereich {

    private Bereich() {
    }

    public static boolean chunk(ResourceKey<Level> welt, int chunkX, int chunkZ) {
        Einstellungen werte = SpawnGuard.einstellungen();
        if (!werte.enabled || !welt.identifier().toString().equals(werte.dimension)) {
            return false;
        }
        int mitteX = werte.centerX >> 4;
        int mitteZ = werte.centerZ >> 4;
        return Math.abs(chunkX - mitteX) <= werte.radiusChunks
                && Math.abs(chunkZ - mitteZ) <= werte.radiusChunks;
    }

    public static boolean block(ResourceKey<Level> welt, BlockPos ort) {
        return chunk(welt, ort.getX() >> 4, ort.getZ() >> 4);
    }
}
