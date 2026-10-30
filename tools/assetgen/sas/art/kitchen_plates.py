"""Plated meals. All share the white/pale-blue plate (rows 8-15); the food layer is drawn on
its own sprite and outlined so it casts a crisp dark edge onto the ceramic."""
from __future__ import annotations

from .kitchen_kit import C, dome, plate_dish, put, puts, reg, rp, stamp
from .kitchen_parts import BROCCOLI, POTATO_SKIN, bacon_strip, basil, broccoli, fried_egg, lemon_wedge


@reg("spaghetti_bolognese")
def spaghetti_bolognese():
    def f(s):
        pasta = rp("#f0d07a", 5, 0.08)
        pts = dome(s, 7.6, 10.6, 6.0, 3.6, pasta)
        # strands: curved light / dark stripes
        for x, y in pts:
            k = (x * 2 + y * 3 + (x // 3)) % 5
            if k == 0:
                s.set(x, y, pasta[4])
            elif k == 3:
                s.set(x, y, pasta[1])
        sauce = rp("#a8301a", 5, 0.09)
        sp = dome(s, 7.4, 8.6, 3.8, 2.6, sauce, flat=0.8)
        for x, y in sp:
            if (x * 3 + y * 5) % 4 == 0:
                s.set(x, y, sauce[1])           # mince texture
        puts(s, [(5, 7), (6, 7)], sauce[4])
        puts(s, [(7, 8), (9, 9), (5, 9)], "#fbf4dc")   # parmesan
        basil(s, 8, 5)
        # a stray strand curling onto the plate
        puts(s, [(1, 11), (2, 12), (3, 12), (12, 13), (13, 12)], pasta[3])
    return plate_dish(f)


@reg("lasagna")
def lasagna():
    def f(s):
        rows = [
            #0123456789abcdef
            "................",  # 0
            "................",
            "................",
            "....hcCcccCcc...",  # 3  bubbly cheese top
            "...cCcchcccCcz..",  # 4
            "..cccCccccCccz..",  # 5
            "..ppppppppppppz.",  # 6  pasta edge
            "..rrRrrrrRrrrrz.",  # 7  meat sauce
            "..wwwwwwwwwwwwz.",  # 8  bechamel
            "..ppppppppppppz.",  # 9  pasta
            "..rrrRrrrrRrrrz.",  # 10 sauce
            "..ppppppppppppz.",  # 11 pasta
            "..rr.......rr...",  # 12 sauce oozing onto the plate
        ]
        pal = {"h": "#fff2b0", "c": "#f2d070", "C": "#c8862e", "z": "#a8641e",
               "p": "#f0c860", "r": "#b83a1a", "R": "#7a2410", "w": "#f8eed0"}
        stamp(s, rows, pal)
        # light the front-left edge, darken the right side
        for y in range(6, 12):
            put(s, 2, y, C({"p": "#fadc84", "r": "#d4522a", "w": "#fffaea"}[rows[y][2]]))
            put(s, 13, y, C({"p": "#c89a3a", "r": "#8a2a14", "w": "#d8ccb0"}[rows[y][13]]))
        basil(s, 9, 2)
    return plate_dish(f)


@reg("ratatouille")
def ratatouille():
    def f(s):
        sauce = rp("#c03a24", 5, 0.08)
        dome(s, 7.6, 11.6, 6.2, 2.4, sauce, flat=0.5)
        tom = {"o": "#9a1c14", "i": "#e8483a", "c": "#f69070"}
        egg = {"o": "#3c1648", "i": "#f2e6c8", "c": "#d8c8a0"}
        zuc = {"o": "#2a6020", "i": "#dcecaa", "c": "#a8c870"}
        disc = [".oo.", "oici", "oiio", ".oo."]
        # a fanned row of overlapping slices (each covers the previous one's right edge)
        for i, x in enumerate((1, 4, 7, 10)):
            stamp(s, disc, (tom, egg, zuc, tom)[i], x, 5 + (i % 2))
        for i, x in enumerate((2, 5, 8, 11)):
            stamp(s, disc, (zuc, tom, egg, zuc)[i], x, 9 - (i % 2))
        basil(s, 6, 2)
    return plate_dish(f)


@reg("paella")
def paella():
    def f(s):
        rice = rp("#f0b81a", 5, 0.07)
        pts = dome(s, 7.6, 11.0, 6.2, 3.2, rice, flat=0.6)
        for x, y in pts:
            if (x * 7 + y * 3 + (y // 2) * 5) % 7 == 0:
                s.set(x, y, rice[4])
            elif (x * 5 + y * 3) % 9 == 4:
                s.set(x, y, rice[1])
        pep = {"h": "#f87050", "b": "#c8281e"}
        stamp(s, ["hbb"], pep, 3, 10)
        stamp(s, ["hb", ".b"], pep, 10, 9)
        shrimp = {"p": "#f4886a", "P": "#fcc0a4", "d": "#c85a3a"}
        stamp(s, [".pP", "p.d", "pd."], shrimp, 5, 7)
        stamp(s, ["Pp.", "d.p", ".dp"], shrimp, 9, 6)
        chick = {"h": "#fbe8cc", "l": "#f0c890", "d": "#c8945a"}
        stamp(s, ["hl", "ld"], chick, 7, 10)
        puts(s, [(4, 12), (11, 12), (6, 9), (12, 10)], "#5aa832")   # peas
        lemon_wedge(s, 1, 7)
    return plate_dish(f)


@reg("stuffed_peppers")
def stuffed_peppers():
    def f(s):
        pepper = [
            "..sS...",   # stem
            ".cCcc..",   # melted cheese & rice in the open top
            "hcrcCcd",
            "hRRrRRd",
            "hRRrRRd",
            "hRRrRdd",
            ".hRrRd.",
            "..ddd..",
        ]
        pal = {"s": "#3f8a2e", "S": "#6ab84a", "c": "#f6d050", "C": "#fbe890", "r": "#f6f2e6",
               "h": "#f8705a", "R": "#d42c20", "d": "#8a1610"}
        stamp(s, pepper, pal, 1, 4)
        stamp(s, pepper, pal, 8, 3)
        # crease highlights & browned cheese
        puts(s, [(3, 8), (10, 7)], "#f8705a")
        puts(s, [(3, 6), (11, 5)], "#c8862e")
    return plate_dish(f)


@reg("omelette")
def omelette():
    def f(s):
        rows = [
            #0123456789abcdef
            "................",
            "................",
            "................",
            "................",
            "................",
            "......hhhhh.....",  # 5
            "....hyyyyyyyy...",  # 6
            "...hyyyYyyyyyo..",  # 7
            "..hyyyyyyyyYyoo.",  # 8
            "..yyyyYyyyyyyoo.",  # 9
            "..oyyyyyyyyyooe.",  # 10
            "...ooyyyyyoooee.",  # 11
            ".....oooooeee...",  # 12
        ]
        pal = {"h": "#fcec90", "y": "#f6d04a", "Y": "#e8b030", "o": "#d8a028", "e": "#b88020"}
        stamp(s, rows, pal)
        puts(s, [(5, 7), (9, 6), (7, 9), (11, 8), (4, 9)], "#d02a1e")   # red pepper
        puts(s, [(6, 8), (10, 9), (8, 7)], "#3f8a2e")                   # chives
        puts(s, [(5, 6), (6, 6)], "#fff6c8")
    return plate_dish(f)


@reg("pancakes")
def pancakes():
    def f(s):
        rows = [
            #0123456789abcdef
            "................",
            "......bbB.......",  # 1  butter pat
            ".....bbbbB......",  # 2
            "...tTTtttttt....",  # 3  top face
            "..ttttTtttttd...",  # 4
            "..Seeeeeeeeeed..",  # 5  pancake edges / fluffy interior
            "..Sggggggggggd..",  # 6
            "..eeeeeeeeeeee..",  # 7
            "..Sggggggggggd..",  # 8
            "..eeeeeeeeeeee..",  # 9
            "..ggggggggggggd.",  # 10
            "..eeeeeeeeeeeed.",  # 11
            "...eeeeeeeeeee..",  # 12
        ]
        pal = {"b": "#fcf0a0", "B": "#e8d070", "t": "#e8a850", "T": "#f2c070", "d": "#b06a24",
               "e": "#c47a2c", "g": "#f2cc80", "S": "#a85a1c"}
        stamp(s, rows, pal)
        # maple syrup pooling on top and running down the front
        syrup, syl = C("#a8501a"), C("#d8802a")
        puts(s, [(5, 4), (6, 4), (7, 4), (8, 3), (9, 4)], syrup)
        puts(s, [(6, 3)], syl)
        puts(s, [(5, 5), (5, 6), (5, 7), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9)], syrup)
        puts(s, [(4, 5), (8, 5)], syl)
        puts(s, [(5, 8), (9, 10)], "#8a3e14")
    return plate_dish(f)


@reg("breakfast_plate")
def breakfast_plate():
    def f(s):
        # toast at the back left
        toast = [
            ".cccc..",
            "cTTttc.",
            "cTtttdc",
            "cttttdc",
            ".cdddc.",
        ]
        stamp(s, toast, {"c": "#9a5a1e", "T": "#f6d898", "t": "#e8b868", "d": "#c8904a"}, 1, 4)
        # bacon strips at the back right
        bacon_strip(s, 8, 4, cooked=True, length=6)
        bacon_strip(s, 8, 7, cooked=True, length=6)
        # grilled tomato half at the front right
        stamp(s, [".RRR.", "RfffR", "RfsfR", ".rrr."],
              {"R": "#c8281e", "r": "#8a1a12", "f": "#f07050", "s": "#a83018"}, 10, 9)
        put(s, 11, 9, "#3a2a10")    # grill char
        fried_egg(s, 2, 8, big=True)
    return plate_dish(f)


@reg("fish_and_chips")
def fish_and_chips():
    def f(s):
        fish = [
            #0123456789
            "....hlh...",
            "..hlllbl..",
            ".hlbllbld.",
            "hllllblbd.",
            "lbllbllbd.",
            ".lbbldbdd.",
            "..bddd....",
        ]
        stamp(s, fish, {"h": "#fcdc98", "l": "#eab656", "b": "#cf9238", "d": "#a2641e"}, 1, 5)
        # chips: separate upright sticks
        chips = [
            ".h.h.h",
            ".l.lhl",
            "hlhlbl",
            "lbldbd",
            "lblbbd",
            "bdbdd.",
        ]
        stamp(s, chips, {"h": "#fdf0a8", "l": "#f8d860", "b": "#e2b03a", "d": "#b8862a"}, 9, 5)
        lemon_wedge(s, 5, 10)
    return plate_dish(f)


@reg("steak_dinner")
def steak_dinner():
    def f(s):
        steak = [
            #0123456789
            "..hhlll...",
            ".hlklllkl.",
            "fhklllklbd",
            "fklllklbdd",
            "flllklbbd.",
            ".fbbbddd..",
        ]
        stamp(s, steak, {"h": "#c07a4a", "l": "#9a5530", "b": "#7a3c1e", "d": "#55260f", "k": "#2e1408",
                         "f": "#f0dcc0"}, 1, 7)
        # baked potato split with butter at the back right
        pot = [
            ".lhl.",
            "lbYbd",
            "bYyYd",
            ".bdd.",
        ]
        stamp(s, pot, {**POTATO_SKIN, "Y": "#f4dc80", "y": "#fcf0b0"}, 9, 4)
        put(s, 11, 5, "#fff8d0")
        broccoli(s, 10, 8)
        stamp(s, ["hl", "bd"], BROCCOLI, 13, 9)
    return plate_dish(f)


@reg("roast_chicken_dinner")
def roast_chicken_dinner():
    def f(s):
        leg = [
            #0123456789ab
            "..........ww",
            ".........wWw",
            "........kwk.",
            "......hlk...",
            "...hhlllb...",
            "..hllllbbd..",
            ".hlllblbdd..",
            ".llbllbdd...",
            "..bbbddd....",
        ]
        stamp(s, leg, {"w": "#f6eedc", "W": "#ffffff", "k": "#d8c8a8", "h": "#f6c47a", "l": "#d8883a",
                       "b": "#b0602a", "d": "#7a3e1a"}, 1, 3)
        carrot = {"h": "#fbb060", "l": "#f08a2a", "d": "#c05a14"}
        stamp(s, ["hll", ".ld"], carrot, 10, 9)
        stamp(s, ["hld"], carrot, 11, 12)
        pot = {"h": "#fbe0a0", "l": "#e8b860", "b": "#c88a3a", "d": "#9a6020"}
        stamp(s, [".hl", "hlb", "lbd"], pot, 7, 10)
        stamp(s, ["hl", "bd"], pot, 12, 7)
        put(s, 9, 9, "#3f8a2e")
    return plate_dish(f)


@reg("grilled_salmon")
def grilled_salmon():
    def f(s):
        # three asparagus spears leaning behind the fillet
        tip, g, G = C("#2f5a1c"), C("#5e9434"), C("#9cca62")
        for x0 in (8, 10, 12):
            for j in range(6):
                x, y = x0 + (2 - j // 2), 3 + j
                s.set(x, y, G if j < 2 else g)
            s.set(x0 + 2, 2, tip)
            s.set(x0 + 2, 3, C("#4a7a2a"))
        fillet = [
            #0123456789
            "..hHhhh...",
            ".hsswssss.",
            "hsswssswsd",
            "sswssswsdd",
            "swsssswsd.",
            ".ddddddd..",
        ]
        stamp(s, fillet, {"h": "#c86a3a", "H": "#a8502a", "s": "#ee8a60", "w": "#fbd0b8", "d": "#c05e3a"}, 1, 7)
        puts(s, [(2, 7), (3, 7)], "#e09060")
        lemon_wedge(s, 10, 10)
        put(s, 9, 12, "#3f8a2e")
    return plate_dish(f)


@reg("caprese_salad")
def caprese_salad():
    def f(s):
        tom = {"o": "#a82018", "i": "#e0382a", "c": "#f47a5a", "s": "#f8c870"}
        moz = {"o": "#d8d2c0", "i": "#fbf9f0", "c": "#ffffff", "s": "#ece6d4"}
        disc = [".ooo.", "oicio", "oisio", ".ooo."]
        spots = [(1, 9), (2, 6), (5, 5), (8, 6), (10, 8), (8, 9), (4, 9)]
        for i, (x, y) in enumerate(spots):
            stamp(s, disc, tom if i % 2 == 0 else moz, x, y)
        basil(s, 4, 4)
        basil(s, 9, 5, flip=True)
        basil(s, 7, 8)
        puts(s, [(3, 12), (12, 12), (8, 13)], "#3a1a10")   # balsamic drops
    return plate_dish(f)
