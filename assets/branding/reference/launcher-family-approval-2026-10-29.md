# Approved Core launcher family — October 29, 2026

Jesse approved [this exact sheet](midwest24-core-launcher-family-approved-2026-10-29.png)
with: “those look great. file them and create the skill for our Midwest24 Core
and MIDWESTGuard branding as it useds the same colors.”

## What was filed

The original generated PNG was copied without resizing, recoloring or cropping.
SHA-256: `447e63588352fe9d109cd80c0ed7e8968963f8b8927bb48754ea4a20b3b0404c`.
Original generation filename: `exec-ba27f31d-0ed5-4ee6-b2c7-3ec89a32d5cf.png`.

Reading left to right, the rows contain:

- Automation, Board, Cameras, Code, Convert.
- Dashboard, Documents, Drive, Edge, Enterprise.
- Institute, Photos, Sign, Vault, Coaching.

This is an approved raster review sheet, not fifteen transparent production
exports and not an editable vector master. Older approval images are retained.
The sheet is the current launcher-style reference; primary wordmark authority
remains unchanged.

## Reuse and review

1. Open this sheet alongside the asset being prepared. Match the dimensional
   navy rim, smoothly curved white inset, shaded royal-blue/navy interior,
   upper-left cyan light and subtle central ridge.
2. Preserve each application's distinct pictogram. Do not substitute generic
   line icons, duplicated marks, flat cyan fills or kinked polygon shields.
3. Review every proposed individual export both enlarged and at launcher size
   alongside unchanged family members. Check smooth edges, matching color,
   proportions, centering, transparency and readable symbols.
4. Keep export/build inputs with the production files. Review the complete
   family before any authorized publication and application remapping.
5. Verify actual served assets after deployment; a local preview or Git push
   alone is not a live-icon verification.

The shared brand color anchors documented in the branding README are navy
`#001F4D`, Core blue `#0EA5FF`, bright-blue accent `#22B8FF`, and white `#FFFFFF`.
They are design anchors, not a four-color replacement for the approved shaded
artwork. Jesse confirmed the shared color family for MIDWESTGuard; its own
wordmark and logo geometry must be preserved.

Existing MIDWESTGuard website CSS has different implementation values
(`#0033A0`, `#00246F`, `#001B52`, `#5C7FBF`). These are recorded as existing
website values, not falsely described as identical to the shared brand anchors.
This filing does not migrate those CSS values or recolor existing logos.

## Publication state

Initially filed as approval evidence only. Subsequently, at Jesse's explicit
request, all 15 icons were extracted without redesign from this sheet and
published under `assets/branding/releases/approved-20261029/`. All 15 Authentik
application mappings now use these versioned files. Brand owner: Jesse Russow.

The icon exports are 240 × 240 PNGs with white backgrounds, not transparent
masters. `scripts/branding/export_approved_20261029.sh` reproduces the crops and
review sheet using ImageMagick. The approved original remains unchanged.

The Identity logo uses `identity-logo.svg` in that same release. It embeds the
existing approved logo over a white backing, preserving its colors and avoiding
navy-on-dark contrast and transparent-edge artifacts. It does not force users
into light mode. `scripts/branding/build_identity_logo_wrapper.py` builds it.

Cloudflare Pages deployment: `d1d9f78a.midwest24-site.pages.dev`.
All 16 files were fetched from `midwest24.com` and SHA-256 matched locally.
The public Authentik current-brand API reports the new logo URL; the login page
was visually checked in a fresh browser tab in light mode. Dark-mode backing is
implemented in the SVG; a dark-mode login session still needs visual confirmation.

## Administrator verification and rollback

Open the application library again to load its current mappings. Each of the
15 tiles should use the shaded blue family shown above. In System > Brands,
the default brand logo should end with `approved-20261029/identity-logo.svg`.
Do not change application access policies or provider settings to change icons.

The pre-change mapping record is retained on TrueNAS at
`/mnt/FastPool/AppData/m24-camera-tls-backup-20261029/branding-before.json`.
Rollback means restoring only each
recorded `meta_icon` and the recorded `branding_logo`. Previous public asset
paths were preserved. Repository commit/push is still pending separately from
this verified asset publication.
