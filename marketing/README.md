# Marketing

Listing copy and artwork for CurseForge and Modrinth. Nothing here ships in the mod JARs except the icon, which is
also every workspace's `logo.png`.

| Path | What it is |
|------|------------|
| `curseforge/description.md` | The project description (Markdown; also works on Modrinth). Images load from this repo's `main` branch. |
| `curseforge/summary.txt` | The one-line summary (215 characters, the limit is 250). |
| `images/banner.png` | 1800×600 header banner. |
| `images/icon.png` | 512×512 project icon; `render.cjs` also copies it to `<version>/common/src/main/resources/logo.png`. |
| `images/card-*.png` | 1600×900 feature cards used in the description and as gallery images. |
| `images/header-*.png`, `images/divider.png` | Transparent section headers and a divider for the description. |
| `images/screenshots/*.jpg` | Real in-game captures (Minecraft 1.21.1, Fabric, 1920×1080) used by the cards and the gallery. |
| `source/render.cjs` | Renders every PNG above from the screenshots, the mod's own textures and the bundled fonts. |
| `source/capture.py` | Builds the showcase world and takes every screenshot from the real game client. |
| `source/badge.png` | The 128×128 pixel-art badge drawn by `tools/assetgen` (hardware lane); the icon is built around it. |
| `source/fonts/` | Caprasimo and Figtree, both under the SIL Open Font License (licence files included). |

The look: a farmhouse recipe card. Cream paper with a faint red gingham check, walnut-brown ink, titles in the chunky
Caprasimo serif and copy in Figtree. Screenshots are taped-on photo prints, and every icon is one of the mod's own
textures drawn at a whole-pixel scale. Each feature has a colour: leaf green for farming, blossom pink for orchards,
tomato red for the kitchen, butter yellow for dishes, water blue for tools, meadow green for the wild. Headers are cream
labels with a stitched border, so they read on both CurseForge's dark page and Modrinth's light one.

## Regenerating the images

Needs Node.js and Playwright with Chromium:

```bash
NODE_PATH="$(npm root -g)" node marketing/source/render.cjs             # everything
NODE_PATH="$(npm root -g)" node marketing/source/render.cjs card-crops  # one asset
```

The cards read item and block textures straight from `1.21.1/common/src/generated/resources`, so they always show
the textures that ship. Rendering `icon` rewrites both workspaces' `logo.png`; commit them together.

## Adding a Minecraft version

The supported versions are listed in exactly two places:

1. `VERSIONS` at the top of `source/render.cjs`. Add one line, for example `{ minecraft: '1.21.4', loaders: ['Fabric',
   'NeoForge'] },`. The banner's loader pills and version line, the compatibility card and the icon copy are built from
   it. Then rerun the script for `banner`, `card-compat` and `icon`.
2. The table under **Downloads** in `curseforge/description.md` (and the version line near the top). Add one row.

A new release name or number goes in `RELEASE` in `render.cjs` and in the first lines of the description.

## Retaking the screenshots

`source/capture.py` takes every screenshot in `images/screenshots/` from the real game. It needs Xvfb, Mesa, xdotool
and ImageMagick, plus the Fabric production server that the QA script downloads:

```bash
(cd 1.21.1 && ./gradlew build)
tools/qa/prod_server.sh 1.21.1 fabric           # sets up build/qa/1.21.1-fabric (server, loader, Fabric API)
python3 marketing/source/capture.py             # all 17 scenes, about 15 minutes
python3 marketing/source/capture.py pots feast  # or a few
```

1. **World**: the production server generates a normal world with the seed at the top of the script, and
   `locate biome minecraft:plains` picks the site (the spawn is in plains for this seed).
2. **Stage**: a datapack flattens a 73×73 site and terraces the ground around it, then builds everything with
   commands: a field with all 40 crops in five bands between water channels, two sprinklers standing on the channels,
   two scarecrows, an orchard with all 12 fruit trees (the cherry, peach and plum trees in blossom), an open spruce
   kitchen with two cooking pots over campfires, four cutting boards with ingredients, a table of pies, pizza and cakes
   and a wall of crates, and a patch of wild gardens.
3. **Shoot**: the 1.21.1 Fabric development client opens the world in a 1920×1080 window on a virtual display. The
   script steps through the scenes with `/trigger sas_next` (typed with xdotool), hides the HUD with F1 where it is not
   wanted and takes each picture with ImageMagick `import`. For the cooking pot screen it right-clicks the pot, and for
   the watering can it holds the use button.

Every screenshot is a single unedited frame. Scenes with moving particles (pot steam, sprinkler spray, watering) take
a few frames 0.6 s apart and keep the one that differs most from the others, which is the one with the most particles.

| Screenshot | Scene |
|------------|-------|
| `farm.jpg` | The whole site from above: the field, the orchard behind it and the kitchen |
| `field.jpg`, `crops.jpg`, `corn.jpg` | The crop field from the path, a low view along the rows, the corn and berry band |
| `orchard.jpg`, `blossom.jpg`, `fruit.jpg` | The orchard, the blossoming cherry and plum trees, an orange tree in fruit |
| `kitchen.jpg`, `pots.jpg`, `boards.jpg` | The kitchen from outside, the two pots steaming over their campfires, the cutting boards |
| `feast.jpg`, `crates.jpg` | The table of pies, pizza and cakes; the crate wall |
| `gardens.jpg`, `scarecrow.jpg` | Wild gardens in the meadow; a scarecrow at the edge of the field |
| `sprinkler.jpg`, `watering.jpg` | A sprinkler spraying the field; first-person watering with the can |
| `pot_gui.jpg` | The cooking pot screen while it cooks tomato soup |
