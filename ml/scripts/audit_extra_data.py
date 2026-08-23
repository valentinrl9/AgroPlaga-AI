#!/usr/bin/env python3
"""Resumen de balance en ml/extra_data/."""

from __future__ import annotations

import sys
from pathlib import Path

ML_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_DIR))

from data_utils import audit_report, save_json  # noqa: E402


def main() -> None:
    report = audit_report()
    print(f"Total imágenes: {report['total']}")
    print(f"Mín/máx por clase: {report['min_count']} / {report['max_count']}")
    if report["missing_classes"]:
        print("Sin fotos:", ", ".join(report["missing_classes"]))
    print("\nPor clase:")
    for label, count in report["per_class"].items():
        print(f"  {label}: {count}")
    save_json(ML_DIR / "reports" / "extra_data_audit.json", report)


if __name__ == "__main__":
    main()
