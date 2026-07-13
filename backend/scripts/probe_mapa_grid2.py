"""Deep inspect MAPA grid rows and usos."""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"})

r = session.get(
    "https://servicio.mapa.gob.es/regfiweb/Productos/ProductosGrid",
    params={"IdEstado": "1", "page": "1", "rows": "3"},
    timeout=60,
)
html = r.text
soup = BeautifulSoup(html, "html.parser")
tr = soup.select("tbody tr")[0]
print(tr.prettify()[:2500])

# all hrefs
for a in soup.find_all("a", href=True)[:10]:
    print("link", a.get("href"), a.get("data-id"), a.get_text(strip=True)[:30])

# try usos endpoints
for url in [
    "https://servicio.mapa.gob.es/regfiweb/Usos/UsosGrid?idProducto=59724",
    "https://servicio.mapa.gob.es/regfiweb/Productos/UsosGrid/59724",
    "https://servicio.mapa.gob.es/regfiweb/Productos/UsosProductoGrid/59724",
    "https://servicio.mapa.gob.es/regfiweb/Autorizaciones/AutorizacionesGrid?idProducto=59724",
]:
    rr = session.get(url, timeout=30)
    print(url.split("regfiweb/")[-1], rr.status_code, len(rr.text))
    if rr.status_code == 200 and len(rr.text) > 200:
        print(rr.text[:400])

# cultivo filter like web UI
r2 = session.get(
    "https://servicio.mapa.gob.es/regfiweb/Productos/ProductosGrid",
    params={
        "NombreComercial": "",
        "Titular": "",
        "NumRegistro": "",
        "Fabricante": "",
        "IdSustancia": "-1",
        "IdEstado": "1",
        "IdAmbito": "-1",
        "IdPlaga": "-1",
        "IdFuncion": "-1",
        "IdCultivo": "0103010301000000",
        "IdSistemaCultivo": "-1",
        "IdTipoUsuario": "-1",
        "Ancestros": "false",
        "page": "1",
        "rows": "5",
    },
    timeout=60,
)
s2 = BeautifulSoup(r2.text, "html.parser")
t2 = s2.find("table", id="tbProductos")
print("tomate filtered rows", t2.get("data-rows") if t2 else None)
