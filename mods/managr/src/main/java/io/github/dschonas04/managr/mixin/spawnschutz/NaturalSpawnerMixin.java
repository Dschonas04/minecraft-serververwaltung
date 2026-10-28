package io.github.dschonas04.managr.mixin.spawnschutz;

import io.github.dschonas04.managr.spawnschutz.Bereich;
import io.github.dschonas04.managr.spawnschutz.Dichte;
import io.github.dschonas04.managr.spawnschutz.SpawnGuard;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.NaturalSpawner;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.chunk.LevelChunk;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Drops the spawn attempt itself, before a mob is created. */
@Mixin(NaturalSpawner.class)
public abstract class NaturalSpawnerMixin {

    /** Natural spawning, once per chunk and mob category. */
    @Inject(method = "spawnCategoryForChunk(Lnet/minecraft/world/entity/MobCategory;"
            + "Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/world/level/chunk/LevelChunk;"
            + "Lnet/minecraft/world/level/NaturalSpawner$SpawnPredicate;"
            + "Lnet/minecraft/world/level/NaturalSpawner$AfterSpawnCallback;)V",
            at = @At("HEAD"), cancellable = true)
    private static void spawnguard$chunk(MobCategory kategorie, ServerLevel welt, LevelChunk brocken,
                                         NaturalSpawner.SpawnPredicate darf,
                                         NaturalSpawner.AfterSpawnCallback danach,
                                         CallbackInfo rueckruf) {
        if (kategorie != MobCategory.MONSTER) {
            return;
        }
        ChunkPos ort = brocken.getPos();
        if (Bereich.chunk(welt.dimension(), ort.getMiddleBlockX() >> 4, ort.getMiddleBlockZ() >> 4)) {
            if (SpawnGuard.einstellungen().debug) {
                SpawnGuard.LOG.info("no monster spawning in chunk {}", ort);
            }
            rueckruf.cancel();
        }
    }

    /** The mobs a freshly generated chunk starts out with. */
    @Inject(method = "spawnMobsForChunkGeneration(Lnet/minecraft/world/level/ServerLevelAccessor;"
            + "Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/ChunkPos;"
            + "Lnet/minecraft/util/RandomSource;)V",
            at = @At("HEAD"), cancellable = true)
    private static void spawnguard$neueBrocken(ServerLevelAccessor welt, BlockPos mitte,
                                               ChunkPos ort, RandomSource zufall,
                                               CallbackInfo rueckruf) {
        if (Bereich.chunk(welt.getLevel().dimension(),
                ort.getMiddleBlockX() >> 4, ort.getMiddleBlockZ() >> 4)) {
            rueckruf.cancel();
        }
    }

    /** Lets friendly mobs try to spawn more often than vanilla's 400 ticks. */
    @ModifyVariable(method = "getFilteredSpawningCategories(Lnet/minecraft/world/level/NaturalSpawner$SpawnState;ZZ)Ljava/util/List;", at = @At("HEAD"), argsOnly = true, index = 1)
    private static boolean spawnguard$tiere(boolean vanilla) {
        return Dichte.tiereDuerfen(vanilla);
    }

    /** The same call's second switch, which covers the categories that stay loaded. */
    @ModifyVariable(method = "getFilteredSpawningCategories(Lnet/minecraft/world/level/NaturalSpawner$SpawnState;ZZ)Ljava/util/List;", at = @At("HEAD"), argsOnly = true, index = 2)
    private static boolean spawnguard$bleibende(boolean vanilla) {
        return Dichte.tiereDuerfenNoch(vanilla);
    }
}
