# Midwest24 Core Enterprise artwork

Status: User-approved artwork; public activation pending.
Approved: 2026-09-11 in Codex task 01a090d1-9dda-7e02-8256-573eb0aeac2d.
Identity authority: jryanrussow-site ACP-011, Approved 2026-09-11.

The approved design uses three white buildings inside the Core-family shield.
The approval reference is ../../reference/midwest24-core-enterprise-approved-reference.png.
These are raster source/approval artifacts, not editable vector masters.
Built-in image generation produced the concept and separate exports. The user
explicitly authorized local image processing to remove the icon's baked-in
checkerboard background and produce exact-size transparent exports.

Production-format assets (not publicly deployed):
- ../../products/midwest24-core-enterprise-logo-light.png: 1600 x 500 RGBA.
- ../../icons/midwest24-core-enterprise-icon.png: 1024 x 1024 RGBA.
- ../../favicons/enterprise/: seven-file favicon package.

The public registry remains unchanged. The existing favicon builder was imported
with ROOT pointing to an isolated package and REGISTRY pointing to the included
enterprise-build-input.json. Its unmodified main() generated all seven files.
For a rebuild use that same isolated-root procedure; do not add Enterprise to
the public registry solely to generate its favicons.

Source processing: keep the approved wordmark alpha, crop to alpha bounds, fit
without distortion into 1600 x 500 with at least 40 px padding. For the icon,
identify the blue outer silhouette per scanline (B-R > 40 and B-G > 12), fill
between left/right edges to retain opaque white interior, make exterior alpha
zero, then fit without distortion into 1024 x 1024 with 76 px padding. Lanczos
resampling was used for both. No production asset was used as an editable master.

Validation: exact export sizes, RGBA alpha extrema 0/255, all seven favicon
files, ICO embedded sizes 16/32/48, and visual review of 16/32/48/180 px icons.
