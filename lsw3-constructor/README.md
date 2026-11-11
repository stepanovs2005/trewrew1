# lsw3-constructor

Level constructor and cross-game character importer for LEGO Star Wars III: The Clone Wars (2011, Traveller's Tales, NuGame engine).

## Status

Reverse-engineering project. No official SDK, no prior full editor. See `docs/roadmap.md` for the honest scope.

## Repo layout

- `core/` — shared primitives (BinaryReader/Writer, type registry, math)
- `formats/` — per-format codecs (GAME.DAT archive, .nup bundles, .gsc scripts, .nut/.nu2 textures, model/level/animation decoders)
- `viewer/` — OpenGL 3D viewport (scene graph, gizmos, picking)
- `gui/` — PyQt6 editor shell (dockable panels, inspector, outliner, asset browser)
- `tools/` — standalone CLI utilities (extract-dat, repack-dat, nup-inspect, char-port, etc.)
- `docs/` — format notes, roadmap, RE journal
- `samples/` — tiny fixtures for round-trip tests (no copyrighted game data committed)

## Running

Requires Python 3.11+, PyQt6, PyOpenGL, numpy, pyrr. Game files are NOT in this repo — user provides their own `GAME.DAT` path at runtime. Nothing from LucasArts/Disney/TT is distributed here.

## Legal

Modifies files the user already owns on their own machine. No redistribution of game assets. Interop research under fair-use reverse-engineering doctrine.
