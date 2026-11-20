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

The icon is published from the governed Cloudflare Pages project at
`https://midwest24-site.pages.dev/assets/branding/releases/curriculum-20261120/midwest24-core-curriculum.png`.
Production deployment `783a189f-fad0-4cfa-837e-f42958d382bf` serves source
commit `343e7fa`; the live bytes match the reviewed release SHA-256
`cd980ca1173d4e9d6c80bd0fb9ae0c9d6844fcfbdc2cfced25d6ca76f16ee667`.

The main `midwest24.com` hostname currently uses a separate Worker asset
bundle and did not yet serve this new file during publication. Authentik
therefore uses the stable Pages project URL rather than an uncommitted Worker
deployment. Changing the icon does not change the Access policy, participant
group, tunnel route, Moodle course, or static curriculum content.
