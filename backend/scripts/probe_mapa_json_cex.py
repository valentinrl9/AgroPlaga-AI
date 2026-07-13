"""Probe MAPA ExportJsonProductosAutorizados."""
from __future__ import annotations

import json
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "mapa"
OUT.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120"})

# warm resumenes page
session.get("https://servicio.mapa.gob.es/regfiweb/Resumenes/Index", timeout=60)

url = "https://servicio.mapa.gob.es/regfiweb/Exportaciones/ExportJsonProductosAutorizados"
for method, kwargs in [
    ("GET", {}),
    ("POST", {"data": {}}),
    ("POST", {"data": {"tipoExportacion": "ProductosAutorizados"}}),
]:
    r = session.request(method, url, timeout=180, headers={"Referer": "https://servicio.mapa.gob.es/regfiweb/Resumenes/Index"}, **kwargs)
    print(method, r.status_code, r.headers.get("content-type"), len(r.content))
    if r.status_code == 200 and len(r.content) > 100:
        path = OUT / "productos_autorizados.json"
        path.write_bytes(r.content)
        try:
            data = r.json()
            print(" json type", type(data).__name__)
            if isinstance(data, list):
                print(" items", len(data), "keys", list(data[0].keys())[:20] if data else [])
            elif isinstance(data, dict):
                print(" keys", list(data.keys())[:20])
                for k, v in data.items():
                    if isinstance(v, list):
                        print(" ", k, "len", len(v))
                        if v:
                            print("  sample", list(v[0].keys())[:20] if isinstance(v[0], dict) else v[0])
        except Exception as exc:
            print(" parse", exc, r.text[:300])
