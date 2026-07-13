"""Probe ExportExcel response and Spintor detail."""
from __future__ import annotations

import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120"})

# warm product search page
session.get("https://servicio.mapa.gob.es/regfiweb/Productos", timeout=60)

dto = (
    '{"nombreComercial":"spintor","titular":"","numRegistro":"","fabricante":"",'
    '"idSustancia":null,"idAmbito":null,"idPlaga":null,"idFuncion":null,'
    '"idEstado":"1","idCultivo":null,"idSistemaCultivo":null,"idTipoUsuario":null,'
    '"ancestros":false,"fecRenoDesde":"","fecRenoHasta":"","fecInscDesde":"",'
    '"fecInscHasta":"","fecModiDesde":"","fecModiHasta":"","fecCaduDesde":"",'
    '"fecCaduHasta":"","fecLimiDesde":"","fecLimiHasta":""}'
)

r = session.post(
    "https://servicio.mapa.gob.es/regfiweb/Exportaciones/ExportExcel",
    data={"tipoExportacion": "Productos", "dataDto": dto},
    headers={"Referer": "https://servicio.mapa.gob.es/regfiweb/Productos"},
    timeout=120,
)
out = Path(__file__).resolve().parents[1] / "data" / "mapa" / "export_spintor.xlsx"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(r.content)
print("excel", r.status_code, len(r.content), "saved", out)

# detail spintor
html = session.get("https://servicio.mapa.gob.es/regfiweb/Productos/DetalleProducto/110634", timeout=60).text
Path(__file__).resolve().parents[1].joinpath("data", "mapa", "spintor_detail.html").write_text(html, encoding="utf-8")
s = BeautifulSoup(html, "html.parser")
print("h2/h3", [x.get_text(strip=True) for x in s.find_all(["h2", "h3", "h4"])[:15]])
for m in re.findall(r'data-url="([^"]+)"', html):
    print("grid url", m)

# try export from detail
for tipo in ["Usos", "Condiciones", "Autorizaciones", "Productos"]:
    rr = session.post(
        "https://servicio.mapa.gob.es/regfiweb/Exportaciones/ExportExcel",
        data={"tipoExportacion": tipo, "dataDto": f'{{"idProducto":"{110634}"}}'},
        headers={"Referer": f"https://servicio.mapa.gob.es/regfiweb/Productos/DetalleProducto/110634"},
        timeout=120,
    )
    print("export", tipo, rr.status_code, len(rr.content))
