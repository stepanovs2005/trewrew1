# lsw3-constructor

Level constructor + cross-game character porter for **LEGO Star Wars III: The Clone Wars** (2011, Traveller's Tales, NXG-tier "NuGame" engine).

## Status

Reverse-engineering project. No official SDK. Community tooling extracts but does not repack; no LSW3 level editor exists publicly. This repo aims to be the first one.

See `docs/plan.md` for the honest, research-grounded roadmap.

## Repo layout

- `core/` — binary IO primitives + the TT-specific FNV-1a hash (prime `0x199933`)
- `formats/` — per-format codecs
  - `game_dat.py` — `.HDR` + `.DAT` pair (`.CC4` magic), the top-level archive
  - `gsc.py` — GSC/GHG containers (geometry/character), NU20 chunks inside
- `tools/` — CLI utilities
  - `extract_dat.py` — wrapper around QuickBMS + `ttgames.bms`
  - `hdr_probe.py` — minimal header inspector (first probe on a new sample)
- `viewer/` — OpenGL 3D viewport (scheduled for M4)
- `gui/` — PyQt6 editor shell (scheduled for M4-M5)
- `docs/` — format notes, roadmap, RE journal
- `samples/` — tiny fixtures for round-trip tests (no copyrighted game data committed)

## What you need to proceed

The parser skeletons are in place but implementations wait on a real sample. From the LSW3 install:

1. `GAME.DAT` + `GAME.HDR` — **both halves** (HDR alone has no payload; DAT alone has no hash table)
2. `LEGOStarWarsIII.exe` — for cross-referencing struct sizes
3. One pre-extracted level directory if available (TCRF mentions `SimpleRTS` — simple test level)

## Running (when files are provided)

```bash
pip install -r requirements.txt

# M1: extract GAME.DAT into a mirrored tree
python tools/extract_dat.py path/to/game.hdr out/

# first-pass header sanity check
python tools/hdr_probe.py path/to/game.hdr
```

## Dependencies on external tools

- **QuickBMS + `ttgames.bms`** — for DAT extraction (shelled out, not reimplemented)
  - Get `quickbms_4gb_files.exe` from Aluigi (altervista)
  - Get `ttgames.bms` from https://github.com/linterniGamer/Tt-Games-quickbms-scripts

- **TTGamesPatcher** — patches the LSW3 EXE so it loads loose files (needed once per install). Archived repo: https://github.com/AlubJ/TTGamesPatcher
  - Note: TTMagic / acidicoala's Koalyptus does NOT apply — LSW3 is DX9, that bypass targets DX11-era titles.

## Legal

Modifies files the user already owns on their own machine. No redistribution of game assets. Interop research under fair-use reverse-engineering doctrine.

## Where live help comes from

TTGames LEGO Modding Discord (server id `539431629718945793`). Most GitHub repos in this space are 2+ years old or archived; the Discord is where the living work happens.
