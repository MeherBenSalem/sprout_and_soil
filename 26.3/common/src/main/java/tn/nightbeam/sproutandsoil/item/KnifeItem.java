package tn.nightbeam.sproutandsoil.item;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.ToolMaterial;

/**
 * Light, fast blade used on the cutting board; also a decent backup weapon. Built as a sword-like weapon of its
 * material (0.5 extra damage, attack speed -2.0), losing one durability per hit.
 */
public class KnifeItem extends Item {

    public KnifeItem(ToolMaterial material, Properties properties) {
        super(properties.sword(material, 0.5F, -2.0F));
    }
}
