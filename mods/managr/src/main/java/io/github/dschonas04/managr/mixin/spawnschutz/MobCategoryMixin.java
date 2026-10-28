package io.github.dschonas04.managr.mixin.spawnschutz;

import io.github.dschonas04.managr.spawnschutz.Dichte;
import net.minecraft.world.entity.MobCategory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Raises or lowers how many mobs of a category may live around the players. */
@Mixin(MobCategory.class)
public abstract class MobCategoryMixin {

    @Inject(method = "getMaxInstancesPerChunk()I", at = @At("RETURN"), cancellable = true)
    private void spawnguard$grenze(CallbackInfoReturnable<Integer> rueckruf) {
        int vanilla = rueckruf.getReturnValue();
        int neu = Dichte.grenze((MobCategory) (Object) this, vanilla);
        if (neu != vanilla) {
            rueckruf.setReturnValue(neu);
        }
    }
}
