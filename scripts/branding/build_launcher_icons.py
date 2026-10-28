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
  <g fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" stroke-width="26">{glyph}</g>
</svg>'''


GLYPHS = {
    "automation": '''
      <path d="M156 220h92m16 0h92M256 236v82"/>
      <circle cx="140" cy="220" r="28" fill="#fff" stroke="none"/>
      <circle cx="256" cy="220" r="28" fill="#fff" stroke="none"/>
      <circle cx="372" cy="220" r="28" fill="#fff" stroke="none"/>
      <circle cx="256" cy="320" r="28" fill="#fff" stroke="none"/>''',
    "cameras": '''
      <path d="M118 220h72l22-34h88l22 34h72v154H118Z" fill="#fff" stroke="none"/>
      <circle cx="256" cy="297" r="60" fill="#0878e8" stroke="none"/>
      <circle cx="256" cy="297" r="34" fill="#fff" stroke="none"/>
      <circle cx="354" cy="252" r="13" fill="#001f4d" stroke="none"/>''',
    "code": '''
      <path d="m206 176-88 80 88 80M306 176l88 80-88 80M278 150l-44 212"/>''',
    "dashboard": '''
      <rect x="126" y="270" width="66" height="70" rx="12" fill="#fff" stroke="none"/>
      <rect x="223" y="216" width="66" height="124" rx="12" fill="#fff" stroke="none"/>
      <rect x="320" y="162" width="66" height="178" rx="12" fill="#fff" stroke="none"/>''',
    "documents": '''
      <path d="M152 132h142l74 74v184H152Z" fill="#fff" stroke="none"/>
      <path d="M294 132v74h74" stroke="#0878e8"/>
      <path d="M196 264h128m-128 50h128m-128 50h86" stroke="#0878e8"/>''',
    "photos": '''
      <rect x="118" y="164" width="276" height="194" rx="18" fill="#fff" stroke="none"/>
      <circle cx="326" cy="220" r="25" fill="#0878e8" stroke="none"/>
      <path d="m148 330 72-74 52 48 38-38 72 64" stroke="#0878e8"/>''',
    "sign": '''
      <path d="M144 140h148l72 72v146H144Z" fill="#fff" stroke="none"/>
      <path d="M292 140v72h72M188 260h116m-116 46h80" stroke="#0878e8"/>
      <path d="m238 350 94-94 30 30-94 94-44 14Z" fill="#001f4d" stroke="none"/>
      <path d="m348 264 30 30" stroke="#fff"/>''',
    "vault": '''
      <rect x="132" y="222" width="248" height="132" rx="24" fill="#fff" stroke="none"/>
      <path d="M184 232v-42a72 72 0 0 1 144 0v42"/>
      <circle cx="256" cy="300" r="18" fill="#0878e8" stroke="none"/>
      <path d="M256 318v24" stroke="#0878e8"/>''',
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
