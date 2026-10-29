#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/jesse/Documents/Projects/midwest24-site
OUT="$ROOT/assets/branding/releases/approved-20261029"
mkdir -p "$OUT"
names=(automation board cameras code convert dashboard documents drive edge enterprise institute photos sign vault coaching)
for i in "${!names[@]}"; do
  x=$((28 + (i % 5) * 297))
  y=$((14 + (i / 5) * 350))
  convert "$ROOT/assets/branding/reference/midwest24-core-launcher-family-approved-2026-10-29.png" -crop "240x230+$x+$y" +repage -gravity center -background white -extent 240x240 "$OUT/${names[$i]}.png"
done
montage "$OUT/automation.png" "$OUT/board.png" "$OUT/cameras.png" "$OUT/code.png" "$OUT/convert.png" "$OUT/dashboard.png" "$OUT/documents.png" "$OUT/drive.png" "$OUT/edge.png" "$OUT/enterprise.png" "$OUT/institute.png" "$OUT/photos.png" "$OUT/sign.png" "$OUT/vault.png" "$OUT/coaching.png" -tile 5x3 -geometry 120x120+12+12 /tmp/m24-approved-export-review.png
