#!/usr/bin/env python3
"""
Paso 5 (presupuesto 0 €): importar datos, reentrenar y evaluar.

Orden:
  1. sync semilla → extra_data
  2. PlantDoc + IP102 + datasets públicos (Mendeley)
  3. EPPO + iNaturalist → semilla → sync de nuevo
  4. Eval baseline TFLite
  5. Reentreno v1.6
  6. Eval modelo nuevo

Uso:
  python ml/scripts/run_paso5_zero_budget.py
  python ml/scripts/run_paso5_zero_budget.py --skip-train
  python ml/scripts/run_paso5_zero_budget.py --skip-fetch
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ML_DIR = ROOT / "ml"
PYTHON = sys.executable


def _run(cmd: list[str], label: str) -> bool:
    print(f"\n{'=' * 60}\n>>> {label}\n{'=' * 60}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"AVISO: {label} terminó con código {result.returncode}")
        return False
    return True


def _load_eppo_key() -> bool:
    if os.environ.get("EPPO_API_KEY", "").strip():
        return True
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("EPPO_API_KEY=") and line.split("=", 1)[1].strip():
                return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline paso 5 — datos 0 € + reentreno")
    parser.add_argument("--skip-fetch", action="store_true", help="No descargar EPPO/iNaturalist/Mendeley")
    parser.add_argument("--skip-train", action="store_true", help="Solo importar datos y evaluar baseline")
    parser.add_argument("--max-per-class", type=int, default=250)
    parser.add_argument("--epochs", type=int, default=18)
    args = parser.parse_args()

    log: dict = {"started_at": datetime.now(timezone.utc).isoformat(), "steps": []}

    def step(name: str, ok: bool) -> None:
        log["steps"].append({"name": name, "ok": ok})

    step("sync_semilla_1", _run([PYTHON, "ml/scripts/sync_semilla_to_extra.py"], "Sync semilla -> extra_data (1)"))

    if not args.skip_fetch:
        step("plantdoc", _run(
            [PYTHON, "ml/import_extra_data.py", "--plantdoc", "--max-per-class", "80"],
            "Import PlantDoc",
        ))
        ip102_dir = ML_DIR / "datasets" / "ip102" / "ip102_v1.1"
        if ip102_dir.exists():
            step("ip102", _run(
                [
                    PYTHON, "ml/import_extra_data.py", "--ip102",
                    "--ip102-dir", str(ip102_dir),
                    "--max-per-class", "80",
                ],
                "Import IP102",
            ))
        else:
            print("IP102 no encontrado en ml/datasets/ip102/ip102_v1.1 — omitido")
            step("ip102", False)

        step("public_datasets", _run(
            [PYTHON, "ml/scripts/import_public_datasets.py", "--all", "--max-per-class", "80"],
            "Import datasets públicos (Mendeley/Zenodo)",
        ))

        if _load_eppo_key():
            step("eppo", _run(
                [
                    PYTHON, "ml/scripts/fetch_eppo_photos.py", "--all",
                    "--skip-existing", "--max-per-subfolder", "25",
                ],
                "Descarga fotos EPPO -> semilla",
            ))
        else:
            print("EPPO_API_KEY no configurada — omitido")
            step("eppo", False)

        step("inaturalist", _run(
            [
                PYTHON, "ml/scripts/fetch_inaturalist.py", "--critical",
                "--max-per-subfolder", "25",
            ],
            "Descarga iNaturalist (plagas críticas)",
        ))

        step("sync_semilla_2", _run([PYTHON, "ml/scripts/sync_semilla_to_extra.py"], "Sync semilla -> extra_data (2)"))

    step("audit", _run([PYTHON, "ml/scripts/audit_extra_data.py"], "Auditoría extra_data"))

    reports_dir = ML_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    baseline_out = reports_dir / "eval_baseline_paso5.json"

    step("eval_baseline", _run(
        [PYTHON, "ml/evaluate_plagascan.py", "--output", str(baseline_out)],
        "Evaluación modelo actual (baseline)",
    ))

    if not args.skip_train:
        experiment_dir = ML_DIR / "models" / "experiments" / "paso5"
        step("train", _run(
            [
                PYTHON, "ml/train_plagascan.py",
                "--epochs", str(args.epochs),
                "--head-epochs", "12",
                "--max-per-class", str(args.max_per_class),
                "--fine-tune",
                "--balance",
                "--model-version", "v1.6-tflite-paso5",
                "--output-dir", str(experiment_dir),
            ],
            "Reentrenamiento PlagaScan (experimento, no despliega en APK)",
        ))
        step("eval_new", _run(
            [
                PYTHON, "ml/evaluate_plagascan.py",
                "--model", str(experiment_dir / "plaga_model.tflite"),
                "--output", str(reports_dir / "eval_paso5.json"),
            ],
            "Evaluación modelo reentrenado",
        ))

    log["finished_at"] = datetime.now(timezone.utc).isoformat()
    log_path = reports_dir / "paso5_run.json"
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nLog guardado en {log_path}")

    if baseline_out.exists():
        report = json.loads(baseline_out.read_text(encoding="utf-8"))
        print(f"\nBaseline top-1: {report.get('top1_accuracy', 0):.2%}")
        print(f"Baseline top-6 top-1: {report.get('top6_top1_accuracy', 0):.2%}")

    new_out = reports_dir / "eval_paso5.json"
    if new_out.exists():
        report = json.loads(new_out.read_text(encoding="utf-8"))
        print(f"Nuevo top-1: {report.get('top1_accuracy', 0):.2%}")
        print(f"Nuevo top-6 top-1: {report.get('top6_top1_accuracy', 0):.2%}")


if __name__ == "__main__":
    main()
