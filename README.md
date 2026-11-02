# Aetherfall: The World Eater

A Minecraft **1.20.1 Forge** boss mod. Descend into a ruined Void Temple, light its altar and face
**Aetherfall, the World Eater**: a colossal star-winged dragon that walks, flies, breathes a beam of
void energy, tears the sky open with meteors and calls its Voidling brood.

| | |
|---|---|
| Minecraft | 1.20.1 |
| Loader | Forge 47.4.28 or newer (47.x) |
| Required | GeckoLib 4.8.4 or newer for 1.20.1 |
| Java | 17 (Gradle downloads it automatically) |

## Building

```bash
./gradlew build
```

The mod jar is written to `build/libs/aetherfall-<version>.jar`. Put it and the GeckoLib jar in
your `mods` folder.

## Development

```bash
./gradlew runClient   # development client
./gradlew runServer   # dedicated server
./gradlew runData     # regenerate block states, models, tags, loot tables and damage types into src/generated
./gradlew runGameTestServer   # run the automated boss tests (16 tests: scaling, phases, every attack, Erosion, death)
```

## Original assets

Every texture, sound and the score are original and generated from source code in `tools/`. To
regenerate them you need Python 3 with numpy and Pillow, plus ffmpeg built with libvorbis.

```bash
python3 tools/assets/gen_textures.py   # block and item textures (16x16, animated rune and core frames)
python3 tools/assets/gen_logo.py       # mod list logo
python3 tools/audio/sfx.py             # all 51 sound effects (mono, positional)
python3 tools/audio/music.py           # "Aetherfall - The World Eater", 3:12 battle theme (stereo, streamed)
```

## Configuration

* `config/aetherfall-common.toml`: boss health, armor, damage, multiplayer scaling, terrain
  destruction rules (these respect `mobGriefing`), arena protection, altar cooldown and temple
  generation.
* `config/aetherfall-client.toml`: boss music, screen shake, ornate boss bar and particle density.

## License

All Rights Reserved.
