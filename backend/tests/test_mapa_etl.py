"""Tests ETL MAPA CEX."""

from __future__ import annotations

import json
from pathlib import Path

from app.mapa.transform import transform_cex_productos

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "mapa_productos_sample.json"


def test_transform_matches_tuta_tomate():
    productos = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = transform_cex_productos(productos)

    tuta_rows = [r for r in rows if r["plague"] == "tuta absoluta" and r["crop"] == "tomate"]
    assert len(tuta_rows) >= 2
    delfin = next(r for r in tuta_rows if r["registry_no"] == "19159")
    assert delfin["name"] == "DELFIN"


def test_transform_matches_lepidopteros_as_oruga_or_tuta():
    productos = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = transform_cex_productos(productos)

    spintor = [r for r in rows if r["registry_no"] == "22839"]
    assert len(spintor) == 1
    assert spintor[0]["crop"] == "tomate"
    assert spintor[0]["plague"] == "tuta absoluta"
    assert spintor[0]["dose_min_l_ha"] == 0.2
    assert spintor[0]["safety_hours"] == 72


def test_transform_cc_hl_to_l_ha():
    productos = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = transform_cex_productos(productos)
    spintor = next(r for r in rows if r["registry_no"] == "22839")
    assert spintor["dose_unit"] == "cc/hl"
    assert spintor["dose_max_l_ha"] == 0.25
