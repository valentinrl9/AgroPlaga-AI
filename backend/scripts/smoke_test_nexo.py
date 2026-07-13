"""Smoke test exhaustivo de la API NEXO (local)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field

BASE = "http://localhost:8000"
PASS = "nexo1234"

USERS = {
    "agricultor": "local.agricultor@nexo.test",
    "perito": "local.perito@nexo.test",
    "cooperativa": "local.cooperativa@nexo.test",
    "admin": "admin@example.com",
}


@dataclass
class Report:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def ok(self, label: str) -> None:
        self.passed.append(label)
        print(f"  [OK] {label}")

    def fail(self, label: str, detail: str) -> None:
        self.failed.append(f"{label}: {detail}")
        print(f"  [FAIL] {label} -> {detail[:120]}")

    def skip(self, label: str, reason: str) -> None:
        self.skipped.append(f"{label}: {reason}")
        print(f"  [SKIP] {label} -> {reason}")


def login(email: str, password: str = PASS) -> str | None:
    try:
        status, body = _req("POST", "/api/v1/auth/login", data={"email": email, "password": password})
        if status == 200 and isinstance(body, dict):
            return body["access_token"]
    except Exception as exc:
        return None
    return None


def _req(method: str, path: str, token: str | None = None, data=None, expect: int | None = None):
    headers = {}
    body_bytes = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body_bytes = json.dumps(data).encode()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(BASE + path, data=body_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=45) as resp:
            raw = resp.read().decode()
            parsed = json.loads(raw) if raw else None
            return resp.status, parsed
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return exc.code, parsed


def check_get(report: Report, label: str, path: str, token: str, expect=200) -> dict | list | None:
    status, body = _req("GET", path, token=token)
    if status == expect:
        report.ok(label)
        return body
    report.fail(label, f"HTTP {status} {body}")
    return None


def main() -> int:
    report = Report()
    print("=== SMOKE TEST EXHAUSTIVO NEXO API ===\n")

    # --- Auth & demo users ---
    print("[Auth & usuarios demo]")
    tokens: dict[str, str] = {}
    for role, email in USERS.items():
        pw = "admin1234" if role == "admin" else PASS
        tok = login(email, pw)
        if tok:
            tokens[role] = tok
            report.ok(f"Login {role} ({email})")
        else:
            report.fail(f"Login {role}", email)

    if "agricultor" not in tokens:
        print("\nBackend no disponible o usuarios demo ausentes.")
        return 1

    ag = tokens["agricultor"]
    tech = tokens.get("perito") or tokens.get("cooperativa") or tokens.get("admin")
    admin = tokens.get("admin") or tech

    # --- Perfil ---
    print("\n[Perfil]")
    profile = check_get(report, "GET /users/me", "/api/v1/users/me", ag)
    if profile and profile.get("role") != "farmer":
        report.fail("Rol agricultor demo", f"role={profile.get('role')}")

    # --- Field: zonas, plagas, fincas ---
    print("\n[Field — zonas, plagas, fincas]")
    zones = check_get(report, "GET /zones", "/api/v1/zones", ag)
    check_get(report, "GET /plagues", "/api/v1/plagues", ag)
    farms = check_get(report, "GET /farms", "/api/v1/farms", ag)

    farm_id = None
    if farms:
        farm_id = next((f["id"] for f in farms if f.get("sigpac_code")), None)
        if farm_id:
            report.ok(f"Finca con SIGPAC encontrada (id={farm_id})")
        else:
            report.skip("Finca SIGPAC", "crear finca manualmente en UI")

    # --- Escaneos ---
    print("\n[Field — escaneos]")
    scan_id = None
    payload = {
        "crop": "Tomate",
        "plague": "tuta absoluta",
        "severity": "Moderado",
        "confidence": 0.88,
        "farm_id": farm_id,
    }
    st, scan = _req("POST", "/api/v1/scans", token=ag, data=payload)
    if st == 201:
        scan_id = scan["id"]
        report.ok(f"POST /scans (id={scan_id})")
    else:
        report.fail("POST /scans", f"HTTP {st} {scan}")

    check_get(report, "GET /scans", "/api/v1/scans", ag)

    # --- Tratamientos MAPA ---
    print("\n[Field — tratamientos MAPA]")
    check_get(report, "GET /treatments/catalog/status", "/api/v1/treatments/catalog/status", ag)
    biocides = check_get(
        report,
        "GET /treatments/biocides",
        "/api/v1/treatments/biocides?plague=tuta%20absoluta&crop=Tomate",
        ag,
    )
    if biocides and len(biocides) > 0:
        reg = biocides[0]["registry_no"]
        st, dose = _req(
            "POST",
            "/api/v1/treatments/dose/calculate",
            token=ag,
            data={"surface_m2": 5000, "registry_no": reg, "plague": "tuta absoluta", "crop": "Tomate"},
        )
        if st == 200:
            report.ok(f"POST /treatments/dose/calculate ({dose.get('dose_ml')} ml)")
        else:
            report.fail("POST /treatments/dose/calculate", f"HTTP {st}")

        if farm_id:
            st, tr = _req(
                "POST",
                "/api/v1/treatments",
                token=ag,
                data={
                    "farm_id": farm_id,
                    "scan_id": scan_id,
                    "product_name": biocides[0]["name"],
                    "registry_number": reg,
                    "safety_hours": biocides[0].get("safety_hours", 48),
                    "dose_ml": dose.get("dose_ml") if isinstance(dose, dict) else 250,
                },
            )
            if st == 201:
                report.ok(f"POST /treatments (siex_entry={tr.get('siex_entry_id')})")
            else:
                report.fail("POST /treatments", f"HTTP {st} {tr}")
        else:
            report.skip("POST /treatments", "sin finca SIGPAC")
    else:
        report.skip("Tratamientos MAPA", "catálogo vacío — ejecutar ETL MAPA")

    check_get(report, "GET /treatments/active", "/api/v1/treatments/active", ag)

    # --- SIEX ---
    print("\n[SIEX]")
    access = check_get(report, "GET /siex/access", "/api/v1/siex/access", ag)
    if access and not access.get("has_access"):
        report.fail("SIEX access agricultor", "has_access=false")
    check_get(report, "GET /siex/entries", "/api/v1/siex/entries", ag)
    if tech:
        check_get(report, "GET /siex/entries/pending (perito)", "/api/v1/siex/entries/pending", tech)
        check_get(report, "GET /siex/entries/export", "/api/v1/siex/entries/export", ag)

    # --- Climate ---
    print("\n[Climate]")
    check_get(report, "GET /climate/access", "/api/v1/climate/access", ag)
    check_get(report, "GET /climate/health", "/api/v1/climate/health", ag)
    check_get(report, "GET /climate/actual", "/api/v1/climate/actual", ag)
    check_get(report, "GET /climate/prediccion", "/api/v1/climate/prediccion?dias=7", ag)
    check_get(report, "GET /climate/alertas", "/api/v1/climate/alertas", ag)
    check_get(report, "GET /climate/riesgo", "/api/v1/climate/riesgo?dias=7", ag)
    check_get(report, "GET /climate/recomendaciones", "/api/v1/climate/recomendaciones?dias=7", ag)

    # --- Mapa comunitario ---
    print("\n[Mapa comunitario]")
    check_get(report, "GET /heatmap", "/api/v1/heatmap?hours=168", ag)
    if zones and isinstance(zones, list) and zones:
        zid = zones[0]["id"]
        check_get(report, "GET /outbreak-events", f"/api/v1/outbreak-events?zone_id={zid}&hours=168", ag)

    # --- Alertas & analytics ---
    print("\n[Alertas & analítica]")
    check_get(report, "GET /alerts", "/api/v1/alerts", ag)
    check_get(report, "GET /alerts/preferences", "/api/v1/alerts/preferences", ag)
    check_get(report, "GET /analytics/me", "/api/v1/analytics/me", ag)
    check_get(report, "GET /community/profile", "/api/v1/community/profile", ag)
    check_get(report, "GET /stats/summary", "/api/v1/stats/summary", ag)

    # --- Perito / panel ---
    if tech:
        print("\n[Perito / panel enterprise]")
        check_get(report, "GET /tech/dashboard", "/api/v1/tech/dashboard?hours=168", tech)
        check_get(report, "GET /tech/pending-scans", "/api/v1/tech/pending-scans", tech)
        check_get(report, "GET /tech/farmers", "/api/v1/tech/farmers", tech)

    if admin:
        check_get(report, "GET /admin/users", "/api/v1/admin/users", admin)

    # --- Panel web static ---
    print("\n[Panel web]")
    try:
        with urllib.request.urlopen("http://localhost:5173/panel/", timeout=5) as resp:
            if resp.status == 200:
                report.ok("Panel Vite http://localhost:5173/panel/")
            else:
                report.fail("Panel Vite", f"HTTP {resp.status}")
    except Exception as exc:
        report.skip("Panel Vite", str(exc))

    # --- Resumen ---
    total = len(report.passed) + len(report.failed) + len(report.skipped)
    print("\n=== RESUMEN ===")
    print(f"  OK:    {len(report.passed)}")
    print(f"  FAIL:  {len(report.failed)}")
    print(f"  SKIP:  {len(report.skipped)}")
    print(f"  Total: {total}")

    if report.failed:
        print("\nFallos:")
        for item in report.failed:
            print(f"  - {item}")

    if report.skipped:
        print("\nOmitidos (no críticos o requieren UI/datos):")
        for item in report.skipped:
            print(f"  - {item}")

    print("\nNo automatizable en este script:")
    print("  - Cámara / TFLite escaneo en dispositivo")
    print("  - PDF Climate en Flutter")
    print("  - Navegación visual pestañas Field/Climate/SIEX")
    print("  - Validación escaneos con foto en panel web")

    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
