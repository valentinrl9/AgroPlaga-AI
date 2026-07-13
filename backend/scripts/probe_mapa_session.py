"""Probe MAPA ExportJson with session cookies."""
from __future__ import annotations

import json

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "es-ES,es;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
}
PRODUCT_DTO = (
    '{"nombreComercial":"","titular":"","numRegistro":"","fabricante":"",'
    '"idSustancia":null,"idAmbito":null,"idPlaga":null,"idFuncion":null,'
    '"idEstado":"1","idCultivo":null,"idSistemaCultivo":null,"idTipoUsuario":null,'
    '"ancestros":false,"fecRenoDesde":"","fecRenoHasta":"","fecInscDesde":"",'
    '"fecInscHasta":"","fecModiDesde":"","fecModiHasta":"","fecCaduDesde":"",'
    '"fecCaduHasta":"","fecLimiDesde":"","fecLimiHasta":""}'
)

session = requests.Session()
session.headers.update(HEADERS)

home = session.get("https://servicio.mapa.gob.es/regfiweb/", timeout=60)
print("home", home.status_code, "cookies", len(session.cookies))

urls = [
    "https://servicio.mapa.gob.es/regfiweb/Exportaciones/ExportJson",
    "https://servicio.mapa.gob.es/regfiweb/Exportaciones/ExportarJson",
]
for url in urls:
    r = session.post(
        url,
        data={"tipoExportacion": "Productos", "dataDto": PRODUCT_DTO},
        headers={"Referer": "https://servicio.mapa.gob.es/regfiweb/"},
        timeout=120,
    )
    print(url, "->", r.status_code, r.headers.get("content-type"), len(r.content))
    if r.status_code == 200:
        try:
            data = r.json()
            print("  keys", list(data.keys()) if isinstance(data, dict) else type(data))
            if isinstance(data, dict) and data.get("Contenido"):
                inner = json.loads(data["Contenido"])
                print("  products", len(inner))
                print("  sample keys", list(inner[0].keys())[:15])
        except Exception as exc:
            print("  parse err", exc, r.text[:200])

# ProductosGrid pagination
grid = session.get(
    "https://servicio.mapa.gob.es/regfiweb/Productos/ProductosGrid",
    params={
        "IdEstado": "1",
        "IdCultivo": "-1",
        "IdPlaga": "-1",
        "page": "1",
        "rows": "50",
    },
    headers={"Referer": "https://servicio.mapa.gob.es/regfiweb/"},
    timeout=60,
)
print("grid", grid.status_code, len(grid.text), grid.text[:300])
