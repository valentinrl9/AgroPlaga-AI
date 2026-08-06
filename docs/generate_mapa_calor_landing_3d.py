"""Genera mapa de calor 3D en relieve (sur de Almería) — PNG para landing."""

from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PNG = ROOT / "landing" / "assets" / "mapa-calor-sur-almeria-3d.png"

W, H = 1400, 880
PAD = 72

LON_MIN, LON_MAX = -3.22, -1.76
LAT_MIN, LAT_MAX = 36.68, 37.30

MUNICIPIOS: list[tuple[str, float, float, str | None, tuple[int, int]]] = [
    ("Albuñol", -3.1333, 36.7833, None, (0, -18)),
    ("Adra", -3.0208, 36.7496, "media", (0, 22)),
    ("Balanegra", -2.9050, 36.7400, None, (0, 22)),
    ("Berja", -2.9494, 36.8461, None, (-28, -12)),
    ("El Ejido", -2.8144, 36.7763, "muy_alta", (0, -22)),
    ("Dalías", -2.8667, 36.8267, "alta", (-22, -14)),
    ("La Mojonera", -2.6917, 36.7936, "media", (0, -22)),
    ("Vícar", -2.6421, 36.8310, "baja", (0, -22)),
    ("Roquetas", -2.6147, 36.7642, "alta", (0, 24)),
    ("Ríoja", -2.5444, 36.7444, "media", (18, 20)),
    ("Almería", -2.4637, 36.8340, "media", (0, -22)),
    ("Níjar", -2.2055, 36.9663, "baja", (-32, 0)),
    ("San José", -2.1069, 36.7589, None, (0, 24)),
    ("Carboneras", -1.8956, 36.9967, None, (0, -18)),
    ("Mojácar", -1.8489, 37.1403, "baja", (0, -18)),
    ("Garrucha", -1.8225, 37.1814, None, (18, 0)),
    ("Vera", -1.8569, 37.2461, None, (-18, -14)),
]

HEAT = {
    "muy_alta": ((255, 60, 60), 95),
    "alta": ((255, 120, 40), 78),
    "media": ((255, 210, 50), 62),
    "baja": ((50, 220, 120), 48),
}

COASTLINE = [
    (-3.18, 36.795), (-3.08, 36.748), (-3.02, 36.742), (-2.92, 36.732),
    (-2.82, 36.748), (-2.72, 36.756), (-2.62, 36.758), (-2.56, 36.748),
    (-2.50, 36.768), (-2.46, 36.812), (-2.44, 36.838), (-2.38, 36.828),
    (-2.28, 36.792), (-2.20, 36.758), (-2.17, 36.718), (-2.08, 36.748),
    (-2.00, 36.768), (-1.92, 36.820), (-1.90, 36.900), (-1.88, 36.980),
    (-1.84, 37.060), (-1.82, 37.130), (-1.80, 37.190), (-1.82, 37.250),
]
INLAND = [
    (-1.82, 37.280), (-1.88, 37.120), (-2.00, 36.980), (-2.12, 36.920),
    (-2.28, 36.900), (-2.50, 36.890), (-2.72, 36.885), (-2.92, 36.875),
    (-3.08, 36.840), (-3.18, 36.810),
]
PLASTIC_PONIENTE = [(-3.04, 36.815), (-2.58, 36.815), (-2.58, 36.738), (-3.04, 36.738)]
PLASTIC_ALMERIA = [(-2.58, 36.795), (-2.42, 36.795), (-2.42, 36.735), (-2.58, 36.735)]

# Perspectiva oblicua (vista aérea inclinada)
SHEAR = 0.28
DEPTH = 0.86


def project(lon: float, lat: float) -> tuple[float, float]:
    x = PAD + (lon - LON_MIN) / (LON_MAX - LON_MIN) * (W - 2 * PAD)
    y = PAD + 52 + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * (H - 2 * PAD - 80)
    depth = (y - PAD) / (H - 2 * PAD)
    x += (1.0 - depth) * SHEAR * (W * 0.12)
    y = PAD + 52 + (y - PAD - 52) * DEPTH + depth * 18
    return x, y


def land_polygon() -> list[tuple[float, float]]:
    return [project(lon, lat) for lon, lat in COASTLINE + INLAND]


def point_in_poly(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1):
            inside = not inside
    return inside


def plastic_polygons() -> list[list[tuple[float, float]]]:
    return [
        [project(lon, lat) for lon, lat in PLASTIC_PONIENTE],
        [project(lon, lat) for lon, lat in PLASTIC_ALMERIA],
    ]


def elevation_at(lon: float, lat: float) -> float:
    """Relieve sintético: llanura costera + sierras al norte + cabo de Gata bajo."""
    north = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)
    sierra = max(0.0, float(north - 0.38)) ** 1.4 * 2.8
    cape = math.exp(-((lon + 2.12) ** 2) / 0.018 - ((lat - 36.76) ** 2) / 0.004) * 0.35
    coastal = max(0.0, 0.22 - (LAT_MAX - lat) * 0.07)
    return max(0.05, sierra + coastal - cape)


def build_terrain_layer(land: list[tuple[float, float]]) -> Image.Image:
    xs = np.linspace(LON_MIN, LON_MAX, W)
    ys = np.linspace(LAT_MAX, LAT_MIN, H)
    elev = np.zeros((H, W), dtype=np.float32)
    for j, lat in enumerate(ys):
        for i, lon in enumerate(xs):
            if point_in_poly(i, j, land):
                elev[j, i] = elevation_at(lon, lat)

    gy, gx = np.gradient(elev)
    az, alt = math.radians(315), math.radians(42)
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy) + 1e-6)
    aspect = np.arctan2(-gy, gx)
    shade = (
        np.sin(alt) * np.sin(slope)
        + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
    )
    shade = np.clip(shade, 0, 1)

    base_g = (18 + elev * 55).astype(np.uint8)
    base_r = (12 + elev * 38).astype(np.uint8)
    base_b = (10 + elev * 18).astype(np.uint8)

    rgb = np.stack([base_r, base_g, base_b], axis=-1).astype(np.float32)
    rgb *= (0.35 + 0.75 * shade[..., None])
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    mask = np.zeros((H, W), dtype=np.uint8)
    img_tmp = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img_tmp).polygon(land, fill=255)
    mask = np.array(img_tmp)

    rgba = np.dstack([rgb, mask])
    return Image.fromarray(rgba, "RGBA")


def draw_sea(draw: ImageDraw.ImageDraw) -> None:
    for y in range(H):
        t = y / H
        c = (
            int(8 + 18 * t),
            int(18 + 28 * t),
            int(32 + 40 * t),
        )
        draw.line([(0, y), (W, y)], fill=c)


def draw_iso_greenhouse(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    bw: float,
    bh: float,
    rng: random.Random,
) -> None:
    h = bw * rng.uniform(0.35, 0.55)
    skew = bw * 0.28
    top = [
        (x, y - h),
        (x + bw, y - h),
        (x + bw + skew, y - h - skew * 0.35),
        (x + skew, y - h - skew * 0.35),
    ]
    front = [(x, y), (x + bw, y), (x + bw, y - h), (x, y - h)]
    side = [(x + bw, y), (x + bw + skew, y - skew * 0.35), (x + bw + skew, y - h - skew * 0.35), (x + bw, y - h)]

    tone = rng.randint(175, 210)
    draw.polygon(side, fill=(tone - 35, tone - 30, tone - 25))
    draw.polygon(front, fill=(tone - 10, tone - 8, tone - 5))
    draw.polygon(top, fill=(tone + 15, tone + 18, tone + 20))
    draw.line([top[0], top[1]], fill=(255, 255, 255, 80), width=1)


def fill_greenhouses(base: Image.Image, rng: random.Random) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    polys = plastic_polygons()
    for poly in polys:
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x0, x1 = int(min(xs)), int(max(xs))
        y0, y1 = int(min(ys)), int(max(ys))
        step = 8
        for gy in range(y0, y1, step):
            for gx in range(x0, x1, step):
                if point_in_poly(gx + rng.uniform(-2, 2), gy + rng.uniform(-2, 2), poly):
                    bw = rng.uniform(8, 13)
                    draw_iso_greenhouse(draw, gx + rng.uniform(0, 3), gy + rng.uniform(0, 3), bw, bw * 0.65, rng)
    return Image.alpha_composite(base, layer)


def add_glow_layer(color: tuple[int, int, int], x: float, y: float, radius: int) -> Image.Image:
    size = radius * 4
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = size // 2, size // 2
    for i, scale in enumerate((1.0, 0.72, 0.48, 0.28)):
        r = radius * scale
        alpha = int(165 * (0.95 - i * 0.16))
        gdraw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius // 4 + 3))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(glow, (int(x - size // 2), int(y - size // 2)), glow)
    return out


def add_heat_markers(base: Image.Image) -> Image.Image:
    """Brotes luminosos con anillos concéntricos (estilo mapa anterior)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    for _, lon, lat, level, _ in MUNICIPIOS:
        if not level:
            continue
        x, y = project(lon, lat)
        color, radius = HEAT[level]
        base = Image.alpha_composite(base, add_glow_layer(color, x, y, radius))
        for i, scale in enumerate((1.0, 0.65, 0.38)):
            r = radius * scale * 0.55
            alpha = 200 - i * 55
            ldraw.ellipse(
                (x - r, y - r, x + r, y + r),
                outline=(*color, alpha),
                width=3 - i,
            )
        ldraw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(*color, 240), outline=(255, 255, 255, 180))
    return Image.alpha_composite(base, layer)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def draw_ui(base: Image.Image, land: list[tuple[float, float]]) -> Image.Image:
    draw = ImageDraw.Draw(base)
    font_title = load_font(28, bold=True)
    font_sub = load_font(16)
    font_sm = load_font(13)
    font_xs = load_font(11)

    # Costa resaltada
    coast = [project(lon, lat) for lon, lat in COASTLINE]
    for i in range(len(coast) - 1):
        draw.line([coast[i], coast[i + 1]], fill=(0, 210, 196, 180), width=3)

    draw = ImageDraw.Draw(base)

    # Marcadores y etiquetas
    for name, lon, lat, level, (ox, oy) in MUNICIPIOS:
        x, y = project(lon, lat)
        tx, ty = x + ox, y + oy
        draw.line([(x, y), (tx, ty - 6)], fill=(0, 210, 196, 160), width=1)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(0, 210, 196), outline=(11, 25, 44))
        weight = font_sm if level in {"muy_alta", "alta"} else font_xs
        tw = draw.textlength(name, font=weight)
        draw.rounded_rectangle(
            (tx - tw / 2 - 8, ty - 16, tx + tw / 2 + 8, ty + 6),
            radius=6,
            fill=(11, 25, 44, 210),
            outline=(51, 65, 85),
        )
        draw.text((tx - tw / 2, ty - 14), name, fill=(255, 255, 255), font=weight)

    # Título
    draw.text((PAD, 36), "Sur de Almería", fill=(255, 255, 255), font=font_title)
    draw.text(
        (PAD, 72),
        "Mapa de calor de brotes · datos agregados por zona",
        fill=(0, 168, 107),
        font=font_sub,
    )

    # Leyenda
    lx, ly = W - PAD - 200, H - PAD - 150
    draw.rounded_rectangle((lx, ly, lx + 200, ly + 138), radius=12, fill=(11, 25, 44, 230), outline=(51, 65, 85))
    draw.text((lx + 14, ly + 14), "Intensidad", fill=(226, 232, 240), font=font_sm)
    legend = [
        ("Muy alta", (239, 68, 68), 9),
        ("Alta", (249, 115, 22), 8),
        ("Media", (234, 179, 8), 7),
        ("Baja", (34, 197, 94), 6),
    ]
    for i, (label, col, r) in enumerate(legend):
        yy = ly + 40 + i * 24
        draw.ellipse((lx + 16, yy - r, lx + 16 + 2 * r, yy + r), fill=col)
        draw.text((lx + 40, yy - 8), label, fill=(203, 213, 225), font=font_xs)

    # Región
    draw.text((PAD, H - PAD - 8), "Poniente", fill=(100, 116, 139), font=font_xs)
    draw.text((W // 2 - 40, H - PAD - 8), "Cabo de Gata", fill=(100, 116, 139), font=font_xs)
    draw.text((W - PAD - 80, H - PAD - 8), "Levante", fill=(100, 116, 139), font=font_xs)
    draw.text(
        (PAD, H - 28),
        "De Adra a Vera · tu finca no se muestra, solo el paraje",
        fill=(148, 163, 184),
        font=font_xs,
    )

    return base


def main() -> None:
    rng = random.Random(42)
    land = land_polygon()

    sea = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    sdraw = ImageDraw.Draw(sea)
    draw_sea(sdraw)

    terrain = build_terrain_layer(land)
    img = Image.alpha_composite(sea, terrain)

    # Sombra de relieve hacia el mar (efecto 3D)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    coast_pts = [project(lon, lat) for lon, lat in COASTLINE]
    shifted = [(x + 8, y + 14) for x, y in coast_pts]
    sd.polygon(shifted + list(reversed(coast_pts)), fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, shadow)

    # Brillo en llanura costera
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gloss)
    for poly in plastic_polygons():
        gdraw.polygon(poly, fill=(255, 255, 255, 18))
    img = Image.alpha_composite(img, gloss)

    img = fill_greenhouses(img, rng)
    img = add_heat_markers(img)
    img = draw_ui(img, land)

    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(OUTPUT_PNG, "PNG", optimize=True)
    print(f"PNG 3D generado: {OUTPUT_PNG} ({W}x{H})")


if __name__ == "__main__":
    main()
