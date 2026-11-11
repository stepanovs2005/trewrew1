"""TT Games 2011-2012 archive — header/payload split (`.HDR` + `.DAT`).

Format source: Luigi Auriemma's `ttgames.bms` (linterniGamer mirror), cross-referenced
against DATOneArchiver (LSW1/LSW2 only), with LSW3 specifics still to be confirmed from
a live sample.

Layout recap:
    game.hdr   — magic `.CC4` (0x3443432E LE), header fields, name blob, file table,
                 FNV-1a hash table (32-bit TT or standard 64-bit)
    game.dat   — raw payload, each entry at `offset` carries `comp_size` bytes, optionally
                 wrapped in a per-chunk compression (LZ2K / DFLT / Defl / RFPK / RNC_)

`CMP2CMP2CMP2CMP2` prefix on the header means the TOC itself is LZMA-compressed under a
16-byte hash + u64 uncompressed size — decompress before parsing. Unlikely for LSW3 but
cheap to probe.

Current status: parser skeleton — field widths and record order to be confirmed from a
sample; the public surface (`open`, `entries`, `read`, `extract_all`) stays stable.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import mmap
import struct

from ..core.binary import BinaryReader
from ..core.fnv import tt_fnv1a_32, fnv1a_64


MAGIC_CC4 = b'.CC4'
MAGIC_LZMA_WRAP = b'CMP2CMP2CMP2CMP2'


@dataclass
class Entry:
    name: str                 # resolved via name blob, else hex of hash
    name_hash: int            # FNV-1a (32 TT-prime, or 64 standard)
    offset: int               # absolute offset into companion .DAT
    comp_size: int            # stored size on disk
    uncomp_size: int          # size after decompression
    packed: int = 0           # per-chunk compression flag
    extra: int = 0            # high bits of offset / flags, format-specific

    @property
    def is_compressed(self) -> bool:
        return self.packed != 0 or self.comp_size != self.uncomp_size


@dataclass
class GameDat:
    hdr_path: Path
    dat_path: Path
    entries: list[Entry] = field(default_factory=list)
    hash_bits: int = 64
    endian_little: bool = True
    _hdr_mm: mmap.mmap | None = None
    _dat_mm: mmap.mmap | None = None

    @classmethod
    def open(cls, hdr_path: str | Path, dat_path: str | Path | None = None) -> 'GameDat':
        hdr_path = Path(hdr_path)
        if dat_path is None:
            # convention: foo.hdr paired with foo.dat
            dat_path = hdr_path.with_suffix('.dat')
            if not dat_path.exists():
                dat_path = hdr_path.with_suffix('.DAT')
        dat_path = Path(dat_path)
        if not dat_path.exists():
            raise FileNotFoundError(f'payload not found alongside {hdr_path}: expected {dat_path}')

        hdr_f = open(hdr_path, 'rb')
        dat_f = open(dat_path, 'rb')
        hdr_mm = mmap.mmap(hdr_f.fileno(), 0, access=mmap.ACCESS_READ)
        dat_mm = mmap.mmap(dat_f.fileno(), 0, access=mmap.ACCESS_READ)
        arc = cls(hdr_path=hdr_path, dat_path=dat_path, _hdr_mm=hdr_mm, _dat_mm=dat_mm)
        arc._parse_header()
        return arc

    def _probe_header_magic(self, r: BinaryReader) -> None:
        """Read the first bytes and sanity-check against known magics."""
        first = r.read(4)
        if first == MAGIC_CC4:
            return
        if first == b'TAD0' or first == b'DAT0':
            # single-file variant seen in newer TT titles (NOT typical for LSW3)
            return
        # possible outer LZMA wrap
        r.seek(0)
        prefix = r.read(16)
        if prefix == MAGIC_LZMA_WRAP:
            raise NotImplementedError('CMP2-wrapped header — LZMA preamble not yet handled')
        raise ValueError(f'unknown header magic: {first!r}')

    def _parse_header(self) -> None:
        """Parse `.HDR` layout. IMPLEMENTATION IN PROGRESS.

        Reference per aluigi script (older .hdr+.dat flavor):
            INFO_OFF -> info table of 16-byte records { offset, comp_size, uncomp_size,
                                                        packed + extra offset bits }
            NAME_OFF -> name table (8- or 12-byte records: next/prev links, name_offset,
                                     optional extra)
            CRC_OFF  -> name->file hash table (32 or 64 bits wide)
            NAMES_OFF -> flat null-terminated string blob

        Exact widths and the order of these top-level offsets must be read from a live
        sample. Entries whose first name byte >= 0xF0 are invalid/skipped.
        """
        assert self._hdr_mm is not None
        r = BinaryReader(self._hdr_mm, little=self.endian_little)
        self._probe_header_magic(r)

        # TODO: after confirming field order on a real sample, populate self.entries
        raise NotImplementedError(
            'HDR body parser pending a real `.HDR` sample. '
            'The script lays out: header size, type tag, version, file count, name count, '
            'name-table size — but widths differ per title. Extract once with '
            '`quickbms_4gb_files.exe ttgames.bms game.hdr out/` to produce a reference '
            'file list, then we lock in offsets here.'
        )

    def _decompress(self, raw: bytes, entry: Entry) -> bytes:
        """Dispatch on per-chunk compression tag.

        Each compressed payload begins with a 4-char codec code. Known from the script:
            b'LZ2K' / b'DFLT' / b'Defl' / b'RFPK' / b'RNC_'
        plus the untested b'ZIPX' branch with RC4 which does not fire on retail builds.

        Implementation note: `Defl` ships a 0x24-byte local header followed by raw deflate;
        `DFLT` and `LZ2K` are chunked with a size table — `DFLT`'s sizes are reversed vs
        `LZ2K`'s.
        """
        tag = raw[:4]
        if tag == b'DFLT':
            raise NotImplementedError('DFLT chunked deflate reader pending')
        if tag == b'LZ2K':
            raise NotImplementedError('LZ2K reader pending (TT-specific LZ)')
        if tag == b'Defl':
            # Deflate_v1.0 — 0x24-byte header then raw deflate
            import zlib
            return zlib.decompress(raw[0x24:], wbits=-15)
        if tag == b'RFPK':
            raise NotImplementedError('RFPK reader pending')
        if tag == b'RNC_':
            raise NotImplementedError('RNC_ reader pending (Rob Northen Compression)')
        if tag == b'ZIPX':
            raise NotImplementedError('ZIPX+RC4 branch — untested on retail, not expected here')
        raise ValueError(f'unknown per-chunk codec tag: {tag!r}')

    def read(self, entry: Entry) -> bytes:
        if self._dat_mm is None:
            raise RuntimeError('archive not open')
        raw = bytes(self._dat_mm[entry.offset:entry.offset + entry.comp_size])
        if entry.is_compressed:
            return self._decompress(raw, entry)
        return raw

    def extract_all(self, out_dir: Path) -> None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for e in self.entries:
            data = self.read(e)
            target = out_dir / e.name.replace('\\', '/')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    def close(self) -> None:
        for mm in (self._hdr_mm, self._dat_mm):
            if mm is not None:
                mm.close()
        self._hdr_mm = None
        self._dat_mm = None

    def __enter__(self) -> 'GameDat':
        return self

    def __exit__(self, *_exc) -> None:
        self.close()


def write_archive(hdr_path: Path, dat_path: Path, entries: list[tuple[str, bytes]], hash_bits: int = 64) -> None:
    """Pack a list of (name, data) into a `.HDR` + `.DAT` pair.

    IMPLEMENTATION PENDING. First working version will emit a `.CC4` header with all
    entries stored uncompressed (packed=0) and FNV-1a hashes at the given width; once the
    game loads that, we add Deflate (`Defl` variant — the simplest supported codec) for
    size.

    No LSW3 repacker exists in the community; this is the first-wall milestone.
    """
    raise NotImplementedError('repacker pending — this is the main M1 deliverable')
