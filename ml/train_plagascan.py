"""
Entrena PlagaScan (MobileNetV3) con PlantVillage y exporta plaga_model.tflite.

Uso:
  pip install -r ml/requirements.txt
  python ml/train_plagascan.py --epochs 8 --max-per-class 120

Salida:
  frontend/assets/ml/plaga_model.tflite
  frontend/assets/ml/labels.txt  (15 clases Poniente Almeriense)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds

ML_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_DIR))

from plague_catalog import LABELS, PLANT_VILLAGE_TO_LABEL  # noqa: E402

ROOT = ML_DIR.parent
ASSETS_DIR = ROOT / "frontend" / "assets" / "ml"
LABELS_FILE = ASSETS_DIR / "labels.txt"
MODEL_FILE = ASSETS_DIR / "plaga_model.tflite"
METADATA_FILE = ASSETS_DIR / "model_metadata.json"

IMG_SIZE = 224
SEED = 42


def _label_to_index(label: str) -> int:
    return LABELS.index(label)


def _as_tf_datasets(
    train_images: list[tf.Tensor],
    train_labels: list[tf.Tensor],
    val_images: list[tf.Tensor],
    val_labels: list[tf.Tensor],
) -> tuple[tf.data.Dataset, tf.data.Dataset]:
    train_ds = (
        tf.data.Dataset.from_tensor_slices((tf.stack(train_images), tf.stack(train_labels)))
        .shuffle(512, seed=SEED)
        .batch(32)
        .prefetch(tf.data.AUTOTUNE)
    )
    val_ds = (
        tf.data.Dataset.from_tensor_slices((tf.stack(val_images), tf.stack(val_labels)))
        .batch(32)
        .prefetch(tf.data.AUTOTUNE)
    )
    return train_ds, val_ds


def _build_dataset_from_extra(max_per_class: int) -> tuple[tf.data.Dataset, tf.data.Dataset, int]:
    images, labels = _load_extra_data(max_per_class)
    if not images:
        raise RuntimeError("No hay imágenes en ml/extra_data/. Importa PlantDoc/IP102 primero.")

    indices = np.random.default_rng(SEED).permutation(len(images))
    split = max(1, int(len(indices) * 0.8))
    train_idx, val_idx = indices[:split], indices[split:]

    train_images = [images[i] for i in train_idx]
    train_labels = [labels[i] for i in train_idx]
    val_images = [images[i] for i in val_idx] if len(val_idx) else train_images[-8:]
    val_labels = [labels[i] for i in val_idx] if len(val_idx) else train_labels[-8:]

    train_ds, val_ds = _as_tf_datasets(train_images, train_labels, val_images, val_labels)
    return train_ds, val_ds, len(train_images)


def _load_extra_data(max_per_class: int) -> tuple[list[tf.Tensor], list[tf.Tensor]]:
    extra_dir = ROOT / "ml" / "extra_data"
    images: list[tf.Tensor] = []
    labels: list[tf.Tensor] = []
    if not extra_dir.exists():
        return images, labels

    per_class: dict[int, int] = {}
    for label in LABELS:
        folder = extra_dir / label
        if not folder.exists():
            continue
        idx = _label_to_index(label)
        for path in sorted(folder.glob("*")):
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            if per_class.get(idx, 0) >= max_per_class:
                break
            raw = tf.io.read_file(str(path))
            image = tf.image.decode_image(raw, channels=3, expand_animations=False)
            image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE))
            image = tf.cast(image, tf.float32) / 255.0
            images.append(image)
            labels.append(tf.one_hot(idx, len(LABELS)))
            per_class[idx] = per_class.get(idx, 0) + 1
    return images, labels


def _build_dataset(max_per_class: int, extra_only: bool = False) -> tuple[tf.data.Dataset, tf.data.Dataset, int]:
    if extra_only:
        print("Modo extra_data: omitiendo PlantVillage.")
        return _build_dataset_from_extra(max_per_class)

    try:
        builder = tfds.builder("plant_village")
        builder.download_and_prepare()
    except Exception as exc:
        print(f"PlantVillage no disponible ({exc}). Entrenando solo con ml/extra_data/...")
        return _build_dataset_from_extra(max_per_class)

    raw_train = builder.as_dataset(split="train", shuffle_files=True)
    raw_val = builder.as_dataset(split="validation", shuffle_files=False)

    per_class: dict[int, int] = {}
    train_images: list[tf.Tensor] = []
    train_labels: list[tf.Tensor] = []

    for example in tfds.as_numpy(raw_train):
        label_name = example["label"].decode("utf-8")
        mapped = PLANT_VILLAGE_TO_LABEL.get(label_name)
        if mapped is None:
            continue
        idx = _label_to_index(mapped)
        if per_class.get(idx, 0) >= max_per_class:
            continue
        per_class[idx] = per_class.get(idx, 0) + 1
        image = tf.image.resize(example["image"], (IMG_SIZE, IMG_SIZE))
        image = tf.cast(image, tf.float32) / 255.0
        train_images.append(image)
        train_labels.append(tf.one_hot(idx, len(LABELS)))

    val_images: list[tf.Tensor] = []
    val_labels: list[tf.Tensor] = []
    val_per_class: dict[int, int] = {}
    val_limit = max(10, max_per_class // 5)

    for example in tfds.as_numpy(raw_val):
        label_name = example["label"].decode("utf-8")
        mapped = PLANT_VILLAGE_TO_LABEL.get(label_name)
        if mapped is None:
            continue
        idx = _label_to_index(mapped)
        if val_per_class.get(idx, 0) >= val_limit:
            continue
        val_per_class[idx] = val_per_class.get(idx, 0) + 1
        image = tf.image.resize(example["image"], (IMG_SIZE, IMG_SIZE))
        image = tf.cast(image, tf.float32) / 255.0
        val_images.append(image)
        val_labels.append(tf.one_hot(idx, len(LABELS)))

    extra_images, extra_labels = _load_extra_data(max_per_class)
    train_images.extend(extra_images)
    train_labels.extend(extra_labels)

    if not train_images:
        print("PlantVillage sin clases mapeadas. Entrenando solo con ml/extra_data/...")
        return _build_dataset_from_extra(max_per_class)

    train_ds, val_ds = _as_tf_datasets(train_images, train_labels, val_images, val_labels)
    return train_ds, val_ds, len(train_images)


def _build_model(num_classes: int) -> tf.keras.Model:
    base = tf.keras.applications.MobileNetV3Small(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )
    base.trainable = False

    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = base(inputs, training=False)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
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
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--max-per-class", type=int, default=120)
    parser.add_argument(
        "--extra-only",
        action="store_true",
        help="Entrenar solo con ml/extra_data/ (sin PlantVillage)",
    )
    args = parser.parse_args()

    print(f"Clases AgroPlaga ({len(LABELS)}): {', '.join(LABELS)}")
    if not args.extra_only:
        print("Cargando PlantVillage...")
    train_ds, val_ds, train_count = _build_dataset(args.max_per_class, extra_only=args.extra_only)
    print(f"Muestras de entrenamiento: {train_count}")

    model = _build_model(len(LABELS))
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
    ]
    history = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    LABELS_FILE.write_text("\n".join(LABELS) + "\n", encoding="utf-8")
    _export_tflite(model, MODEL_FILE)

    val_acc = float(history.history.get("val_accuracy", [0])[-1])
    metadata = {
        "model_version": "v1.5-tflite",
        "architecture": "MobileNetV3Small",
        "input_size": IMG_SIZE,
        "labels": LABELS,
        "val_accuracy": round(val_acc, 4),
        "train_samples": train_count,
        "plant_village_mapping": PLANT_VILLAGE_TO_LABEL,
    }
    METADATA_FILE.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Modelo exportado: {MODEL_FILE} ({MODEL_FILE.stat().st_size / 1024:.1f} KB)")
    print(f"Etiquetas: {LABELS_FILE}")
    print(f"Precisión validación: {val_acc:.2%}")


if __name__ == "__main__":
    main()
