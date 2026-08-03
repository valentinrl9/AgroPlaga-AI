"""
Diseño camiseta negra — layout horizontal.
Logo izquierda · PlagaScan superpuesto en esquina inferior derecha del logo.

  python docs/logo_calmiseta.py
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "assets"
LOGO_PATH = ROOT / "assets" / "app_logo.png"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CANVAS = 3000
CX = CANVAS // 2

GREEN = (0, 168, 107)
GREEN_DARK = (0, 90, 62)
CYAN = (0, 210, 196)
CYAN_BRIGHT = (120, 255, 245)
WHITE = (255, 255, 255)


def load_font(size: int, heavy: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    if not heavy:
        paths = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"] + paths
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def radial_glow_layer(
    size: tuple[int, int],
    center: tuple[int, int],
    radius: int,
    inner: tuple[int, int, int],
    outer: tuple[int, int, int],
    peak_alpha: int = 180,
) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy = center
    y0, y1 = max(0, cy - radius), min(h, cy + radius)
    x0, x1 = max(0, cx - radius), min(w, cx + radius)
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = math.hypot(x - cx, y - cy)
            if d > radius:
                continue
            t = (1.0 - d / radius) ** 1.6
            r = int(inner[0] * t + outer[0] * (1 - t))
            g = int(inner[1] * t + outer[1] * (1 - t))
            b = int(inner[2] * t + outer[2] * (1 - t))
            layer.putpixel((x, y), (r, g, b, int(peak_alpha * t)))
    return layer.filter(ImageFilter.GaussianBlur(radius=28))


def linear_gradient_text(
    text: str,
    font: ImageFont.ImageFont,
    width: int,
    height: int,
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
    mask = img.split()[3]
    grad = Image.new("RGBA", (width, height))
    gdraw = ImageDraw.Draw(grad)
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        gdraw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    grad.putalpha(mask)
    return grad


def render_3d_text(
    text: str,
    font: ImageFont.ImageFont,
    depth: int = 16,
    extrude: tuple[int, int, int] = GREEN_DARK,
    top_color: tuple[int, int, int] = CYAN_BRIGHT,
    bottom_color: tuple[int, int, int] = GREEN,
) -> Image.Image:
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = depth + 36
    w, h = tw + pad * 2, th + pad * 2
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    for i in range(depth, 0, -1):
        d = ImageDraw.Draw(layer)
        alpha = int(120 + 130 * (i / depth))
        d.text((pad + i * 1.1, pad + i * 1.1), text, font=font, fill=(*extrude, alpha))

    face = linear_gradient_text(text, font, tw + 8, th + 8, top_color, bottom_color)
    layer.paste(face, (pad, pad), face)

    shine = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shine).text((pad - 4, pad - 5), text, font=font, fill=(255, 255, 255, 55))
    layer = Image.alpha_composite(layer, shine)

    outline = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(outline)
    for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
        odraw.text((pad + dx, pad + dy), text, font=font, fill=(0, 40, 35, 200))
    return Image.alpha_composite(outline, layer)


def glow_from_image(source: Image.Image, color: tuple[int, int, int], blur: int = 45, alpha: int = 200) -> Image.Image:
    glow = source.copy().convert("RGBA")
    _, _, _, a = glow.split()
    tint = Image.new("RGBA", glow.size, (*color, 0))
    tint.putalpha(a.point(lambda x: min(255, int(x * alpha / 255))))
    return tint.filter(ImageFilter.GaussianBlur(blur))


def load_logo(size: int) -> Image.Image:
    if not LOGO_PATH.exists():
        fb = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(fb).rounded_rectangle(
            [20, 20, size - 20, size - 20], radius=80, fill=(18, 36, 52, 255), outline=GREEN, width=8
        )
        return fb

    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((size, size), Image.Resampling.LANCZOS)
    sq = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sq.paste(logo, ((size - logo.width) // 2, (size - logo.height) // 2), logo)
    return sq


def build_design() -> Image.Image:
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))

    logo_size = 960
    font_brand = load_font(200)
    font_tag = load_font(52, heavy=False)

    brand = render_3d_text(
        "PlagaScan",
        font_brand,
        depth=16,
        extrude=(0, 55, 48),
        top_color=CYAN_BRIGHT,
        bottom_color=GREEN,
    )

    tag = "La IA fitosanitaria offline"
    tag_bbox = font_tag.getbbox(tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_h = tag_bbox[3] - tag_bbox[1]

    # Superposición: texto ancla en esquina inferior derecha del logo
    overlap_x = int(logo_size * 0.42)
    overlap_y = int(logo_size * 0.48)

    comp_w = logo_size + brand.width - overlap_x
    comp_h = logo_size + 70 + tag_h
    block_x = (CANVAS - comp_w) // 2
    block_y = (CANVAS - comp_h) // 2 - 40

    logo_x = block_x
    logo_y = block_y
    text_x = block_x + logo_size - overlap_x
    text_y = block_y + logo_size - overlap_y - brand.height + int(logo_size * 0.06)

    glow_cx = block_x + comp_w // 2
    glow_cy = logo_y + logo_size // 2

    canvas = Image.alpha_composite(
        canvas, radial_glow_layer((CANVAS, CANVAS), (glow_cx, glow_cy), 720, GREEN, (0, 0, 0), 120)
    )
    canvas = Image.alpha_composite(
        canvas, radial_glow_layer((CANVAS, CANVAS), (glow_cx, glow_cy), 480, CYAN, (0, 0, 0), 85)
    )

    logo = load_logo(logo_size)
    logo_glow = glow_from_image(logo, CYAN, blur=50, alpha=200)
    logo_glow2 = glow_from_image(logo, GREEN, blur=32, alpha=140)
    canvas.paste(logo_glow2, (logo_x - 24, logo_y - 24), logo_glow2)
    canvas.paste(logo_glow, (logo_x - 16, logo_y - 16), logo_glow)
    canvas.paste(logo, (logo_x, logo_y), logo)

    # Texto encima del logo (esquina inferior derecha)
    text_glow = glow_from_image(brand, CYAN, blur=28, alpha=160)
    canvas.paste(text_glow, (text_x - 12, text_y - 8), text_glow)
    canvas.paste(brand, (text_x, text_y), brand)

    # Tagline centrada bajo el bloque
    tag_y = max(logo_y + logo_size, text_y + brand.height) + 44
    tag_x = block_x + (comp_w - tag_w) // 2
    tag_layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tag_layer)
    tdraw.text((tag_x + 2, tag_y + 2), tag, font=font_tag, fill=(0, 0, 0, 100))
    tdraw.text((tag_x, tag_y), tag, font=font_tag, fill=(*WHITE, 220))
    line_x0 = tag_x - 40
    line_x1 = tag_x + tag_w + 40
    tdraw.line([(line_x0, tag_y - 18), (line_x1, tag_y - 18)], fill=(*CYAN, 160), width=3)
    canvas = Image.alpha_composite(canvas, tag_layer)

    return canvas


def preview_on_black(design: Image.Image) -> Image.Image:
    bg = Image.new("RGB", (CANVAS, CANVAS), (8, 8, 10))
    bg.paste(design, (0, 0), design)
    return bg


def main() -> None:
    design = build_design()
    out_png = OUT_DIR / "camiseta_plagascan.png"
    out_preview = OUT_DIR / "camiseta_plagascan_preview.png"
    design.save(out_png, "PNG")
    preview_on_black(design).save(out_preview, "PNG", quality=95)
    print(f"OK  Transparente: {out_png}")
    print(f"OK  Preview:      {out_preview}")


if __name__ == "__main__":
    main()
