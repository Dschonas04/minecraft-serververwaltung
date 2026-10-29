// Autor: Dschonas04 (https://github.com/Dschonas04)

package io.github.dschonas04.managr.spawnschutz;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.loader.api.FabricLoader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Keeps hostile mobs from spawning inside a chosen area — nothing is spawned and killed
 * again, the spawn attempt itself is dropped.
 */
public final class SpawnGuard implements ModInitializer {

    public static final String ID = "spawn-guard";
    public static final Logger LOG = LoggerFactory.getLogger("Spawn Guard");

    private static Einstellungen einstellungen = new Einstellungen();

    public static Einstellungen einstellungen() {
        return einstellungen;
    }

    @Override
    public void onInitialize() {
        einstellungen = Einstellungen.lies(
                FabricLoader.getInstance().getConfigDir().resolve(ID + ".properties"));
        LOG.info("caps at monster {}x, animal {}x, water {}x, ambient {}x, animals try every {} ticks",
                einstellungen.monsterCap, einstellungen.animalCap, einstellungen.waterCap,
                einstellungen.ambientCap, einstellungen.animalIntervalTicks);
        if (!einstellungen.enabled) {
            LOG.info("the guarded area is switched off in the config");
            return;
        }
        LOG.info("no hostile spawns within {} chunks of {} {}/{}{}",
                einstellungen.radiusChunks, einstellungen.dimension,
                einstellungen.centerX, einstellungen.centerZ,
                einstellungen.blockOtherSources ? ", other spawn sources blocked too" : "");
        if (einstellungen.protectBlocksFromExplosions) {
            LOG.info("explosions break no blocks inside the area");
        }
    }
}
