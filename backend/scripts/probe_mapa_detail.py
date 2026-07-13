"""Parse MAPA product detail for usos/dosis."""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120"})

# Spintor-like: search abamectina product
r = session.get(
    "https://servicio.mapa.gob.es/regfiweb/Productos/ProductosGrid",
    params={"NombreComercial": "spintor", "IdEstado": "1", "rows": "10"},
    timeout=60,
)
soup = BeautifulSoup(r.text, "html.parser")
for tr in soup.select("tbody tr"):
    btn = tr.select_one(".btnBuscarProductoId")
    if not btn:
        continue
    pid = btn.get("data-id")
    cells = [td.get_text(strip=True) for td in tr.find_all("td") if "d-none" not in (td.get("class") or [])]
    print("product", pid, cells[:4])

# detail for first spintor
r2 = session.get("https://servicio.mapa.gob.es/regfiweb/Productos/DetalleProducto/59724", timeout=60)
html = r2.text
( open := __import__("pathlib").Path(__file__).resolve().parents[1] / "data" / "mapa" / "detalle_sample.html" )
open.parent.mkdir(parents=True, exist_ok=True)
open.write_text(html, encoding="utf-8")
print("detail len", len(html))

s2 = BeautifulSoup(html, "html.parser")
for table in s2.find_all("table"):
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    if headers:
        print("table headers", headers[:10])
        for tr in table.select("tbody tr")[:2]:
            print("  row", [td.get_text(" ", strip=True)[:50] for td in tr.find_all("td")])

# grep grids in detail
for m in re.findall(r'data-url="([^"]+)"', html):
    print("data-url", m)
for m in re.findall(r'/regfiweb/[A-Za-z]+/[A-Za-z]+[^"\']*', html):
    if "Grid" in m or "Export" in m or "Usos" in m:
        print("path", m[:100])
