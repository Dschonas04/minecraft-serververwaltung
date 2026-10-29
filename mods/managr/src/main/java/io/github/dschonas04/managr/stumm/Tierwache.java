// Autor: Dschonas04 (https://github.com/Dschonas04)

package io.github.dschonas04.managr.stumm;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.animal.happyghast.HappyGhast;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Schreibt jedes getötete Tier (alle Mobs, die keine Monster sind) mit Täter, Ort und Besitzer ins Server-Log
 * und nach logs/tiere.log. Tote ohne Spieler als Täter nur, wenn das Tier einen Namen oder Besitzer hat oder
 * ein Happy Ghast ist, sonst füllen Farmen das Log.
 */
final class Tierwache {
    private static final Logger LOG = LogManager.getLogger("Tierwache");
    private static final Path DATEI = FabricLoader.getInstance().getGameDir().resolve("logs").resolve("tiere.log");
    private static final DateTimeFormatter ZEIT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private Tierwache() {}

    static void register() {
        ServerLivingEntityEvents.AFTER_DEATH.register(Tierwache::gestorben);
    }

    private static void gestorben(LivingEntity tier, DamageSource quelle) {
        if (!(tier instanceof Mob) || tier instanceof Enemy) return;
        Entity taeter = quelle.getEntity();
        String besitzer = besitzer(tier);
        boolean besonders = tier.hasCustomName() || besitzer != null || tier instanceof HappyGhast;
        if (!(taeter instanceof Player) && !besonders) return;

        BlockPos pos = tier.blockPosition();
        String zeile = String.format("%s getötet von %s (%s)%s%s in %s bei %d %d %d",
                BuiltInRegistries.ENTITY_TYPE.getKey(tier.getType()),
                taeter == null ? "-" : taeter.getName().getString(),
                quelle.getMsgId(),
                tier.hasCustomName() ? ", Name „" + tier.getCustomName().getString() + "“" : "",
                besitzer == null ? "" : ", Besitzer " + besitzer,
                tier.level().dimension().identifier(), pos.getX(), pos.getY(), pos.getZ());
        LOG.info(zeile);
        try {
            Files.writeString(DATEI, "[" + LocalDateTime.now().format(ZEIT) + "] " + zeile + "\n", StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (IOException e) {
            LOG.warn("logs/tiere.log nicht schreibbar: {}", e.toString());
        }
    }

    private static String besitzer(LivingEntity tier) {
        if (!(tier instanceof OwnableEntity eigen) || eigen.getOwnerReference() == null) return null;
        LivingEntity owner = eigen.getOwner();
        return owner != null ? owner.getName().getString() : eigen.getOwnerReference().getUUID().toString();
    }
}
