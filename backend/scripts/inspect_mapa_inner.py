"""Inspect MAPA Contenido inner JSON."""
from __future__ import annotations

import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "data" / "mapa" / "productos_autorizados.json"
outer = json.loads(path.read_text(encoding="utf-8"))
if isinstance(outer, str):
    outer = json.loads(outer)

print("fecha", outer.get("Fecha"), "tipo", outer.get("Tipo"))
inner = json.loads(outer["Contenido"])
print("inner type", type(inner).__name__)

if isinstance(inner, list):
    print("products", len(inner))
    sample = inner[0]
    print("keys", list(sample.keys()))
    print("sample", json.dumps(sample, ensure_ascii=False)[:800])
    # save small sample for tests
    out = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "mapa_productos_sample.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inner[:5], ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved fixture", out)

    # count with usos/cultivo
    with_usos = sum(1 for p in inner if p.get("Usos") or p.get("usos") or p.get("Autorizaciones"))
    print("with usos field", with_usos)

elif isinstance(inner, dict):
    print("inner keys", list(inner.keys())[:20])
