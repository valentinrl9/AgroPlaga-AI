"""
Entrena PlagaScan (MobileNetV3) y exporta plaga_model.tflite.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import tensorflow as tf

ML_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_DIR))

from data_utils import (  # noqa: E402
    ASSETS_DIR,
    IMG_SIZE,
    balance_samples,
    cap_per_class,
    filter_semilla,
    iter_extra_image_paths,
    load_labels,
    samples_to_dataset,
    save_json,
    stratified_split,
)
from plague_catalog import PLANT_VILLAGE_TO_LABEL  # noqa: E402

LABELS_FILE = ASSETS_DIR / "labels.txt"
MODEL_FILE = ASSETS_DIR / "plaga_model.tflite"
METADATA_FILE = ASSETS_DIR / "model_metadata.json"
BACKUP_DIR = ML_DIR / "models"


def _build_model(num_classes: int, trainable_base: bool = False) -> tf.keras.Model:
    base = tf.keras.applications.MobileNetV3Small(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )
    base.trainable = trainable_base
    if trainable_base:
        for layer in base.layers[:-20]:
            layer.trainable = False

    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = base(inputs, training=trainable_base)
    x = tf.keras.layers.Dropout(0.35)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    lr = 5e-5 if trainable_base else 1e-3
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def _export_tflite(model: tf.keras.Model, output_path: Path) -> None:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    tflite_model = converter.convert()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(tflite_model)


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrenar PlagaScan y exportar TFLite")
    parser.add_argument("--epochs", type=int, default=18)
    parser.add_argument("--head-epochs", type=int, default=12)
    parser.add_argument("--max-per-class", type=int, default=250)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--extra-only", action="store_true")
    parser.add_argument("--semilla-only", action="store_true", help="Solo fotos semilla_* curadas")
    parser.add_argument("--fine-tune", action="store_true")
    parser.add_argument("--balance", action="store_true", help="Oversampling por clase en train")
    parser.add_argument("--model-version", type=str, default="v1.6-tflite")
    args = parser.parse_args()

    labels = load_labels()
    samples = cap_per_class(iter_extra_image_paths(), args.max_per_class)
    if args.semilla_only:
        samples = filter_semilla(samples)
        print(f"Modo semilla-only: {len(samples)} imágenes")

    if not samples:
        raise SystemExit("No hay imágenes para entrenar.")

    train_samples, val_samples = stratified_split(samples, val_ratio=0.2)
    if args.balance:
        train_samples = balance_samples(train_samples)

    print(f"Muestras train/val: {len(train_samples)} / {len(val_samples)}")

    train_ds = samples_to_dataset(train_samples, len(labels), training=True, batch_size=args.batch_size)
    val_ds = samples_to_dataset(val_samples, len(labels), training=False, batch_size=args.batch_size)

    model = _build_model(len(labels), trainable_base=False)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True, monitor="val_accuracy"),
        tf.keras.callbacks.ReduceLROnPlateau(patience=2, factor=0.5, min_lr=1e-6),
    ]

    head_epochs = min(args.head_epochs, args.epochs)
    print(f"Fase 1 — cabeza ({head_epochs} ep)...")
    history_head = model.fit(train_ds, validation_data=val_ds, epochs=head_epochs, callbacks=callbacks, verbose=1)

    history_tail = None
    remaining = max(0, args.epochs - head_epochs)
    if args.fine_tune and remaining > 0:
        print(f"Fase 2 — fine-tune ({remaining} ep)...")
        base_model = model.layers[1]
        base_model.trainable = True
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=5e-5),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        history_tail = model.fit(train_ds, validation_data=val_ds, epochs=remaining, callbacks=callbacks, verbose=1)

    val_acc = float(history_head.history.get("val_accuracy", [0])[-1])
    if history_tail is not None:
        val_acc = max(val_acc, float(max(history_tail.history.get("val_accuracy", [0]))))

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    LABELS_FILE.write_text("\n".join(labels) + "\n", encoding="utf-8")
    _export_tflite(model, MODEL_FILE)

    metadata = {
        "model_version": args.model_version,
        "architecture": "MobileNetV3Small",
        "input_size": IMG_SIZE,
        "labels": labels,
        "val_accuracy": round(val_acc, 4),
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "max_per_class": args.max_per_class,
        "fine_tune": args.fine_tune,
        "balance": args.balance,
        "semilla_only": args.semilla_only,
        "plant_village_mapping": PLANT_VILLAGE_TO_LABEL,
    }
    METADATA_FILE.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    save_json(ML_DIR / "reports" / "train_latest.json", metadata)
    print(f"Modelo exportado: {MODEL_FILE} ({MODEL_FILE.stat().st_size / 1024:.1f} KB)")
    print(f"Precision val (Keras): {val_acc:.2%}")


if __name__ == "__main__":
    main()
