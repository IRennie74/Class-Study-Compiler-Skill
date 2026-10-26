#!/bin/zsh
# extract.sh MATERIALS_DIR WORK_DIR
# Pulls everything readable out of a folder of course materials:
#   PDFs   -> text (pdftotext -layout) + page images and 2x2 grids (for image-only slides)
#   ZIPs   -> unpacked into their own folders, then processed
#   Videos -> duration, embedded subtitles, 1 frame / 20 s, 4x4 contact sheets, header strips
#   PPTX/DOCX -> converted to PDF with LibreOffice when available
# Requires: poppler (pdftotext, pdftoppm, pdfinfo), ffmpeg/ffprobe. Optional: soffice.
set -u
SRC=${1:?usage: extract.sh MATERIALS_DIR WORK_DIR}
WORK=${2:?usage: extract.sh MATERIALS_DIR WORK_DIR}
mkdir -p "$WORK"/{txt,pages,video,unzipped,converted}

# 1. Unpack archives (each into its own empty folder; never run anything from inside)
for z in "$SRC"/*.zip(N); do
  d="$WORK/unzipped/${z:t:r}"; mkdir -p "$d"; unzip -o -q "$z" -d "$d" && echo "unzipped: ${z:t}"
done

# 2. Convert office documents if LibreOffice exists
if command -v soffice >/dev/null; then
  for f in "$SRC"/*.(pptx|ppt|docx|doc)(N); do
    soffice --headless --convert-to pdf --outdir "$WORK/converted" "$f" >/dev/null 2>&1 && echo "converted: ${f:t}"
  done
fi

# 3. PDFs: text + page images
for f in "$SRC"/*.pdf(N) "$WORK"/converted/*.pdf(N) "$WORK"/unzipped/**/*.pdf(N); do
  b=${f:t:r}
  pages=$(pdfinfo "$f" 2>/dev/null | awk '/^Pages:/{print $2}')
  pdftotext -layout "$f" "$WORK/txt/$b.txt"
  chars=$(tr -d '[:space:]' < "$WORK/txt/$b.txt" | wc -c | tr -d ' ')
  echo "pdf: ${f:t}  pages=$pages  textchars=$chars"
  # If the text layer is thin (scanned or image slides), render the pages so they can be read visually
  if [ "${pages:-0}" -gt 0 ] && [ "$chars" -lt $(( ${pages:-1} * 120 )) ]; then
    mkdir -p "$WORK/pages/$b"
    pdftoppm -r 100 -png "$f" "$WORK/pages/$b/p"
    imgs=("$WORK/pages/$b"/p-*.png(N))
    n=${#imgs}; i=0
    for (( k=1; k<=n; k+=4 )); do
      i=$((i+1))
      # pad the last grid by repeating the final page so no page is dropped
      a=${imgs[k]}; bb=${imgs[k+1]:-${imgs[n]}}; c=${imgs[k+2]:-${imgs[n]}}; d=${imgs[k+3]:-${imgs[n]}}
      ffmpeg -v error -y -i "$a" -i "$bb" -i "$c" -i "$d" \
        -filter_complex "[0][1][2][3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0" "$WORK/pages/$b/grid_$(printf %02d $i).png"
    done
    echo "   -> image-heavy: rendered page grids in pages/$b/grid_*.png (read them visually)"
  fi
done

# 4. Videos: subtitles, frames and contact sheets
for v in "$SRC"/*.(mp4|m4v|mov|mkv|webm)(N) "$WORK"/unzipped/**/*.(mp4|m4v|mov|mkv|webm)(N); do
  b=${v:t:r}; d="$WORK/video/$b"; mkdir -p "$d"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v")
  echo "video: ${v:t}  duration=${dur}s"
  ffmpeg -v error -y -i "$v" -map 0:s:0 "$d/subs.srt" 2>/dev/null && echo "   subtitles: $(wc -c < "$d/subs.srt") bytes"
  ffmpeg -v error -y -i "$v" -vf "fps=1/20,scale=960:-1" "$d/f_%03d.jpg"
  ffmpeg -v error -y -pattern_type glob -i "$d/f_*.jpg" -vf "scale=480:-1,tile=4x4" "$d/sheet_%02d.jpg"
  # header strips: slide titles over time (finds which problem is on screen when)
  ffmpeg -v error -y -pattern_type glob -i "$d/f_*.jpg" -vf "crop=480:110:60:20,scale=240:-1,tile=8x18" "$d/titles_%02d.jpg"
  echo "   frames: $(ls "$d"/f_*.jpg | wc -l | tr -d ' ')  sheets: $(ls "$d"/sheet_*.jpg | wc -l | tr -d ' ')"
done
echo "done -> $WORK"
