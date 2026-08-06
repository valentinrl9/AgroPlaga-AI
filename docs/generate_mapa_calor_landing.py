"""Genera mapa de calor SVG (sur de Almería) con coordenadas WGS84 reales."""

from __future__ import annotations

from pathlib import Path

OUTPUT_SVG = Path(__file__).resolve().parents[1] / "landing" / "assets" / "mapa-calor-sur-almeria.svg"

# Centro urbano WGS84 (lon, lat) — fuentes: IGN / OpenStreetMap
# level = intensidad ilustrativa del brote (None = sin foco activo)
MUNICIPIOS: list[tuple[str, float, float, str | None, tuple[float, float]]] = [
    ("Albuñol", -3.1333, 36.7833, None, (0, -11)),
    ("Adra", -3.0208, 36.7496, "media", (0, 12)),
    ("Balanegra", -2.9050, 36.7400, None, (0, 12)),
    ("Berja", -2.9494, 36.8461, None, (-18, -8)),
    ("El Ejido", -2.8144, 36.7763, "muy_alta", (0, -12)),
    ("Dalías", -2.8667, 36.8267, "alta", (-14, -10)),
    ("La Mojonera", -2.6917, 36.7936, "media", (0, -12)),
    ("Vícar", -2.6421, 36.8310, "baja", (0, -12)),
    ("Roquetas", -2.6147, 36.7642, "alta", (0, 12)),
    ("Ríoja", -2.5444, 36.7444, "media", (12, 10)),
    ("Almería", -2.4637, 36.8340, "media", (0, -12)),
    ("Níjar", -2.2055, 36.9663, "baja", (-22, 0)),
    ("San José", -2.1069, 36.7589, None, (0, 12)),
    ("Carboneras", -1.8956, 36.9967, None, (0, -11)),
    ("Mojácar", -1.8489, 37.1403, "baja", (0, -11)),
    ("Garrucha", -1.8225, 37.1814, None, (12, 0)),
    ("Vera", -1.8569, 37.2461, None, (-12, -10)),
]

# Vista: Poniente + bahía de Almería + Cabo de Gata + Levante
LON_MIN, LON_MAX = -3.22, -1.76
LAT_MIN, LAT_MAX = 36.68, 37.30
W, H = 960, 620
PAD = 52

HEAT = {
    "muy_alta": ("#EF4444", 0.55, 54),
    "alta": ("#F97316", 0.45, 44),
    "media": ("#EAB308", 0.38, 34),
    "baja": ("#22C55E", 0.32, 26),
}

# Costa sur de Almería (oeste → este), con península de Cabo de Gata
COASTLINE_LONLAT = [
    (-3.18, 36.795),
    (-3.08, 36.748),
    (-3.02, 36.742),
    (-2.92, 36.732),
    (-2.82, 36.748),
    (-2.72, 36.756),
    (-2.62, 36.758),
    (-2.56, 36.748),
    (-2.50, 36.768),
    (-2.46, 36.812),
    (-2.44, 36.838),
    (-2.38, 36.828),
    (-2.28, 36.792),
    (-2.20, 36.758),
    (-2.17, 36.718),  # punta Cabo de Gata
    (-2.08, 36.748),
    (-2.00, 36.768),
    (-1.92, 36.820),
    (-1.90, 36.900),
    (-1.88, 36.980),
    (-1.84, 37.060),
    (-1.82, 37.130),
    (-1.80, 37.190),
    (-1.82, 37.250),
]

# Límite tierra (norte / interior) — este → oeste, cierra con la costa
INLAND_LONLAT = [
    (-1.82, 37.280),
    (-1.88, 37.120),
    (-2.00, 36.980),
    (-2.12, 36.920),
    (-2.28, 36.900),
    (-2.50, 36.890),
    (-2.72, 36.885),
    (-2.92, 36.875),
    (-3.08, 36.840),
    (-3.18, 36.810),
]

# Mar de plástico — Poniente (Adra → Roquetas)
PLASTIC_PONIENTE = [
    (-3.04, 36.815),
    (-2.58, 36.815),
    (-2.58, 36.738),
    (-3.04, 36.738),
]

# Invernaderos bahía de Almería (Ríoja / Aguadulce)
PLASTIC_ALMERIA = [
    (-2.58, 36.795),
    (-2.42, 36.795),
    (-2.42, 36.735),
    (-2.58, 36.735),
]


def project(lon: float, lat: float) -> tuple[float, float]:
    x = PAD + (lon - LON_MIN) / (LON_MAX - LON_MIN) * (W - 2 * PAD)
    y = PAD + 40 + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * (H - 2 * PAD - 56)
    return x, y


def poly_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    parts = [f"M {points[0][0]:.1f},{points[0][1]:.1f}"]
    parts.extend(f"L {x:.1f},{y:.1f}" for x, y in points[1:])
    return " ".join(parts)


def lonlat_poly(lonlats: list[tuple[float, float]], close: bool = False) -> str:
    pts = [project(lon, lat) for lon, lat in lonlats]
    path = poly_path(pts)
    if close and pts:
        path += " Z"
    return path


def heat_blob(x: float, y: float, level: str) -> str:
    color, opacity, r = HEAT[level]
    rings = ""
    for i, scale in enumerate((1.0, 0.72, 0.48)):
        rr = r * scale
        op = opacity * (0.85 - i * 0.2)
        rings += (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" '
            f'fill="{color}" fill-opacity="{op:.2f}"/>'
        )
    return rings


def main() -> None:
    coast_pts = [project(lon, lat) for lon, lat in COASTLINE_LONLAT]
    inland_pts = [project(lon, lat) for lon, lat in INLAND_LONLAT]
    land_fill = poly_path(coast_pts + inland_pts) + " Z"

    plastic_poniente = lonlat_poly(PLASTIC_PONIENTE, close=True)
    plastic_almeria = lonlat_poly(PLASTIC_ALMERIA, close=True)
    coast_stroke = poly_path(coast_pts)

    blobs = ""
    for name, lon, lat, level, _ in MUNICIPIOS:
        if level:
            x, y = project(lon, lat)
            blobs += heat_blob(x, y, level)

    labels = ""
    for name, lon, lat, level, (ox, oy) in MUNICIPIOS:
        x, y = project(lon, lat)
        weight = "700" if level in {"muy_alta", "alta"} else "500"
        fill = "#FFFFFF" if level else "#CBD5E1"
        tx, ty = x + ox, y + oy - 10
        labels += (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#00D2C4" '
            f'stroke="#0B192C" stroke-width="1"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
            f'font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="11" '
            f'font-weight="{weight}" fill="{fill}">{name}</text>'
        )

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img"
     aria-label="Mapa de calor de brotes fitosanitarios en el sur de Almería">
  <defs>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f2744"/>
      <stop offset="100%" stop-color="#071018"/>
    </linearGradient>
    <pattern id="grid" width="14" height="14" patternUnits="userSpaceOnUse">
      <path d="M 14 0 L 0 0 0 14" fill="none" stroke="#ffffff" stroke-opacity="0.06" stroke-width="0.6"/>
    </pattern>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#sea)"/>
  <path d="{land_fill}" fill="#1a3a2f" fill-opacity="0.88"/>
  <path d="{plastic_poniente}" fill="url(#grid)" fill-opacity="0.92" stroke="#ffffff" stroke-opacity="0.10"/>
  <path d="{plastic_almeria}" fill="url(#grid)" fill-opacity="0.85" stroke="#ffffff" stroke-opacity="0.10"/>
  <path d="{coast_stroke}" fill="none" stroke="#00D2C4" stroke-opacity="0.40" stroke-width="2"/>
  <g filter="url(#glow)">{blobs}</g>
  {labels}
  <g font-family="Plus Jakarta Sans, Arial, sans-serif">
    <text x="{PAD}" y="34" fill="#FFFFFF" font-size="20" font-weight="800">Sur de Almería</text>
    <text x="{PAD}" y="56" fill="#00A86B" font-size="13" font-weight="600">Mapa de calor de brotes · datos agregados por zona</text>
    <text x="{PAD}" y="{H-16}" fill="#94A3B8" font-size="10">De Adra a Vera · tu finca no se muestra, solo el paraje</text>
  </g>
  <g transform="translate({W-PAD-158},{H-PAD-128})">
    <rect width="158" height="118" rx="10" fill="#0B192C" fill-opacity="0.88" stroke="#334155"/>
    <text x="12" y="22" fill="#E2E8F0" font-size="11" font-weight="700">Intensidad</text>
    <circle cx="22" cy="42" r="7" fill="#EF4444"/><text x="36" y="46" fill="#CBD5E1" font-size="10">Muy alta</text>
    <circle cx="22" cy="62" r="6" fill="#F97316"/><text x="36" y="66" fill="#CBD5E1" font-size="10">Alta</text>
    <circle cx="22" cy="82" r="5" fill="#EAB308"/><text x="36" y="86" fill="#CBD5E1" font-size="10">Media</text>
    <circle cx="22" cy="102" r="4" fill="#22C55E"/><text x="36" y="106" fill="#CBD5E1" font-size="10">Baja</text>
  </g>
  <g transform="translate({PAD},{H-PAD-48})" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="9" fill="#64748B">
    <text x="0" y="0" fill="#00D2C4" font-size="10" font-weight="600">O</text>
    <line x1="10" y1="-2" x2="10" y2="-16" stroke="#64748B" stroke-width="1"/>
    <text x="6" y="-20">N</text>
    <text x="28" y="0">Poniente</text>
    <text x="420" y="0">Cabo de Gata</text>
    <text x="720" y="0">Levante</text>
  </g>
</svg>
"""
    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    print(f"SVG generado: {OUTPUT_SVG}")


if __name__ == "__main__":
    main()
