#!/bin/zsh
# contact_sheet.sh PDF OUT_PNG [COLS] [DPI]
# Renders every page of a finished PDF and tiles them into one image, to eyeball layout
# (empty pages, clipped tables, page breaks in the middle of a problem).
set -eu
PDF=${1:?usage: contact_sheet.sh PDF OUT_PNG [COLS] [DPI]}
OUT=${2:?usage: contact_sheet.sh PDF OUT_PNG [COLS] [DPI]}
COLS=${3:-8}; DPI=${4:-40}
T=$(mktemp -d)
pdftoppm -r "$DPI" -png "$PDF" "$T/p"
N=$(ls "$T"/p-*.png | wc -l | tr -d ' ')
ROWS=$(( (N + COLS - 1) / COLS ))
ffmpeg -v error -y -pattern_type glob -i "$T/p-*.png" -vf "tile=${COLS}x${ROWS}" "$OUT"
rm -rf "$T"
echo "$OUT ($N pages)"
