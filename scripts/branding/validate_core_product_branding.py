#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]

REGISTRY = (
    ROOT
    / "assets"
    / "branding"
    / "products"
    / "midwest24-core-products.json"
)

EXPECTED = {
    "drive.midwest24.com":
        "Midwest24 Core Drive",

    "board.midwest24.com":
        "Midwest24 Core Board",

    "auth.midwest24.com":
        "Midwest24 Core Identity",

    "office.midwest24.com":
        "Midwest24 Core Documents",

    "vault.midwest24.com":
        "Midwest24 Core Vault",

    "institute.midwest24.com":
        "Midwest24 Core Institute",

    "command.midwest24.com":
        "Midwest24 Core Command",

    "convert.midwest24.com":
        "Midwest24 Core Convert",
}

PNG_SIZES = {
    "favicon-16x16.png":
        (16, 16),

    "favicon-32x32.png":
        (32, 32),

    "apple-touch-icon.png":
        (180, 180),

    "android-chrome-192x192.png":
        (192, 192),

    "android-chrome-512x512.png":
        (512, 512),
}

PRODUCT_HASHES = {
    "assets/branding/icons/midwest24-core-drive-icon.png": "17d46bbfeef19d9f978e269eba4d13e3b5eb675b1a622788077bd9e9d3dc2131",
    "assets/branding/products/midwest24-core-drive-logo-light.png": "7ee219b2659736688ede3dc287f3a2cf66c7bdbda408774ad731e3eb162a6db0",
    "assets/branding/icons/midwest24-core-board-icon.png": "19bd488b1061d1326f79ebf2af78d91a059c50524e4725eacd32f26e5c496d73",
    "assets/branding/products/midwest24-core-board-logo-light.png": "8b9912e73cd39ff682e9f055695cb52d709a86a15b9cc50bb6d59dc0e533f1b6",
    "assets/branding/icons/midwest24-core-identity-icon.png": "70fe4085b4f018f5b0d0df853569cb13d8dc22cf6e29032479394cce6ef54ac6",
    "assets/branding/products/midwest24-core-identity-logo-light.png": "c564251a535577e572fe9d6dd408f1c113fa9960b7afacc8e1050901b457866e",
    "assets/branding/icons/midwest24-core-documents-icon.png": "12563acbcf7947baf376226a11306efef4c3093d08485c9dbb8b252b384458eb",
    "assets/branding/products/midwest24-core-documents-logo-light.png": "5a8a1ef2db1dcfcee854a1783c1e453859940869c3dc6e8894634bd46a7ce7ac",
    "assets/branding/icons/midwest24-core-vault-icon.png": "c41fcfd0fb03d557e8f17efa294408ee2183de2b773e3f315e5f112fbea1e2de",
    "assets/branding/products/midwest24-core-vault-logo-light.png": "ca3bbb7286326a86c160f12368c39aabf0c12fcd528c9d951468b27647a7532e",
    "assets/branding/icons/midwest24-core-institute-icon.png": "3ddd74c33b1aaad682c25f4cdb84b7253a21aad0c139f38b1a676e971c85bfb3",
    "assets/branding/products/midwest24-core-institute-logo-light.png": "08a7cf98c2dac221259b3f7d3646ad608d124dbc04c43c5663ea88391e5e0586",
    "assets/branding/icons/midwest24-core-command-icon.png": "9c8a7e26d6c76c062659a84942fc8fe0c0dcda37f9cebb534749548148b8e0be",
    "assets/branding/products/midwest24-core-command-logo-light.png": "7fc9449f799537941d33b1b508279ba0d3b8918d8e547f312210dd6f4245e934",
    "assets/branding/icons/midwest24-core-convert-icon.png": "3ca402b64e92d27175d6775681abfb61bd30f5aa3b0538d70be147231311cde3",
    "assets/branding/products/midwest24-core-convert-logo-light.png": "b470f690f7c6db06b1a0014559c90c5f6a72586a9b66a080f04d72e53400a261"
}


def digest(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as fh:
        for block in iter(
            lambda: fh.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(
        f"FAIL: {message}"
    )


def main() -> None:
    data = json.loads(
        REGISTRY.read_text(
            encoding="utf-8",
        )
    )

    products = data.get(
        "products",
        [],
    )

    actual = {
        p["hostname"]:
            p["product_name"]
        for p in products
    }

    if actual != EXPECTED:
        fail(
            "public product registry mismatch\n"
            f"Expected: {EXPECTED}\n"
            f"Actual: {actual}"
        )

    if any(
        "midwestguard.net"
        in p["hostname"]
        for p in products
    ):
        fail(
            "midwestguard.net service found "
            "in Midwest24 Core public registry"
        )

    for old in (
        ROOT
        / "assets/branding/"
        "midwest-24-core-command-logo.png",

        ROOT
        / "assets/branding/icons/"
        "midwest-24-core-command-icon.png",
    ):
        if old.exists():
            fail(
                "legacy Command asset path "
                f"still exists: {old}"
            )

    for relative, expected_hash in (
        PRODUCT_HASHES.items()
    ):
        path = ROOT / relative

        if not path.is_file():
            fail(
                "missing approved product "
                f"asset: {relative}"
            )

        if digest(path) != expected_hash:
            fail(
                "approved product asset "
                f"hash changed: {relative}"
            )

    catalog = (
        ROOT
        / "archive/docs/product-catalog.md"
    ).read_text(
        encoding="utf-8",
    )

    for product in products:
        logo = ROOT / product["logo"]
        icon = ROOT / product["icon"]
        fdir = ROOT / product["favicon_dir"]

        if not logo.is_file():
            fail(
                f"{product['key']}: "
                f"missing logo "
                f"{product['logo']}"
            )

        if not icon.is_file():
            fail(
                f"{product['key']}: "
                f"missing icon "
                f"{product['icon']}"
            )

        if (
            product["product_name"]
            not in catalog
        ):
            fail(
                f"{product['key']}: "
                "product missing from "
                "authoritative catalog"
            )

        for filename, expected_size in (
            PNG_SIZES.items()
        ):
            path = fdir / filename

            if not path.is_file():
                fail(
                    f"{product['key']}: "
                    f"missing {path}"
                )

            with Image.open(path) as image:
                if image.size != expected_size:
                    fail(
                        f"{product['key']}: "
                        f"{filename} size "
                        f"{image.size}; expected "
                        f"{expected_size}"
                    )

        if not (
            fdir / "favicon.ico"
        ).is_file():
            fail(
                f"{product['key']}: "
                "favicon.ico missing"
            )

        if not (
            fdir
            / "site.webmanifest"
        ).is_file():
            fail(
                f"{product['key']}: "
                "site.webmanifest missing"
            )

        print(
            f"PASS: "
            f"{product['product_name']} | "
            f"{product['hostname']} | "
            f"logo={product['logo_scope']} | "
            f"icon={product['icon_scope']}"
        )

    print()
    print(
        "PASS: all eight current "
        "midwest24.com Core products have"
    )
    print(
        "      an approved logo assignment "
        "and complete favicon package."
    )


if __name__ == "__main__":
    main()
