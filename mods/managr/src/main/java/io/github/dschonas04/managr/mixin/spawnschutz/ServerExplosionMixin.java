// Autor: Dschonas04 (https://github.com/Dschonas04)

package io.github.dschonas04.managr.mixin.spawnschutz;

import io.github.dschonas04.managr.spawnschutz.Bereich;
import io.github.dschonas04.managr.spawnschutz.SpawnGuard;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ServerExplosion;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Keeps blocks inside the guarded area whole when something explodes. The explosion still
 * happens — sound, particles, knockback and damage to mobs and players stay — it just breaks
 * and ignites nothing inside the area.
 */
@Mixin(ServerExplosion.class)
public abstract class ServerExplosionMixin {

    @Inject(method = "calculateExplodedPositions()Ljava/util/List;", at = @At("RETURN"), cancellable = true)
    private void spawnguard$bloeckeSchonen(CallbackInfoReturnable<List<BlockPos>> rueckruf) {
        if (!SpawnGuard.einstellungen().protectBlocksFromExplosions) {
            return;
        }
        ServerLevel welt = ((ServerExplosion) (Object) this).level();
        List<BlockPos> alle = rueckruf.getReturnValue();
        List<BlockPos> erlaubt = new ArrayList<>(alle.size());
        for (BlockPos ort : alle) {
            if (!Bereich.block(welt.dimension(), ort)) {
                erlaubt.add(ort);
            }
        }
        if (erlaubt.size() != alle.size()) {
            if (SpawnGuard.einstellungen().debug) {
                SpawnGuard.LOG.info("kept {} blocks whole in an explosion", alle.size() - erlaubt.size());
            }
            rueckruf.setReturnValue(erlaubt);
        }
    }
}
