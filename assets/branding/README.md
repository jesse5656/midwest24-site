# Midwest24 Brand Asset Standards

## Purpose

This directory contains the canonical brand sources, current exports, production assets, product-specific assets, icons, and archived branding materials for Midwest24 and its approved product brands.

This structure exists to:

- Preserve authoritative editable sources.
- Separate editable sources from generated exports.
- Identify assets currently used in production.
- Retain superseded assets without confusing them with current assets.
- Define the required process for future brand changes.

---

## Directory Structure

```text
assets/branding/
├── archive/
│   ├── legacy-exports-2026-06/
│   ├── retired-products/
│   └── site-backups-2026-07/
├── exports/
│   └── current/
│       ├── midwest24-logo.svg
│       ├── midwest24-logo.pdf
│       └── png/
│           ├── midwest24-logo-2048.png
│           ├── midwest24-logo-1024.png
│           ├── midwest24-logo-512.png
│           └── midwest24-logo-256.png
├── favicons/
├── icons/
├── products/
├── source/
│   ├── midwest24-logo-master.svg
│   └── editable XCF source files
├── authentik-custom.css
└── README.md
```

---

## Canonical Midwest24 Logo Source

The authoritative editable source for the primary Midwest24 logo is:

```text
assets/branding/source/midwest24-logo-master.svg
```

All future changes to the primary Midwest24 logo must begin with this file.

Do not modify an exported PNG, PDF, or publication SVG and treat that modified file as the new master.

Editable XCF files under `source/` remain source files for the specific legacy or product assets they represent, but they do not supersede the primary Midwest24 master SVG.

---

## Current Export Set

Approved exports generated from the canonical master are stored in:

```text
assets/branding/exports/current/
```

The approved current export set is:

```text
assets/branding/exports/current/midwest24-logo.svg
assets/branding/exports/current/midwest24-logo.pdf
assets/branding/exports/current/png/midwest24-logo-2048.png
assets/branding/exports/current/png/midwest24-logo-1024.png
assets/branding/exports/current/png/midwest24-logo-512.png
assets/branding/exports/current/png/midwest24-logo-256.png
```

These files are publication and distribution artifacts.

The `exports/current/` directory must contain only the presently approved export set.

---

## Production Website Asset

The current production logo used by the Midwest24 website is:

```text
assets/branding/products/midwest24-logo-light.png
```

This production asset is a deployed copy of an approved export. It is not the canonical editable source.

Changing the master SVG or the files under `exports/current/` does not automatically update the production website.

The approved export must be copied deliberately into the production path and then verified on desktop and mobile.

---

## Product Assets

Actively used product assets are stored in:

```text
assets/branding/products/
```

Assets that are no longer approved or actively used must be moved to the appropriate archive directory.

---

## Icons

Application, service, and product icons are stored in:

```text
assets/branding/icons/
```

Icons are separate production assets and must not be treated as substitutes for the canonical primary logo.

---

## Approved Midwest24 Core Product Family Visual Reference

The approved visual reference for the current Midwest24 Core product family is:

```text
assets/branding/reference/midwest24-core-product-family-approved-reference.png
```

This reference governs the visual appearance of the current product-specific
icons and logo lockups for:

- Midwest24 Core Drive
- Midwest24 Core Board
- Midwest24 Core Identity
- Midwest24 Core Documents
- Midwest24 Core Vault
- Midwest24 Core Institute
- Midwest24 Core Command
- Midwest24 Core Convert

Production exports must visually correspond to this approved reference.
Filename, dimension, registry, and hash validation do not replace visual
comparison against the approved reference.

The reference image is an approval artifact, not an editable master source.

---

## Public Midwest24 Core Product Branding

The canonical registry for currently published `midwest24.com` Core
products is:

```text
assets/branding/products/midwest24-core-products.json
```

The registry maps each public hostname to its official Midwest24 Core
product identity, approved logo, approved icon, and generated favicon
directory.

Current public product scope:

```text
drive.midwest24.com      -> Midwest24 Core Drive
board.midwest24.com      -> Midwest24 Core Board
auth.midwest24.com       -> Midwest24 Core Identity
office.midwest24.com     -> Midwest24 Core Documents
vault.midwest24.com      -> Midwest24 Core Vault
institute.midwest24.com  -> Midwest24 Core Institute
command.midwest24.com    -> Midwest24 Core Command
convert.midwest24.com    -> Midwest24 Core Convert
```

This registry intentionally excludes `midwestguard.net` services.

A Core product may inherit the canonical Midwest24 Core logo or icon
until distinct product artwork has been explicitly approved. Shared
artwork must be recorded as `shared-core`; product-specific artwork must
be recorded as `product-specific`. Do not fabricate distinct artwork
merely to create unique filenames.

Each registered product must have a generated favicon set containing:

```text
favicon.ico
favicon-16x16.png
favicon-32x32.png
apple-touch-icon.png
android-chrome-192x192.png
android-chrome-512x512.png
site.webmanifest
```

Rebuild and validate these assets with:

```bash
python3 scripts/branding/build_core_product_favicons.py
python3 scripts/branding/validate_core_product_branding.py
```

---

## Archive Structure

### Legacy Exports

```text
assets/branding/archive/legacy-exports-2026-06/
```

Contains superseded logo exports. These files are not approved for new production use.

### Retired Product Assets

```text
assets/branding/archive/retired-products/
```

Contains product assets that are no longer approved for active production use.

### Site Backups

```text
assets/branding/archive/site-backups-2026-07/
```

Contains historical site-support files retained during branding and header-logo corrections.

These files are reference backups only and must not be loaded by the production website.

---

## Logo Update Workflow

Future updates to the primary Midwest24 logo must follow this sequence:

```text
Canonical master SVG
        ↓
Approved current exports
        ↓
Production asset replacement
        ↓
Desktop and mobile verification
        ↓
Archive superseded assets
        ↓
Governance validation
        ↓
Git commit and push
```

Required procedure:

1. Edit `assets/branding/source/midwest24-logo-master.svg`.
2. Review the logo at normal desktop and mobile display sizes.
3. Export the approved SVG, PDF, and PNG sizes into `exports/current/`.
4. Replace the applicable production asset deliberately.
5. Verify the production result on desktop and mobile.
6. Move superseded assets into the appropriate archive directory.
7. Update this README when paths, standards, or procedures change.
8. Stage the complete change set.
9. Run repository governance validation.
10. Commit and push only after validation passes.

---

## Source and Export Rules

### Required

- Preserve the canonical master SVG.
- Maintain the original aspect ratio.
- Generate exports from the canonical source.
- Keep current exports separate from production deployment copies.
- Keep archived assets separate from current assets.
- Use descriptive and stable filenames.
- Record structural or procedural branding changes in this README.

### Prohibited

- Editing a PNG and treating it as the canonical source.
- Stretching or distorting the logo.
- Changing shield proportions without an approved logo revision.
- Recoloring the logo outside the approved palette.
- Adding unapproved shadows, outlines, or effects.
- Returning retired assets to production without review.
- Overwriting the canonical source with a flattened export.
- Keeping multiple ambiguous files presented as the current master.

---

## Brand Colors

### Primary Navy

```text
#001F4D
```

### Core Blue

```text
#0EA5FF
```

### Bright Blue Accent

```text
#22B8FF
```

### White

```text
#FFFFFF
```

---

## Export Standards

PNG exports should use:

- Transparent backgrounds where appropriate.
- Preserved aspect ratio.
- Appropriate resolution for the intended use.
- Color-profile preservation when supported.
- Lossless optimization where practical.

Current standard PNG sizes:

```text
2048 px
1024 px
512 px
256 px
```

Visual quality, transparency, correct dimensions, and accurate rendering must also be verified.

---

## Governance

Brand assets are governed repository content.

Governance validation reviews the staged files before a commit is created and checks them against the repository rules implemented by the governance engine.

Governance validation does not replace visual review, browser testing, HTML validation, accessibility testing, or application testing.

Run governance validation with:

```bash
python3 scripts/governance/governance_engine.py
```

Only commit branding changes after governance validation passes.

---

## Ownership

Brand owner:

```text
Midwest24
```

Founder:

```text
Jesse Russow
```

All approved logos, graphics, trademarks, source files, exports, and branding materials in this repository are proprietary Midwest24 assets.
