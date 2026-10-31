// Renders the listing artwork in marketing/images/ from real in-game captures (marketing/images/screenshots/),
// the mod's own textures and the bundled OFL fonts. Usage (from the repository root):
//   NODE_PATH="$(npm root -g)" node marketing/source/render.cjs [name...]
// Requires the `playwright` package with a Chromium build available.
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

// The release and the supported Minecraft versions. Adding a version is one line here
// (plus one row in the download table of curseforge/description.md).
const RELEASE = { version: '1.0', name: 'The Harvest Update' };
const VERSIONS = [
  { minecraft: '1.20.1', loaders: ['Fabric', 'Forge'] },
  { minecraft: '1.21.1', loaders: ['Fabric', 'NeoForge'] },
];
const LOADERS = ['Fabric', 'Forge', 'NeoForge'].filter((loader) => VERSIONS.some((v) => v.loaders.includes(loader)));

// The palette: a farmhouse kitchen. Cream paper, dark walnut ink, and one colour per feature.
const C = {
  paper: '#fbf3e2', linen: '#f2e3c4', ink: '#3a2414', soft: '#6b4f37', tomato: '#d9432f', leaf: '#4f8a2b',
  sprout: '#8cc04b', butter: '#f1b52e', water: '#2f8fc4', blossom: '#d4598b', fruit: '#e8862a', wood: '#a8703f',
  meadow: '#3e8f6d',
};

const root = path.resolve(__dirname, '..', '..');
const out = path.join(root, 'marketing', 'images');
const shots = path.join(out, 'screenshots');
const fonts = path.join(__dirname, 'fonts');
const textures = path.join(root, '1.21.1', 'common', 'src', 'generated', 'resources', 'assets', 'sprout_and_soil', 'textures');
// The pixel-art badge drawn by tools/assetgen (hardware lane). The rendered icon becomes every workspace's logo.png.
const logoFile = path.join(__dirname, 'badge.png');
const url = (file) => 'file://' + file;
const shot = (name) => url(path.join(shots, name));
const tex = (name) => url(path.join(textures, name.includes('/') ? name : `item/${name}`) + '.png');

const css = `
@font-face { font-family: Display; src: url('${url(path.join(fonts, 'caprasimo-400.woff2'))}'); }
@font-face { font-family: Body; font-weight: 600; src: url('${url(path.join(fonts, 'figtree-600.woff2'))}'); }
@font-face { font-family: Body; font-weight: 700; src: url('${url(path.join(fonts, 'figtree-700.woff2'))}'); }
@font-face { font-family: Body; font-weight: 800; src: url('${url(path.join(fonts, 'figtree-800.woff2'))}'); }
@font-face { font-family: Body; font-weight: 900; src: url('${url(path.join(fonts, 'figtree-900.woff2'))}'); }
* { box-sizing: border-box; }
html, body { margin: 0; background: ${C.paper}; color: ${C.ink}; font-family: Body, sans-serif; font-weight: 700; }
.stage { position: relative; overflow: hidden;
         background: radial-gradient(ellipse at 12% 0%, rgba(255,255,255,.75) 0%, rgba(255,255,255,0) 55%),
                     radial-gradient(ellipse at 100% 100%, rgba(214,180,120,.35) 0%, rgba(214,180,120,0) 60%), ${C.paper}; }
.gingham { position: absolute; inset: 0; opacity: .045;
           background: repeating-linear-gradient(0deg, ${C.tomato} 0 16px, transparent 16px 32px),
                       repeating-linear-gradient(90deg, ${C.tomato} 0 16px, transparent 16px 32px); }
.grain { position: absolute; inset: 0; opacity: .05;
         background: repeating-linear-gradient(97deg, #000 0 1px, transparent 1px 7px); }
.display { font-family: Display, serif; font-weight: 400; letter-spacing: .005em; }
.kicker { font-weight: 900; letter-spacing: .2em; font-size: 21px; text-transform: uppercase; }
.vine { height: 10px; background:
          radial-gradient(ellipse 7px 4px at 50% 50%, var(--c) 98%, transparent 100%) 0 0 / 34px 10px repeat-x,
          linear-gradient(var(--c), var(--c)) 0 50% / 100% 2px no-repeat; opacity: .9; }
.pixel { image-rendering: pixelated; image-rendering: crisp-edges; display: block; }
.photo { position: relative; background: #fffdf8; padding: 14px 14px 16px; border-radius: 6px;
         box-shadow: 0 2px 0 rgba(58,36,20,.25), 0 22px 48px rgba(58,36,20,.32); }
.photo > .img { position: relative; overflow: hidden; border-radius: 3px; }
.photo > .img img { display: block; }
.tape { position: absolute; width: 150px; height: 34px; background: rgba(241,181,46,.55); top: -15px; left: 50%;
        transform: translateX(-50%) rotate(-3deg); box-shadow: 0 1px 2px rgba(0,0,0,.12); }
.label { position: absolute; display: inline-flex; align-items: center; gap: 9px; padding: 8px 16px 7px; border-radius: 999px;
         font-weight: 900; font-size: 17px; letter-spacing: .08em; text-transform: uppercase; color: #fff; background: ${C.ink};
         box-shadow: 0 6px 16px rgba(0,0,0,.3); }
ul.points { list-style: none; padding: 0; margin: 0; }
ul.points li { position: relative; padding-left: 38px; margin: 0 0 15px; font-size: 27px; line-height: 1.3; font-weight: 700; color: ${C.ink}; }
ul.points li::before { content: ''; position: absolute; left: 4px; top: 7px; width: 18px; height: 18px;
                       border-radius: 0 60% 0 60%; background: var(--accent, ${C.leaf}); transform: rotate(-8deg); }
b.hi { color: var(--accent, ${C.tomato}); font-weight: 900; }
.stats { display: flex; gap: 14px; }
.stats > div { flex: 1; padding: 12px 18px 10px; border-radius: 14px; background: #fffaf0; border: 3px dashed var(--accent, ${C.leaf});
               box-shadow: 0 10px 24px rgba(58,36,20,.14); }
.stats .t { font-weight: 900; font-size: 14px; letter-spacing: .16em; color: ${C.soft}; text-transform: uppercase; }
.stats .v { font-family: Display, serif; font-size: 34px; color: ${C.ink}; margin-top: 2px; white-space: nowrap; }
.pill { display: inline-block; border-radius: 999px; padding: 8px 22px 7px; margin-right: 10px; font-weight: 900; font-size: 21px;
        letter-spacing: .05em; color: #fff; background: ${C.leaf}; box-shadow: 0 4px 0 #2f5a17; }
.tiles { display: flex; flex-wrap: wrap; gap: 10px; }
.tile { width: 78px; height: 78px; border-radius: 14px; background: #fffaf0; border: 3px solid ${C.linen};
        display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 14px rgba(58,36,20,.12); }
`;

const page = (width, height, body, transparent = false) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}
body { width: ${width}px; height: ${height}px; } .stage { width: ${width}px; height: ${height}px; }
${transparent ? 'html, body, .stage { background: transparent; }' : ''}</style></head>
<body><div class="stage">${body}</div></body></html>`;

// An exact region (x, y, w, h in 1920x1080 pixels) of a capture, scaled to W pixels wide.
const region = (file, x, y, w, h, W) => `<div class="img" style="width:${W}px;height:${Math.round(W * h / w)}px">
    <img src="${shot(file)}" style="position:absolute;max-width:none;width:${W * 1920 / w}px;left:${-x * W / w}px;top:${-y * W / w}px"></div>`;
const photo = (inner, { tilt = 0, style = '', tape = true } = {}) =>
  `<div class="photo" style="transform:rotate(${tilt}deg);${style}">${tape ? '<div class="tape"></div>' : ''}${inner}</div>`;
const label = (text, color, pos) => `<span class="label" style="${pos};background:${color}">${text}</span>`;
const stats = (items) => `<div class="stats">${items.map(([t, v]) => `<div><div class="t">${t}</div><div class="v">${v}</div></div>`).join('')}</div>`;
const icon = (name, size = 48) => `<img class="pixel" src="${tex(name)}" style="width:${size}px;height:${size}px">`;
const tiles = (names, size = 48) => `<div class="tiles">${names.map((n) => `<div class="tile">${icon(n, size)}</div>`).join('')}</div>`;

// A feature card: copy on the left, artwork on the right.
const card = ({ kicker, title, points, art, color, width = 1600, height = 900, artWidth = 930 }) => page(width, height, `
  <div class="gingham"></div><div class="grain"></div>
  <div style="position:absolute;left:76px;top:0;bottom:0;width:${width - artWidth - 150}px;display:flex;flex-direction:column;justify-content:center;--accent:${color}">
    <div class="kicker" style="color:${color}">${kicker}</div>
    <div class="display" style="font-size:72px;line-height:1.02;margin:12px 0 20px;color:${C.ink}">${title}</div>
    <div class="vine" style="--c:${color};width:230px;margin-bottom:30px"></div>
    <ul class="points">${points.map((p) => `<li>${p.endsWith('>') ? p : p.replace(/ (\S+)$/, '&nbsp;$1')}</li>`).join('')}</ul>
  </div>
  <div style="position:absolute;right:62px;top:50%;transform:translateY(-50%);width:${artWidth}px;--accent:${color}">${art}</div>`);

const versionText = VERSIONS.map((v) => v.minecraft).join(' · ');

// Leaves of one tree through its four stages, as the block textures (tiled 2x2 like in the world).
const leafStages = (tree) => `<div style="display:flex;gap:14px">${['Leafy', 'Blossom', 'Unripe', 'Ripe'].map((stage, i) => `
  <div style="text-align:center"><div style="width:96px;height:96px;border-radius:12px;overflow:hidden;border:3px solid ${C.linen};
    background:url('${tex(`block/${tree}_leaves_${i}`)}') 0 0 / 48px 48px repeat;image-rendering:pixelated;box-shadow:0 6px 14px rgba(58,36,20,.15)"></div>
    <div style="font-weight:900;font-size:14px;letter-spacing:.12em;text-transform:uppercase;color:${C.soft};margin-top:6px">${stage}</div></div>`).join('')}</div>`;

// Growth stages of one crop, as block textures.
const cropStages = (crop) => `<div style="display:flex;gap:10px;align-items:flex-end">${[0, 1, 2, 3].map((i) => `
  <div style="width:84px;height:84px;border-radius:12px;background:linear-gradient(#fffaf0 70%, #6b4a2c 70%);border:3px solid ${C.linen};
     display:flex;align-items:flex-end;justify-content:center;overflow:hidden">${icon(`block/${crop}_stage${i}`, 72)}</div>`).join('')}</div>`;

const header = (title, color, left, right) => page(1400, 120, `
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">
    <div style="display:flex;align-items:center;gap:22px;padding:14px 40px 12px;border-radius:18px;background:${C.paper};
                box-shadow:0 0 0 4px ${color}, 0 0 0 7px ${C.paper}, 0 10px 24px rgba(0,0,0,.35);position:relative">
      <div style="position:absolute;inset:7px;border:2px dashed ${color};border-radius:12px;opacity:.55"></div>
      ${icon(left, 48)}
      <div class="display" style="font-size:52px;line-height:1;color:${C.ink};white-space:nowrap;padding-top:4px">${title}</div>
      ${icon(right, 48)}
    </div>
  </div>`, true);

const divider = () => page(1400, 48, `
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:14px">
    <div class="vine" style="--c:${C.sprout};width:470px"></div>
    ${['tomato', 'corn', 'orange', 'cherries', 'lettuce'].map((n) => icon(n, 40)).join('')}
    <div class="vine" style="--c:${C.sprout};width:470px"></div>
  </div>`, true);

// Every item the mod adds, grouped (the textures as they ship).
const ALL_ITEMS = fs.readdirSync(path.join(textures, 'item')).filter((f) => f.endsWith('.png')).map((f) => f.slice(0, -4)).sort();

const assets = {
  banner: () => page(1800, 600, `
    <img src="${shot('farm.jpg')}" style="position:absolute;right:-60px;top:-40px;width:1180px;
         -webkit-mask-image:linear-gradient(100deg,transparent 0%,#000 22%);mask-image:linear-gradient(100deg,transparent 0%,#000 22%)">
    <div class="gingham" style="-webkit-mask-image:linear-gradient(90deg,#000 0%,#000 44%,transparent 62%);mask-image:linear-gradient(90deg,#000 0%,#000 44%,transparent 62%)"></div>
    <div style="position:absolute;left:0;top:0;bottom:0;width:820px;background:linear-gradient(90deg,${C.paper} 0%,${C.paper} 78%,rgba(251,243,226,0) 100%)"></div>
    <div class="gingham" style="right:auto;width:820px;-webkit-mask-image:linear-gradient(90deg,#000 70%,transparent 100%);mask-image:linear-gradient(90deg,#000 70%,transparent 100%)"></div>
    <div style="position:absolute;left:70px;top:58px;width:900px">
      <div style="display:flex;align-items:center;gap:26px">
        <img class="pixel" src="${url(logoFile)}" style="width:170px;height:170px;filter:drop-shadow(0 10px 16px rgba(58,36,20,.35))">
        <div>
          <div class="kicker" style="color:${C.tomato}">${RELEASE.version} · ${RELEASE.name}</div>
          <div class="display" style="font-size:104px;line-height:1;margin-top:8px;white-space:nowrap">Sprout <span style="color:${C.tomato}">&amp;</span> Soil</div>
        </div>
      </div>
      <div class="vine" style="--c:${C.leaf};width:560px;margin:26px 0 22px"></div>
      <div style="font-size:31px;line-height:1.32;font-weight:800;color:${C.ink}">The all-in-one farming and cooking mod: 40 crops,<br>12 fruit trees, 150+ foods and a real kitchen.</div>
      <div style="margin-top:28px;display:flex;align-items:center">${LOADERS.map((l) => `<span class="pill">${l}</span>`).join('')}
        <span style="font-size:22px;color:${C.soft};margin-left:6px;font-weight:900">${versionText}</span></div>
    </div>`),

  icon: () => page(512, 512, `
    <div style="position:absolute;inset:0;border-radius:96px;overflow:hidden;background:${C.paper}">
      <img src="${shot('field.jpg')}" style="position:absolute;width:1500px;left:-560px;top:-300px;filter:blur(3px) saturate(1.15)">
      <div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(251,243,226,.0) 30%,rgba(58,36,20,.55) 85%)"></div>
      <img class="pixel" src="${url(logoFile)}" style="position:absolute;left:64px;top:64px;width:384px;height:384px;filter:drop-shadow(0 14px 22px rgba(0,0,0,.55))">
    </div>
    <div style="position:absolute;inset:0;border-radius:96px;border:12px solid ${C.paper};box-shadow:inset 0 0 0 4px ${C.tomato}"></div>`, true),

  'card-crops': () => card({
    kicker: 'Farming', title: 'Forty crops,<br>one field', color: C.leaf,
    points: ['Vegetables, grains, berries, herbs, coffee, tea and cotton', 'Four growth stages each, on vanilla crop rules: bone meal, bees, villagers',
      '<b class="hi">Right-click</b> a ripe crop to harvest and replant it (wheat too)', 'Berries, peppers, tomatoes and herbs regrow after picking', 'Corn grows two blocks tall'],
    art: `<div style="position:relative">${photo(region('field.jpg', 0, 60, 1920, 1020, 900), { tilt: -1.2 })}
      <div style="position:absolute;right:-30px;bottom:-78px">${photo(region('crops.jpg', 420, 180, 1080, 720, 360), { tilt: 2.5, tape: false })}</div></div>
      <div style="margin-top:40px;display:flex;align-items:center;gap:18px">${cropStages('tomato')}
        <div style="font-weight:900;font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:${C.soft};line-height:1.4">Tomato<br>stages 1–4</div></div>` }),

  'card-orchard': () => card({
    kicker: 'Orchards', title: 'Twelve<br>fruit trees', color: C.blossom,
    points: ['Apple, orange, lemon, lime, peach, pear, plum, cherry, mango, avocado, banana and olive',
      'Leaves blossom, set fruit and ripen; <b class="hi">right-click</b> to pick', 'Trees grow wild in matching biomes, or from saplings',
      'Fruit crates, pies, juices and smoothies'],
    art: `<div style="position:relative">${photo(region('orchard.jpg', 0, 40, 1920, 1040, 900), { tilt: 1.2 })}
      <div style="position:absolute;right:-30px;bottom:-84px">${photo(region('blossom.jpg', 240, 120, 1440, 900, 360), { tilt: 2.5, tape: false })}</div></div>
      <div style="margin-top:44px">${leafStages('orange')}</div>` }),

  'card-kitchen': () => card({
    kicker: 'The kitchen', title: 'The cooking<br>pot', color: C.tomato,
    points: ['Up to <b class="hi">six ingredients</b> and a bowl, plate, mug or bottle', 'Needs heat below: a lit campfire, fire, magma or lava',
      'Hoppers feed it from the top and sides and empty it from below', 'Pays out experience, like a furnace'],
    art: `<div style="position:relative">${photo(region('pots.jpg', 240, 100, 1440, 860, 900), { tilt: -1 })}
      <div style="position:absolute;right:-34px;bottom:-96px">${photo(region('pot_gui.jpg', 600, 230, 720, 560, 400), { tilt: 2, tape: false })}</div></div>
      <div style="margin-top:56px;width:480px">${stats([['Ingredients', '6'], ['Heat', 'fire or lava'], ['Recipes', '50']])}</div>` }),

  'card-cutting': () => card({
    kicker: 'Prep work', title: 'Boards, knives<br>and a mortar', color: C.wood,
    points: ['Put an ingredient on a <b class="hi">cutting board</b>, use a knife', 'Bacon, mince, chicken cuts, fish fillets, pumpkin and melon slices',
      'Five knife tiers, from flint to netherite; they take weapon enchantments', 'The <b class="hi">mortar &amp; pestle</b> grinds flour, cornmeal, pepper and oil in the crafting grid'],
    art: `${photo(region('boards.jpg', 160, 90, 1600, 900, 900), { tilt: 1 })}
      <div style="margin-top:34px">${tiles(['flint_knife', 'iron_knife', 'golden_knife', 'diamond_knife', 'netherite_knife', 'mortar_and_pestle', 'bacon', 'minced_beef', 'flour'], 54)}</div>` }),

  'card-feasts': () => card({
    kicker: 'Dishes', title: 'Soups, stews,<br>pies and more', color: C.butter,
    points: ['More than <b class="hi">150</b> foods and drinks', 'Pies, pizza and cakes you place and share slice by slice',
      'Hearty meals make you <b class="hi">Well Fed</b>, hot drinks <b class="hi">Cozy</b>, coffee <b class="hi">Caffeinated</b>',
      'Bowls, plates, mugs and bottles come back when you finish'],
    art: `${photo(region('feast.jpg', 160, 90, 1600, 900, 900), { tilt: -1 })}
      <div style="margin-top:34px">${tiles(['tomato_soup', 'beef_stew', 'ramen', 'paella', 'hamburger', 'salmon_maki', 'pancakes', 'hot_cocoa', 'coffee'], 54)}</div>` }),

  'card-tools': () => card({
    kicker: 'Tools of the trade', title: 'Water, guard<br>and reap', color: C.water,
    points: ['<b class="hi">Watering can</b>: hold to water a 3×3 patch and speed it up', '<b class="hi">Sprinkler</b>: next to water, it waters and grows a 9×9 field',
      '<b class="hi">Sickles</b> harvest and replant 3×3 or 5×5 at once', '<b class="hi">Scarecrow</b>: no trampling within 8 blocks', '<b class="hi">Fertilizer</b>: bone meal for a 5×5 patch'],
    art: `<div style="display:grid;grid-template-columns:1fr 1fr;gap:26px">
      <div style="position:relative">${photo(region('watering.jpg', 320, 120, 1280, 840, 440), { tilt: -1.5 })}${label('Watering can', C.water, 'left:26px;bottom:24px')}</div>
      <div style="position:relative">${photo(region('sprinkler.jpg', 320, 120, 1280, 840, 440), { tilt: 1.5 })}${label('Sprinkler', C.water, 'left:26px;bottom:24px')}</div></div>
      <div style="margin-top:30px">${tiles(['watering_can', 'iron_sickle', 'golden_sickle', 'diamond_sickle', 'netherite_sickle', 'fertilizer'], 54)}</div>` }),

  'card-wild': () => card({
    kicker: 'Into the wild', title: 'Wild gardens<br>and trades', color: C.meadow,
    points: ['Six kinds of <b class="hi">wild garden</b>, from meadow to marsh, drop the seeds that grow there',
      'Breaking grass can turn up seeds too', 'Farmers trade seeds, produce and meals; wandering traders bring saplings',
      'All produce composts, and farmer villagers plant the seeds'],
    art: `${photo(region('gardens.jpg', 160, 90, 1600, 900, 900), { tilt: 1 })}
      <div style="margin-top:34px">${tiles(['meadow_garden', 'woodland_garden', 'highland_garden', 'arid_garden', 'tropical_garden', 'marsh_garden'].map((g) => `block/${g}`), 54)}</div>` }),

  'card-items': () => page(1600, 900, `
    <div class="gingham"></div><div class="grain"></div>
    <div style="position:absolute;left:76px;top:70px;width:440px;--accent:${C.tomato}">
      <div class="kicker" style="color:${C.tomato}">Made for this mod</div>
      <div class="display" style="font-size:72px;line-height:1.02;margin:12px 0 20px">Every item,<br>hand-made</div>
      <div class="vine" style="--c:${C.tomato};width:230px;margin-bottom:30px"></div>
      <ul class="points"><li>${ALL_ITEMS.length} items, each with its own texture</li><li>Four growth stages for every crop, four leaf stages for every tree</li>
        <li>Real 3D models for the pot, board, scarecrow and sprinkler</li><li>Nothing borrowed from vanilla or other mods</li></ul>
    </div>
    <div style="position:absolute;right:62px;top:50px;width:960px;padding:26px;border-radius:22px;background:#fffaf0;border:4px solid ${C.linen};
                box-shadow:0 22px 48px rgba(58,36,20,.22);display:grid;grid-template-columns:repeat(15, 52px);gap:6px;justify-content:center">
      ${ALL_ITEMS.slice(0, 180).map((n) => `<div style="width:52px;height:52px;display:flex;align-items:center;justify-content:center">${icon(n, 48)}</div>`).join('')}
    </div>`),

  'card-compat': () => card({
    kicker: 'For servers and modpacks', title: 'Plays well<br>with others', color: C.soft,
    points: [`${LOADERS.join(', ')} on Minecraft ${VERSIONS.map((v) => v.minecraft).join(' and ')}`,
      'Vanilla crop blocks: bone meal, bees, villagers and farming add-ons just work',
      'Convention tags (<b class="hi">c:crops/*</b>, <b class="hi">c:seeds/*</b>, knives, foods; <b class="hi">forge:</b> on 1.20.1)',
      '<b class="hi">JEI</b> shows every cooking pot and cutting board recipe', 'Recipes, heat sources and drops are data: tune them with a datapack'],
    art: `<div style="position:relative">${photo(region('kitchen.jpg', 0, 40, 1920, 1040, 900), { tilt: -1 })}</div>
      <div style="margin-top:40px">${stats([['Loaders', LOADERS.length], ['Versions', VERSIONS.length], ['Crops', '40'], ['Items', ALL_ITEMS.length]])}</div>` }),
};

const HEADERS = {
  'header-inside': ['What’s Inside', C.leaf, 'tomato', 'cabbage'],
  'header-farming': ['Farming', C.leaf, 'lettuce', 'corn'],
  'header-orchards': ['Orchards', C.blossom, 'orange', 'cherries'],
  'header-kitchen': ['The Kitchen', C.tomato, 'tomato_soup', 'iron_knife'],
  'header-dishes': ['Dishes & Drinks', C.butter, 'apple_pie', 'coffee'],
  'header-tools': ['Tools of the Trade', C.water, 'watering_can', 'iron_sickle'],
  'header-wild': ['Into the Wild', C.meadow, 'strawberry', 'blueberries'],
  'header-items': ['Every Item', C.tomato, 'eggplant', 'mango'],
  'header-compatibility': ['Compatibility', C.soft, 'cooking_pot', 'cutting_board'],
  'header-downloads': ['Downloads', C.leaf, 'onion', 'garlic'],
  'header-faq': ['FAQ', C.butter, 'mint', 'basil'],
  'header-gallery': ['Gallery', C.blossom, 'peach', 'plum'],
};
for (const [name, [title, color, left, right]] of Object.entries(HEADERS)) {
  assets[name] = () => header(title, color, left, right);
}
assets.divider = divider;

(async () => {
  const wanted = process.argv.slice(2);
  const names = wanted.length ? wanted : Object.keys(assets);
  const browser = await chromium.launch();
  const context = await browser.newContext({ deviceScaleFactor: 1 });
  for (const name of names) {
    if (!assets[name]) {
      console.error('unknown asset', name);
      continue;
    }
    const html = assets[name]();
    const file = path.join(__dirname, `.render-${name}.html`);
    fs.writeFileSync(file, html);
    const p = await context.newPage();
    await p.goto(url(file));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(250);
    const { width, height } = await p.evaluate(() => ({ width: document.body.scrollWidth, height: document.body.scrollHeight }));
    await p.setViewportSize({ width, height });
    const transparent = name.startsWith('header') || name === 'divider' || name === 'icon';
    await p.screenshot({ path: path.join(out, `${name}.png`), omitBackground: transparent });
    if (name === 'icon') {
      for (const v of VERSIONS) {
        fs.copyFileSync(path.join(out, 'icon.png'), path.join(root, v.minecraft, 'common', 'src', 'main', 'resources', 'logo.png'));
      }
    }
    await p.close();
    fs.unlinkSync(file);
    console.log('rendered', name);
  }
  await browser.close();
})();
