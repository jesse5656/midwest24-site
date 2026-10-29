---
name: midwest24-core-icon-design
description: Extend or repair Midwest24 Core application icons using the approved historical family, visual review, and governed production assets.
---

# Midwest24 Core Icon Design

Use this skill when creating, repairing, mapping, or reviewing Midwest24 Core
application icons and launcher tiles. Do not use it for ordinary Midwest24
wordmarks, unrelated website artwork, or a new product identity.

## Authority and required outcome

The approved Core product family is the visual authority. Before changing an
icon, inspect the latest approved launcher sheet and relevant historical images named in
[historical family reference](references/historical-family.md). Do not infer a
new style from a filename, a small dashboard thumbnail, or a generic icon set.

Every icon must read as a member of the same historical family at launcher
size while retaining a distinct, semantically appropriate pictogram. Never use
the same icon for two applications. Do not substitute another product's icon.

## Workflow

1. Locate the existing approved source and production asset. Preserve it when
   it already matches the reference.
2. For a missing application icon, derive the new mark from the approved
   family’s actual construction: dimensional navy edge, shaded royal-blue/navy
   field with upper-left cyan highlight, smoothly curved white inset, and
   a centered white pictogram with the same visual weight and light direction.
   Do not introduce a flat-outline, monochrome, generic Material, emoji, or
   unrelated logo style.
3. Generate a complete contact sheet containing every launcher icon—not only
   the changed ones—and compare it visually with the approved references at
   normal launcher size.
4. Keep icon source/build inputs under the repository's branding source tree,
   commit generated production PNGs with their source, and update the branding
   README when the inventory or rebuild instructions change.
5. Before altering Authentik, publish the versioned production assets, then
   map each application to its corresponding public asset. Do not leave Edge,
   Coaching, or another launcher icon as a private Authentik-media-only copy.

## Guardrails

- An approved reference is a design contract. Do not redesign it because a
  local icon generator is convenient.
- If the matching source is not available or the reference conflicts with the
  requested icon, stop with a visual review rather than publishing a guess.
- A local contact sheet, committed source, and uploaded site are different
  states. Report the actual state plainly.
