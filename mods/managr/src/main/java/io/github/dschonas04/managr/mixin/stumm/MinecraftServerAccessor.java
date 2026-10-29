// Autor: Dschonas04 (https://github.com/Dschonas04)

package io.github.dschonas04.managr.mixin.stumm;

import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.storage.LevelStorageSource;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Macht den Weltspeicher erreichbar, um den Ordner einer Dimension zu finden (für /sichern). */
@Mixin(MinecraftServer.class)
public interface MinecraftServerAccessor {

    @Accessor("storageSource")
    LevelStorageSource.LevelStorageAccess managr$speicher();
}
