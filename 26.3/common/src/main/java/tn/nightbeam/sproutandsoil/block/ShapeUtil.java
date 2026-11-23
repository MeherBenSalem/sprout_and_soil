package tn.nightbeam.sproutandsoil.block;

import net.minecraft.core.Direction;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.EnumMap;
import java.util.Map;

/** Rotates shapes authored facing north to the other horizontal facings (matching blockstate y-rotation). */
public final class ShapeUtil {
    private ShapeUtil() {
    }

    public static Map<Direction, VoxelShape> horizontal(VoxelShape north) {
        Map<Direction, VoxelShape> out = new EnumMap<>(Direction.class);
        for (Direction facing : Direction.Plane.HORIZONTAL) {
            out.put(facing, rotate(north, facing));
        }
        return out;
    }

    public static VoxelShape rotate(VoxelShape north, Direction facing) {
        VoxelShape[] result = {Shapes.empty()};
        north.forAllBoxes((x1, y1, z1, x2, y2, z2) -> {
            VoxelShape box = switch (facing) {
                case SOUTH -> Shapes.box(1 - x2, y1, 1 - z2, 1 - x1, y2, 1 - z1);
                case EAST -> Shapes.box(1 - z2, y1, x1, 1 - z1, y2, x2);
                case WEST -> Shapes.box(z1, y1, 1 - x2, z2, y2, 1 - x1);
                default -> Shapes.box(x1, y1, z1, x2, y2, z2);
            };
            result[0] = Shapes.or(result[0], box);
        });
        return result[0].optimize();
    }
}
