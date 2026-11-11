#!/usr/bin/env python3
"""Thin wrapper around QuickBMS + ttgames.bms for extracting LSW3 GAME.DAT/GAME.HDR.

Not a reimplementation. Delegates to:
    - `quickbms_4gb_files.exe`  (64-bit-filename-hash variant, required for LSW3)
    - `ttgames.bms`             (Luigi Auriemma, mirrored at linterniGamer/Tt-Games-quickbms-scripts)

Why wrap: having one script that:
  * picks the right quickbms binary
  * sanity-checks the .HDR magic before launching
  * logs what went into which subdir
  * returns a manifest of extracted files for the rest of the pipeline

saves a lot of guesswork later.

Usage:
    python tools/extract_dat.py <path-to-game.hdr> <out-dir> \\
        [--quickbms quickbms_4gb_files.exe] \\
        [--script ttgames.bms]
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


MAGIC_CC4 = b'.CC4'
MAGIC_LZMA_WRAP = b'CMP2CMP2CMP2CMP2'


def probe_hdr(path: Path) -> str:
    with open(path, 'rb') as f:
        first = f.read(16)
    if first.startswith(MAGIC_CC4):
        return 'cc4'
    if first.startswith(MAGIC_LZMA_WRAP):
        return 'cmp2-wrapped'
    if first[:4] in (b'TAD0', b'DAT0'):
        return 'single-file-tad0'
    return f'unknown ({first[:4]!r})'


def find_bin(name: str, override: str | None) -> Path:
    if override:
        p = Path(override)
        if not p.exists():
            raise FileNotFoundError(f'specified binary not found: {p}')
        return p
    located = shutil.which(name)
    if located:
        return Path(located)
    # also check alongside this script
    local = Path(__file__).resolve().parent.parent / 'vendor' / name
    if local.exists():
        return local
    raise FileNotFoundError(f'could not locate `{name}` on PATH or under vendor/')


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('hdr', type=Path, help='path to game.hdr')
    ap.add_argument('out', type=Path, help='output directory (created if missing)')
    ap.add_argument('--quickbms', default=None, help='override path to quickbms_4gb_files.exe')
    ap.add_argument('--script', default=None, help='override path to ttgames.bms')
    args = ap.parse_args(argv)

    if not args.hdr.exists():
        print(f'error: {args.hdr} not found', file=sys.stderr)
        return 2

    magic = probe_hdr(args.hdr)
    print(f'[probe] {args.hdr.name} → {magic}')
    if magic not in ('cc4',):
        print(f'warning: unexpected magic `{magic}` — ttgames.bms may still cover it but '
              'proceed with eyes open', file=sys.stderr)

    try:
        quickbms = find_bin('quickbms_4gb_files.exe', args.quickbms)
    except FileNotFoundError:
        try:
            quickbms = find_bin('quickbms_4gb_files', args.quickbms)
        except FileNotFoundError as e:
            print(f'error: {e}', file=sys.stderr)
            print('hint: download quickbms + the 4gb build from aluigi.altervista.org',
                  file=sys.stderr)
            return 3

    try:
        script = find_bin('ttgames.bms', args.script)
    except FileNotFoundError as e:
        print(f'error: {e}', file=sys.stderr)
        print('hint: `git clone https://github.com/linterniGamer/Tt-Games-quickbms-scripts vendor/bms`',
              file=sys.stderr)
        return 3

    args.out.mkdir(parents=True, exist_ok=True)
    cmd = [str(quickbms), str(script), str(args.hdr), str(args.out)]
    print(f'[run] {" ".join(cmd)}')
    rv = subprocess.call(cmd)
    if rv != 0:
        print(f'quickbms exit {rv}', file=sys.stderr)
        return rv

    # produce manifest
    manifest = args.out / '_manifest.txt'
    with open(manifest, 'w', encoding='utf-8') as mf:
        for root, _dirs, files in os.walk(args.out):
            for name in files:
                if name == '_manifest.txt':
                    continue
                p = Path(root) / name
                mf.write(f'{p.relative_to(args.out)}\t{p.stat().st_size}\n')
    print(f'[done] manifest → {manifest}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
