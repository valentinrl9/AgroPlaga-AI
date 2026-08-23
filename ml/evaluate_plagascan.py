#!/usr/bin/env python3
"""Evalúa plaga_model.tflite (top-1, top-3, por clase)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

ML_DIR = Path(__file__).resolve().parent
ROOT = ML_DIR.parent
sys.path.insert(0, str(ML_DIR))

from data_utils import (  # noqa: E402
    ASSETS_DIR,
    cap_per_class,
    class_counts,
    iter_extra_image_paths,
    load_image_tensor,
    load_labels,
    save_json,
    stratified_split,
)

TOP6 = {"tuta absoluta", "trips", "mosca blanca", "arañuela roja", "mildiu", "botritis"}


def evaluate_tflite(
    model_path: Path,
    samples,
    labels: list[str],
) -> dict:
    interpreter = tf.lite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    y_true: list[int] = []
    top1_ok = 0
    top3_ok = 0
    per_class_total: dict[int, int] = {}
    per_class_top1: dict[int, int] = {}
    confusion: dict[str, dict[str, int]] = {label: {l: 0 for l in labels} for label in labels}

    for sample in samples:
        image = load_image_tensor(sample.path).numpy()
        image = np.expand_dims(image, axis=0).astype(np.float32)
        interpreter.set_tensor(input_details[0]["index"], image)
        interpreter.invoke()
        scores = interpreter.get_tensor(output_details[0]["index"])[0]
        order = np.argsort(scores)[::-1]
        pred_idx = int(order[0])
        true_idx = sample.label_index

        y_true.append(true_idx)
        per_class_total[true_idx] = per_class_total.get(true_idx, 0) + 1
        if pred_idx == true_idx:
            top1_ok += 1
            per_class_top1[true_idx] = per_class_top1.get(true_idx, 0) + 1
        if true_idx in order[:3]:
            top3_ok += 1

        true_label = labels[true_idx]
        pred_label = labels[pred_idx]
        confusion[true_label][pred_label] += 1

    total = len(samples)
    per_class_recall = {}
    for idx, label in enumerate(labels):
        n = per_class_total.get(idx, 0)
        if n == 0:
            per_class_recall[label] = None
        else:
            per_class_recall[label] = round(per_class_top1.get(idx, 0) / n, 4)

    top6_samples = [s for s in samples if s.label_name in TOP6]
    top6_top1 = 0
    top6_top3 = 0
    for sample in top6_samples:
        image = load_image_tensor(sample.path).numpy()
        image = np.expand_dims(image, axis=0).astype(np.float32)
        interpreter.set_tensor(input_details[0]["index"], image)
        interpreter.invoke()
        scores = interpreter.get_tensor(output_details[0]["index"])[0]
        order = np.argsort(scores)[::-1]
        if int(order[0]) == sample.label_index:
            top6_top1 += 1
        if sample.label_index in order[:3]:
            top6_top3 += 1

    return {
        "samples": total,
        "top1_accuracy": round(top1_ok / total, 4) if total else 0.0,
        "top3_accuracy": round(top3_ok / total, 4) if total else 0.0,
        "top6_top1_accuracy": round(top6_top1 / len(top6_samples), 4) if top6_samples else 0.0,
        "top6_top3_accuracy": round(top6_top3 / len(top6_samples), 4) if top6_samples else 0.0,
        "per_class_recall": per_class_recall,
        "class_counts": class_counts(samples),
        "confusion": confusion,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluar PlagaScan TFLite")
    parser.add_argument("--model", type=Path, default=ASSETS_DIR / "plaga_model.tflite")
    parser.add_argument("--max-per-class", type=int, default=300)
    parser.add_argument("--output", type=Path, default=ML_DIR / "reports" / "eval_latest.json")
    args = parser.parse_args()

    labels = load_labels()
    all_samples = cap_per_class(iter_extra_image_paths(), args.max_per_class)
    _, val_samples = stratified_split(all_samples, val_ratio=0.2)

    if not val_samples:
        raise SystemExit("No hay muestras de validación.")

    print(f"Evaluando {args.model.name} con {len(val_samples)} imágenes hold-out...")
    report = evaluate_tflite(args.model, val_samples, labels)
    report["model"] = str(args.model)
    save_json(args.output, report)

    print(f"Top-1: {report['top1_accuracy']:.2%}")
    print(f"Top-3: {report['top3_accuracy']:.2%}")
    print(f"Top-6 top-1: {report['top6_top1_accuracy']:.2%}")
    print(f"Top-6 top-3: {report['top6_top3_accuracy']:.2%}")
    print("\nRecall por clase:")
    for label, recall in report["per_class_recall"].items():
        if recall is None:
            print(f"  {label}: (sin muestras val)")
        else:
            print(f"  {label}: {recall:.2%}")


if __name__ == "__main__":
    main()
