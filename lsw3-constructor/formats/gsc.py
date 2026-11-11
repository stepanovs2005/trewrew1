"""GSC / GHG (NXG-tier) container for LSW3.

LSW3 per-level folders contain:
    <name>.GSC         — classic-tier (geometry/model) container
    <name>_NXG.GSC     — NXG variant, the live one on PC/PS3/X360
    <name>_LR.GSC      — low-res / Wii fallback
    <name>.GIZ         — paired with GSC, undocumented
    <name>.TXT         — plain-text level driver

GHG is the rigged-character/vehicle sub-variant of GSC. Same container shape; payload
differs (adds skeleton, skinning).

Internal layout (per mortar-eng reading of LSW1 NUP/HGP, seed for LSW3):

    header:
        4-byte signature
        u32 section-offset table of fixed length
        every internal reference is relative to BODY_OFFSET
            NUP (level):       BODY_OFFSET = 0x40
            HGP (character):   BODY_OFFSET = 0x30

NXG delta from LSW1: mortar-eng trails 106 u32 of `unk` in NUPModelHeader. LSW3 almost
certainly repurposed that region. Byte-diff an LSW3 level against an LSW1 scene to find
new fields. Endianness: NXG PC payloads reported big-endian — HSEM reads as MESH if read
little-endian. Confirm from a real sample on day one.

Inside the container, geometry/texture chunks are NU20-based (not the DAT format itself,
not to be confused). Tags observed in the family: NU20, DISP, MESH/HSEM, NTBL.

Vertex layouts (keyed by u32 vertexType in the mesh header):
    0x59 — 36-byte static  : POS vec3 / NORMAL vec3 / COLOR d3dcolor / UV vec2
    0x5D — 56-byte skinned : POS / BW vec2 / BI vec3 / NORMAL / COLOR / UV at 0x30

Indices: u16 triangle strips. Bone palette per draw ≤ 16.

Materials: 2-word flags (alpha = flags & 0xF, lit = (flags & 0x30000) != 2), 3-f32 RGB,
i16 texture index (0x8000 bit = atlas marker), u8 effectType. No PBR, no normal maps in
this generation.

Textures: inlined DDS blobs in the container's texture block. Pirates moved some textures
to external .tex; LSW3 reporters failed to find external textures, so embedded is the
working assumption until confirmed.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum


BODY_OFFSET_NUP = 0x40
BODY_OFFSET_HGP = 0x30


class VertexType(IntEnum):
    STATIC_36  = 0x59
    SKINNED_56 = 0x5D


@dataclass
class SectionOffsets:
    """Offset table at the top of the container. Field names from mortar-eng NUPHeader.

    All offsets are relative to BODY_OFFSET of the container type.
    """
    strings:         int = 0
    texture_header:  int = 0
    material_header: int = 0
    vertex_header:   int = 0
    model_header:    int = 0
    instances:       int = 0


@dataclass
class ModelHeader:
    """NUPModelHeader. Seed from mortar-eng LSW1 — NXG delta pending."""
    num_materials:          int = 0
    num_mesh_blocks:        int = 0
    mesh_header_list_off:   int = 0
    num_instances:          int = 0
    num_special_objects:    int = 0   # spawns / triggers / lights candidate region
    num_splines:            int = 0
    splines_off:            int = 0
    # NXG delta lives in a trailing unk region (106 u32 in LSW1) — repurposed in NXG tier


@dataclass
class Instance:
    transform:    bytes = b''   # 16 f32, 64 bytes, column-major
    mesh_idx:     int = 0
    matrix_off:   int = 0       # optional indirection to a shared/animated transform
    extra:        int = 0


@dataclass
class Mesh:
    vertex_type:  int = 0
    vertex_count: int = 0
    vertex_blob:  bytes = b''
    index_blob:   bytes = b''   # u16 triangle strip indices
    material_idx: int = -1
    skin_matrix_indices: list[int] = field(default_factory=list)  # ≤ 16 u16


@dataclass
class Material:
    flags:        int = 0
    more_flags:   int = 0
    rgb:          tuple[float, float, float] = (1.0, 1.0, 1.0)
    texture_idx:  int = -1       # high bit 0x8000 = atlas marker
    effect_type:  int = 0

    @property
    def alpha_blend(self) -> bool:
        return (self.flags & 0xF) != 0

    @property
    def dynamically_lit(self) -> bool:
        return (self.flags & 0x30000) != 2


@dataclass
class Scene:
    """Decoded container. Populated by `parse()`, consumed by writers (glTF/Blender)."""
    body_offset:   int
    section:       SectionOffsets = field(default_factory=SectionOffsets)
    model:         ModelHeader = field(default_factory=ModelHeader)
    materials:     list[Material] = field(default_factory=list)
    meshes:        list[Mesh] = field(default_factory=list)
    instances:     list[Instance] = field(default_factory=list)
    textures_dds:  list[bytes] = field(default_factory=list)
    endian_big:    bool = False
    nxg:           bool = False


def parse(buf: bytes, is_ghg: bool = False) -> Scene:
    """Parse a GSC or GHG container.

    IMPLEMENTATION PENDING a real sample. The section-offset table layout is known from
    mortar-eng; NXG field layout under the trailing unk region is not.

    First working version will:
      1. Detect endianness by probing vertexType plausibility on the first mesh
      2. Read SectionOffsets
      3. Walk model header → instances → meshes → materials → textures
      4. Return a Scene regardless of partial failure (carry errors as warnings)
    """
    raise NotImplementedError('GSC/GHG parser pending real sample')


def serialize(scene: Scene, is_ghg: bool = False) -> bytes:
    """Write a Scene back to GSC/GHG bytes. Deferred past the viewer milestone."""
    raise NotImplementedError('GSC/GHG serializer deferred to M5')
