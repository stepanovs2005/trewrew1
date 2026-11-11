"""FNV-1a hash variants used by Traveller's Tales DAT TOCs.

Two flavors observed in Aluigi's `ttgames.bms`:

- TT-specific 32-bit: offset basis 0x811C9DC5 (standard), prime **0x199933** (NON-standard —
  standard FNV-1a prime is 0x01000193). Used in older/smaller archives.

- Standard 64-bit FNV-1a: offset basis 0xCBF29CE484222325, prime 1099511628211. Used in
  the large LSW3 / Batman 2 / HP5-7 archives, hence the need for `quickbms_4gb_files.exe`.

Names are hashed as lowercase, backslash-separated paths. Behavior around case/encoding
needs verification against real TOC entries once we have a sample.
"""
from __future__ import annotations


TT_FNV32_OFFSET = 0x811C9DC5
TT_FNV32_PRIME  = 0x199933            # TT-specific; NOT standard FNV-1a

FNV64_OFFSET    = 0xCBF29CE484222325
FNV64_PRIME     = 1099511628211

_U32 = 0xFFFFFFFF
_U64 = 0xFFFFFFFFFFFFFFFF


def tt_fnv1a_32(name: str) -> int:
    """FNV-1a with TT's non-standard 32-bit prime 0x199933."""
    buf = name.replace('/', '\\').lower().encode('utf-8')
    h = TT_FNV32_OFFSET
    for b in buf:
        h = ((h ^ b) * TT_FNV32_PRIME) & _U32
    return h


def fnv1a_64(name: str) -> int:
    """Standard 64-bit FNV-1a."""
    buf = name.replace('/', '\\').lower().encode('utf-8')
    h = FNV64_OFFSET
    for b in buf:
        h = ((h ^ b) * FNV64_PRIME) & _U64
    return h


def hash_name(name: str, bits: int) -> int:
    if bits == 32:
        return tt_fnv1a_32(name)
    if bits == 64:
        return fnv1a_64(name)
    raise ValueError(f'unsupported hash width: {bits}')
