# Roadmap

Honest scope. No promises past what the state of community research allows.

## Dependencies on user

Nothing of substance can be coded without:
1. A legit copy of `GAME.DAT` from the user's LSW3 install (`...\LEGO Star Wars III\GAME.DAT`)
2. Access to sibling games for cross-port (`...\LEGO Batman 2\GAME.DAT`, `...\LEGO Pirates of the Caribbean\GAME.DAT`, `...\LEGO Harry Potter Years 5-7\GAME.DAT`)
3. Willingness to test builds on a Windows machine (or Wine on macOS)

Without (1), progress stops at the first milestone.

## Milestones

### M1 — Archive IO (days)
- Parse GAME.DAT header + TOC
- Enumerate entries, dump raw blobs to disk
- Repack entries into a loadable GAME.DAT
- Round-trip test: extract + repack = byte-identical (or game-loadable if not bit-exact)

**Blocker:** real GAME.DAT needed. Community format notes (XeNTaX/ZenHAX) will seed the parser.

### M2 — Asset bundles (.nup) (1-2 weeks)
- Identify sub-blob types inside .nup (model, texture, anim, script)
- Decode texture formats (DXT variants, swizzled console textures?)
- Decode mesh geometry (vertex streams, indices, skeleton bindings)
- Blender exporter for inspection

### M3 — Character porter (1 week after M2)
- Load character .nup from LSW3
- Load character .nup from sibling NuGame game
- Match/remap skeleton if compatible; refuse if incompatible with clear diagnostic
- Inject target character into LSW3's character bundle
- Test: character appears in-game with working animations

### M4 — Level reader (2-3 weeks)
- Decode level .nup: static mesh instances, props, spawns, lights, triggers
- Load level into read-only 3D viewport
- Click → inspect entity properties

### M5 — Level writer + GSC passthrough (2-3 weeks)
- Serialize edited scene back to .nup
- Preserve/edit mission script (.gsc) — initial pass is passthrough (keep game logic intact), later pass adds opcode-level editing
- In-game load test: a vanilla level re-encoded by our tool must be indistinguishable from the original

### M6 — Full level constructor (open-ended)
- New level from scratch: terrain brush, mesh placement, trigger wiring, spawn setup
- Scripting GUI for common mission events (die-respawn, stud reward, cutscene stub)
- Playtest loop: launch LSW3, auto-load the WIP level

### M7 — GSC decompiler/recompiler (months, maybe never complete)
- Disassemble opcodes → readable listing
- Recompile edited listing
- Required only if M6 scripting GUI isn't enough

## What we won't ship

- Pirated game assets
- A tool that bypasses DRM (LSW3 PC has SafeDisc, mostly bypassed by community already; our tooling targets a working install)
- Cross-port of characters from NON-NuGame games (different era rigs, out of scope)

## Current blocker

Waiting on research findings and user's `GAME.DAT`.
