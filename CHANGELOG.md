# Changelog

## 1.0.0 — The Harvest Update

A complete rewrite. Sprout & Soil is now an all-in-one farming and cooking mod.

### Added
- 40 crops (vegetables, grains, legumes, berries, herbs, spices, coffee, tea, cotton) with new art for every
  growth stage; corn grows two blocks tall.
- Right-click harvest with automatic replanting for all crops, including vanilla ones; perennial crops regrow.
- 12 fruit trees with blossoming, fruiting and ripening leaves; natural generation in matching biomes.
- Six wild garden types that spawn across the world and drop climate-appropriate seeds.
- Cooking pot (6 ingredients + serving container, heat source, hopper automation, XP).
- Cutting board with five knife tiers; mortar & pestle for crafting-grid grinding.
- 100+ ingredients, dishes, drinks and desserts; placeable pies, pizza and cakes.
- Well Fed, Cozy and Caffeinated effects.
- Watering can, sprinkler, four sickle tiers, fertilizer and scarecrow.
- 23 produce crates.
- Farmer and wandering trader trades, compostables, convention tags, JEI integration and an advancement tree.
- Code-generated, original pixel-art textures and 3D models for everything.

### Changed
- Targets Minecraft 1.21.1 on Fabric and NeoForge. Other Minecraft versions will be ported from this codebase.
- Crops use vanilla `CropBlock` ages (0-7) instead of one block per growth stage.

### Removed
- 0.x blocks and items (`tomato_plant_stage_*`, `garlic_plant_stage_*`, `letuce*`). Existing 0.x worlds lose them.
- The 1.20.1 (Forge/Fabric) and 26.2 workspaces; they will return as ports of 1.0.

## 0.3.0

- MultiLoader rewrite: Fabric + Forge on 1.20.1; Fabric + NeoForge on 1.21.1 and 26.2
- Apache License 2.0
- Consolidated crop stage blocks with shared growth logic and working random-tick growth
- Removed MCreator build dependency and unused jauml metadata

## 0.2.0

- Initial Forge 1.20.1 release (MCreator)
