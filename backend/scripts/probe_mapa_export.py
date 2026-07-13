"""Probe MAPA ExportExcel and product grids."""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120"})

pid = "110634"  # SPINTOR 480 SC

for grid in [
    f"https://servicio.mapa.gob.es/regfiweb/Productos/FuncionesGrid?IdProducto={pid}",
    f"https://servicio.mapa.gob.es/regfiweb/Productos/SustanciasGrid?IdProducto={pid}",
    f"https://servicio.mapa.gob.es/regfiweb/Productos/UsosGrid?IdProducto={pid}",
    f"https://servicio.mapa.gob.es/regfiweb/Productos/CondicionesGrid?IdProducto={pid}",
    f"https://servicio.mapa.gob.es/regfiweb/Productos/CultivosGrid?IdProducto={pid}",
]:
    r = session.get(grid, timeout=60)
    name = grid.split("/")[-1]
    print(name, r.status_code, len(r.text))
    if r.status_code == 200 and "table" in r.text:
        s = BeautifulSoup(r.text, "html.parser")
        headers = [th.get_text(strip=True) for th in s.find_all("th")]
        print("  headers", headers[:12])
        tr = s.select("tbody tr")[0] if s.select("tbody tr") else None
        if tr:
            print("  row0", [td.get_text(" ", strip=True)[:40] for td in tr.find_all("td")][:8])

# ExportExcel
dto = (
    '{"nombreComercial":"","titular":"","numRegistro":"","fabricante":"",'
    '"idSustancia":null,"idAmbito":null,"idPlaga":null,"idFuncion":null,'
    '"idEstado":"1","idCultivo":null,"idSistemaCultivo":null,"idTipoUsuario":null,'
    '"ancestros":false,"fecRenoDesde":"","fecRenoHasta":"","fecInscDesde":"",'
    '"fecInscHasta":"","fecModiDesde":"","fecModiHasta":"","fecCaduDesde":"",'
    '"fecCaduHasta":"","fecLimiDesde":"","fecLimiHasta":""}'
)
for url in [
    "https://servicio.mapa.gob.es/regfiweb/Exportaciones/ExportExcel",
    "https://servicio.mapa.gob.es/regfiweb/Exportaciones/ExportarExcel",
]:
    r = session.post(
        url,
        data={"tipoExportacion": "Productos", "dataDto": dto},
        headers={"Referer": "https://servicio.mapa.gob.es/regfiweb/"},
        timeout=120,
    )
    print(url.split("/")[-1], r.status_code, r.headers.get("content-type"), len(r.content))

# read site.min.js for export strings
js = session.get("https://servicio.mapa.gob.es/regfiweb/js/site.min.js", timeout=60).text
for needle in ["ExportJson", "ExportExcel", "UsosGrid", "tipoExportacion", "idCultivo"]:
    idx = js.find(needle)
    print(needle, "found" if idx >= 0 else "missing", js[idx:idx+120] if idx >= 0 else "")
