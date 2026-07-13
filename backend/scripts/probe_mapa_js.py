"""Find MAPA AJAX endpoints from JS bundles."""
from __future__ import annotations

import re

import requests

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120"})

# fetch main layout scripts
home = session.get("https://servicio.mapa.gob.es/regfiweb/", timeout=60).text
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', home)
print("scripts", scripts)

for script in scripts[:8]:
    if not script.startswith("http"):
        script = "https://servicio.mapa.gob.es" + script
    js = session.get(script, timeout=60).text
    hits = set(re.findall(r"/regfiweb/[A-Za-z]+/[A-Za-z]+", js))
    export_hits = [h for h in hits if "Export" in h or "Grid" in h or "Detalle" in h or "Usos" in h]
    if export_hits:
        print(script.split("/")[-1], sorted(export_hits)[:20])

# detail partial
for url in [
    "https://servicio.mapa.gob.es/regfiweb/Productos/DetalleProducto/90625",
    "https://servicio.mapa.gob.es/regfiweb/Productos/DetalleProductoPartial/90625",
    "https://servicio.mapa.gob.es/regfiweb/Productos/GetDetalle/90625",
]:
    r = session.get(url, timeout=60)
    print(url.split("/")[-2:], r.status_code, len(r.text))
    if r.status_code == 200:
        for kw in ["Usos", "Cultivo", "Plaga", "Dosis", "Plazo", "json"]:
            if kw.lower() in r.text.lower():
                print("  has", kw)

# cultivo grid row id
r = session.get(
    "https://servicio.mapa.gob.es/regfiweb/Cultivos/CultivosGrid",
    params={"NombreComun": "tomate", "rows": "5"},
    timeout=60,
)
from bs4 import BeautifulSoup

s = BeautifulSoup(r.text, "html.parser")
for tr in s.select("tbody tr"):
    print("cultivo row", tr.get("data-id"), [td.get_text(strip=True)[:30] for td in tr.find_all("td")])
