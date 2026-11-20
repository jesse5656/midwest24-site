# Midwest24 Core Curriculum icon — generation record

Owner: Jesse Russow. Prepared November 20, 2026.

## Purpose

Create a distinct launcher icon for the protected static curriculum mirror at
`curriculum.midwest24.com`. The launcher entry helps an authorized Coaching
participant distinguish the simple reading copy from the Moodle workspace at
`coaching.midwest24.com`.

## Design authority

- Approved family: `../reference/midwest24-core-launcher-family-approved-2026-10-29.png`
- Approval record: `../reference/launcher-family-approval-2026-10-29.md`
- Editable source: `midwest24-core-curriculum-icon.svg`
- Complete-family review: `../reference/midwest24-core-launcher-family-curriculum-review-20261120.png`

The shield reuses the approved Core construction: dimensional navy rim,
smooth white inset, upper-left cyan illumination, shaded royal-blue/navy field,
central ridge, and white dimensional pictogram. The open book represents the
readable curriculum. Its three connected nodes and upward arrow represent the
ordered learning path. This pictogram is deliberately different from Coaching
(coach and learner), Documents (single document), Institute (graduation cap),
Files (folder), and Records (filing cabinet).

## Rebuild

From the `midwest24-site` repository root:

```bash
inkscape assets/branding/source/midwest24-core-curriculum-icon.svg \
  --export-type=png \
  --export-filename=assets/branding/icons/midwest24-core-curriculum-icon.png \
  --export-width=1024 --export-height=1024

convert assets/branding/icons/midwest24-core-curriculum-icon.png \
  -resize 240x240 \
  assets/branding/releases/curriculum-20261120/midwest24-core-curriculum.png
```

The complete contact sheet is assembled from the 15 approved October 29
release icons, Workspace, Files, Records, and the Curriculum export. Review the
Curriculum mark enlarged and at 240-pixel launcher size before publishing.

## Publication boundary

The icon must be available from the governed `midwest24.com` static asset path
before Authentik's Curriculum application receives the public `meta_icon` URL.
Changing the icon does not change the Access policy, participant group, tunnel
route, Moodle course, or static curriculum content.
