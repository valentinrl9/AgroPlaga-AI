"""Inspecciona campos de la API EPPO photos (solo nombres, sin volcar secretos)."""
from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.request
from pathlib import Path

try:
    import certifi

    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
CODE = sys.argv[1] if len(sys.argv) > 1 else "BOTRCI"


def _load_api_key() -> str:
    key = os.environ.get("EPPO_API_KEY")
    if key:
        return key
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("EPPO_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("Define EPPO_API_KEY en .env o entorno")


def main() -> None:
    api_key = _load_api_key()
    url = f"https://api.eppo.int/gd/v2/taxons/taxon/{CODE}/photos"
    req = urllib.request.Request(
        url,
        headers={"X-Api-Key": api_key, "Accept": "application/json", "User-Agent": "AgroPlaga-AI/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as response:
        payload = json.loads(response.read().decode("utf-8"))

    records = payload if isinstance(payload, list) else payload.get("photos", [])
    print(f"{CODE}: {len(records)} registros")
    if not records:
        return
    sample = records[0]
    print("Campos:", sorted(sample.keys()))
    for key in sorted(sample.keys()):
        val = sample[key]
        if isinstance(val, str) and val.startswith("http"):
            print(f"  URL field {key}: {val[:120]}")
        elif key == "files":
            print(f"  files sample: {json.dumps(val, ensure_ascii=False)[:500]}")
        elif key == "tags":
            print(f"  tags sample: {json.dumps(val, ensure_ascii=False)[:200]}")


if __name__ == "__main__":
    main()
