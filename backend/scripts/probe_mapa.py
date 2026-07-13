"""Probe MAPA / Sanidad endpoints for ETL design."""
from __future__ import annotations

import json
import re
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "mapa"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "NEXO-Agro-ETL/1.0 (piloto; contacto@agroplaga-ai.farm)"}
EXPORT_URL = "https://servicio.mapa.gob.es/regfiweb/Exportaciones/ExportJson"

PRODUCT_DTO = (
    '{"nombreComercial":"","titular":"","numRegistro":"","fabricante":"",'
    '"idSustancia":null,"idAmbito":null,"idPlaga":null,"idFuncion":null,'
    '"idEstado":"1","idCultivo":null,"idSistemaCultivo":null,"idTipoUsuario":null,'
    '"ancestros":false,"fecRenoDesde":"","fecRenoHasta":"","fecInscDesde":"",'
    '"fecInscHasta":"","fecModiDesde":"","fecModiHasta":"","fecCaduDesde":"",'
    '"fecCaduHasta":"","fecLimiDesde":"","fecLimiHasta":""}'
)


def probe_export(tipo: str, data_dto: str | None = None) -> None:
    payload = {"tipoExportacion": tipo, "dataDto": data_dto or PRODUCT_DTO}
    r = requests.post(EXPORT_URL, data=payload, timeout=120, headers=HEADERS)
    print(f"export {tipo!r} -> {r.status_code} {r.headers.get('content-type','')} len={len(r.content)}")
    if r.status_code != 200:
        return
    try:
        outer = r.json()
    except Exception as exc:
        print("  not json:", exc)
        (OUT / f"export_{tipo}_raw.txt").write_bytes(r.content)
        return
    (OUT / f"export_{tipo}_outer.json").write_text(json.dumps(outer, ensure_ascii=False, indent=2)[:200000], encoding="utf-8")
    contenido = outer.get("Contenido") if isinstance(outer, dict) else None
    if contenido:
        inner = json.loads(contenido) if isinstance(contenido, str) else contenido
        if isinstance(inner, list):
            print(f"  items={len(inner)} keys={list(inner[0].keys())[:12] if inner else []}")
            (OUT / f"export_{tipo}_sample.json").write_text(
                json.dumps(inner[:3], ensure_ascii=False, indent=2), encoding="utf-8"
            )
        else:
            print(f"  inner type={type(inner).__name__}")


def probe_regfiweb() -> None:
    r = requests.get("https://servicio.mapa.gob.es/regfiweb/", timeout=60, headers=HEADERS)
    print("regfiweb", r.status_code, len(r.text))


def probe_sanidad() -> None:
    url = "https://www.sanidad.gob.es/ciudadanos/productos.do?tipo=biocidas"
    r = requests.get(url, timeout=60, headers=HEADERS)
    print("sanidad", r.status_code, len(r.text))
    print("  realizarBusqueda:", "realizarBusqueda" in r.text)


if __name__ == "__main__":
    probe_regfiweb()
    for tipo in ["Productos", "Usos", "Cultivos", "Plagas", "Agentes", "Autorizaciones"]:
        probe_export(tipo)
    # Tomate + tuta filter attempt (MAPA cultivo tomate)
    tomate_dto = PRODUCT_DTO.replace('"idCultivo":null', '"idCultivo":"0103010301000000"')
    probe_export("Productos", tomate_dto)
    probe_sanidad()
