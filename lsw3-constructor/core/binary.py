"""Binary reader/writer primitives. Endian-flexible, offset-based.

NuGame assets on PC are little-endian; console builds may differ.
"""
from __future__ import annotations
import struct
from dataclasses import dataclass


class BinaryReader:
    __slots__ = ('buf', 'pos', 'little')

    def __init__(self, buf: bytes | bytearray | memoryview, little: bool = True):
        self.buf = memoryview(buf)
        self.pos = 0
        self.little = little

    @property
    def end(self) -> int:
        return len(self.buf)

    @property
    def rem(self) -> int:
        return len(self.buf) - self.pos

    def seek(self, pos: int) -> None:
        if pos < 0 or pos > len(self.buf):
            raise ValueError(f'seek out of range: {pos} / {len(self.buf)}')
        self.pos = pos

    def skip(self, n: int) -> None:
        self.seek(self.pos + n)

    def read(self, n: int) -> bytes:
        if self.pos + n > len(self.buf):
            raise EOFError(f'short read: want {n} have {self.rem} @ {self.pos:#x}')
        out = bytes(self.buf[self.pos:self.pos + n])
        self.pos += n
        return out

    def _unpack(self, fmt: str, n: int):
        return struct.unpack(('<' if self.little else '>') + fmt, self.read(n))[0]

    def u8(self) -> int: return self._unpack('B', 1)
    def i8(self) -> int: return self._unpack('b', 1)
    def u16(self) -> int: return self._unpack('H', 2)
    def i16(self) -> int: return self._unpack('h', 2)
    def u32(self) -> int: return self._unpack('I', 4)
    def i32(self) -> int: return self._unpack('i', 4)
    def u64(self) -> int: return self._unpack('Q', 8)
    def f32(self) -> float: return self._unpack('f', 4)
    def f64(self) -> float: return self._unpack('d', 8)

    def cstring(self, max_len: int = 256) -> str:
        start = self.pos
        for i in range(max_len):
            if self.pos >= len(self.buf):
                break
            if self.buf[self.pos] == 0:
                s = bytes(self.buf[start:self.pos]).decode('utf-8', errors='replace')
                self.pos += 1
                return s
            self.pos += 1
        raise ValueError(f'cstring not terminated within {max_len} bytes @ {start:#x}')

    def fixed_string(self, n: int) -> str:
        raw = self.read(n)
        end = raw.find(b'\x00')
        if end >= 0:
            raw = raw[:end]
        return raw.decode('utf-8', errors='replace')

    def align(self, boundary: int) -> None:
        m = self.pos % boundary
        if m:
            self.skip(boundary - m)


class BinaryWriter:
    __slots__ = ('buf', 'little')

    def __init__(self, little: bool = True):
        self.buf = bytearray()
        self.little = little

    def _pack(self, fmt: str, value) -> None:
        self.buf += struct.pack(('<' if self.little else '>') + fmt, value)

    def u8(self, v: int) -> None: self._pack('B', v)
    def u16(self, v: int) -> None: self._pack('H', v)
    def u32(self, v: int) -> None: self._pack('I', v)
    def u64(self, v: int) -> None: self._pack('Q', v)
    def i32(self, v: int) -> None: self._pack('i', v)
    def f32(self, v: float) -> None: self._pack('f', v)

    def raw(self, data: bytes) -> None:
        self.buf += data

    def cstring(self, s: str) -> None:
        self.buf += s.encode('utf-8') + b'\x00'

    def fixed_string(self, s: str, n: int) -> None:
        enc = s.encode('utf-8')[:n]
        self.buf += enc + b'\x00' * (n - len(enc))

    def align(self, boundary: int, pad: int = 0) -> None:
        m = len(self.buf) % boundary
        if m:
            self.buf += bytes([pad]) * (boundary - m)

    @property
    def pos(self) -> int:
        return len(self.buf)

    def patch_u32(self, offset: int, value: int) -> None:
        struct.pack_into('<I' if self.little else '>I', self.buf, offset, value)

    def bytes(self) -> bytes:
        return bytes(self.buf)


@dataclass
class Span:
    """A (offset, size) reference into a parent buffer. Useful for lazy decoding."""
    offset: int
    size: int

    @property
    def end(self) -> int:
        return self.offset + self.size

    def reader(self, parent: BinaryReader) -> BinaryReader:
        return BinaryReader(parent.buf[self.offset:self.end], little=parent.little)
