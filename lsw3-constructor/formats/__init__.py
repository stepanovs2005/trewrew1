"""Per-format codecs.

Each submodule owns one on-disk format. Codecs expose `parse(buf) -> Model` and
`serialize(model) -> bytes`. Internal structure is dataclasses, not dicts —
dumb containers that the parser fills and the serializer reads.

Currently known formats to implement (ordered by priority):
- game_dat     — top-level archive (M1)
- nup          — asset bundle inside archive (M2)
- nut / nu2    — textures (M2)
- model        — character/prop mesh + skeleton (M2)
- anim         — animation tracks (M3)
- level        — level data: static instances, triggers, spawns (M4)
- gsc          — script bytecode (M5-M7)

Until research lands the exact byte layouts, these are stubs with the right
module names and function signatures — import paths won't change once filled.
"""
