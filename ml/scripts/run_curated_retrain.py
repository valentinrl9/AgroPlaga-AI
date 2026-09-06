#!/usr/bin/env python3
"""
Reentrena con datos curados (semilla/EPPO/iNat) y despliega solo si mejora el baseline.

Uso:
  python ml/scripts/run_curated_retrain.py
  python ml/scripts/run_curated_retrain.py --deploy-threshold 0.125
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ML_DIR = ROOT / "ml"
PYTHON = sys.executable
ASSETS = ROOT / "frontend" / "assets" / "ml"
EXPERIMENT = ML_DIR / "models" / "experiments" / "curated"
BASELINE_MODEL = ASSETS / "plaga_model.tflite"
REPORTS = ML_DIR / "reports"


def _run(cmd: list[str]) -> None:
    print("\n>>>", " ".join(cmd))
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def _read_top1(path: Path) -> float:
    if not path.exists():
        return 0.0
    return float(json.loads(path.read_text(encoding="utf-8")).get("top1_accuracy", 0.0))


def main() -> None:
    parser = argparse.ArgumentParser(description="Reentreno curated + deploy condicional")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--max-per-class", type=int, default=200)
    parser.add_argument("--deploy-threshold", type=float, default=0.125, help="Top-1 mínimo vs baseline")
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Copiar a frontend/assets/ml/ solo si supera el umbral",
    )
    args = parser.parse_args()

    baseline_report = REPORTS / "eval_baseline_paso5.json"
    baseline_top1 = _read_top1(baseline_report) or _read_top1(REPORTS / "eval_latest.json")

    _run([PYTHON, "ml/scripts/sync_semilla_to_extra.py"])

    _run(
        [
            PYTHON,
            "ml/evaluate_plagascan.py",
            "--model",
            str(BASELINE_MODEL),
            "--output",
            str(REPORTS / "eval_pre_curated.json"),
        ]
    )
    pre_top1 = _read_top1(REPORTS / "eval_pre_curated.json")
    if baseline_top1 <= 0:
        baseline_top1 = pre_top1
    print(f"Baseline top-1 referencia: {baseline_top1:.2%}")

    EXPERIMENT.mkdir(parents=True, exist_ok=True)
    _run(
        [
            PYTHON,
            "ml/train_plagascan.py",
            "--curated-only",
            "--fine-tune",
            "--balance",
            "--epochs",
            str(args.epochs),
            "--head-epochs",
            "10",
            "--max-per-class",
            str(args.max_per_class),
            "--model-version",
            "v1.6-tflite-curated",
            "--output-dir",
            str(EXPERIMENT),
        ]
    )

    eval_out = REPORTS / "eval_curated.json"
    _run(
        [
            PYTHON,
            "ml/evaluate_plagascan.py",
            "--model",
            str(EXPERIMENT / "plaga_model.tflite"),
            "--output",
            str(eval_out),
        ]
    )

    new_top1 = _read_top1(eval_out)
    threshold = max(args.deploy_threshold, baseline_top1)
    print(f"Nuevo top-1 curated: {new_top1:.2%} (umbral deploy: {threshold:.2%})")

    if args.deploy and new_top1 >= threshold:
        shutil.copy2(EXPERIMENT / "plaga_model.tflite", ASSETS / "plaga_model.tflite")
        shutil.copy2(EXPERIMENT / "model_metadata.json", ASSETS / "model_metadata.json")
        meta = json.loads((ASSETS / "model_metadata.json").read_text(encoding="utf-8"))
        meta["eval_holdout_top1"] = round(new_top1, 4)
        meta["deployed_from"] = "run_curated_retrain.py"
        (ASSETS / "model_metadata.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print("DESPLEGADO en frontend/assets/ml/ (mejor o igual que baseline)")
    elif not args.deploy:
        print("Entrenamiento guardado en experiments/curated. Usa --deploy para publicar en APK.")
    else:
        print("No desplegado: el modelo curated no supera el baseline. Producción intacta.")


if __name__ == "__main__":
    main()
