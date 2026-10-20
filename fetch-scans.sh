#!/bin/bash
# fetch-scans.sh — regenerate the five scans from the Internet Archive.
#
# NOT run by `make`, and never needed for a build: the scans already sit in
# ~/bibliotek, and SCANS.tsv identifies each by sha256. Run this only if a scan
# is lost, or to show where one came from.
#
# Each scan is a cut, made with qpdf, from a full journal-issue PDF on archive.org.
# The cuts are written to OUTDIR (default: a fresh temporary directory), never into
# ~/bibliotek and never into this repo. A regenerated cut need not be byte-identical
# to the one in SCANS.tsv (qpdf versions differ): compare page count and page size,
# then copy it into ~/bibliotek and run `python3 scans.py rehash <paper> <path>`.
#
# Usage:  bash fetch-scans.sh [OUTDIR] [paper ...]      e.g.  bash fetch-scans.sh /tmp/cuts laue

set -euo pipefail
OUT="${1:-$(mktemp -d)}"; shift || true
mkdir -p "$OUT"
WANT="$*"

#    paper      archive.org identifier                                                      first last
SCANS="ehrenfest  per_physikalische-zeitschrift_physikalische-zeitschrift_1909-11-22_23        54  54
laue       per_physikalische-zeitschrift_physikalische-zeitschrift_1911-02-01_3          5   7
herglotz   sim_annalen-der-physik_1910_31_2                                             165 187
noether    sim_annalen-der-physik_1910_31_5                                              75 100
born       sim_annalen-der-physik_1909_30_11                                              9  64"

echo "$SCANS" | while read -r name id first last; do
  if [ -n "$WANT" ] && ! echo " $WANT " | grep -q " $name "; then continue; fi
  issue="$OUT/issue-$name.pdf"
  [ -f "$issue" ] || curl -L --fail -o "$issue" "https://archive.org/download/$id/$id.pdf"
  qpdf --empty --pages "$issue" "$first-$last" -- "$OUT/$name.pdf"
  echo "$name: $OUT/$name.pdf  ($(pdfinfo "$OUT/$name.pdf" | awk '/^Pages/{print $2}') pp.)  sha256 $(sha256sum "$OUT/$name.pdf" | cut -c1-16)…"
done
echo "Compare with SCANS.tsv (pages, page_size); the issue PDFs are left in $OUT."
