#!/usr/bin/env python3
"""Minimal `.HDR` probe — reads magic and the first fixed-offset table, no parsing of
TOC bodies yet. Useful as a first sanity check on any TT Games archive sample before
investing in the full parser.

Usage:
    python tools/hdr_probe.py path/to/game.hdr [--endian le|be]
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


MAGIC_CC4 = b'.CC4'
MAGIC_LZMA_WRAP = b'CMP2CMP2CMP2CMP2'


def hexdump(data: bytes, offset: int = 0, width: int = 16, limit: int | None = 256) -> None:
    end = min(len(data), limit) if limit is not None else len(data)
    for i in range(0, end, width):
        chunk = data[i:i + width]
        hx = ' '.join(f'{b:02x}' for b in chunk)
        asc = ''.join((chr(b) if 32 <= b < 127 else '.') for b in chunk)
        print(f'{offset + i:08x}  {hx:<{width * 3}}  {asc}')


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('hdr', type=Path)
    ap.add_argument('--endian', choices=('le', 'be'), default='le')
    ap.add_argument('--dump', type=int, default=256, help='bytes to hexdump at head')
    args = ap.parse_args(argv)

    if not args.hdr.exists():
        print(f'not found: {args.hdr}', file=sys.stderr)
        return 2

    with open(args.hdr, 'rb') as f:
        head = f.read(4096)

    print(f'file     : {args.hdr}  ({args.hdr.stat().st_size:,} bytes)')
    print(f'magic    : {head[:4]!r}')
    if head[:16] == MAGIC_LZMA_WRAP:
        print('-> CMP2-wrapped header (LZMA preamble present — decompress before further parsing)')
        return 0
    if head[:4] not in (MAGIC_CC4, b'TAD0', b'DAT0'):
        print(f'-> unrecognized magic. First 64 bytes:')
        hexdump(head[:64])
        return 1

    import struct
    fmt = ('<' if args.endian == 'le' else '>') + 'I'
    print(f'endian   : {args.endian}')
    print(f'u32 @ 0x04 : 0x{struct.unpack(fmt, head[4:8])[0]:08x}')
    print(f'u32 @ 0x08 : 0x{struct.unpack(fmt, head[8:12])[0]:08x}')
    print(f'u32 @ 0x0c : 0x{struct.unpack(fmt, head[12:16])[0]:08x}')
    print(f'u32 @ 0x10 : 0x{struct.unpack(fmt, head[16:20])[0]:08x}')
    print(f'u32 @ 0x14 : 0x{struct.unpack(fmt, head[20:24])[0]:08x}')
    print(f'u32 @ 0x18 : 0x{struct.unpack(fmt, head[24:28])[0]:08x}')
    print(f'u32 @ 0x1c : 0x{struct.unpack(fmt, head[28:32])[0]:08x}')
    print()
    print(f'head dump ({args.dump} bytes):')
    hexdump(head, limit=args.dump)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
