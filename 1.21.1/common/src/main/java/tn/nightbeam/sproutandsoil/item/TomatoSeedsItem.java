package tn.nightbeam.sproutandsoil.item;

import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.context.UseOnContext;
import tn.nightbeam.sproutandsoil.crop.CropLogic;
import tn.nightbeam.sproutandsoil.crop.CropType;

public class TomatoSeedsItem extends Item {
    public TomatoSeedsItem() {
        super(new Item.Properties().stacksTo(64).rarity(Rarity.COMMON));
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        if (context.getLevel().isClientSide()) {
            return InteractionResult.SUCCESS;
        }
        if (CropLogic.tryPlant(context.getLevel(), context.getClickedPos(), CropType.TOMATO)) {
            if (context.getPlayer() != null && !context.getPlayer().getAbilities().instabuild) {
                context.getItemInHand().shrink(1);
            }
            return InteractionResult.CONSUME;
        }
        return InteractionResult.PASS;
    }
}
