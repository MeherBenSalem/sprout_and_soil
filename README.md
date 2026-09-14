# Sprout & Soil

Multi-stage tomato, garlic, and lettuce crops for Minecraft, with fertilizer support and farmer villager trades.

## Features

- Tomato (8 growth stages), garlic and lettuce (4 stages each)
- Plant on farmland; bone meal (`crops:fertilizer`) advances growth
- Farmer trades for seeds and crops
- Creative tab with the four main items

## Supported versions

| Workspace | Minecraft | Loaders | Java |
| --- | --- | --- | --- |
| `1.20.1/` | 1.20.1 | Fabric, Forge | 17 |
| `1.21.1/` | 1.21.1 | Fabric, NeoForge | 21 |
| `26.2/` | 26.2 | Fabric, NeoForge | 25 |

## Build

```bash
# All loaders into all-jars/
./gradlew buildAll

# Or one Minecraft line
cd 1.20.1 && ./gradlew build
```

Set `JAVA_HOME_17`, `JAVA_HOME_21`, and `JAVA_HOME_25` when using the root orchestrator.

## Publish (local)

```bash
./gradlew buildAll
node scripts/upload_platforms.mjs --version 0.3.0
```

Requires `MODRINTH_TOKEN`, `CURSEFORGE_TOKEN`, and `CURSEFORGE_API_KEY` (see NightBeam `local.env`).

## Contributing / Security / License

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](.github/SECURITY.md)
- Licensed under the [Apache License 2.0](LICENSE)
