import os
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]          # tools/assetgen
REPO = TOOLS.parents[1]
WORKSPACE = REPO / "1.21.1"
GENERATED = WORKSPACE / "common" / "src" / "generated" / "resources"
ASSETS = GENERATED / "assets" / "sprout_and_soil"
DATA = GENERATED / "data"
TEXTURES = ASSETS / "textures"
MODELS = ASSETS / "models"
MAIN_RESOURCES = WORKSPACE / "common" / "src" / "main" / "resources"
# The pixel-art badge the listing icon (and so every logo.png) is built from, see marketing/source/render.cjs
BADGE = REPO / "marketing" / "source" / "badge.png"
# Minecraft 1.20.1 workspace: same content, converted by sas.legacy
LEGACY_GENERATED = REPO / "1.20.1" / "common" / "src" / "generated" / "resources"
BUILD = TOOLS / "build"          # scratch output (previews, contact sheets) - git-ignored
# Optional: root of an extracted vanilla client jar (the folder that contains assets/minecraft), used only to show
# vanilla items next to ours in previews and to resolve vanilla parent models in render3d. Never copied.
VANILLA_REF = os.environ.get("SAS_VANILLA_ASSETS") or None
