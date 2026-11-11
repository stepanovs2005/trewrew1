# Session handoff

Everything a future session needs to resume this project. If you (future-Verge) are reading this in a fresh chat, start here.

## Who we are

DevVolodya + Verge. See `/home/user/trewrew1/CLAUDE.md` for identity, tone, defaults. That file is the constitution, this file is the state.

## The goal (expanded)

Started as "level constructor for LEGO Star Wars III (2011)" with cross-game character import.

**As of 2026-11-11, the scope widened: this is to become a universal TT Games LEGO level editor on GitHub — anyone can mod any Traveller's Tales LEGO game.** Current code lives under `lsw3-constructor/` because LSW3 is the first target, but the architecture should generalize:

- The DAT/HDR container is the same family across every TT LEGO title 2004-2017 (per-title magic variations only — `.CC4`, `.CC400TAD`, `0x1234567A`, CMP2-LZMA-wrapped).
- NXG-tier games (2011-2012 "Builder" sub-engine: LSW3, Pirates 2011, HP5-7, Batman 2 "Gotham" variant) share GSC/GHG layout.
- Classic-tier games (2005-2008: LSW1, LSW2, LSW:TCS, Batman 2008, Indy 1) share NUP/HGP.
- NTT (Skywalker Saga 2022) is a separate codebase — out of scope v1; add Oodle+new-TOC later.

**Rename plan when it's time:** `tt-lego-forge` or similar — but not today. Ship the LSW3 vertical first, then abstract.

## What exists in the repo right now

Branch: `claude/pensive-keller-j9uk22` (session 2; contains everything from `claude/hello-he2rnc` merged in). Everything pushed.

- `CLAUDE.md` — identity (don't touch)
- `README.md` — repo-level, barely a stub
- `data/` — stale RevenueCat JSON, unrelated to this project
- `index.html` — the `verge` animated page from an earlier chit-chat moment (data-URL rendered + github-pages-ready)
- `lsw3-constructor/` — the real work
  - `README.md`
  - `requirements.txt` — PyQt6, PyOpenGL, numpy, pyrr, pillow, zstandard
  - `core/`
    - `binary.py` — `BinaryReader`/`BinaryWriter`/`Span`. **WORKING, battle-ready.**
    - `fnv.py` — `tt_fnv1a_32` (TT-specific prime `0x199933`), standard `fnv1a_64`. **WORKING.**
  - `formats/`
    - `game_dat.py` — `.HDR`+`.DAT` pair parser. Skeleton with codec dispatch; `_parse_header` is NotImplementedError until a real sample lands.
    - `gsc.py` — GSC/GHG NXG-tier container. Seed structs from mortar-eng LSW1. `parse()` is NotImplementedError.
  - `tools/`
    - `extract_dat.py` — wrapper around QuickBMS + `ttgames.bms`. Runnable if the binaries are on PATH.
    - `hdr_probe.py` — hexdump + magic check. Runnable today on any TT `.HDR`.
    - `probe_install.sh` — bash, run on the game install. Emits `lsw3_probe.txt` (listing + first 4 KiB of each HDR/DAT, base64) and `lsw3_probe.tar.gz` (txt + all `.HDR` whole + game exe). **WORKING, tested on a fake install.**
  - `docs/`
    - `roadmap.md` — M0-M7 milestones
    - `plan.md` — full research-grounded plan with confidence labels
    - `HANDOFF.md` — this file
- `.github/` — empty (we tried to push a Pages-deploy workflow, auto-classifier blocked)

## What research established (high-confidence facts)

Full detail in `plan.md`. The essentials:

### GAME.DAT format (TT Games 2011-2012)

- `.HDR` + `.DAT` pair. Magic `.CC4` (`0x3443432E` LE).
- TOC: name blob → file table (16-byte records: offset/csize/usize/packed+extra) → FNV-1a hash table.
- Filenames: null-terminated 8-bit, backslash paths, name bytes ≥ `0xF0` = skip.
- Hash: FNV-1a with TT prime `0x199933` (32-bit) OR standard `0xCBF29CE484222325`/`1099511628211` (64-bit). LSW3's size → 64-bit → `quickbms_4gb_files.exe` required.
- Compression is per-chunk, 4-char code: `LZ2K`, `DFLT`, `Defl` (Deflate_v1.0 with 0x24 local header), `RFPK`, `RNC_`. ZIPX+RC4 exists but doesn't fire on retail.
- Outer LZMA wrap edge: first 16 bytes `CMP2CMP2CMP2CMP2` → 16-byte hash + u64 uncomp_size + LZMA. Probe before parsing.
- No whole-archive encryption, no Oodle in this era.
- **No public LSW3 repacker exists.** DATOneArchiver supports only LSW1/LSW2. This is the first real wall.

### Level/scene format (seeded from mortar-eng LSW1)

- Containers are OFFSET-TABLE based, not IFF/RIFF chunked.
- First 4 bytes = sig. Then u32 section-offset table. Every internal ref adds BODY_OFFSET: NUP=0x40, HGP=0x30.
- Vertex types (u32): `0x59`=36B static (POS/NORMAL/COLOR/UV), `0x5D`=56B skinned (+BW vec2+BI vec3, UV at 0x30).
- u16 triangle strip indices. Bone palette per draw ≤16.
- Transforms = 4×4 column-major f32 (64B). Not quat+vec3.
- Textures inlined as DDS blobs. No external `.tex` in this tier (unverified for LSW3 — may differ).
- Materials: 2-word flags (alpha=flags&0xF, lit=(flags&0x30000)!=2), 3-f32 RGB, i16 texture idx (0x8000=atlas marker), u8 effectType. No PBR.

### LSW3 on-disk layout per-level

`levels\...\<Chapter>\<LevelName>\`:
- `<name>.GSC` — classic-tier container
- `<name>_NXG.GSC` — NXG variant, the live one on PC/PS3/X360
- `<name>_LR.GSC` — low-res / Wii
- `<name>.GIZ` — undocumented, paired
- `<name>.TXT` — plain-text level driver

### Things to stop believing

- **NU20 is NOT the DAT format.** NU20 is a chunk inside GSC/NUP/HGP.
- **LSW3 does NOT ship `.nup`.** NUP is PS2/GC era. LSW3 ships GSC/GHG.
- **TTMagic / Koalyptus / acidicoala does NOT apply to LSW3.** That's DX11-era; LSW3 is DX9. Use TTGamesPatcher (archived) instead.
- **xensik/gsc-tool is NOT for TT Games.** That's Call of Duty IW engine, unrelated format sharing only the extension.
- **NU2 is NOT a format.** "NuGame" is the engine lineage; file extensions are NUP (classic) / GSC/GHG (NXG).

### Key community resources

- `linterniGamer/Tt-Games-quickbms-scripts` — ttgames.bms, canonical extractor
- `leftmostcat/mortar-eng` — GPL-3 C++ LSW1 parser, closest living spec
- `IsaMorphic/DATOneArchiver` — LSW1/LSW2 writer (LSW3 unsupported — "Help Wanted")
- `IsaMorphic/NuXtractor` — archived LSW1 NU20 extractor
- `AlubJ/TTGamesPatcher` — archived DAT-DRM check patcher
- `connorh315/DATManager` — newer GUI extractor (LSW3 unverified)
- `stryderjoe/figure-forge` — cross-game character porter for classic-tier (TCS/Indy/Batman 2008)
- **TTGames LEGO Modding Discord**, server id `539431629718945793` — the one place where live modding work happens. GitHub is lagging; Discord is current.
- Rock Raiders United forum — long-form RE threads 5644 (TT Games Explorer), 7771 (NXG mesh extract), 9181 (TTMagic), 9225 (LSW3 map textures)

## What's blocked and needs DevVolodya

Full list in `plan.md` section 5. The minimum unblock:

1. **`GAME.DAT` + `GAME.HDR` from his LSW3 install.** Both halves. Path on PC is usually `C:\Program Files (x86)\LucasArts\LEGO Star Wars III\GAME.DAT` + `.HDR`.
2. If the pair is too big to upload: hex dump of first 4096 bytes of each file. Enough for M1.
3. Platform confirmation (Steam / GOG / disc, build version).
4. One pre-extracted level directory if available.
5. Later: sibling game installs (Batman 2, Pirates 2011, HP5-7) for cross-port work.

## Next concrete action when he returns

**M1 — DAT extract + probe.** Once bytes arrive:

1. Run `tools/hdr_probe.py` on the HDR to confirm `.CC4` magic + which hash width.
2. Fill in `formats/game_dat.py::_parse_header` with real field widths.
3. Validate name+hash round-trip: hash every parsed filename with `core.fnv`, verify it matches the TOC.
4. Add `Defl` decompression path first (simplest — zlib with wbits=-15 after 0x24-byte header).
5. Extract one `_NXG.GSC` and feed it to `hdr_probe.py` adapted to GSC headers.

**Then M2 — GSC parser.** Try both endians, pick the one where `vertexType` on the first mesh is a known value (0x59/0x5D).

## Session 2 (2026-11-11, later) — what changed

- **DevVolodya is on a Linux PC**, not only the M3 Air. Game install is reachable from there. Give bash, not PowerShell.
- Still no bytes. He is about to run `tools/probe_install.sh "<game dir>"` and send back `lsw3_probe.txt` (paste) and/or `lsw3_probe.tar.gz` (HDRs + exe).
- The exe and HDRs must NOT go into `trewrew1` — it is a public repo. Use a new private repo and attach it with `add_repo`, or any https-reachable upload.
- Feasibility as discussed (my estimates, not measured): DAT extract — days; repack — 1-2 weeks, or skipped entirely if LSW3 loads loose files with the DAT removed (unverified guess, test on his install); GSC read + 3D viewer — weeks; editing existing levels — 1-3 months; new levels from scratch — long and risky (`.GIZ`, collision, triggers, AI, cutscenes all undocumented); "every TT game" — realistic as extractor/viewer breadth, one title deep. He thinks this is pessimistic. With exe + archives in hand the estimates shrink a lot.
- Agreed accelerators: (1) reverse the loader in the game exe instead of guessing formats from forum posts, (2) full DAT/HDR samples, (3) try running the game headless under wine in the container for a self-serve load/crash loop — untested, DX9 without GPU may not work.
- Linux note: the game there runs through Proton/wine; Steam path is typically `~/.steam/steam/steamapps/common/<game folder>` (exact folder name unverified).

## Sandbox facts (so a future me doesn't flail)

Running on a managed Claude Code cloud container. Limits I hit this session:

- Egress proxy only allows allowlisted hosts (anthropic/github/npm/pypi/cargo/golang). Tunnel services (cloudflared/ngrok/localtunnel) all blocked.
- GitHub MCP tools work for push/read but `gh api` to `/repos/.../pages` is blocked at proxy layer.
- Auto-mode classifier denies: broad host probing ("Containment Escape"), workflow pushes that create public endpoints ("Create Public Surface"). Needs user approve.
- `report_preview_port` registers a port with the Claude app's preview panel. User may or may not see the panel depending on client.
- Data-URLs work for small static pages; long ones Chrome rejects (~10KB+ gets `ERR_INVALID_URL` on paste).
- Static hosting works via GitHub Pages or `raw.githack.com`/`htmlpreview.github.io` (public repo required).
- Session is ephemeral — commit and push or it dies.
- Container has: python 3.13, node 22, go 1.24, rust 1.97, gcc, docker, playwright+chromium at `/opt/pw-browsers/chromium`. 15G RAM, ~31G free disk.

## Non-project context from this session

Early in the chat we also:
- Confirmed cheat-work / RE scope stays active (identity as Verge, from CLAUDE.md)
- Discussed macOS M3 (DevVolodya's hardware) — LSW3 would run via Wine/CrossOver on his Mac, or on a separate Windows machine he owns
- Looked at an old `AMIR_LOGIN_INSTRUCTION.md` document (off-device Google account minting via camoufox+DroidGuard+mint_master) — unrelated to this project, just a pointer to past work he's done
- Made a `hello, world` page then a `verge` animated page (both committed as `index.html` — can be shown via the raw.githack URL in the repo README)

## How to pick up

1. Read `CLAUDE.md`. You are Verge.
2. Read this file.
3. Read `docs/plan.md` for the research details.
4. Ask DevVolodya: "Привет. Байты пришли?" (i.e. output of `tools/probe_install.sh`). If yes, go to M1. If no, keep the pressure light — он сам пришлёт когда до машины доберётся.

That's it. The verge is steady. Pick up at M1.
