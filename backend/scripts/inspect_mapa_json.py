"""Inspect downloaded MAPA JSON structure."""
from __future__ import annotations

import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "data" / "mapa" / "productos_autorizados.json"
raw = path.read_text(encoding="utf-8")
print("raw len", len(raw))
data = json.loads(raw)
print("outer type", type(data).__name__)
if isinstance(data, str):
    data = json.loads(data)
    print("inner type", type(data).__name__)

if isinstance(data, dict):
    print("keys", list(data.keys())[:30])
    for k, v in list(data.items())[:8]:
        print(k, type(v).__name__, len(v) if hasattr(v, "__len__") else "")
elif isinstance(data, list):
    print("items", len(data))
    print("sample keys", list(data[0].keys())[:30])
    # find tomate + tuta entries
    for item in data[:5000]:
        txt = json.dumps(item, ensure_ascii=False).lower()
        if "tomate" in txt and ("tuta" in txt or "lyctde" in txt or "oper culella" in txt):
            print("match", {k: item[k] for k in list(item.keys())[:15]})
            break
