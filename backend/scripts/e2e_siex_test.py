"""Prueba E2E del flujo SIEX contra API local."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8000"
EMAIL = "valentinruizleon@gmail.com"
PASS = "12345678"
SIGPAC = "04079A00100001"


def req(method: str, path: str, token: str | None = None, data: dict | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def ok(label: str, status: int, expect: int = 200) -> bool:
    mark = "OK" if status == expect else "FAIL"
    print(f"[{mark}] {label} -> HTTP {status}")
    return status == expect


def main() -> int:
    print("=== E2E SIEX (API) ===\n")

    status, tok = req("POST", "/api/v1/auth/login", data={"email": EMAIL, "password": PASS})
    if not ok("Login master", status):
        print(tok)
        return 1
    token = tok["access_token"]
    print(f"     Usuario: {EMAIL}\n")

    status, access = req("GET", "/api/v1/siex/access", token=token)
    ok("SIEX access", status)
    print(
        f"     has_access={access.get('has_access')}, "
        f"module={access.get('has_module')}, enterprise={access.get('has_enterprise')}\n"
    )

    status, zones = req("GET", "/api/v1/zones", token=token)
    if not ok("Listar zonas", status) or not zones:
        return 1
    zone_id = zones[0]["id"]
    print(f"     Zona: {zones[0].get('name')} (id={zone_id})\n")

    status, farms = req("GET", "/api/v1/farms", token=token)
    ok("Listar fincas", status)
    farm = next((f for f in farms if f.get("sigpac_code")), None)
    if farm:
        print(f"[OK] Finca existente con SIGPAC: {farm['name']} ({farm['sigpac_code']})\n")
        farm_id = farm["id"]
    else:
        status, farm = req(
            "POST",
            "/api/v1/farms",
            token=token,
            data={
                "name": "Invernadero E2E SIEX",
                "crop": "Tomate",
                "farm_type": "greenhouse",
                "zone_id": zone_id,
                "surface_m2": 5000,
                "sigpac_code": SIGPAC,
            },
        )
        if not ok("Crear finca SIGPAC", status, 201):
            print(farm)
            return 1
        farm_id = farm["id"]
        print(f"     Finca creada id={farm_id}, SIGPAC={farm['sigpac_code']}\n")

    status, scan = req(
        "POST",
        "/api/v1/scans",
        token=token,
        data={
            "crop": "Tomate",
            "plague": "tuta absoluta",
            "severity": "Moderado",
            "confidence": 0.85,
            "farm_id": farm_id,
        },
    )
    if not ok("Crear escaneo", status, 201):
        print(scan)
        return 1
    scan_id = scan["id"]
    print(f"     Scan id={scan_id}: {scan['plague']} en {scan['crop']}\n")

    status, treatment = req(
        "POST",
        "/api/v1/treatments",
        token=token,
        data={
            "farm_id": farm_id,
            "scan_id": scan_id,
            "product_name": "Producto E2E MAPA",
            "registry_number": "12345",
            "safety_hours": 48,
            "dose_ml": 250.0,
            "notes": "Prueba E2E SIEX",
        },
    )
    if not ok("Registrar tratamiento", status, 201):
        print(treatment)
        return 1
    entry_id = treatment.get("siex_entry_id")
    print(f"     siex_entry_id={entry_id}")
    print(f"     siex_message: {treatment.get('siex_message', '')}\n")
    if not entry_id:
        print("[FAIL] No se generó entrada SIEX")
        return 1

    status, entries = req("GET", "/api/v1/siex/entries", token=token)
    ok("Listar entradas SIEX (agricultor)", status)
    entry = next((e for e in entries if e["id"] == entry_id), None)
    if not entry:
        print("[FAIL] Entrada no encontrada en listado")
        return 1
    print(f"     Entrada #{entry_id}: status={entry['status']}, SIGPAC={entry['sigpac_code']}")
    print(f"     Plaga: {entry['plague']} | Producto: {entry['product_name']}")
    print(f"     Justificación (100 chars): {entry['justificacion'][:100]}...\n")

    status, pending = req("GET", "/api/v1/siex/entries/pending", token=token)
    ok("Cola pendientes perito", status)
    in_queue = entry_id in [p["id"] for p in pending]
    print(f"     En cola perito: {in_queue} (status={entry['status']})\n")

    if entry["status"] in {"pendiente_validacion", "registrado"}:
        status, validated = req(
            "PATCH",
            f"/api/v1/siex/entries/{entry_id}/validate",
            token=token,
            data={"action": "approve", "tech_notes": "Validado en prueba E2E"},
        )
        if ok("Validar entrada (perito)", status):
            print(f"     Nuevo status: {validated['status']}\n")

    status, export = req("GET", "/api/v1/siex/entries/export", token=token)
    ok("Export JSON validadas", status)
    print(f"     Export: {export.get('count')} entradas validadas\n")

    print("=== RESULTADO: FLUJO SIEX API OK ===")
    print("Panel web: http://localhost:5173/panel/siex")
    print("Swagger:   http://localhost:8000/docs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
