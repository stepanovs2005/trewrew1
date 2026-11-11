# Roadmap

Research-grounded. See `plan.md` for the full synthesis and confidence labels.

## Blocker on user

Nothing substantive gets implemented without:
1. `GAME.DAT` + `GAME.HDR` from LSW3 install
2. `LEGOStarWarsIII.exe`
3. Platform confirmation (PC Windows retail DX9 — Steam/GOG)
4. Access to sibling titles later (Batman 2, Pirates, HP5-7) for character porting

## Milestones

### M0 — Scaffold (done)

- Repo layout, binary IO primitives, TT-FNV hash, format module shells with stable API.
- Plan document grounded in research of community RE work.

### M1 — DAT extract + probe (1-2 days once sample lands)

- `tools/extract_dat.py` — wraps QuickBMS + ttgames.bms. Produces mirrored tree + manifest.
- `tools/hdr_probe.py` — dumps magic + first offset table words.
- `formats/game_dat.py::GameDat.open` — Python-native parser for `.HDR` (so we don't depend on QuickBMS forever). Field order confirmed against a real sample.

### M2 — GSC/GHG reader (NXG tier) (1-2 weeks)

- Parse section-offset table (BODY_OFFSET=0x40 NUP / 0x30 HGP).
- Walk ModelHeader, Instances, Meshes, Materials, embedded DDS textures.
- Handle vertexType 0x59 (static) first; 0x5D (skinned) after.
- Endianness probe: try LE, retry BE if `vertexType` comes out insane.
- **NXG delta identification:** byte-diff LSW3 `_NXG.GSC` against mortar-eng LSW1 struct dump — every non-zero bit in the trailing `unk` region is a lead.

### M3 — Level viewer (glTF output, Blender add-on later) (1 week after M2)

- Emit per-instance scene graph to glTF (static geometry only).
- Open in Blender / gltf.report for visual verification.
- Add textures once DDS extraction + material resolution lands.

### M4 — PyQt6 + OpenGL editor shell (2-3 weeks)

- Scene outliner, inspector panel, 3D viewport with picking + translate/rotate/scale gizmos.
- Edit instance transforms, delete, duplicate. No new primitives yet.
- Serialize edited scene back to GSC (first working repack is the milestone).

### M5 — Character porter cross-game (parallel with M4, 1-2 weeks after M2)

- Load GHG from sibling NXG-tier game (Batman 2 / Pirates / HP5-7).
- Verify / remap skeleton compatibility.
- Inject target character into LSW3 chars bundle.
- Validate in-game.

### M6 — Full constructor (open-ended)

- Create levels from scratch: terrain blocks, mesh placement from library, trigger wiring, spawns.
- Scripting GUI for common mission events (die-respawn, stud rewards, cutscene stubs).
- Play-test loop: autolaunch game with the WIP level loaded.

### M7 — GSC script bytecode decompiler (months, maybe never)

- Only needed if M6 scripting GUI can't cover a given use case.
- No opcode table published anywhere — real cold RE.

## Out of scope

- Pirated game assets or DRM bypass (LSW3 PC DRM is already defeated by community — we target a working install)
- Cross-port from non-NXG titles (LSW:TCS older engine; Skywalker Saga NTT newer — different rigs, out of scope)
- Oodle-compressed titles (LSW3 doesn't use Oodle; that's Skywalker Saga only)

## Reality checks

- **Repack is the real wall.** Extract/view is plumbing. Writing a `.CC4` LSW3 accepts is where this stops being a weekend and starts being a project.
- **GSC script VM is a trap.** For a data-only constructor, we reuse existing compiled scripts and edit the data side. Don't let scope creep.
- **mortar-eng's LSW1 structs will not be byte-exact for LSW3.** NXG tier added fields in the trailing unk region. Expect to fix during M2.
- **Archived-tool problem is real.** NuXtractor, TTGamesPatcher, DATOneArchiver — all last touched 2021-2022 or archived. Live work is on the TTGames LEGO Modding Discord.
