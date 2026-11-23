package tn.nightbeam.sproutandsoil.client;

import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.Inventory;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.menu.CookingPotMenu;

public class CookingPotScreen extends AbstractContainerScreen<CookingPotMenu> {
    public static final Identifier TEXTURE = SproutAndSoil.id("textures/gui/container/cooking_pot.png");
    public static final int FLAME_X = 49;
    public static final int FLAME_Y = 56;
    public static final int ARROW_X = 89;
    public static final int ARROW_Y = 26;

    public CookingPotScreen(CookingPotMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title, 176, 166);
        inventoryLabelY = imageHeight - 94;
    }

    @Override
    protected void extractTooltip(GuiGraphicsExtractor graphics, int mouseX, int mouseY) {
        super.extractTooltip(graphics, mouseX, mouseY);
        if (isHovering(FLAME_X, FLAME_Y, 14, 14, mouseX, mouseY)) {
            graphics.setTooltipForNextFrame(Component.translatable(menu.isHeated()
                    ? "container.sprout_and_soil.cooking_pot.heated" : "container.sprout_and_soil.cooking_pot.not_heated"),
                    mouseX, mouseY);
        }
    }

    @Override
    public void extractBackground(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float a) {
        super.extractBackground(graphics, mouseX, mouseY, a);
        int x = leftPos;
        int y = topPos;
        graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, x, y, 0.0F, 0.0F, imageWidth, imageHeight, 256, 256);
        if (menu.isHeated()) {
            graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, x + FLAME_X, y + FLAME_Y, 176.0F, 0.0F, 14, 14, 256, 256);
        }
        int progress = menu.progress(24);
        if (progress > 0) {
            graphics.blit(RenderPipelines.GUI_TEXTURED, TEXTURE, x + ARROW_X, y + ARROW_Y, 176.0F, 14.0F, progress, 17, 256, 256);
        }
    }
}
