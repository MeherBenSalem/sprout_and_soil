package tn.nightbeam.sproutandsoil.content;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.resources.ResourceLocation;
import tn.nightbeam.sproutandsoil.SproutAndSoil;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.Function;

/** Loads {@code /sprout_and_soil/content/manifest.json} from the mod jar. */
public final class Content {
    private static final String MANIFEST = "/sprout_and_soil/content/manifest.json";
    private static ContentManifest manifest;

    private Content() {
    }

    public static synchronized void load() {
        if (manifest != null) {
            return;
        }
        try (InputStream in = Content.class.getResourceAsStream(MANIFEST)) {
            if (in == null) {
                throw new IllegalStateException("Missing " + MANIFEST + " - run tools/assetgen/build_assets.py");
            }
            try (Reader reader = new InputStreamReader(in, StandardCharsets.UTF_8)) {
                manifest = parse(JsonParser.parseReader(reader).getAsJsonObject());
            }
        } catch (IOException e) {
            throw new IllegalStateException("Could not read " + MANIFEST, e);
        }
    }

    public static ContentManifest manifest() {
        if (manifest == null) {
            load();
        }
        return manifest;
    }

    // ------------------------------------------------------------------------------------ parsing

    private static ContentManifest parse(JsonObject root) {
        List<ContentManifest.Crop> crops = list(root, "crops", o -> new ContentManifest.Crop(
                str(o, "id"), str(o, "block"), str(o, "planting_item"), str(o, "produce"),
                ContentManifest.CropModel.valueOf(str(o, "model").toUpperCase(Locale.ROOT)), o.get("regrow_age").getAsInt()));
        List<ContentManifest.Tree> trees = list(root, "trees", o -> new ContentManifest.Tree(
                str(o, "id"), str(o, "sapling"), str(o, "leaves"), rl(o, "fruit"), rl(o, "feature")));
        List<ContentManifest.ItemEntry> items = list(root, "items", o -> new ContentManifest.ItemEntry(
                str(o, "id"), o.has("stack") ? o.get("stack").getAsInt() : 64,
                o.has("food") ? food(o.getAsJsonObject("food")) : null,
                o.has("container") ? rl(o, "container") : null,
                o.has("remainder") ? rl(o, "remainder") : null,
                bool(o, "drink"), o.has("plants") ? str(o, "plants") : null, bool(o, "tooltip")));
        List<ContentManifest.Feast> feasts = list(root, "feasts", o -> new ContentManifest.Feast(
                str(o, "id"), ContentManifest.FeastKind.valueOf(str(o, "kind").toUpperCase(Locale.ROOT)),
                o.has("slice") ? str(o, "slice") : null));
        List<ContentManifest.Worldgen> worldgen = list(root, "worldgen", o -> new ContentManifest.Worldgen(
                rl(o, "feature"), rl(o, "biomes")));

        Map<ResourceLocation, Float> compost = new LinkedHashMap<>();
        root.getAsJsonObject("compost").entrySet()
                .forEach(e -> compost.put(ResourceLocation.parse(e.getKey()), e.getValue().getAsFloat()));
        Map<String, List<ResourceLocation>> tabs = new LinkedHashMap<>();
        root.getAsJsonObject("tabs").entrySet().forEach(e -> tabs.put(e.getKey(), ids(e.getValue().getAsJsonArray())));
        JsonObject t = root.getAsJsonObject("trades");
        ContentManifest.TradePools trades = new ContentManifest.TradePools(ids(t.getAsJsonArray("seeds")),
                ids(t.getAsJsonArray("produce")), ids(t.getAsJsonArray("fruits")), ids(t.getAsJsonArray("saplings")),
                ids(t.getAsJsonArray("meals")));

        return new ContentManifest(crops, trees, items, feasts, strings(root.getAsJsonArray("crates")),
                strings(root.getAsJsonArray("gardens")), compost, worldgen, tabs, trades);
    }

    private static ContentManifest.Food food(JsonObject o) {
        List<ContentManifest.Effect> effects = o.has("effects") ? list(o, "effects", e -> new ContentManifest.Effect(
                rl(e, "effect"), e.get("duration").getAsInt(), e.get("amplifier").getAsInt(),
                e.get("chance").getAsFloat())) : List.of();
        return new ContentManifest.Food(o.get("nutrition").getAsInt(), o.get("saturation").getAsFloat(),
                bool(o, "always_edible"), bool(o, "fast"), effects);
    }

    private static <T> List<T> list(JsonObject parent, String key, Function<JsonObject, T> mapper) {
        List<T> out = new ArrayList<>();
        if (parent.has(key)) {
            for (JsonElement e : parent.getAsJsonArray(key)) {
                out.add(mapper.apply(e.getAsJsonObject()));
            }
        }
        return List.copyOf(out);
    }

    private static List<ResourceLocation> ids(JsonArray array) {
        List<ResourceLocation> out = new ArrayList<>();
        array.forEach(e -> out.add(ResourceLocation.parse(e.getAsString())));
        return List.copyOf(out);
    }

    private static List<String> strings(JsonArray array) {
        List<String> out = new ArrayList<>();
        array.forEach(e -> out.add(e.getAsString()));
        return List.copyOf(out);
    }

    private static String str(JsonObject o, String key) {
        return o.get(key).getAsString();
    }

    private static boolean bool(JsonObject o, String key) {
        return o.has(key) && o.get(key).getAsBoolean();
    }

    private static ResourceLocation rl(JsonObject o, String key) {
        String value = str(o, key);
        return value.contains(":") ? ResourceLocation.parse(value) : SproutAndSoil.id(value);
    }
}
