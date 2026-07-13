"""Extract CSRF and export flow from MAPA site."""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120"})

pages = [
    "https://servicio.mapa.gob.es/regfiweb/",
    "https://servicio.mapa.gob.es/regfiweb/Productos",
    "https://servicio.mapa.gob.es/regfiweb/Productos/Index",
    "https://servicio.mapa.gob.es/regfiweb/Resumenes",
    "https://servicio.mapa.gob.es/regfiweb/Resumenes/Index",
]
for url in pages:
    r = session.get(url, timeout=60)
    print(url.split("/")[-1] or "home", r.status_code, len(r.text))
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "__RequestVerificationToken"})
        if token:
            print("  token", token.get("value", "")[:30])
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "export" in href.lower() or "json" in href.lower() or "resumen" in href.lower():
                print("  link", href, a.get_text(strip=True)[:40])

js = session.get("https://servicio.mapa.gob.es/regfiweb/js/site.min.js", timeout=60).text
# extract export function chunk
idx = js.find("Exportaciones")
print("Exportaciones chunks:")
start = 0
while True:
    idx = js.find("Exportaciones", start)
    if idx < 0:
        break
    print(js[idx - 40 : idx + 200].replace("\n", " "))
    start = idx + 12

# search consulta cultivo paths
for pat in ["ConsultaCultivo", "ConsultaPlaga", "Buscador", "Resumen", "ExportJson", "exportJson"]:
    print(pat, js.find(pat))
