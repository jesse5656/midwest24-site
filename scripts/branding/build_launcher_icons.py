#!/usr/bin/env python3
"""Build distinct Midwest24 Core launcher icons for internal applications.

These icons intentionally use the same blue shield construction as the
approved Core product family.  They are launcher artwork, not public product
identities or replacements for the governed product registry.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "assets" / "branding" / "icons"

SIZE = 1024
SCALE = 4

ICONS = {
    "automation": "flow",
    "cameras": "camera",
    "code": "code",
    "dashboard": "dashboard",
    "sign": "sign",
}


def points(items: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return [(x * SCALE, y * SCALE) for x, y in items]


def rect(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(value * SCALE for value in box)


def gradient(
    size: tuple[int, int],
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    *,
    diagonal: bool = False,
) -> Image.Image:
    # Pillow performs this natively.  The original pixel-by-pixel version made
    # a high-resolution icon review unnecessarily slow.
    alpha = Image.linear_gradient("L").resize(size, Image.Resampling.BILINEAR)
    if diagonal:
        alpha = alpha.rotate(45, resample=Image.Resampling.BICUBIC)
    return Image.composite(
        Image.new("RGBA", size, end + (255,)),
        Image.new("RGBA", size, start + (255,)),
        alpha,
    )


def polygon_fill(
    canvas: Image.Image,
    shape: list[tuple[int, int]],
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    *,
    diagonal: bool = False,
) -> None:
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).polygon(shape, fill=255)
    canvas.alpha_composite(Image.composite(gradient(canvas.size, start, end, diagonal=diagonal), Image.new("RGBA", canvas.size), mask))


def shield() -> Image.Image:
    canvas = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
    outer = points([(512, 55), (878, 220), (842, 560), (770, 755), (512, 945), (254, 755), (182, 560), (146, 220)])
    white = points([(512, 108), (824, 250), (790, 547), (728, 720), (512, 880), (296, 720), (234, 547), (200, 250)])
    inner = points([(512, 155), (782, 276), (750, 532), (691, 686), (512, 817), (333, 686), (274, 532), (242, 276)])
    polygon_fill(canvas, outer, (0, 26, 81), (0, 57, 141), diagonal=True)
    polygon_fill(canvas, white, (255, 255, 255), (229, 242, 255))
    polygon_fill(canvas, inner, (27, 221, 246), (0, 82, 202), diagonal=True)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.polygon(points([(512, 155), (782, 276), (750, 532), (691, 686), (512, 817)]), fill=(0, 40, 128, 80))
    canvas.alpha_composite(overlay)
    return canvas


def line(draw: ImageDraw.ImageDraw, xy: list[tuple[int, int]], *, width: int = 38) -> None:
    scaled = points(xy)
    draw.line(scaled, fill=(0, 34, 99, 255), width=(width + 24) * SCALE, joint="curve")
    draw.line(scaled, fill=(255, 255, 255, 255), width=width * SCALE, joint="curve")


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, *, fill: tuple[int, int, int, int], outline: tuple[int, int, int, int] | None = None, width: int = 0) -> None:
    draw.rounded_rectangle(rect(box), radius=radius * SCALE, fill=fill, outline=outline, width=width * SCALE)


def glyph_flow(draw: ImageDraw.ImageDraw) -> None:
    line(draw, [(325, 475), (512, 475), (675, 360)], width=28)
    line(draw, [(512, 475), (675, 590)], width=28)
    for x, y in ((285, 475), (512, 475), (715, 360), (715, 590)):
        draw.ellipse(rect((x - 56, y - 56, x + 56, y + 56)), fill=(0, 34, 99, 255))
        draw.ellipse(rect((x - 35, y - 35, x + 35, y + 35)), fill=(255, 255, 255, 255))


def glyph_camera(draw: ImageDraw.ImageDraw) -> None:
    rounded(draw, (265, 380, 759, 650), 46, fill=(0, 34, 99, 255))
    rounded(draw, (286, 401, 738, 629), 28, fill=(255, 255, 255, 255))
    rounded(draw, (360, 326, 520, 401), 24, fill=(0, 34, 99, 255))
    rounded(draw, (379, 344, 501, 401), 18, fill=(255, 255, 255, 255))
    draw.ellipse(rect((430, 438, 646, 654)), fill=(0, 34, 99, 255))
    draw.ellipse(rect((462, 470, 614, 622)), fill=(38, 201, 244, 255))
    draw.ellipse(rect((500, 502, 554, 556)), fill=(255, 255, 255, 210))


def glyph_code(draw: ImageDraw.ImageDraw) -> None:
    line(draw, [(435, 360), (315, 510), (435, 660)], width=42)
    line(draw, [(589, 360), (709, 510), (589, 660)], width=42)
    line(draw, [(558, 330), (466, 690)], width=38)


def glyph_dashboard(draw: ImageDraw.ImageDraw) -> None:
    rounded(draw, (278, 346, 746, 670), 38, fill=(0, 34, 99, 255))
    rounded(draw, (300, 368, 724, 648), 22, fill=(255, 255, 255, 255))
    for x, y, width, height in ((334, 522, 66, 92), (453, 454, 66, 160), (572, 400, 66, 214)):
        rounded(draw, (x, y, x + width, y + height), 12, fill=(0, 86, 201, 255))
    draw.line(points([(336, 462), (438, 430), (531, 482), (652, 396)]), fill=(0, 34, 99, 255), width=18 * SCALE, joint="curve")
    for x, y in ((336, 462), (438, 430), (531, 482), (652, 396)):
        draw.ellipse(rect((x - 16, y - 16, x + 16, y + 16)), fill=(0, 34, 99, 255))


def glyph_sign(draw: ImageDraw.ImageDraw) -> None:
    rounded(draw, (320, 318, 620, 682), 24, fill=(0, 34, 99, 255))
    rounded(draw, (343, 341, 597, 659), 12, fill=(255, 255, 255, 255))
    draw.polygon(points([(525, 341), (597, 341), (597, 413)]), fill=(183, 224, 251, 255))
    for y, width in ((445, 150), (500, 138), (555, 115)):
        draw.rounded_rectangle(rect((385, y, 385 + width, y + 20)), radius=10 * SCALE, fill=(0, 86, 201, 255))
    draw.line(points([(510, 650), (715, 445)]), fill=(0, 34, 99, 255), width=72 * SCALE)
    draw.line(points([(510, 650), (715, 445)]), fill=(255, 255, 255, 255), width=40 * SCALE)
    draw.polygon(points([(493, 670), (526, 642), (514, 631)]), fill=(0, 34, 99, 255))
    draw.polygon(points([(724, 434), (747, 457), (716, 473)]), fill=(41, 196, 244, 255))


def build_icon(kind: str) -> Image.Image:
    canvas = shield()
    draw = ImageDraw.Draw(canvas)
    {
        "flow": glyph_flow,
        "camera": glyph_camera,
        "code": glyph_code,
        "dashboard": glyph_dashboard,
        "sign": glyph_sign,
    }[kind](draw)
    return canvas.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def build_review(images: dict[str, Image.Image], destination: Path) -> None:
    card = 420
    canvas = Image.new("RGB", (card * len(images), 500), "white")
    draw = ImageDraw.Draw(canvas)
    for index, (name, icon) in enumerate(images.items()):
        preview = icon.copy()
        preview.thumbnail((330, 330), Image.Resampling.LANCZOS)
        x = index * card + (card - preview.width) // 2
        canvas.paste(preview, (x, 30), preview)
        draw.text((index * card + 30, 390), name.title(), fill="#001f4d")
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path)
    args = parser.parse_args()

    OUTPUT.mkdir(parents=True, exist_ok=True)
    images: dict[str, Image.Image] = {}
    for name, kind in ICONS.items():
        icon = build_icon(kind)
        destination = OUTPUT / f"midwest24-core-{name}-icon.png"
        icon.save(destination, optimize=True)
        images[name] = icon
        print(f"BUILT: {destination.relative_to(ROOT)}")

    if args.review:
        build_review(images, args.review)
        print(f"REVIEW: {args.review}")


if __name__ == "__main__":
    main()
