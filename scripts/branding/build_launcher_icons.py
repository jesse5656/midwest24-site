#!/usr/bin/env python3
"""Build crisp, grid-aligned Midwest24 application-library icons.

The editable SVGs are retained under assets/branding/source/launcher-icons/.
PNG files are exported at 1024px for Authentik's application library.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
ICON_DIR = ROOT / "assets" / "branding" / "icons"
SOURCE_DIR = ROOT / "assets" / "branding" / "source" / "launcher-icons"


def svg(glyph: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="core" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#22d3ee"/>
      <stop offset="1" stop-color="#0878e8"/>
    </linearGradient>
  </defs>
  <path d="M256 24 448 104v148c0 121-74 194-192 236C138 446 64 373 64 252V104Z" fill="#001f4d"/>
  <path d="M256 49 424 119v133c0 104-61 166-168 207-107-41-168-103-168-207V119Z" fill="#fff"/>
  <path d="M256 73 400 133v119c0 87-48 141-144 180-96-39-144-93-144-180V133Z" fill="url(#core)"/>
  <g fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" stroke-width="16">{glyph}</g>
</svg>'''


GLYPHS = {
    "automation": '''
      <path d="M148 256h92m32 0h92m-92 0v92"/>
      <circle cx="124" cy="256" r="25"/>
      <circle cx="256" cy="256" r="25"/>
      <circle cx="388" cy="256" r="25"/>
      <circle cx="256" cy="380" r="25"/>''',
    "cameras": '''
      <path d="M152 214h208l28 34h54v150H70V248h54Z"/>
      <path d="M182 214v-42h94v42"/>
      <circle cx="256" cy="323" r="58"/>''',
    "code": '''
      <path d="m211 186-92 70 92 70M301 186l92 70-92 70M281 158l-50 196"/>''',
    "dashboard": '''
      <path d="M142 356V280m114 76V218m114 138V164"/>
      <path d="m126 222 86-54 72 40 102-86"/>
      <circle cx="126" cy="222" r="8" fill="#fff"/>
      <circle cx="212" cy="168" r="8" fill="#fff"/>
      <circle cx="284" cy="208" r="8" fill="#fff"/>
      <circle cx="386" cy="122" r="8" fill="#fff"/>''',
    "documents": '''
      <path d="M160 140h132l76 76v176H160Z"/>
      <path d="M292 140v76h76M204 266h116m-116 48h116m-116 48h82"/>''',
    "photos": '''
      <path d="M132 162h248v188H132Z"/>
      <circle cx="306" cy="218" r="20"/>
      <path d="m160 322 64-66 48 46 36-34 44 54"/>''',
    "sign": '''
      <path d="M154 138h150l54 54v182H154Z"/>
      <path d="M304 138v54h54M198 256h116m-116 46h72M250 370l112-112m-94 130 20-20m74-110 26 26"/>''',
    "vault": '''
      <rect x="148" y="218" width="216" height="158" rx="20"/>
      <path d="M194 218v-34a62 62 0 0 1 124 0v34M256 278v42"/>
      <circle cx="256" cy="278" r="12"/>''',
}


def build_review(images: dict[str, Path], destination: Path) -> None:
    labels = list(images)
    card = 330
    canvas = Image.new("RGB", (card * 4, 900), "white")
    draw = ImageDraw.Draw(canvas)
    for index, label in enumerate(labels):
        source = Image.open(images[label]).convert("RGBA")
        source.thumbnail((250, 250), Image.Resampling.LANCZOS)
        column, row = index % 4, index // 4
        x = column * card + (card - source.width) // 2
        y = row * 430 + 28
        canvas.paste(source, (x, y), source)
        draw.text((column * card + 24, row * 430 + 320), label.title(), fill="#001f4d")
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path)
    args = parser.parse_args()
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    generated: dict[str, Path] = {}
    for name, glyph in GLYPHS.items():
        source = SOURCE_DIR / f"midwest24-core-{name}-icon.svg"
        output = ICON_DIR / f"midwest24-core-{name}-icon.png"
        source.write_text(svg(glyph), encoding="utf-8")
        subprocess.run(
            ["inkscape", str(source), "--export-type=png", f"--export-filename={output}", "--export-width=1024", "--export-height=1024"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        generated[name] = output
        print(f"BUILT: {output.relative_to(ROOT)}")
    if args.review:
        build_review(generated, args.review)
        print(f"REVIEW: {args.review}")


if __name__ == "__main__":
    main()
