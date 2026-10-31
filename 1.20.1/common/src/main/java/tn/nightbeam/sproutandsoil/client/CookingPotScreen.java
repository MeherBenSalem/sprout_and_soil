package tn.nightbeam.sproutandsoil.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import tn.nightbeam.sproutandsoil.SproutAndSoil;
import tn.nightbeam.sproutandsoil.menu.CookingPotMenu;

import java.util.List;

public class CookingPotScreen extends AbstractContainerScreen<CookingPotMenu> {
    public static final ResourceLocation TEXTURE = SproutAndSoil.id("textures/gui/container/cooking_pot.png");
    public static final int FLAME_X = 49;
    public static final int FLAME_Y = 56;
    public static final int ARROW_X = 89;
    public static final int ARROW_Y = 26;

    public CookingPotScreen(CookingPotMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
        imageWidth = 176;
        imageHeight = 166;
        inventoryLabelY = imageHeight - 94;
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        super.render(graphics, mouseX, mouseY, partialTick);
        renderTooltip(graphics, mouseX, mouseY);
        if (isHovering(FLAME_X, FLAME_Y, 14, 14, mouseX, mouseY)) {
            graphics.renderComponentTooltip(font, List.of(Component.translatable(menu.isHeated()
                    ? "container.sprout_and_soil.cooking_pot.heated" : "container.sprout_and_soil.cooking_pot.not_heated")),
                    mouseX, mouseY);
        }
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        int x = leftPos;
        int y = topPos;
        graphics.blit(TEXTURE, x, y, 0, 0, imageWidth, imageHeight);
        if (menu.isHeated()) {
            graphics.blit(TEXTURE, x + FLAME_X, y + FLAME_Y, 176, 0, 14, 14);
        }
        int progress = menu.progress(24);
        if (progress > 0) {
            graphics.blit(TEXTURE, x + ARROW_X, y + ARROW_Y, 176, 14, progress, 17);
        }
    }
}
