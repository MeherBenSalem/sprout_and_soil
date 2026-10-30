"""Hardware lane: 3D workstation block models + their textures.

Each ``build_<id>()`` returns ``(model_json, {texture_rel_path: Sprite})`` where texture paths
are relative to ``textures/block/``. Models face north (front on -z), keep 1 texel per model
unit and carry a full ``display`` block fitted with :func:`render3d.fit_display`.
"""
from __future__ import annotations

from .core import CLEAR, Color, Sprite, hexc, shade
from .hardware_mdl import Paint, all_faces, box, display, rot_y, tex_ref
from .render3d import fit_display

# --------------------------------------------------------------------------- palettes

IRON = [hexc(c) for c in ("#17181d", "#23252c", "#2f323a", "#3c3f48", "#4a4e57", "#5b5f69", "#6f747e", "#8a8f98")]
COPPER = [hexc(c) for c in ("#4a1d10", "#6e2e18", "#924020", "#b45528", "#c8643a", "#dc7e4e", "#ec9c6a", "#f8c49a")]
PATINA = [hexc(c) for c in ("#1f5a50", "#2f7a6a", "#46a08a", "#68c0a8")]
WOOD = [hexc(c) for c in ("#3a2412", "#553519", "#6e4622", "#8a5a2a", "#a06c36", "#b8844a", "#cc9a5e", "#ddb27a")]
STRAW = [hexc(c) for c in ("#5e4614", "#80621e", "#a2822c", "#c0a03c", "#d8b85a", "#e8cc72", "#f4e09a")]
PUMPKIN = [hexc(c) for c in ("#5a2406", "#8a3c08", "#b4580c", "#d06e12", "#e8901a", "#f4a832", "#fcc45a")]
BURLAP = [hexc(c) for c in ("#3e2c18", "#5a4428", "#745a38", "#8e7248", "#a88a5a", "#bea270", "#d2b886")]
POST = [hexc(c) for c in ("#2c1c0e", "#402a16", "#563a1e", "#6a4a2a", "#7e5a34", "#946c40")]


def _seq(n: int, c: Color) -> list[Color]:
    return [c] * n


# =========================================================================== cooking pot
#
#   foot   [3,0,3]-[13,1,13]        cast iron
#   body   [2.5,1,2.5]-[13.5,7,13.5]  cast iron, 11 wide
#   band   hollow copper rim 12x2x12 at y 7..9 (four walls) with stew 1px below its top
#   lid    10x10 iron plate slid 1.5px toward south-west (ajar: a gap shows at the north-east),
#          raised boss + copper knob
#   handles iron loops on west/east at rim height

def build_cooking_pot():
    P, R, L, B = "pot", "rim", "lid", "broth"
    els = []
    # --- pot body
    els.append(box([3, 0, 3], [13, 1, 13], {**all_faces(P, (0, 5)), "down": (P, [0, 10, 10, 16])}, name="foot"))
    els.append(box([2.5, 1, 2.5], [13.5, 7, 13.5], {**all_faces(P, (0, 0)), "down": (P, [0, 10, 11, 16])},
                   name="body"))
    els.append(box([2, 2, 2], [14, 6, 14], {**all_faces(P, (0, 6)), "up": (P, [13, 2, 16, 5]),
                                            "down": (P, [13, 2, 16, 5])}, name="belly"))
    # --- copper rim band (hollow), top ring painted as one 12x12 picture at rim.png (0,4)
    els.append(box([2, 7, 2], [14, 9, 3], {"north": (R, (0, 0)), "south": (R, (1, 2)), "west": (R, (0, 0)),
                                             "east": (R, (0, 0)), "up": (R, (0, 4)), "down": (R, (0, 4))},
                   name="rim north"))
    els.append(box([2, 7, 13], [14, 9, 14], {"south": (R, (0, 0)), "north": (R, (1, 2)), "west": (R, (0, 0)),
                                              "east": (R, (0, 0)), "up": (R, (0, 15)), "down": (R, (0, 15))},
                   name="rim south"))
    els.append(box([2, 7, 3], [3, 9, 13], {"west": (R, (1, 0)), "east": (R, (1, 2)), "up": (R, (0, 5)),
                                            "down": (R, (0, 5))}, name="rim west"))
    els.append(box([13, 7, 3], [14, 9, 13], {"east": (R, (1, 0)), "west": (R, (1, 2)), "up": (R, (11, 5)),
                                              "down": (R, (11, 5))}, name="rim east"))
    els.append(box([3, 7, 3], [13, 8, 13], {"up": (B, (3, 3))}, name="stew"))
    # --- handles (iron loops)
    for side, gx, ax in (("west", 0, 1), ("east", 15, 14)):
        els.append(box([gx, 7.5, 6], [gx + 1, 8.5, 10], {**all_faces(P, (11, 0)), "up": (P, (11, 1)),
                                                          "down": (P, (11, 1))}, name=f"{side} handle grip"))
        for z in (6, 9):
            fc = {"north": (P, (11, 2)), "south": (P, (11, 2)), "up": (P, (12, 2)), "down": (P, (12, 2))}
            els.append(box([ax, 7.5, z], [ax + 1, 8.5, z + 1], fc, name=f"{side} handle arm"))
    # --- lid (slid 1.5px toward the south-west)
    lx, lz = 1.5, 4.5
    els.append(box([lx, 9, lz], [lx + 10, 10, lz + 10], {**all_faces(L, (0, 10)), "up": (L, (0, 0)),
                                                          "down": (L, (0, 0))}, name="lid"))
    els.append(box([lx + 2, 10, lz + 2], [lx + 8, 11, lz + 8], {**all_faces(L, (10, 6)), "up": (L, (10, 0))},
                   name="lid boss"))
    els.append(box([lx + 4, 11, lz + 4], [lx + 6, 12.5, lz + 6], {**all_faces(R, (12, 2)), "up": (R, (12, 0))},
                   name="lid knob"))

    textures = {
        "particle": tex_ref("cooking_pot/pot"),
        "pot": tex_ref("cooking_pot/pot"),
        "rim": tex_ref("cooking_pot/rim"),
        "lid": tex_ref("cooking_pot/lid"),
        "broth": tex_ref("cooking_pot/broth"),
    }
    model = {"parent": "minecraft:block/block", "textures": textures, "elements": els}
    model["display"] = display(
        gui=fit_display(els, [30, 225, 0], extent=15.0, max_scale=0.8),
        ground={"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.3, 0.3, 0.3]},
        fixed={"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.6, 0.6, 0.6]},
        head={"rotation": [0, 0, 0], "translation": [0, 0.75, 0], "scale": [1, 1, 1]},
        thirdperson_righthand={"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.4, 0.4, 0.4]},
        thirdperson_lefthand={"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.4, 0.4, 0.4]},
        firstperson_righthand={"rotation": [0, 45, 0], "translation": [0, 1, 0], "scale": [0.45, 0.45, 0.45]},
        firstperson_lefthand={"rotation": [0, 225, 0], "translation": [0, 1, 0], "scale": [0.45, 0.45, 0.45]},
    )
    return model, _cooking_pot_textures()


def _cooking_pot_textures() -> dict[str, Sprite]:
    I, C = IRON, COPPER
    # ---------------------------------------------------------------- pot.png
    p = Paint(seed="pot")
    p.rect(0, 0, 16, 16, I[3])

    def body(x, y):
        # cylinder-ish shading: lit band at x 2..3, falling off to the right; dark under the rim
        light = {0: 1, 1: 2, 2: 3, 3: 3, 4: 2, 5: 2, 6: 1, 7: 1, 8: 0, 9: 0, 10: -1}[x]
        row = {0: -2, 1: 0, 2: 0, 3: 0, 4: -1, 5: -2}[y]
        return I[max(0, min(7, 3 + light + row))]

    p.region(0, 0, 11, 6, body)
    # cast-iron pitting / casting seam
    for (x, y) in ((1, 2), (5, 3), (8, 1), (9, 4), (3, 4), (6, 1)):
        p.px(x, y, shade(p.s.get(x, y), -0.05))
    p.px(2, 1, I[7])
    p.px(3, 1, I[6])
    p.px(2, 2, I[6])
    # bottom (10x10 foot / 11x11 body underside)
    p.noise(0, 10, 12, 6, I, 2, 0.4)
    # belly band (12x4 sides at (0,6)); the 12x12 ledge faces reuse the same rows
    def belly(x, y):
        light = {0: 1, 1: 2, 2: 3, 3: 3, 4: 2, 5: 2, 6: 1, 7: 1, 8: 0, 9: 0, 10: -1, 11: -1}[x]
        row = {0: 1, 1: 0, 2: 0, 3: -1}.get(y, -1)
        return I[max(0, min(7, 3 + light + row))]

    p.region(0, 6, 12, 4, belly)
    for (x, y) in ((4, 7), (9, 8), (1, 8)):
        p.px(x, y, shade(p.s.get(x, y), -0.05))
    # handle iron (grip long faces 4x1 at (11,0), top (11,1), arms (11,2),(12,2))
    p.rect(11, 0, 4, 1, I[6])
    p.px(11, 0, I[7])
    p.px(14, 0, I[5])
    p.rect(11, 1, 4, 1, I[7])
    p.px(14, 1, I[6])
    p.px(11, 2, I[5])
    p.px(12, 2, I[6])
    p.rect(13, 2, 3, 4, I[3])
    p.rect(11, 3, 2, 3, I[3])

    # ---------------------------------------------------------------- rim.png (copper)
    r = Paint(seed="rim")
    r.rect(0, 0, 16, 16, C[4])

    def band(x, y):
        if y == 0:
            return C[6] if x % 4 != 3 else C[5]
        return C[4] if x % 4 != 3 else C[3]

    r.region(0, 0, 12, 2, band)
    for x in (2, 6, 10):            # rivets
        r.px(x, 1, C[7])
    r.px(0, 0, C[5])
    r.px(11, 1, C[3])
    # inner face of the band (in shadow)
    r.region(0, 2, 12, 2, lambda x, y: C[2] if y == 0 else C[1])
    # top ring 12x12 at (0,4): 1px copper rim, top-left lit, bottom-right darker
    def ring(x, y):
        if x in (0, 11) or y in (0, 11):
            if y == 0 or x == 0:
                return C[7] if (x + y) % 5 else C[6]
            return C[5]
        return C[0]

    r.region(0, 4, 12, 12, ring)
    # knob: top (12,0) 2x2, side (12,2) 2x1.5
    r.rect(12, 0, 2, 2, C[6])
    r.px(12, 0, C[7])
    r.rect(12, 2, 2, 2, C[4])
    r.px(12, 2, C[5])
    r.px(13, 3, C[3])

    # ---------------------------------------------------------------- lid.png (iron)
    lid = Paint(seed="lid")
    lid.rect(0, 0, 16, 16, I[4])

    def plate(x, y):
        edge = x in (0, 9) or y in (0, 9)
        if edge:
            return I[6] if (x == 0 or y == 0) else I[3]
        inner = x in (1, 8) or y in (1, 8)
        if inner:
            return I[4] if (x == 1 or y == 1) else I[4]
        return I[5] if (x, y) in ((2, 2), (3, 2), (2, 3)) else I[4]

    lid.region(0, 0, 10, 10, plate)
    lid.region(0, 10, 10, 1, lambda x, y: I[4] if x < 7 else I[3])
    lid.px(0, 10, I[5])

    def boss(x, y):
        if x == 0 or y == 0:
            return I[7] if x + y < 4 else I[6]
        if x == 5 or y == 5:
            return I[4]
        return I[5]

    lid.region(10, 0, 6, 6, boss)
    lid.region(10, 6, 6, 1, lambda x, y: I[5] if x < 4 else I[4])

    # ---------------------------------------------------------------- broth.png (stew surface)
    b = Paint(seed="broth")
    stew = [hexc(c) for c in ("#5a2a10", "#7a3a16", "#9a4c1c", "#b45e24", "#c8743a", "#e0a060")]
    b.noise(0, 0, 16, 16, stew, 2, 0.5)
    for (x, y, c) in ((5, 5, "#e88a2a"), (9, 7, "#e88a2a"), (11, 4, "#5a9a2a"), (6, 10, "#5a9a2a"),
                      (10, 11, "#f0d070"), (4, 8, "#f0d070"), (12, 9, "#e88a2a"), (7, 4, stew[5]),
                      (8, 4, stew[5]), (3, 11, stew[5])):
        b.px(x, y, c)
    # inner shadow near the rim
    for i in range(3, 13):
        b.px(i, 3, stew[0])
        b.px(3, i, stew[0])
    return {"cooking_pot/pot": p.s, "cooking_pot/rim": r.s, "cooking_pot/lid": lid.s,
            "cooking_pot/broth": b.s}


# =========================================================================== cutting board
#
# A 14x10 end-to-end board, 1px thick, rounded ends and a handle with a hanging hole
# (transparent texel -> cutout). The top is one picture mapped by absolute x/z position, so
# all four elements line up seamlessly; the item rendered on top sits at y~1.5.

BOARD_PARTS = [  # (from, to, name)
    ([1, 0, 4], [2, 1, 12], "west round"),
    ([2, 0, 3], [11, 1, 13], "board"),
    ([11, 0, 4], [12, 1, 12], "east round"),
    ([12, 0, 6], [15, 1, 10], "handle"),
]


def build_cutting_board():
    T = "board"
    els = []
    for frm, to, name in BOARD_PARTS:
        x1, _, z1 = frm
        x2, _, z2 = to
        faces = {
            "up": (T, [x1, z1, x2, z2]),
            "down": (T, [x1, z2, x2, z1]),           # same picture seen from below (hole lines up)
            "north": (T, [x1, 0, x2, 1]),
            "south": (T, [x1, 1, x2, 2]),
            "west": (T, [z1, 15, z2, 16]),
            "east": (T, [z1, 15, z2, 16]),
        }
        els.append(box(frm, to, faces, name=name))
    textures = {"particle": tex_ref("cutting_board/board"), "board": tex_ref("cutting_board/board")}
    model = {"parent": "minecraft:block/block", "render_type": "minecraft:cutout", "textures": textures,
             "elements": els}
    model["display"] = display(
        gui=fit_display(els, [55, 20, 0], extent=15.5, max_scale=1.0),
        ground={"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.35, 0.35, 0.35]},
        fixed={"rotation": [-90, 0, 0], "translation": [0, 0, -5.6], "scale": [0.75, 0.75, 0.75]},
        head={"rotation": [0, 0, 0], "translation": [0, 16, 0], "scale": [1, 1, 1]},
        thirdperson_righthand={"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
        thirdperson_lefthand={"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
        firstperson_righthand={"rotation": [10, 45, 0], "translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
        firstperson_lefthand={"rotation": [10, 225, 0], "translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
    )
    return model, {"cutting_board/board": _board_texture()}


def _board_texture() -> Sprite:
    W = WOOD
    p = Paint(seed="board")
    # footprint mask in top view (x 1..14, z 3..12)
    def inside(x, z):
        if 2 <= x <= 10 and 3 <= z <= 12:
            return True
        if x in (1, 11) and 4 <= z <= 11:
            return True
        return 12 <= x <= 14 and 6 <= z <= 9

    def edge_kind(x, z):
        """0 interior, 1 top-left rim (lit), 2 bottom-right rim (shade)."""
        n = [(x, z - 1), (x - 1, z)]
        sdir = [(x, z + 1), (x + 1, z)]
        if any(not inside(*q) for q in n):
            return 1
        if any(not inside(*q) for q in sdir):
            return 2
        return 0

    # long grain along x: alternating row tones with a few longer dark streaks
    row_tone = {3: 6, 4: 5, 5: 5, 6: 6, 7: 5, 8: 5, 9: 6, 10: 5, 11: 5, 12: 6}
    streaks = {(4, 5), (5, 5), (6, 5), (7, 8), (8, 8), (9, 8), (10, 8), (2, 10), (3, 10), (12, 7), (13, 9)}
    for z in range(16):
        for x in range(16):
            if not inside(x, z):
                continue
            k = edge_kind(x, z)
            if k == 1:
                c = W[7] if (x + z) % 4 else W[6]
            elif k == 2:
                c = W[3]
            else:
                c = W[4] if (x, z) in streaks else W[row_tone.get(z, 5)]
            p.px(x, z, c)
    # juice groove one pixel inside the rim of the main board
    for x in range(3, 11):
        p.px(x, 4, W[3] if x > 3 else W[4])
        p.px(x, 11, W[4])
    for z in range(5, 11):
        p.px(3, z, W[3])
        p.px(10, z, W[4])
    p.px(3, 4, W[3])
    p.px(10, 11, W[4])
    # knife score marks (pale nicks)
    for (x, z) in ((5, 7), (6, 8), (8, 6), (9, 7)):
        p.px(x, z, W[7])
    # texels outside the footprint are never mapped: fill them with plain wood for particles
    for z in range(2, 15):
        for x in range(16):
            if not inside(x, z):
                p.px(x, z, W[5] if (x + z) % 5 else W[4])
    # handle hole (see-through)
    p.px(13, 7, CLEAR)
    p.px(13, 8, CLEAR)
    p.px(12, 7, W[3])
    p.px(12, 8, W[4])
    p.px(14, 7, W[6])
    # side strips: rows 0 (north/front edge, lit) / 1 (south edge), row 15 ends
    for x in range(16):
        p.px(x, 0, W[5] if x % 5 else W[4])
        p.px(x, 1, W[4] if x % 4 else W[3])
        p.px(x, 15, W[4] if x % 3 else W[3])
    return p.s


# =========================================================================== scarecrow
#
# post, burlap shirt (front patch, rope belt) with straw-stuffed sleeves and collar, carved
# pumpkin head (face on north) and a straw hat; reaches y=30 (taller than one block).

def build_scarecrow():
    S, H, W, ST = "shirt", "pumpkin", "post", "straw"
    els = []
    els.append(box([7, 0, 7], [9, 10, 9], {**all_faces(W, (0, 0)), "down": (W, (6, 0))}, name="post"))
    # straw hanging under the shirt
    els.append(box([4.5, 8.5, 6.5], [11.5, 10, 9.5], {**all_faces(ST, (0, 13)), "down": (ST, (0, 13))},
                   name="straw hem"))
    els.append(box([4, 10, 6], [12, 18, 10], {"north": (S, (0, 0)), "south": (S, (8, 0)), "west": (S, (0, 8)),
                                              "east": (S, (4, 8)), "up": (S, (8, 8)), "down": (S, (8, 12))},
                   name="shirt"))
    for side, x1, x2, tx1, tx2 in (("west", 1, 4, 0, 1), ("east", 12, 15, 15, 16)):
        sl = {"north": (S, (0, 8)), "south": (S, (0, 8)), "up": (S, (4, 8)), "down": (S, (4, 12))}
        sl["west" if side == "west" else "east"] = (S, (1, 12))
        els.append(box([x1, 14.5, 6.5], [x2, 17.5, 9.5], sl, name=f"{side} sleeve"))
        tf = {**all_faces(ST, (12, 0)), "up": (ST, (12, 6)), "down": (ST, (12, 6))}
        els.append(box([tx1, 15, 7], [tx2, 17, 9], tf, name=f"{side} straw cuff"))
    els.append(box([5.5, 18, 6.5], [10.5, 19, 9.5], {**all_faces(ST, (0, 13)), "up": (ST, (1, 13))},
                   name="straw collar"))
    els.append(box([4, 19, 4], [12, 27, 12], {"north": (H, (0, 0)), "south": (H, (8, 0)), "west": (H, (8, 0)),
                                              "east": (H, (8, 0)), "up": (H, (0, 8)), "down": (H, (8, 8))},
                   name="pumpkin head"))
    els.append(box([2, 26.5, 2], [14, 27.5, 14], {**all_faces(ST, (0, 12)), "up": (ST, (0, 0)),
                                                   "down": (ST, [0, 12, 12, 0])}, name="hat brim"))
    els.append(box([5, 27.5, 5], [11, 30, 11], {**all_faces(ST, (0, 13)), "up": (ST, (3, 3))}, name="hat crown"))
    els.append(box([4.9, 27.5, 4.9], [11.1, 28.5, 11.1], {**all_faces(ST, (7, 14))}, name="hat band"))

    textures = {"particle": tex_ref("scarecrow/straw"), "shirt": tex_ref("scarecrow/shirt"),
                "pumpkin": tex_ref("scarecrow/pumpkin"), "post": tex_ref("scarecrow/post"),
                "straw": tex_ref("scarecrow/straw")}
    model = {"parent": "minecraft:block/block", "textures": textures, "elements": els}
    model["display"] = display(
        gui=fit_display(els, [25, 205, 0], extent=15.5, max_scale=1.0),
        ground={"rotation": [0, 0, 0], "translation": [0, 1, 0], "scale": [0.2, 0.2, 0.2]},
        fixed={"rotation": [0, 0, 0], "translation": [0, -3.5, 0], "scale": [0.45, 0.45, 0.45]},
        head={"rotation": [0, 0, 0], "translation": [0, -12, 0], "scale": [1, 1, 1]},
        thirdperson_righthand={"rotation": [75, 45, 0], "translation": [0, 1, 0], "scale": [0.3, 0.3, 0.3]},
        thirdperson_lefthand={"rotation": [75, 45, 0], "translation": [0, 1, 0], "scale": [0.3, 0.3, 0.3]},
        firstperson_righthand={"rotation": [0, 45, 0], "translation": [0, -2, 0], "scale": [0.3, 0.3, 0.3]},
        firstperson_lefthand={"rotation": [0, 225, 0], "translation": [0, -2, 0], "scale": [0.3, 0.3, 0.3]},
    )
    return model, _scarecrow_textures()


def _scarecrow_textures() -> dict[str, Sprite]:
    B, ST, PK, PO = BURLAP, STRAW, PUMPKIN, POST
    # ---------------------------------------------------------------- shirt.png
    s = Paint(seed="shirt")
    s.noise(0, 0, 16, 16, B, 4, 0.45)
    # weave: darker every other texel diagonally
    for y in range(16):
        for x in range(16):
            if (x + 2 * y) % 4 == 0:
                s.px(x, y, shade(s.s.get(x, y), -0.04))
    # front (0,0) 8x8: lit left, patch, buttons, rope belt at y=6
    for y in range(8):
        s.px(7, y, B[3])
        s.px(0, y, B[5])
    s.region(1, 1, 3, 3, lambda x, y: hexc("#b03a2e") if (x + y) % 2 == 0 else hexc("#7a2a3e"))  # plaid patch
    for (x, y) in ((1, 1), (3, 1), (1, 3), (3, 3)):
        s.px(x, y, "#d8c8a0")
    s.px(5, 2, "#3a2a1a")
    s.px(5, 4, "#3a2a1a")
    # back (8,0) 8x8
    s.region(11, 2, 3, 2, lambda x, y: hexc("#4a6a8e") if x != 1 else hexc("#3a5070"))
    # sides (0,8)/(4,8) 4x8
    # rope belt across front/back/sides at row 6 (front/back) and row 14 (sides)
    rope = [hexc("#c8b078"), hexc("#9a8250")]
    for x in range(16):
        s.px(x, 6, rope[x % 2])
    for x in range(8):
        s.px(x, 14, rope[x % 2])
    s.px(2, 7, rope[0])      # knot tail
    s.px(3, 7, rope[1])
    # shoulders top (8,8) 8x4 lit, bottom (8,12) darker
    s.region(8, 8, 8, 4, lambda x, y: B[5] if (x + y) % 3 else B[4])
    s.region(8, 12, 8, 4, lambda x, y: B[2] if (x + y) % 3 else B[3])
    # ---------------------------------------------------------------- pumpkin.png
    p = Paint(seed="pumpkin")

    def rib(x, y):  # vertical ribs: groove every 3-4 px, lit left
        groove = x in (0, 3, 7) if x < 8 else (x - 8) in (0, 4, 7)
        base = 3 if groove else 4 + (1 if (x % 8) in (1, 4) else 0)
        if y == 0:
            base += 1
        if y == 7:
            base -= 1
        return PK[max(0, min(6, base))]

    p.region(0, 0, 16, 8, rib)
    face_dark, face_glow = hexc("#3a1404"), hexc("#f8d050")
    # carved face (front 8x8): triangle eyes, toothy grin
    for (x, y) in ((1, 2), (2, 2), (2, 1), (5, 1), (5, 2), (6, 2)):
        p.px(x, y, face_dark)
    p.px(1, 2, hexc("#7a3008"))
    p.px(6, 2, hexc("#7a3008"))
    for x in range(1, 7):
        p.px(x, 5, face_dark)
    for x in (2, 3, 4, 5):
        p.px(x, 6, face_dark)
    p.px(2, 5, PK[3])          # teeth
    p.px(5, 5, PK[3])
    p.px(3, 4, face_dark)      # nose
    p.px(4, 4, face_dark)
    # top (0,8) 8x8 with stem, bottom (8,8)
    def top(x, y):
        d = max(abs(x - 3.5), abs(y - 3.5))
        return PK[5] if d < 1.5 else PK[4] if d < 3 else PK[3]

    p.region(0, 8, 8, 8, top)
    p.rect(3, 11, 2, 2, hexc("#5a7a2a"))
    p.px(3, 11, hexc("#7a9a3a"))
    p.region(8, 8, 8, 8, lambda x, y: PK[2] if (x + y) % 4 else PK[1])
    # ---------------------------------------------------------------- post.png
    w = Paint(seed="post")
    w.region(0, 0, 16, 16, lambda x, y: PO[3 + (1 if x % 2 == 0 else 0) - (1 if (x * 5 + y) % 7 == 0 else 0)])
    for y in range(16):
        w.px(1, y, PO[2])
    # ---------------------------------------------------------------- straw.png
    t = Paint(seed="straw")
    t.rect(0, 0, 16, 16, ST[3])

    def brim(x, y):
        # woven straw rings around the crown; lit north-west
        d = max(abs(x - 5.5), abs(y - 5.5))
        if d >= 5.5:
            return ST[4] if (x == 0 or y == 0) else ST[2]
        ring = int(d) % 2
        c = ST[5] if ring else ST[4]
        if (x + y) % 5 == 0:
            c = ST[3]
        return c

    t.region(0, 0, 12, 12, brim)
    # crown top lives under the crown (centre 6x6 at (3,3))
    t.region(3, 3, 6, 6, lambda x, y: ST[6] if (x + y) < 3 else ST[5] if (x + y) % 3 else ST[4])
    t.region(0, 12, 12, 1, lambda x, y: ST[3] if x % 3 else ST[2])            # brim side
    t.region(0, 13, 7, 3, lambda x, y: ST[5] if (x + y) % 3 else ST[4])       # crown side / tufts
    t.px(0, 13, ST[6])
    t.region(7, 13, 7, 3, lambda x, y: hexc("#8a2a22") if y < 2 else hexc("#5a1a16"))   # ribbon band
    t.region(7, 14, 7, 1, lambda x, y: hexc("#a83a2e") if x % 3 else hexc("#8a2a22"))
    t.region(12, 0, 4, 12, lambda x, y: ST[(5, 4, 3, 5)[x] - (1 if (y + x) % 4 == 0 else 0)])  # loose straw
    t.region(14, 12, 2, 4, lambda x, y: ST[3])
    return {"scarecrow/shirt": s.s, "scarecrow/pumpkin": p.s, "scarecrow/post": w.s, "scarecrow/straw": t.s}


# =========================================================================== sprinkler
#
# copper base plate + small tank (with water inlet), a short pipe and a 4-nozzle head turned
# 22.5 degrees (reads as spinning); ~9px tall.

def build_sprinkler():
    Bd, Hd = "body", "head"
    els = []
    els.append(box([4, 0, 4], [12, 1, 12], {**all_faces(Bd, (0, 14)), "up": (Bd, (0, 0)), "down": (Bd, (8, 8))},
                   name="base plate"))
    els.append(box([5, 1, 5], [11, 4, 11], {**all_faces(Bd, (8, 0)), "up": (Bd, (8, 3)), "down": (Bd, (8, 3))},
                   name="tank"))
    els.append(box([11, 1.5, 7], [12.5, 3, 9], {"north": (Bd, (14, 0)), "south": (Bd, (14, 0)),
                                                 "up": (Bd, (14, 2)), "down": (Bd, (14, 2)),
                                                 "east": (Bd, (14, 4))}, name="inlet"))
    els.append(box([7, 4, 7], [9, 6.5, 9], {**all_faces(Hd, (0, 0))}, name="pipe"))
    r = rot_y(22.5, (8, 7, 8))
    els.append(box([6.5, 6.5, 6.5], [9.5, 8, 9.5], {**all_faces(Hd, (2, 0)), "up": (Hd, (2, 2)),
                                                     "down": (Hd, (2, 2))}, rotation=r, name="hub"))
    arms = {
        "north": ([7.5, 6.75, 4], [8.5, 7.75, 6.5]),
        "south": ([7.5, 6.75, 9.5], [8.5, 7.75, 12]),
        "west": ([4, 6.75, 7.5], [6.5, 7.75, 8.5]),
        "east": ([9.5, 6.75, 7.5], [12, 7.75, 8.5]),
    }
    for d, (frm, to) in arms.items():
        els.append(box(frm, to, {**all_faces(Hd, (6, 0)), "up": (Hd, (6, 0)), "down": (Hd, (6, 1))},
                       rotation=r, name=f"{d} arm"))
    # upturned nozzles at the arm ends (opening on top)
    tips = {
        "north": ([7.25, 6.5, 2.75], [8.75, 8.5, 4.25]),
        "south": ([7.25, 6.5, 11.75], [8.75, 8.5, 13.25]),
        "west": ([2.75, 6.5, 7.25], [4.25, 8.5, 8.75]),
        "east": ([11.75, 6.5, 7.25], [13.25, 8.5, 8.75]),
    }
    for d, (frm, to) in tips.items():
        fc = {**all_faces(Hd, (10, 0)), "up": (Hd, (12, 0)), "down": (Hd, (10, 2))}
        els.append(box(frm, to, fc, rotation=r, name=f"{d} nozzle"))
    els.append(box([7, 8, 7], [9, 9, 9], {**all_faces(Hd, (14, 0)), "up": (Hd, (14, 1))}, rotation=r,
                   name="cap"))
    textures = {"particle": tex_ref("sprinkler/body"), "body": tex_ref("sprinkler/body"),
                "head": tex_ref("sprinkler/head")}
    model = {"parent": "minecraft:block/block", "textures": textures, "elements": els}
    model["display"] = display(
        gui=fit_display(els, [30, 225, 0], extent=14.5, max_scale=1.0),
        ground={"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.4, 0.4, 0.4]},
        fixed={"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.75, 0.75, 0.75]},
        head={"rotation": [0, 0, 0], "translation": [0, 16, 0], "scale": [1, 1, 1]},
        thirdperson_righthand={"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.5, 0.5, 0.5]},
        thirdperson_lefthand={"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.5, 0.5, 0.5]},
        firstperson_righthand={"rotation": [0, 45, 0], "translation": [0, 2, 0], "scale": [0.55, 0.55, 0.55]},
        firstperson_lefthand={"rotation": [0, 225, 0], "translation": [0, 2, 0], "scale": [0.55, 0.55, 0.55]},
    )
    return model, _sprinkler_textures()


def _sprinkler_textures() -> dict[str, Sprite]:
    C, PT = COPPER, PATINA
    b = Paint(seed="sprinkler_body")
    b.rect(0, 0, 16, 16, C[4])
    # base top 8x8 at (0,0): plate with bolt heads in the corners, lit north-west rim
    def plate(x, y):
        if x == 0 or y == 0:
            return C[6]
        if x == 7 or y == 7:
            return C[3]
        return C[4] if (x + y) % 6 else C[5]

    b.region(0, 0, 8, 8, plate)
    for (x, y) in ((1, 1), (6, 1), (1, 6), (6, 6)):
        b.px(x, y, C[7])
    # tank sides 6x3 at (8,0): riveted band, patina drip
    def tank(x, y):
        light = (1, 2, 2, 1, 0, -1)[x]
        return C[max(0, min(7, 4 + light - (1 if y == 2 else 0)))]

    b.region(8, 0, 6, 3, tank)
    b.px(9, 1, C[7])
    b.px(12, 1, C[6])
    b.px(13, 2, PT[2])
    b.px(8, 2, PT[1])
    # tank top 6x6 at (8,3) with filler cap ring
    def ttop(x, y):
        if x == 0 or y == 0:
            return C[6]
        if x == 5 or y == 5:
            return C[3]
        if 2 <= x <= 3 and 2 <= y <= 3:
            return C[2]
        return C[5]

    b.region(8, 3, 6, 6, ttop)
    # inlet (14,0) sides, (14,2) top, (14,4) open end
    b.rect(14, 0, 2, 2, C[5])
    b.px(14, 0, C[6])
    b.rect(14, 2, 2, 2, C[6])
    b.rect(14, 4, 2, 2, C[2])
    b.px(14, 4, hexc("#2a1810"))
    # base side 8x1 at (0,14), base bottom at (8,8)
    b.region(0, 14, 8, 1, lambda x, y: C[4] if x % 3 else C[3])
    b.region(8, 8, 8, 8, lambda x, y: C[2] if (x + y) % 3 else C[1])
    b.region(0, 8, 8, 6, lambda x, y: C[4])
    b.region(0, 15, 8, 1, lambda x, y: C[3])

    h = Paint(seed="sprinkler_head")
    h.rect(0, 0, 16, 16, C[4])
    # pipe sides 2x2.5 at (0,0)
    h.region(0, 0, 2, 3, lambda x, y: C[6] if x == 0 else C[4])
    # hub sides 4x1.5 at (2,0), hub top 4x4 at (2,2)
    h.region(2, 0, 4, 2, lambda x, y: C[6] if y == 0 else C[4])
    def hub(x, y):
        if x == 0 or y == 0:
            return C[6]
        if x == 3 or y == 3:
            return C[4]
        return C[5]

    h.region(2, 2, 4, 4, hub)
    # arms 2.5x1 at (6,0)
    h.region(6, 0, 3, 1, lambda x, y: C[6] if x else C[5])
    h.region(6, 1, 3, 1, lambda x, y: C[4])
    # nozzle sides (10,0) 1.5x2: copper with a verdigris ring, bottom (10,2); top opening (12,0)
    h.region(10, 0, 2, 2, lambda x, y: (C[6], PT[2])[y] if x == 0 else (C[5], PT[1])[y])
    h.region(10, 2, 2, 2, lambda x, y: C[3])
    h.region(12, 0, 2, 2, lambda x, y: C[6] if (x, y) == (0, 0) else hexc("#1a2a30") if (x, y) == (1, 1) else PT[1])
    # cap (14,0) sides 2x1, (14,1) top
    h.region(14, 0, 2, 1, lambda x, y: C[5])
    h.region(14, 1, 2, 2, lambda x, y: C[7] if (x, y) == (0, 0) else C[6])
    h.region(0, 4, 16, 12, lambda x, y: C[4] if (x + y) % 4 else C[3])
    return {"sprinkler/body": b.s, "sprinkler/head": h.s}


BUILDERS = {
    "cooking_pot": build_cooking_pot,
    "cutting_board": build_cutting_board,
    "scarecrow": build_scarecrow,
    "sprinkler": build_sprinkler,
}
