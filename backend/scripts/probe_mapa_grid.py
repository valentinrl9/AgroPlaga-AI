"""Inspect ProductosGrid HTML structure."""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120",
        "Accept-Language": "es-ES,es;q=0.9",
    }
)

def fetch_grid(**params):
    defaults = {
        "IdEstado": "1",
        "IdCultivo": "-1",
        "IdPlaga": "-1",
        "page": "1",
        "rows": "5",
    }
    defaults.update(params)
    r = session.get(
        "https://servicio.mapa.gob.es/regfiweb/Productos/ProductosGrid",
        params=defaults,
        timeout=60,
    )
    return r.text

html = fetch_grid(rows=5)
soup = BeautifulSoup(html, "html.parser")
table = soup.find("table", id="tbProductos")
print("rows attr", table.get("data-rows") if table else None)
for tr in soup.select("tbody tr")[:3]:
    print("---")
    print("attrs", tr.attrs)
    print("cells", [td.get_text(strip=True)[:40] for td in tr.find_all("td")])

# filtered tomate
html2 = fetch_grid(IdCultivo="0103010301000000", rows=5)
soup2 = BeautifulSoup(html2, "html.parser")
table2 = soup2.find("table", id="tbProductos")
print("tomate rows", table2.get("data-rows") if table2 else None)

# product detail json guess
for path in [
    "https://servicio.mapa.gob.es/regfiweb/Productos/DetalleProductoJson/59724",
    "https://servicio.mapa.gob.es/regfiweb/Productos/GetProducto/59724",
    "https://servicio.mapa.gob.es/regfiweb/Productos/ObtenerProducto?idProducto=59724",
]:
    r = session.get(path, timeout=30)
    print(path.split("/")[-2:], r.status_code, r.headers.get("content-type", "")[:40], len(r.content))
