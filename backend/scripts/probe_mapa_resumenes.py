"""List MAPA Resumenes download links."""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120"})

for path in [
    "/regfiweb/Resumenes/Index",
    "/regfiweb/Resumenes/CuadernoExplotacion",
    "/regfiweb/Resumenes/ProductosAutorizados",
    "/regfiweb/Resumenes/DescripcionJson",
]:
    r = session.get("https://servicio.mapa.gob.es" + path, timeout=60)
    print(path, r.status_code)
    if r.status_code != 200:
        continue
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = a["href"]
        if text or "json" in href.lower() or "descarg" in href.lower():
            print(" ", text[:60], "->", href[:100])
    for inp in soup.find_all("input", type="hidden"):
        if "json" in (inp.get("id") or "").lower() or "export" in (inp.get("id") or "").lower():
            print(" hidden", inp.get("id"), inp.get("value"))
