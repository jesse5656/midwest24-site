#!/usr/bin/env python3
"""Build the governed Midwest24 Core launcher-icon family.

The approved Core artwork is the visual authority: navy outer shield, white
inset, cyan/blue field, restrained highlight, and a single white glyph. This
builder is only for internal launcher marks without a separate approved master.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "assets" / "branding" / "icons"
SIZE, SCALE = 1024, 4
LAUNCHER_ICONS = {
    "automation": "automation", "cameras": "camera", "code": "code",
    "dashboard": "dashboard", "sign": "sign", "photos": "photos",
    "edge": "edge", "coaching": "coaching",
}
NAVY, BLUE, DEEP_BLUE, WHITE = (0, 31, 77, 255), (14, 165, 255, 255), (0, 94, 205, 255), (255, 255, 255, 255)

def sc(v: int) -> int: return v * SCALE
def box(v: tuple[int, int, int, int]) -> tuple[int, int, int, int]: return tuple(sc(x) for x in v)
def pts(v: list[tuple[int, int]]) -> list[tuple[int, int]]: return [(sc(x), sc(y)) for x, y in v]

def polygon_gradient(canvas: Image.Image, shape: list[tuple[int, int]], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).polygon(shape, fill=255)
    gradient = Image.new("RGBA", canvas.size)
    draw = ImageDraw.Draw(gradient)
    for y in range(canvas.height):
        p = y / (canvas.height - 1)
        colour = tuple(round(top[i] * (1 - p) + bottom[i] * p) for i in range(3)) + (255,)
        draw.line((0, y, canvas.width, y), fill=colour)
    canvas.alpha_composite(Image.composite(gradient, Image.new("RGBA", canvas.size), mask))

def shield() -> Image.Image:
    """Start from an approved historical Core shield, then clear its glyph.

    This deliberately retains the actual family bevel, navy edge treatment,
    white inset, and light direction rather than approximating them with a new
    geometric shield.  The inner field is replaced only inside the field so a
    launcher mark cannot inherit Vault's lock or another product glyph.
    """
    approved = OUTPUT / "midwest24-core-vault-icon.png"
    canvas = Image.open(approved).convert("RGBA").resize((sc(SIZE), sc(SIZE)), Image.Resampling.LANCZOS)
    inner = pts([(512,176),(704,262),(688,465),(647,600),(577,696),(512,744),(447,696),(377,600),(336,465),(320,262)])
    polygon_gradient(canvas, inner, (25,193,247), (0,91,202))
    gloss = Image.new("RGBA", canvas.size, (0,0,0,0)); mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).polygon(pts([(512,176),(704,262),(688,465),(512,570)]), fill=64)
    gloss.paste(WHITE, mask=mask); canvas.alpha_composite(gloss)
    return canvas

def line(draw: ImageDraw.ImageDraw, p: list[tuple[int,int]], width: int = 36) -> None:
    draw.line(pts(p), fill=NAVY, width=sc(width + 18), joint="curve")
    draw.line(pts(p), fill=WHITE, width=sc(width), joint="curve")
def rounded(draw: ImageDraw.ImageDraw, v: tuple[int,int,int,int], radius: int, fill=WHITE) -> None:
    draw.rounded_rectangle(box(v), radius=sc(radius), fill=fill)
def circle(draw: ImageDraw.ImageDraw, x: int, y: int, r: int, fill=WHITE) -> None:
    draw.ellipse(box((x-r,y-r,x+r,y+r)), fill=fill)

def automation(d):
    line(d, [(330,480),(512,480),(684,362)], 26); line(d, [(512,480),(684,598)], 26)
    for x,y in ((294,480),(512,480),(720,362),(720,598)): circle(d,x,y,48,NAVY); circle(d,x,y,29)
def camera(d):
    rounded(d,(278,380,746,657),42,NAVY); rounded(d,(299,402,725,635),25); rounded(d,(359,330,514,404),22,NAVY); rounded(d,(380,347,494,404),16)
    circle(d,544,519,102,NAVY); circle(d,544,519,69,BLUE); circle(d,519,493,20)
def code(d):
    line(d,[(437,356),(322,510),(437,664)],40); line(d,[(587,356),(702,510),(587,664)],40); line(d,[(557,330),(467,690)],36)
def dashboard(d):
    rounded(d,(287,342,737,677),38,NAVY); rounded(d,(308,363,716,656),20)
    for x,y,h in ((345,525,93),(462,452,166),(579,394,224)): rounded(d,(x,y,x+67,y+h),12,DEEP_BLUE)
    line(d,[(342,465),(442,432),(537,481),(652,396)],16)
def sign(d):
    rounded(d,(329,314,620,689),25,NAVY); rounded(d,(350,336,599,667),12)
    d.polygon(pts([(525,336),(599,336),(599,410)]), fill=(194,231,255,255))
    for y,w in ((447,149),(504,130),(561,108)): rounded(d,(390,y,390+w,y+18),9,DEEP_BLUE)
    line(d,[(510,660),(718,452)],33); d.polygon(pts([(495,677),(526,647),(511,632)]),fill=NAVY)
def photos(d):
    circle(d,512,508,195,NAVY); circle(d,512,508,172)
    for wedge in (((512,508),(512,352),(648,430)),((512,508),(648,430),(648,588)),((512,508),(648,588),(512,664)),((512,508),(512,664),(376,588)),((512,508),(376,588),(376,430)),((512,508),(376,430),(512,352))): d.polygon(pts(list(wedge)),fill=DEEP_BLUE)
    circle(d,512,508,64,NAVY); circle(d,512,508,42)
def edge(d):
    line(d,[(338,510),(686,510)],37)
    for x,y0,y1 in ((302,412,608),(365,442,578),(659,442,578),(722,412,608)): rounded(d,(x-25,y0,x+25,y1),12)
def coaching(d):
    circle(d,438,445,57); circle(d,593,465,47); rounded(d,(337,517,539,657),62); rounded(d,(518,523,682,641),55); line(d,[(382,594),(470,537),(550,576),(633,536)],19)
GLYPHS = {name: globals()[kind] for name, kind in LAUNCHER_ICONS.items()}

def build(name: str) -> Image.Image:
    icon = shield(); GLYPHS[name](ImageDraw.Draw(icon)); return icon.resize((SIZE,SIZE),Image.Resampling.LANCZOS)
def review(destination: Path) -> None:
    names = ("automation","board","cameras","code","convert","dashboard","documents","drive","edge","enterprise","institute","photos","sign","vault","coaching")
    card, cols = 310, 5; canvas = Image.new("RGB",(cols*card,((len(names)+cols-1)//cols)*370),"white"); draw = ImageDraw.Draw(canvas)
    for i,name in enumerate(names):
        icon = Image.open(OUTPUT / f"midwest24-core-{name}-icon.png").convert("RGBA"); icon.thumbnail((230,230),Image.Resampling.LANCZOS)
        x,y=(i%cols)*card+(card-icon.width)//2,(i//cols)*370+35; canvas.paste(icon,(x,y),icon); draw.text(((i%cols)*card+26,(i//cols)*370+290),name.title(),fill="#001f4d")
    destination.parent.mkdir(parents=True,exist_ok=True); canvas.save(destination)
def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--review",type=Path); args=parser.parse_args(); OUTPUT.mkdir(parents=True,exist_ok=True)
    for name in LAUNCHER_ICONS:
        destination=OUTPUT/f"midwest24-core-{name}-icon.png"; build(name).save(destination,optimize=True); print(f"BUILT: {destination.relative_to(ROOT)}")
    if args.review: review(args.review); print(f"REVIEW: {args.review}")
if __name__ == "__main__": main()
