#!/bin/zsh
# build.sh BUILD_DIR OUT_DIR PREFIX
# Renders the study pack to PDF with headless Chrome (or Edge/Chromium).
#   BUILD_DIR must contain: mock.html (with body class="__MODE__"), units.json, units/, wb_intro.html,
#                           wb_outro.html, master.html, notes.html, drill.html
#   PREFIX e.g. "CISC221" -> 1_CISC221_Mock_Test.pdf, ...
set -eu
SKILL=${0:A:h:h}
B=${1:?usage: build.sh BUILD_DIR OUT_DIR PREFIX}; B=${B:A}
OUT=${2:?usage: build.sh BUILD_DIR OUT_DIR PREFIX}
P=${3:?usage: build.sh BUILD_DIR OUT_DIR PREFIX}
mkdir -p "$OUT"
cp "$SKILL/templates/style.css" "$B/style.css"   # always use the skill's current styles

CH=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "$(command -v google-chrome 2>/dev/null)" "$(command -v chromium 2>/dev/null)"; do
  [ -n "$c" ] && [ -x "$c" ] && { CH="$c"; break; }
done
[ -n "$CH" ] || { echo "No Chrome/Edge/Chromium found"; exit 1; }

render() { "$CH" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$OUT/$2" "file://$B/$1" 2>/dev/null; }

if [ -f "$B/mock.html" ]; then
  sed 's/__MODE__/test/' "$B/mock.html" > "$B/mock_test.html"
  sed 's/__MODE__/key/' "$B/mock.html" > "$B/mock_key.html"
  render mock_test.html "1_${P}_Mock_Test.pdf"
  render mock_key.html  "2_${P}_Mock_Test_ANSWERS.pdf"
fi
if [ -f "$B/units.json" ]; then
  python3 -I "$SKILL/scripts/assemble.py" "$B"
  render workbook.html "3_${P}_Unit_Problem_Workbook.pdf"
fi
[ -f "$B/master.html" ] && render master.html "4_${P}_Complete_Master_Reference.pdf"
[ -f "$B/notes.html" ]  && render notes.html  "5_${P}_Concepts_Notes.pdf"
python3 -I "$SKILL/scripts/check_drill.py" "$B"
render drill.html "6_${P}_QA_Drill.pdf"

python3 -I "$SKILL/scripts/check_lines.py" "$B"
for f in "$OUT"/*.pdf; do echo "$(basename "$f")  $(pdfinfo "$f" | awk '/^Pages:/{print $2}') pages"; done
