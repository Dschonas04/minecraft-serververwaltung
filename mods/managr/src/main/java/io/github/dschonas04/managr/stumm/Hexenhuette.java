package io.github.dschonas04.managr.stumm;

import java.util.List;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.BuiltinStructures;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer;
import net.minecraft.world.level.levelgen.structure.structures.SwampHutPiece;

/**
 * /hexenhuette <Ecke> legt eine Hexenhütten-Struktur ohne Blöcke an: 7 breit (x), 7 hoch, 9 tief (z),
 * kleinste Ecke an der angegebenen Stelle. Darin erscheinen Hexen wie in einer echten Sumpfhütte,
 * so lässt sich eine Hexenfarm an beliebiger Stelle bauen. Die Struktur steht im Chunk und bleibt auch
 * ohne diese Mod erhalten. Nur für Operatoren.
 */
final class Hexenhuette {
    private Hexenhuette() {}

    static void register() {
        CommandRegistrationCallback.EVENT.register((dispatcher, registry, environment) ->
                dispatcher.register(Commands.literal("hexenhuette").requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .then(Commands.argument("ecke", BlockPosArgument.blockPos())
                                .executes(c -> anlegen(c.getSource(), BlockPosArgument.getLoadedBlockPos(c, "ecke"))))));
    }

    private static int anlegen(CommandSourceStack quelle, BlockPos ecke) {
        ServerLevel level = quelle.getLevel();
        Structure huette = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).getValueOrThrow(BuiltinStructures.SWAMP_HUT);
        // Die Ausrichtung wählt das Teil selbst; gewürfelt wird, bis die lange Seite entlang z liegt.
        SwampHutPiece teil;
        do {
            teil = new SwampHutPiece(level.getRandom(), 0, 0);
        } while (teil.getBoundingBox().getXSpan() != 7);
        BoundingBox bb = teil.getBoundingBox();
        teil.move(ecke.getX() - bb.minX(), ecke.getY() - bb.minY(), ecke.getZ() - bb.minZ());
        BoundingBox box = teil.getBoundingBox();

        ChunkPos start = new ChunkPos(ecke);
        level.getChunk(start.x, start.z).setStartForStructure(huette, new StructureStart(huette, start, 0, new PiecesContainer(List.of(teil))));
        for (int cx = box.minX() >> 4; cx <= box.maxX() >> 4; cx++) {
            for (int cz = box.minZ() >> 4; cz <= box.maxZ() >> 4; cz++) {
                LevelChunk chunk = level.getChunk(cx, cz);
                chunk.addReferenceForStructure(huette, start.toLong());
                chunk.markUnsaved();
            }
        }
        quelle.sendSuccess(() -> Component.literal("Hexenhütte angelegt: " + box.minX() + " " + box.minY() + " " + box.minZ()
                + " bis " + box.maxX() + " " + box.maxY() + " " + box.maxZ()), true);
        return 1;
    }
}
