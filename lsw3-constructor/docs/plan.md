# LSW3 Level Constructor — Research-grounded plan

From parallel research synthesis. Confidence labels on every non-obvious claim.

## 1. What we can code against today

### Container layer (high confidence)

- **GAME.DAT / GAME.HDR is Aluigi `ttgames.bms`-format.** Split pair, header magic `.CC4` (`0x3443432E` LE). TOC = name blob → file table → FNV-1a hash table. Filenames null-terminated 8-bit, backslash-normalized.
- **No whole-archive encryption, no Oodle** in the 2011-2012 era. Per-chunk compression selected by 4-char code: `LZ2K`, `DFLT`, `Defl` (Deflate_v1.0 with 0x24 local header), `RFPK`, `RNC_`. `ZIPX`+RC4 branch exists in script but flagged untested — does not fire on retail.
- **Filename hash is FNV-1a with TT-specific 32-bit prime `0x199933`** (not standard `0x01000193`) OR standard 64-bit FNV-1a. LSW3 likely ships 64-bit → `quickbms_4gb_files.exe`.
- **Outer LZMA wrapper edge case:** if first 16 bytes = `CMP2CMP2CMP2CMP2`, real header is LZMA-compressed under 16-byte hash + u64 uncompressed size. Unlikely for LSW3 but cheap to check.

Extract works today with `quickbms_4gb_files.exe ttgames.bms game.hdr out/`. **Repack does not exist publicly for LSW3.** DATOneArchiver covers LSW1/LSW2 only; DATManager extracts only. This is the first real wall.

### Level/scene layer (seeded from mortar-eng, LSW1)

- **Containers are OFFSET-TABLE based, not IFF/RIFF chunked.** First 4 bytes = sig, then fixed table of u32 section offsets; every internal pointer adds `BODY_OFFSET` (NUP=0x40, HGP=0x30).
- **Vertex layouts keyed by u32 `vertexType`.** `0x59` = 36-byte static (POS vec3 / NORMAL vec3 / COLOR d3dcolor / UV vec2). `0x5D` = 56-byte skinned (POS / BW vec2 / BI vec3 / NORMAL / COLOR / UV at 0x30).
- **Indices are u16 triangle strips. Bone palette per draw ≤ 16.**
- **Transforms = 4×4 column-major f32 matrices (64 bytes).** Not quat+vec3.
- **Textures inlined as DDS blobs** inside the container's texture block. No external `.tex` sidecar in this tier (unverified for LSW3 — Pirates moved some out).
- **Materials flat:** 2-word flags (alpha = flags & 0xF, lit = (flags & 0x30000) != 2), 3-f32 RGB, i16 texture index with 0x8000 as atlas marker, u8 effectType. No PBR, no normal maps.

### LSW3-specific on-disk layout

Per-level folder `levels\...\<Chapter>\<LevelName>\`:
- `<name>.GSC` — classic-tier container (geometry/model)
- `<name>_NXG.GSC` — NXG variant, the live one for PC/360/PS3
- `<name>_LR.GSC` — low-res / Wii fallback
- `<name>.GIZ` — undocumented, paired with GSC
- `<name>.TXT` — plain-text level driver

### Two assertions to stop believing

- **NU20 is NOT the DAT format.** NU20 is a chunk magic *inside* GSC/NUP/HGP. DAT is `.CC4`/ttgames.bms.
- **LSW3 does NOT ship `.nup`.** NUP is PS2/GC era (LSW1/LSW2/Bionicle). LSW3 ships DAT + GSC/GHG.

## 2. Reverse-engineering backlog, prioritized

| # | Thing | Priority | Difficulty | Why |
|---|---|---|---|---|
| 1 | DAT repack (write valid `.CC4` pair) | critical | medium | Extraction solved, authoring not. FNV-1a-0x199933 writer, TOC offsets, Deflate as safest target. |
| 2 | NXG delta from LSW1 NUP/HGP header | critical | medium | mortar-eng trails 106 u32 of `unk`. LSW3 repurposed region for shadow maps / Kinect / expanded skinning. |
| 3 | Endianness per platform | high | low | NXG PC reported big-endian on payloads. HSEM reads as MESH if swapped. |
| 4 | Instance/special-object region | high | medium-high | `NUPModelHeader.num_special_objects` unparsed. Likely houses spawns/triggers/lights. |
| 5 | Collision mesh | high | unknown | Nothing in mortar-eng. Candidates: flagged mesh pass, or parallel list. |
| 6 | GSC script bytecode VM | medium | high | No opcode table published. For data-only constructor can defer — reuse existing mission scripts. |
| 7 | `.GIZ` layout | medium | low | Short, paired with GSC. First-hour hex-editor work. |
| 8 | Navmesh / AI paths | medium | unknown | Probably spline-and-waypoint (mortar-eng has `num_splines`). |
| 9 | `.AN3` vs `.AN4` for LSW3 | low | medium | Batman 2 confirmed `.AN4`. LSW3 probably still `.AN3`. |
| 10 | Skeleton chunk tag in GHG | low | medium | No confirmed `SKEL` magic. figure-forge has working rigs for classic trio. |

## 3. Tool stack

- **Python** for parser/first pass (struct, numpy, construct, REPL loop against hex-dumped files).
- **Rust/C++** only when: real compressor (LZ2K/RFPK) needs speed, shipping repacker, or linking mortar-eng directly.
- **Blender add-on + glTF** for editing/debug. Blender's Python API, free, works on his M3.
- **Noesis** as backup viewer, not build target.

### Existing tools to wrap, not rewrite

- **QuickBMS + `ttgames.bms`** (linterniGamer) — DAT extraction. Shell out.
- **`mortar-eng`** (`leftmostcat/mortar-eng`, GPL-3, C++) — single best living spec. Port NUP/HGP readers to Python; `unk` fields are "look here first" markers for NXG delta.
- **`DATOneArchiver`** (IsaMorphic, C#, LSW1/LSW2) — read its writer path.
- **`TTGamesPatcher`** (archived) — patches EXE's DAT-DRM check so loose files load. LSW3 is DX9 → TTMagic/Koalyptus does NOT apply.
- **`NuXtractor`** (archived, LSW1) — second-opinion NU20 chunk-walker.

### Tools to ignore for LSW3

BrickBench (TCS only), Snufflebox TTGames-Workshop (LSW3 unverified), fisherjoey/tt-save-editor (Batman Legacy only), NuTCrackerV3 (unverified), xensik/gsc-tool (wrong GSC — Call of Duty).

### Host of truth

TTGames LEGO Modding Discord (server id `539431629718945793`). Every GitHub repo here is 2+ years old or archived. Live work is on Discord.

## 4. First deliverable (1-2 days of focused work)

**Target: read-only level inspector that renders LSW3 geometry to glTF/Blender. No textures, no lighting, no animation, no scripts.**

1. DAT extraction wrapper around `quickbms_4gb_files.exe ttgames.bms`. 30 min.
2. `.CC4` header probe. Print magic + first table offsets. 30 min.
3. GSC/NUP header parser. Port mortar-eng `NUPHeader`/`NUPModelHeader`. Endian-configurable (LE default, retry BE if `vertexType` insane). 2-3 h.
4. Vertex/index extractor. Static vertices (0x59) only for v0.1. 2 h.
5. Instance walker. 4×4 matrix per instance, `mesh_idx`. 1 h.
6. glTF writer. `pygltflib` or hand-rolled. 1-2 h.
7. Smoke test in Blender.

What this gives: "point tool at `levels\SomeLevel\SomeLevel_NXG.GSC` → get glTF." No textures, no scripts. Just floor plan.

What we'll know by end: NXG delta direction, actual endianness, embedded-vs-external textures.

## 5. What we need from user

1. **LSW3 install folder**, or at minimum:
   - `GAME.DAT` + `GAME.HDR` — both halves. HDR alone useless (no payload), DAT alone useless (no hash table).
   - `LEGOStarWarsIII.exe` — for cross-referencing struct sizes against engine binary.
2. **One pre-extracted level directory** (TCRF mentions `SimpleRTS` — simple-sounding test level).
3. **Platform confirmation:** PC Windows retail, DX9-era, Steam/GOG?
4. **Any partial dumps** already done — cuts the duplicated extract step.
5. **Optional:** LSW:TCS extracted files for byte-diff against mortar-eng baseline.

## Reality check

- **Repack is the real risk.** Extract-view is plumbing. Writing a `.CC4` LSW3 accepts is the project.
- **GSC script VM is a trap.** Constructor can reuse existing compiled scripts and edit data side only.
- **mortar-eng's LSW1 structs will not be byte-exact for LSW3.**
- **Archived-tool problem is real.** Live work is on Discord, not indexed.
- **Many community sources (tcrf.net, rockraidersunited.com, ttmodding.fandom.com, nexusmods.com) were DNS-blocked in research sessions.** Some "medium" claims above sit on snippets, not verbatim page reads. Discord is court of first appeal before committing to disputed field layouts.
