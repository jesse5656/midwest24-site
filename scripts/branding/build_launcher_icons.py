#!/usr/bin/env python3
"""Build missing Midwest24 Core launcher icons from the approved Core shield.

The Enterprise icon is the approved, transparent Core-family substrate.  The
builder preserves its navy edge and white inset exactly, replaces only its Core
field, and draws a distinct white application pictogram.  It does not rewrite
approved product icons that already have their own governed source.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ICONS = ROOT / "assets" / "branding" / "icons"
SIZE, SCALE = 1024, 4
NAVY, WHITE, CYAN, BLUE = (0, 31, 77, 255), (255, 255, 255, 255), (16, 201, 241, 255), (0, 105, 226, 255)
LAUNCHERS = ("automation", "cameras", "code", "dashboard", "photos", "sign", "edge", "coaching")

def q(value: int) -> int: return value * SCALE
def box(values): return tuple(q(value) for value in values)
def points(values): return [(q(x), q(y)) for x, y in values]
def line(draw, values, width=32):
    draw.line(points(values), fill=NAVY, width=q(width + 18), joint="curve")
    draw.line(points(values), fill=WHITE, width=q(width), joint="curve")
def rounded(draw, values, radius, fill=WHITE): draw.rounded_rectangle(box(values), radius=q(radius), fill=fill)
def circle(draw, x, y, radius, fill=WHITE): draw.ellipse(box((x-radius, y-radius, x+radius, y+radius)), fill=fill)

def approved_shield() -> Image.Image:
    """Retain the approved shell and restore the historical Core field."""
    image = Image.open(ICONS / "midwest24-core-enterprise-icon.png").convert("RGBA")
    image = image.resize((q(SIZE), q(SIZE)), Image.Resampling.LANCZOS)
    # The historical launcher family uses one clean cyan Core field. It is
    # intentionally free of the accidental diagonal seams and soft overlays
    # introduced by the later generated variants.
    field = Image.new("RGBA", image.size, CYAN)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).polygon(points([(512,163), (812,289), (805,520), (746,677), (650,785), (512,862), (374,785), (278,677), (219,520), (212,289)]), fill=255)
    image.alpha_composite(Image.composite(field, Image.new("RGBA", image.size), mask))
    return image

def automation(draw):
    line(draw, [(336,486), (512,486), (679,365)], 25); line(draw, [(512,486), (679,607)], 25)
    for x, y in ((300,486), (512,486), (715,365), (715,607)): circle(draw, x, y, 44, NAVY); circle(draw, x, y, 27)
def cameras(draw):
    rounded(draw, (279,383,745,651), 40, NAVY); rounded(draw, (301,405,723,629), 24); rounded(draw, (363,332,511,405), 19, NAVY); rounded(draw, (383,349,492,405), 14)
    circle(draw, 541, 518, 96, NAVY); circle(draw, 541, 518, 63, BLUE); circle(draw, 518, 494, 17)
def code(draw): line(draw, [(435,361),(322,510),(435,659)],39); line(draw, [(589,361),(702,510),(589,659)],39); line(draw, [(557,332),(467,688)],34)
def dashboard(draw):
    rounded(draw, (285,344,739,676),36,NAVY); rounded(draw, (306,365,718,655),19)
    for x, y, height in ((343,528,89), (462,451,166), (581,395,222)): rounded(draw, (x,y,x+66,y+height), 11, BLUE)
    line(draw, [(339,466),(441,432),(537,481),(653,396)],15)
def photos(draw):
    circle(draw,512,509,187,NAVY); circle(draw,512,509,165)
    for wedge in (((512,509),(512,358),(643,434)), ((512,509),(643,434),(643,585)), ((512,509),(643,585),(512,660)), ((512,509),(512,660),(381,585)), ((512,509),(381,585),(381,434)), ((512,509),(381,434),(512,358))): draw.polygon(points(list(wedge)), fill=BLUE)
    circle(draw,512,509,57,NAVY); circle(draw,512,509,37)
def sign(draw):
    rounded(draw,(329,316,618,687),24,NAVY); rounded(draw,(350,338,597,665),11); draw.polygon(points([(524,338),(597,338),(597,411)]),fill=(200,236,255,255))
    for y, width in ((448,147),(504,128),(559,105)): rounded(draw,(390,y,390+width,y+17),8,BLUE)
    line(draw,[(510,658),(715,453)],32); draw.polygon(points([(494,675),(525,646),(510,631)]),fill=NAVY)
def edge(draw):
    line(draw,[(339,510),(685,510)],36)
    for x,y0,y1 in ((301,413,607),(365,443,577),(659,443,577),(723,413,607)): rounded(draw,(x-23,y0,x+23,y1),10)
def coaching(draw):
    circle(draw,437,445,55); circle(draw,592,465,46); rounded(draw,(337,518,537,655),58); rounded(draw,(519,525,680,640),52); line(draw,[(383,594),(470,539),(550,576),(631,538)],18)
GLYPHS = {name: globals()[name] for name in LAUNCHERS}

def build(name: str) -> Image.Image:
    image = approved_shield(); GLYPHS[name](ImageDraw.Draw(image)); return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)

def review(destination: Path) -> None:
    names = ("automation", "board", "cameras", "code", "convert", "dashboard", "documents", "drive", "edge", "enterprise", "institute", "photos", "sign", "vault", "coaching")
    card, columns = 290, 5
    sheet = Image.new("RGB", (card*columns, ((len(names)+columns-1)//columns)*345), "white")
    draw = ImageDraw.Draw(sheet)
    for index, name in enumerate(names):
        image = Image.open(ICONS / f"midwest24-core-{name}-icon.png").convert("RGBA"); image.thumbnail((220,220), Image.Resampling.LANCZOS)
        column, row = index % columns, index // columns; x = column*card + (card-image.width)//2; y = row*345 + 20
        sheet.paste(image, (x,y), image); draw.text((column*card+25,row*345+270), name.title(), fill="#001f4d")
    destination.parent.mkdir(parents=True, exist_ok=True); sheet.save(destination)

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--review", type=Path); args = parser.parse_args(); ICONS.mkdir(parents=True, exist_ok=True)
    for name in LAUNCHERS: build(name).save(ICONS / f"midwest24-core-{name}-icon.png", optimize=True)
    if args.review: review(args.review)
if __name__ == "__main__": main()
