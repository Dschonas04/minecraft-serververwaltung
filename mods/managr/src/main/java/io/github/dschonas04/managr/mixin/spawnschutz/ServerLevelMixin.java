package io.github.dschonas04.managr.mixin.spawnschutz;

import io.github.dschonas04.managr.spawnschutz.Bereich;
import io.github.dschonas04.managr.spawnschutz.SpawnGuard;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Catches every other way a hostile mob can reach the world: monster spawners, patrols,
 * mod-added spawners, spawn eggs and commands.
 */
@Mixin(ServerLevel.class)
public abstract class ServerLevelMixin {

    @Inject(method = "addFreshEntity(Lnet/minecraft/world/entity/Entity;)Z",
            at = @At("HEAD"), cancellable = true)
    private void spawnguard$neuesWesen(Entity wesen, CallbackInfoReturnable<Boolean> rueckruf) {
        if (!SpawnGuard.einstellungen().blockOtherSources || !(wesen instanceof Mob)) {
            return;
        }
        if (wesen.getType().getCategory() != MobCategory.MONSTER) {
            return;
        }
        ServerLevel welt = (ServerLevel) (Object) this;
        if (Bereich.block(welt.dimension(), wesen.blockPosition())) {
            if (SpawnGuard.einstellungen().debug) {
                SpawnGuard.LOG.info("no {} at {}", wesen.getType(), wesen.blockPosition());
            }
            rueckruf.setReturnValue(false);
        }
    }
}
