#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]

REGISTRY = (
    ROOT
    / "assets"
    / "branding"
    / "products"
    / "midwest24-core-products.json"
)

PNG_SIZES = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "apple-touch-icon.png": 180,
    "android-chrome-192x192.png": 192,
    "android-chrome-512x512.png": 512,
}


def fit_icon(
    source: Image.Image,
    size: int,
) -> Image.Image:
    source = source.convert("RGBA")

    alpha = source.getchannel("A")
    bbox = alpha.getbbox()

    if bbox:
        source = source.crop(bbox)

    canvas = Image.new(
        "RGBA",
        (size, size),
        (0, 0, 0, 0),
    )

    padding = max(
        1,
        round(size * 0.05),
    )

    fitted = source.copy()

    fitted.thumbnail(
        (
            size - 2 * padding,
            size - 2 * padding,
        ),
        Image.Resampling.LANCZOS,
    )

    x = (size - fitted.width) // 2
    y = (size - fitted.height) // 2

    canvas.alpha_composite(
        fitted,
        (x, y),
    )

    return canvas


def build_review(
    products: list[dict],
    destination: Path,
) -> None:
    width = 1800
    row_height = 300
    margin = 30

    canvas = Image.new(
        "RGB",
        (
            width,
            row_height * len(products),
        ),
        "white",
    )

    draw = ImageDraw.Draw(canvas)

    for i, product in enumerate(products):
        y0 = i * row_height

        icon = Image.open(
            ROOT / product["icon"]
        ).convert("RGBA")

        logo = Image.open(
            ROOT / product["logo"]
        ).convert("RGBA")

        icon.thumbnail(
            (190, 190),
            Image.Resampling.LANCZOS,
        )

        logo.thumbnail(
            (720, 190),
            Image.Resampling.LANCZOS,
        )

        canvas.paste(
            icon,
            (margin, y0 + 70),
            icon,
        )

        canvas.paste(
            logo,
            (300, y0 + 70),
            logo,
        )

        draw.text(
            (margin, y0 + 20),
            (
                f"{product['product_name']} — "
                f"{product['hostname']}"
            ),
            fill="black",
        )

        draw.text(
            (1100, y0 + 90),
            f"logo: {product['logo_scope']}",
            fill="black",
        )

        draw.text(
            (1100, y0 + 125),
            f"icon: {product['icon_scope']}",
            fill="black",
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    canvas.save(destination)

    print(
        f"REVIEW: {destination}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--review",
        type=Path,
    )

    args = parser.parse_args()

    data = json.loads(
        REGISTRY.read_text(
            encoding="utf-8",
        )
    )

    products = data["products"]

    for product in products:
        source_path = (
            ROOT
            / product["icon"]
        )

        output_dir = (
            ROOT
            / product["favicon_dir"]
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        source = Image.open(
            source_path
        ).convert("RGBA")

        for filename, size in PNG_SIZES.items():
            fit_icon(
                source,
                size,
            ).save(
                output_dir / filename,
                optimize=True,
            )

        fit_icon(
            source,
            256,
        ).save(
            output_dir / "favicon.ico",
            format="ICO",
            sizes=[
                (16, 16),
                (32, 32),
                (48, 48),
            ],
        )

        manifest = {
            "name": product["product_name"],
            "short_name": (
                product["product_name"]
                .replace(
                    "Midwest24 ",
                    "",
                )
            ),
            "icons": [
                {
                    "src": "android-chrome-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                },
                {
                    "src": "android-chrome-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                },
            ],
            "theme_color": "#001F4D",
            "background_color": "#FFFFFF",
            "display": "standalone",
        }

        (
            output_dir
            / "site.webmanifest"
        ).write_text(
            json.dumps(
                manifest,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        print(
            f"BUILT: "
            f"{product['hostname']} -> "
            f"{output_dir.relative_to(ROOT)}"
        )

    if args.review:
        build_review(
            products,
            args.review.expanduser(),
        )


if __name__ == "__main__":
    main()
