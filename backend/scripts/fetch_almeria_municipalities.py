"""Build Almería municipalities seed from INE CSV + GeoJSON centroids."""

from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from io import StringIO
from pathlib import Path

INE_CSV_URL = (
    "https://raw.githubusercontent.com/codeforspain/"
    "ds-organizacion-administrativa/master/data/municipios.csv"
)
GEOJSON_URL = (
    "https://raw.githubusercontent.com/codeforgermany/"
    "click_that_hood/master/public/data/spain-municipalities.geojson"
)
OUT = Path(__file__).resolve().parents[1] / "app" / "db" / "data" / "almeria_municipalities.json"

# Coordenadas de referencia (Poniente / costa) — prevalecen sobre GeoJSON.
KNOWN_COORDS: dict[str, tuple[float, float]] = {
    "04001": (-2.4597, 36.8381),  # Almería capital
    "04002": (-3.0203, 36.7486),  # Adra
    "04013": (-3.1333, 36.7833),  # Albuñol — legacy seed name
    "04058": (-2.9050, 36.7400),  # Balanegra (04904 en INE nuevo)
    "04070": (-2.9494, 36.8461),  # Berja
    "04079": (-2.8667, 36.8267),  # Dalías
    "04087": (-2.8144, 36.7763),  # El Ejido (04902)
    "04101": (-2.5444, 36.7444),  # Ríoja
    "04102": (-2.6154, 36.7640),  # Roquetas de Mar
    "04151": (-2.6421, 36.8310),  # Vícar
}


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "PlagaIA/1.0 (seed script)"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read().decode("utf-8")


def _load_ine_municipalities() -> list[dict[str, str]]:
    text = _fetch_text(INE_CSV_URL)
    rows: list[dict[str, str]] = []
    for row in csv.DictReader(StringIO(text)):
        if row["provincia_id"] != "04":
            continue
        rows.append(row)
    return rows


def _load_geo_centroids() -> dict[str, tuple[float, float]]:
    try:
        payload = json.loads(_fetch_text(GEOJSON_URL))
    except Exception:
        return {}

    centroids: dict[str, tuple[float, float]] = {}
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        code = str(props.get("codigo") or props.get("ine") or props.get("id") or "").zfill(5)
        if not code.startswith("04"):
            continue
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates")
        if not coords:
            continue
        if geometry.get("type") == "Point":
            lon, lat = coords[0], coords[1]
        else:
            # Primer anillo del polígono más externo.
            ring = coords[0] if geometry.get("type") == "Polygon" else coords[0][0]
            lon = sum(p[0] for p in ring) / len(ring)
            lat = sum(p[1] for p in ring) / len(ring)
        centroids[code] = (round(lon, 4), round(lat, 4))
    return centroids


def _normalize_name(name: str) -> str:
    cleaned = name.strip().strip('"')
    if cleaned.endswith(", El"):
        return f"El {cleaned[:-4].strip()}"
    if cleaned.endswith(", La"):
        return f"La {cleaned[:-4].strip()}"
    if cleaned.endswith(", Los"):
        return f"Los {cleaned[:-5].strip()}"
    if cleaned.endswith(", Las"):
        return f"Las {cleaned[:-5].strip()}"
    return cleaned


def main() -> None:
    ine_rows = _load_ine_municipalities()
    geo = _load_geo_centroids()

    rows: list[dict] = []
    for entry in ine_rows:
        code = entry["municipio_id"].zfill(5)
        name = _normalize_name(entry["nombre"])
        sigpac = f"04-{entry['cmun']}"
        if code in KNOWN_COORDS:
            lon, lat = KNOWN_COORDS[code]
        elif code in geo:
            lon, lat = geo[code]
        else:
            # Centro provincial aproximado (Almería).
            lon, lat = -2.45, 37.15
        rows.append(
            {
                "municipality_code": code,
                "sigpac_code": sigpac,
                "name": name,
                "province": "Almería",
                "lon": lon,
                "lat": lat,
            }
        )

    rows.sort(key=lambda item: item["name"].lower())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} municipalities to {OUT}")


if __name__ == "__main__":
    main()
