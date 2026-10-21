#!/bin/bash
# mirror.sh — copy the editions listed in MIRROR.tsv from ~/danish-texts into
# this repo (see the header of MIRROR.tsv). Run as `make mirror`.
#
# For each row it copies <name>.tex and <name>.pdf with cp -p, so the copies
# keep the source's timestamps and `make` here does not rebuild a PDF that
# danish-texts has already built. Files are copied only when they differ.
# A missing source file stops the run: fix MIRROR.tsv or danish-texts first.
set -euo pipefail
cd "$(dirname "$0")"
SRC="${DANISH_TEXTS:-$HOME/danish-texts}/texts"
[ -d "$SRC" ] || { echo "mirror.sh: no $SRC (set DANISH_TEXTS)"; exit 1; }
n=0
grep -v '^#' MIRROR.tsv | grep -v '^[[:space:]]*$' | while IFS=$'\t' read -r from to files; do
  mkdir -p "texts/$to"
  for f in $files; do
    for ext in tex pdf; do
      s="$SRC/$from/$f.$ext"; d="texts/$to/$f.$ext"
      [ -f "$s" ] || { echo "mirror.sh: missing $s"; exit 1; }
      if ! cmp -s "$s" "$d" 2>/dev/null; then
        cp -p "$s" "$d"; echo "  mirrored $from/$f.$ext -> $d"
      fi
    done
  done
done
echo "mirror: up to date with $SRC"
