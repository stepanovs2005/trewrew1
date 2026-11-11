"""GAME.DAT archive — top-level container for all LSW3 assets.

STATUS: format details pending research. This module exposes the stable
interface the rest of the pipeline consumes; implementation will be
filled once the byte layout is confirmed against a real GAME.DAT.

Known from community (XeNTaX, ZenHAX — to verify against a sample):
- File starts with a small header + table of contents
- Entries are optionally compressed (LZ-family); encrypted in some TT titles
- Filenames may be stored as hashes rather than plain text

Public API (keep stable):
    arc = GameDat.open(path)           # memory-maps the file
    for entry in arc.entries:          # Entry objects
        data = arc.read(entry)         # decompressed bytes
    arc.write(out_path, new_entries)   # repack
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator
import mmap

from ..core.binary import BinaryReader


@dataclass
class Entry:
    name: str              # plaintext filename if known, else hex of hash
    name_hash: int         # 32-bit hash (algo TBD once sampled)
    offset: int            # absolute offset into GAME.DAT
    comp_size: int         # compressed/stored size
    uncomp_size: int       # size after decompression (== comp_size if stored)
    flags: int = 0         # compression kind, encryption, etc.

    @property
    def is_compressed(self) -> bool:
        return self.comp_size != self.uncomp_size


@dataclass
class GameDat:
    path: Path
    entries: list[Entry] = field(default_factory=list)
    endian_little: bool = True
    _mm: mmap.mmap | None = None

    @classmethod
    def open(cls, path: str | Path) -> 'GameDat':
        path = Path(path)
        f = open(path, 'rb')
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        arc = cls(path=path, _mm=mm)
        arc._parse_header()
        return arc

    def _parse_header(self) -> None:
        """Parse header + TOC. IMPLEMENTATION PENDING sample inspection.

        Scaffolding sketch (to be replaced with real logic):
            r = BinaryReader(self._mm)
            magic = r.read(4)                    # expected 4-byte signature
            version = r.u32()
            entry_count = r.u32()
            toc_offset = r.u32()
            r.seek(toc_offset)
            for _ in range(entry_count):
                # read per-entry record: hash, offset, size, size_u, flags
                ...
        """
        raise NotImplementedError('GameDat header parser not yet implemented — '
                                  'waiting on confirmed format from research + sample file')

    def read(self, entry: Entry) -> bytes:
        """Return decompressed bytes for `entry`."""
        if self._mm is None:
            raise RuntimeError('archive not open')
        raw = bytes(self._mm[entry.offset:entry.offset + entry.comp_size])
        if entry.is_compressed:
            return self._decompress(raw, entry)
        return raw

    def _decompress(self, raw: bytes, entry: Entry) -> bytes:
        """Dispatch on entry.flags once compression scheme is confirmed."""
        raise NotImplementedError('decompression kind not yet mapped')

    def extract_all(self, out_dir: Path) -> None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for e in self.entries:
            data = self.read(e)
            (out_dir / e.name).write_bytes(data)

    def close(self) -> None:
        if self._mm is not None:
            self._mm.close()
            self._mm = None

    def __enter__(self) -> 'GameDat':
        return self

    def __exit__(self, *_exc) -> None:
        self.close()


def write_archive(path: Path, entries: list[tuple[str, bytes]]) -> None:
    """Pack a list of (name, data) tuples into a GAME.DAT-compatible archive.

    IMPLEMENTATION PENDING. Will mirror the parser once the format is pinned.
    """
    raise NotImplementedError('repacker pending header format confirmation')
