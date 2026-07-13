"""Transformación catálogo MAPA CEX → filas biocide_products."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

from app.data.plague_catalog import catalog_entries, normalize_plague
from app.mapa.config import DEFAULT_CALDO_L_HA

_CROP_ALIASES: dict[str, list[str]] = {
    "tomate": ["tomate", "tomates"],
    "pimiento": ["pimiento", "pimentón", "pimenton"],
    "pepino": ["pepino", "pepinos"],
    "calabacín": ["calabacín", "calabacin", "calabaza"],
    "berenjena": ["berenjena", "berenjenas"],
    "lechuga": ["lechuga", "lechugas"],
}

_PLAGUE_ALIASES: dict[str, list[str]] = {}


def _build_plague_aliases() -> dict[str, list[str]]:
    if _PLAGUE_ALIASES:
        return _PLAGUE_ALIASES

    for entry in catalog_entries():
        name = normalize_plague(entry["name"])
        if name == "sana":
            continue
        tokens = {name, normalize_plague(entry.get("scientific", ""))}
        if entry.get("eppo"):
            tokens.add(entry["eppo"].lower())
        parts = re.split(r"[,;/]", entry.get("scientific", ""))
        for part in parts:
            part = normalize_plague(part)
            if part:
                tokens.add(part)
        if name == "tuta absoluta":
            tokens.update({"lepidópteros", "lepidopteros", "polilla del tomate"})
        if name == "oruga":
            tokens.add("spodoptera")
        _PLAGUE_ALIASES[name] = sorted(t for t in tokens if t)
    return _PLAGUE_ALIASES


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _norm(value: str) -> str:
    return _strip_accents((value or "").strip().lower())


def _match_crop(cultivo: str) -> str | None:
    cultivo_n = _norm(cultivo)
    for crop, aliases in _CROP_ALIASES.items():
        if any(alias in cultivo_n for alias in aliases):
            return crop
    return None


def _match_plague(agente: str) -> str | None:
    agente_n = _norm(agente)
    for plague, aliases in _build_plague_aliases().items():
        if any(alias in agente_n for alias in aliases):
            return plague
    return None


def _parse_safety_hours(plazo: Any) -> int:
    text = str(plazo or "").strip().upper()
    if not text or text in {"NP", "N/P", "-", "N.A.", "NA"}:
        return 48
    match = re.search(r"(\d+)", text)
    if not match:
        return 48
    days = int(match.group(1))
    return max(days * 24, 24)


def _dose_to_l_ha(dose: float, unit: str, caldo_l_ha: float = DEFAULT_CALDO_L_HA) -> float | None:
    unit_n = _norm(unit)
    if dose <= 0:
        return None
    if unit_n in {"l/ha", "l ha", "litros/ha"}:
        return dose
    if unit_n in {"cc/hl", "ml/hl", "cm3/hl"}:
        # mL producto por 100 L de caldo → L/ha con volumen de caldo dado
        ml_per_ha = dose * (caldo_l_ha / 100.0)
        return ml_per_ha / 1000.0
    if unit_n in {"kg/ha", "g/ha"}:
        # No convertible a L/ha sin densidad; se ignora en dosis automática
        return None
    if unit_n == "%":
        return None
    return None


def _active_substance(composicion: list[dict[str, Any]]) -> str | None:
    if not composicion:
        return None
    first = composicion[0]
    return (first.get("Nombre Sustancia") or first.get("NombreSustancia") or "").strip() or None


def _registry_no(raw: str) -> str:
    return re.sub(r"\s+", "", (raw or "").strip())


def transform_cex_productos(
    productos: list[dict[str, Any]],
    *,
    synced_at: datetime | None = None,
) -> list[dict[str, Any]]:
    """Filtra usos MAPA al catálogo NEXO (cultivo/plaga Poniente)."""
    synced_at = synced_at or datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for product in productos:
        datos = product.get("DATOSPRODUCTO") or {}
        estado = (datos.get("Estado") or "").strip()
        if estado and estado.lower() != "vigente":
            continue

        registry = _registry_no(datos.get("Num_Registro") or datos.get("NumRegistro") or "")
        name = (datos.get("Nombre") or "").strip()
        if not registry or not name:
            continue

        composicion = product.get("COMPOSICION") or []
        active = _active_substance(composicion)
        mapa_product_id = datos.get("IdProducto")

        for uso in product.get("USOS") or []:
            crop = _match_crop(uso.get("Cultivo") or "")
            plague = _match_plague(uso.get("Agente") or "")
            if not crop or not plague:
                continue

            key = (registry, plague, crop)
            if key in seen:
                continue
            seen.add(key)

            dose_min_raw = float(uso.get("Dosis_Min") or 0)
            dose_max_raw = float(uso.get("Dosis_Max") or 0)
            unit = (uso.get("Unidad Medida dosis") or uso.get("UnidadMedidaDosis") or "").strip()
            dose_min = _dose_to_l_ha(dose_min_raw, unit)
            dose_max = _dose_to_l_ha(dose_max_raw, unit) if dose_max_raw else dose_min

            if dose_min is None and dose_max is None:
                # Sin conversión a L/ha: estimación conservadora para cc/hl con caldo estándar
                dose_min = _dose_to_l_ha(dose_min_raw or dose_max_raw, unit or "cc/hl")
                dose_max = dose_min

            if dose_min is None:
                dose_min = 0.01
            if dose_max is None or dose_max < dose_min:
                dose_max = dose_min

            rows.append(
                {
                    "mapa_product_id": mapa_product_id,
                    "registry_no": registry,
                    "name": name,
                    "active_substance": active,
                    "plague": plague,
                    "crop": crop,
                    "dose_min_l_ha": round(dose_min, 4),
                    "dose_max_l_ha": round(dose_max, 4),
                    "dose_unit": unit or None,
                    "agent_name": (uso.get("Agente") or "").strip() or None,
                    "safety_hours": _parse_safety_hours(uso.get("Plazo Seguridad")),
                    "synced_at": synced_at,
                    "source": "mapa_cex",
                    "product_status": estado or "vigente",
                }
            )

    return rows
