package tn.nightbeam.sproutandsoil.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.UntintedParticleLeavesBlock;
import net.minecraft.world.level.block.sounds.AmbientLeavesBlockSoundPlayer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.phys.BlockHitResult;

/**
 * Leaves that flower and fruit: age 0 leafy, 1 blossoming, 2 unripe, 3 ripe.
 * Ripe leaves are picked with right-click and start a new cycle. Fruiting only happens in daylight.
 * Falling-leaf particles as on oak leaves, in a fixed green.
 */
public class FruitLeavesBlock extends UntintedParticleLeavesBlock {
    /** The falling-leaf particle colour: vanilla's default foliage green (the leaf textures carry their own colour). */
    private static final int PARTICLE_COLOR = 0xFF48B518;
    public static final IntegerProperty AGE = BlockStateProperties.AGE_3;
    public static final int MAX_AGE = 3;

    private final Identifier fruitId;

    public FruitLeavesBlock(Properties properties, Identifier fruitId) {
        super(0.01F, ColorParticleOption.create(ParticleTypes.TINTED_LEAVES, PARTICLE_COLOR), AmbientLeavesBlockSoundPlayer.noAmbientSound(),
                properties);
        this.fruitId = fruitId;
        registerDefaultState(defaultBlockState().setValue(AGE, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        super.createBlockStateDefinition(builder);
        builder.add(AGE);
    }

    @Override
    protected boolean isRandomlyTicking(BlockState state) {
        return super.isRandomlyTicking(state) || state.getValue(AGE) < MAX_AGE;
    }

    @Override
    protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (decaying(state)) {
            super.randomTick(state, level, pos, random);
            return;
        }
        int age = state.getValue(AGE);
        if (age < MAX_AGE && level.getRawBrightness(pos, 0) >= 9 && random.nextInt(age == 0 ? 6 : 4) == 0) {
            level.setBlock(pos, state.setValue(AGE, age + 1), Block.UPDATE_CLIENTS);
        }
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (state.getValue(AGE) != MAX_AGE) {
            return InteractionResult.PASS;
        }
        if (!level.isClientSide()) {
            int count = 1 + level.getRandom().nextInt(2);
            popResource(level, pos, new ItemStack(BuiltInRegistries.ITEM.getValue(fruitId), count));
            level.playSound(null, pos, SoundEvents.SWEET_BERRY_BUSH_PICK_BERRIES, SoundSource.BLOCKS, 1.0F,
                    0.8F + level.getRandom().nextFloat() * 0.4F);
            BlockState picked = state.setValue(AGE, 0);
            level.setBlock(pos, picked, Block.UPDATE_CLIENTS);
            level.gameEvent(GameEvent.BLOCK_CHANGE, pos, GameEvent.Context.of(player, picked));
        }
        return InteractionResult.SUCCESS;
    }
}
