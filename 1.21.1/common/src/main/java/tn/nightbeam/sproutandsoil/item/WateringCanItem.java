package tn.nightbeam.sproutandsoil.item;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import tn.nightbeam.sproutandsoil.farming.Watering;
import tn.nightbeam.sproutandsoil.registry.ModDataComponents;

import java.util.List;

/**
 * Hold use to water a 3x3 patch: farmland is fully moisturised, plants get bonus growth ticks and
 * fires are put out. Fill it by using it on water.
 */
public class WateringCanItem extends Item {
    public static final int CAPACITY = 120;
    private static final int TICKS_PER_SPRINKLE = 4;
    private static final int RANGE = 5;

    public WateringCanItem(Properties properties) {
        super(properties);
    }

    public static int getWater(ItemStack stack) {
        return stack.getOrDefault(ModDataComponents.WATER.get(), 0);
    }

    public static void setWater(ItemStack stack, int water) {
        stack.set(ModDataComponents.WATER.get(), Mth.clamp(water, 0, CAPACITY));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        BlockHitResult fluidHit = getPlayerPOVHitResult(level, player, ClipContext.Fluid.SOURCE_ONLY);
        if (fluidHit.getType() == HitResult.Type.BLOCK && level.getFluidState(fluidHit.getBlockPos()).is(FluidTags.WATER)) {
            if (getWater(stack) < CAPACITY) {
                setWater(stack, CAPACITY);
                level.playSound(player, player.blockPosition(), SoundEvents.BUCKET_FILL, SoundSource.PLAYERS, 1.0F, 1.2F);
                return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
            }
            return InteractionResultHolder.pass(stack);
        }
        if (getWater(stack) <= 0 && !player.getAbilities().instabuild) {
            return InteractionResultHolder.fail(stack);
        }
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void onUseTick(Level level, LivingEntity entity, ItemStack stack, int remainingUseDuration) {
        if (!(entity instanceof Player player)) {
            return;
        }
        HitResult hit = player.pick(RANGE, 0.0F, false);
        if (!(hit instanceof BlockHitResult blockHit) || hit.getType() != HitResult.Type.BLOCK) {
            return;
        }
        BlockPos center = blockHit.getBlockPos();
        if (level.isClientSide()) {
            for (int i = 0; i < 3; i++) {
                level.addParticle(ParticleTypes.SPLASH, center.getX() + level.random.nextDouble(), center.getY() + 1.05D,
                        center.getZ() + level.random.nextDouble(), 0.0D, 0.0D, 0.0D);
            }
            return;
        }
        if (remainingUseDuration % TICKS_PER_SPRINKLE != 0) {
            return;
        }
        boolean creative = player.getAbilities().instabuild;
        if (!creative && getWater(stack) <= 0) {
            player.stopUsingItem();
            return;
        }
        ServerLevel serverLevel = (ServerLevel) level;
        BlockState centerState = serverLevel.getBlockState(center);
        if (centerState.getBlock() instanceof FarmBlock) {
            center = center.above();
        }
        for (BlockPos pos : BlockPos.betweenClosed(center.offset(-1, -1, -1), center.offset(1, 1, 1))) {
            Watering.hydrate(serverLevel, pos);
            if (serverLevel.random.nextInt(3) == 0) {
                Watering.boostGrowth(serverLevel, pos, serverLevel.random);
            }
            if (serverLevel.getBlockState(pos).is(Blocks.FIRE)) {
                serverLevel.removeBlock(pos, false);
                serverLevel.playSound(null, pos, SoundEvents.FIRE_EXTINGUISH, SoundSource.BLOCKS, 0.5F, 1.5F);
            }
        }
        serverLevel.playSound(null, center, SoundEvents.WEATHER_RAIN, SoundSource.PLAYERS, 0.15F, 1.8F);
        if (!creative) {
            setWater(stack, getWater(stack) - 1);
        }
    }

    @Override
    public int getUseDuration(ItemStack stack, LivingEntity entity) {
        return 72000;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.BOW;
    }

    @Override
    public boolean isBarVisible(ItemStack stack) {
        return true;
    }

    @Override
    public int getBarWidth(ItemStack stack) {
        return Math.round(13.0F * getWater(stack) / CAPACITY);
    }

    @Override
    public int getBarColor(ItemStack stack) {
        return 0x3FA9F5;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.sprout_and_soil.water", getWater(stack), CAPACITY).withStyle(ChatFormatting.AQUA));
        ItemTooltips.description(this, tooltip);
    }
}
