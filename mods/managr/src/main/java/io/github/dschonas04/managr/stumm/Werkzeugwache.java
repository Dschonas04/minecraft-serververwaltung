// Autor: Dschonas04 (https://github.com/Dschonas04)

package io.github.dschonas04.managr.stumm;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Schreibt ins Log, wenn bei einem Spieler ein Werkzeug, eine Waffe oder Rüstung (alles mit Haltbarkeit) aus dem
 * Inventar verschwindet: mit Ort, Dimension, Rest-Haltbarkeit und vermutetem Grund.
 */
final class Werkzeugwache {
    private static final Logger LOG = LogManager.getLogger("Werkzeugwache");
    /** Je Spieler: Item-ID -> {Anzahl, kleinste Rest-Haltbarkeit}. */
    private static final Map<UUID, Map<String, int[]>> STAND = new HashMap<>();

    private Werkzeugwache() {}

    static void register() {
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTickCount() % 5 != 0) return;
            for (ServerPlayer player : server.getPlayerList().getPlayers()) pruefen(player);
        });
        ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> STAND.remove(handler.player.getUUID()));
    }

    private static void zaehlen(Map<String, int[]> jetzt, ItemStack stack) {
        if (stack.isEmpty() || !stack.isDamageableItem()) return;
        String id = BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
        int rest = stack.getMaxDamage() - stack.getDamageValue();
        int[] wert = jetzt.computeIfAbsent(id, k -> new int[] {0, Integer.MAX_VALUE});
        wert[0] += stack.getCount();
        wert[1] = Math.min(wert[1], rest);
    }

    private static void pruefen(ServerPlayer player) {
        Map<String, int[]> jetzt = new HashMap<>();
        Inventory inventory = player.getInventory();
        for (int i = 0; i < inventory.getContainerSize(); i++) zaehlen(jetzt, inventory.getItem(i));
        zaehlen(jetzt, player.containerMenu.getCarried());
        Map<String, int[]> vorher = STAND.put(player.getUUID(), jetzt);
        if (vorher == null || player.isDeadOrDying()) return;
        for (Map.Entry<String, int[]> eintrag : vorher.entrySet()) {
            int[] alt = eintrag.getValue();
            int[] neu = jetzt.get(eintrag.getKey());
            int weg = alt[0] - (neu == null ? 0 : neu[0]);
            if (weg <= 0) continue;
            String grund;
            if (alt[1] <= 8) grund = "kaputt gegangen (Rest-Haltbarkeit " + alt[1] + ")";
            else if (player.containerMenu != player.inventoryMenu) grund = "in Behälter gelegt? offen: " + player.containerMenu.getClass().getSimpleName();
            else if (!player.level().getEntitiesOfClass(ItemEntity.class, player.getBoundingBox().inflate(6),
                    e -> BuiltInRegistries.ITEM.getKey(e.getItem().getItem()).toString().equals(eintrag.getKey())).isEmpty()) grund = "fallen gelassen (liegt am Boden)";
            else grund = "UNBEKANNT (Rest-Haltbarkeit " + alt[1] + ")";
            LOG.info("{} verliert {}x {} in {} bei {} {} {}, in der Hand: {} - {}", player.getName().getString(), weg, eintrag.getKey(),
                    player.level().dimension().identifier(), player.getBlockX(), player.getBlockY(), player.getBlockZ(),
                    BuiltInRegistries.ITEM.getKey(player.getMainHandItem().getItem()), grund);
        }
    }
}
