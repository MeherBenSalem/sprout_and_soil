package tn.nightbeam.sproutandsoil.farming;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.LevelAccessor;

import java.util.Collections;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.WeakHashMap;

/** Loaded scarecrows per level, so farmland can cheaply ask whether it is protected from trampling. */
public final class ScarecrowTracker {
    public static final int RADIUS = 8;
    public static final int VERTICAL = 4;
    private static final Map<LevelAccessor, Set<BlockPos>> SCARECROWS = Collections.synchronizedMap(new WeakHashMap<>());

    private ScarecrowTracker() {
    }

    public static void add(LevelAccessor level, BlockPos pos) {
        SCARECROWS.computeIfAbsent(level, l -> Collections.synchronizedSet(new HashSet<>())).add(pos.immutable());
    }

    public static void remove(LevelAccessor level, BlockPos pos) {
        Set<BlockPos> set = SCARECROWS.get(level);
        if (set != null) {
            set.remove(pos);
        }
    }

    public static boolean protects(LevelAccessor level, BlockPos farmland) {
        Set<BlockPos> set = SCARECROWS.get(level);
        if (set == null || set.isEmpty()) {
            return false;
        }
        synchronized (set) {
            for (BlockPos pos : set) {
                if (Math.abs(pos.getX() - farmland.getX()) <= RADIUS && Math.abs(pos.getZ() - farmland.getZ()) <= RADIUS
                        && Math.abs(pos.getY() - farmland.getY()) <= VERTICAL) {
                    return true;
                }
            }
        }
        return false;
    }
}
