#!/usr/bin/env bash
# bash 4+ — collects everything needed for M1 from a LEGO Star Wars III install.
#
# Usage:  ./probe_install.sh "/path/to/LEGO Star Wars III" [out_dir]
#
# Writes <out_dir>/lsw3_probe.txt  (file listing + first 4 KiB of every HDR/DAT, base64)
# and    <out_dir>/lsw3_probe.tar.gz (the txt + every .HDR whole + the game exe).
# DAT bodies are never copied — only their first 4 KiB.
set -euo pipefail

game_dir="${1:?usage: $0 <game_dir> [out_dir]}"
out_dir="${2:-$PWD}"
head_bytes=4096

[ -d "$game_dir" ] || { echo "not a directory: $game_dir" >&2; exit 1; }
mkdir -p "$out_dir"
out_dir="$(cd "$out_dir" && pwd)"
report="$out_dir/lsw3_probe.txt"
bundle="$out_dir/lsw3_probe.tar.gz"

cd "$game_dir"

{
    echo "### listing (size  path)"
    find . -maxdepth 2 -type f -printf '%12s  %p\n' | sort -k2
    echo
    echo "### sha256 of executables"
    find . -maxdepth 1 -type f -iname '*.exe' -exec sha256sum {} +
    echo
    find . -maxdepth 1 -type f \( -iname '*.hdr' -o -iname '*.dat' \) -print0 | sort -z |
    while IFS= read -r -d '' f; do
        echo "=== $f  size=$(stat -c %s "$f")"
        head -c "$head_bytes" "$f" | base64 -w 76
        echo
    done
} > "$report"

mapfile -d '' whole < <(find . -maxdepth 1 -type f \( -iname '*.hdr' -o -iname '*.exe' \) -print0)
tar -czf "$bundle" -C "$out_dir" lsw3_probe.txt -C "$game_dir" "${whole[@]}"

echo "report: $report"
echo "bundle: $bundle ($(du -h "$bundle" | cut -f1))"
