"""Find Spintor and tomate+tuta in MAPA CEX JSON."""
from __future__ import annotations

import json
import re
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "data" / "mapa" / "productos_autorizados.json"
outer = json.loads(path.read_text(encoding="utf-8"))
if isinstance(outer, str):
    outer = json.loads(outer)
products = json.loads(outer["Contenido"])["Productos"]

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

for p in products:
    datos = p["DATOSPRODUCTO"]
    if "spintor 480" in norm(datos.get("Nombre", "")):
        print("SPINTOR", datos.get("Num_Registro"), datos.get("Nombre"))
        for u in p.get("USOS", []):
            if "tomate" in norm(u.get("Cultivo", "")):
                print(" uso", json.dumps(u, ensure_ascii=False))

for p in products:
    for u in p.get("USOS", []):
        if "tomate" in norm(u.get("Cultivo", "")) and "tuta" in norm(u.get("Agente", "")):
            d = p["DATOSPRODUCTO"]
            print("MATCH", d.get("Nombre"), d.get("Num_Registro"))
            print(" uso", json.dumps(u, ensure_ascii=False))
            raise SystemExit

print("no tuta+tomate match")
