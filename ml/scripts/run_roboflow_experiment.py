#!/usr/bin/env python3
"""
Experimento Roboflow: importar recortes, reentrenar solo roboflow_*, evaluar vs baseline.

No pisa el modelo de producción salvo que superes el umbral con --deploy.

Uso:
  set ROBOFLOW_API_KEY=tu_clave
  python ml/scripts/run_roboflow_experiment.py
  python ml/scripts/run_roboflow_experiment.py --projects tomato-pest pestnu-aphids-whiteflies
  python ml/scripts/run_roboflow_experiment.py --skip-import   # ya importaste antes
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ML_DIR = ROOT / "ml"
PYTHON = sys.executable
ASSETS = ROOT / "frontend" / "assets" / "ml"
EXPERIMENT = ML_DIR / "models" / "experiments" / "roboflow"
REPORTS = ML_DIR / "reports"


def _run(cmd: list[str]) -> None:
    print("\n>>>", " ".join(cmd))
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def _read_top1(path: Path) -> float:
    if not path.exists():
        return 0.0
    return float(json.loads(path.read_text(encoding="utf-8")).get("top1_accuracy", 0.0))


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline experimento Roboflow")
    parser.add_argument("--projects", nargs="*", default=["tomato-pest"])
    parser.add_argument("--max-per-class", type=int, default=80)
    parser.add_argument("--epochs", type=int, default=18)
    parser.add_argument("--skip-import", action="store_true")
    parser.add_argument("--deploy-threshold", type=float, default=0.145)
    parser.add_argument("--deploy", action="store_true")
    args = parser.parse_args()

    baseline_top1 = _read_top1(REPORTS / "eval_baseline_paso5.json") or _read_top1(REPORTS / "eval_pre_curated.json")
    print(f"Baseline referencia top-1: {baseline_top1:.2%}")

    if not args.skip_import:
        import_cmd = [
            PYTHON,
            "ml/scripts/import_roboflow.py",
            "--max-per-class",
            str(args.max_per_class),
        ]
        for pid in args.projects:
            import_cmd.extend(["--project", pid])
        _run(import_cmd)

    _run([PYTHON, "ml/scripts/audit_extra_data.py"])

    _run(
        [
            PYTHON,
            "ml/evaluate_plagascan.py",
            "--model",
            str(ASSETS / "plaga_model.tflite"),
            "--output",
            str(REPORTS / "eval_pre_roboflow.json"),
        ]
    )

    EXPERIMENT.mkdir(parents=True, exist_ok=True)
    _run(
        [
            PYTHON,
            "ml/train_plagascan.py",
            "--roboflow-only",
            "--fine-tune",
            "--balance",
            "--epochs",
            str(args.epochs),
            "--max-per-class",
            str(args.max_per_class),
            "--output-dir",
            str(EXPERIMENT),
            "--model-version",
            "v1.6-tflite-roboflow",
        ]
    )

    _run(
        [
            PYTHON,
            "ml/evaluate_plagascan.py",
            "--model",
            str(EXPERIMENT / "plaga_model.tflite"),
            "--output",
            str(REPORTS / "eval_roboflow.json"),
        ]
    )

    new_top1 = _read_top1(REPORTS / "eval_roboflow.json")
    delta = new_top1 - baseline_top1
    summary = {
        "baseline_top1": baseline_top1,
        "roboflow_top1": new_top1,
        "delta_pp": round(delta * 100, 2),
        "projects": args.projects,
        "deployed": False,
    }

    if args.deploy and new_top1 >= args.deploy_threshold and new_top1 > baseline_top1:
        import shutil

        for name in ("plaga_model.tflite", "labels.txt", "model_metadata.json"):
            shutil.copy2(EXPERIMENT / name, ASSETS / name)
        summary["deployed"] = True
        print(f"\nDesplegado a {ASSETS} (top-1 {new_top1:.2%})")
    else:
        print(f"\nNo desplegado. Roboflow top-1={new_top1:.2%} vs baseline={baseline_top1:.2%} (umbral {args.deploy_threshold:.2%})")

    out = REPORTS / "roboflow_run.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Resumen: {out}")


if __name__ == "__main__":
    main()
