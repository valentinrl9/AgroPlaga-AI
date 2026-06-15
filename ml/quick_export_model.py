"""Exporta un modelo TFLite mínimo válido (15 clases, antes del entrenamiento completo)."""

import json
import sys
from pathlib import Path

import tensorflow as tf

ML_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_DIR))

from plague_catalog import LABELS  # noqa: E402

ROOT = ML_DIR.parent
ASSETS = ROOT / "frontend" / "assets" / "ml"
IMG_SIZE = 224


def main() -> None:
    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = tf.keras.layers.Rescaling(1.0 / 255.0)(inputs)
    base = tf.keras.applications.MobileNetV3Small(
        include_top=False, input_tensor=x, weights="imagenet", pooling="avg"
    )
    base.trainable = False
    outputs = tf.keras.layers.Dense(len(LABELS), activation="softmax")(base.output)
    model = tf.keras.Model(inputs, outputs)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "plaga_model.tflite").write_bytes(tflite_model)
    (ASSETS / "labels.txt").write_text("\n".join(LABELS) + "\n", encoding="utf-8")
    (ASSETS / "model_metadata.json").write_text(
        json.dumps(
            {
                "model_version": "v1.5-tflite-stub",
                "architecture": "MobileNetV3Small",
                "input_size": IMG_SIZE,
                "labels": LABELS,
                "note": "Modelo sin entrenar; ejecutar ml/train_plagascan.py para precisión real.",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Modelo base exportado ({len(tflite_model) / 1024:.1f} KB, {len(LABELS)} clases)")


if __name__ == "__main__":
    main()
