"""Inspect MAPA Productos array."""
from __future__ import annotations

import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "data" / "mapa" / "productos_autorizados.json"
outer = json.loads(path.read_text(encoding="utf-8"))
if isinstance(outer, str):
    outer = json.loads(outer)
inner = json.loads(outer["Contenido"])
products = inner["Productos"]
print("products", len(products))
sample = products[0]
print("keys", list(sample.keys()))
print("sample", json.dumps(sample, ensure_ascii=False)[:1200])

# find spintor
for p in products:
    name = (p.get("Nombre") or p.get("nombreComercial") or "").lower()
    if "spintor 480" in name:
        print("spintor keys", list(p.keys()))
        print(json.dumps(p, ensure_ascii=False)[:2000])
        break

# find tomate+tuta in usos
for p in products:
    usos = p.get("Usos") or p.get("usos") or []
    for u in usos if isinstance(usos, list) else []:
        blob = json.dumps(u, ensure_ascii=False).lower()
        if "tomate" in blob and "tuta" in blob:
            print("found uso product", p.get("Nombre") or p.get("NumRegistro"))
            print(json.dumps(u, ensure_ascii=False)[:500])
            raise SystemExit

out = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "mapa_productos_sample.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(products[:3], ensure_ascii=False, indent=2), encoding="utf-8")
