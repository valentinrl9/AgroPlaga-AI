"""Carga y split de imágenes para PlagaScan."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tensorflow as tf

ML_DIR = Path(__file__).resolve().parent
ROOT = ML_DIR.parent
EXTRA_DIR = ML_DIR / "extra_data"
ASSETS_DIR = ROOT / "frontend" / "assets" / "ml"

IMG_SIZE = 224
SEED = 42
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class Sample:
    path: Path
    label_index: int
    label_name: str


def load_labels() -> list[str]:
    from plague_catalog import LABELS

    return LABELS


def iter_extra_image_paths(extra_dir: Path | None = None) -> list[Sample]:
    extra_dir = extra_dir or EXTRA_DIR
    labels = load_labels()
    label_to_idx = {name: i for i, name in enumerate(labels)}
    samples: list[Sample] = []

    if not extra_dir.exists():
        return samples

    for label_name in labels:
        folder = extra_dir / label_name
        if not folder.exists():
            continue
        idx = label_to_idx[label_name]
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            samples.append(Sample(path=path, label_index=idx, label_name=label_name))
    return samples


def cap_per_class(samples: list[Sample], max_per_class: int) -> list[Sample]:
    counts: dict[int, int] = {}
    capped: list[Sample] = []
    for sample in samples:
        n = counts.get(sample.label_index, 0)
        if n >= max_per_class:
            continue
        counts[sample.label_index] = n + 1
        capped.append(sample)
    return capped


def stratified_split(
    samples: list[Sample],
    val_ratio: float = 0.2,
    seed: int = SEED,
) -> tuple[list[Sample], list[Sample]]:
    rng = np.random.default_rng(seed)
    by_class: dict[int, list[Sample]] = {}
    for sample in samples:
        by_class.setdefault(sample.label_index, []).append(sample)

    train: list[Sample] = []
    val: list[Sample] = []
    for class_samples in by_class.values():
        indices = rng.permutation(len(class_samples))
        split_at = max(1, int(len(class_samples) * (1 - val_ratio)))
        if len(class_samples) <= 2:
            train.extend(class_samples)
            continue
        shuffled = [class_samples[i] for i in indices]
        train.extend(shuffled[:split_at])
        val.extend(shuffled[split_at:])
    return train, val


def class_counts(samples: list[Sample]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sample in samples:
        counts[sample.label_name] = counts.get(sample.label_name, 0) + 1
    return dict(sorted(counts.items()))


def compute_class_weights(samples: list[Sample], num_classes: int) -> dict[int, float]:
    counts = np.zeros(num_classes, dtype=np.float32)
    for sample in samples:
        counts[sample.label_index] += 1.0
    total = float(len(samples))
    weights: dict[int, float] = {}
    for idx in range(num_classes):
        if counts[idx] <= 0:
            weights[idx] = 0.0
        else:
            weights[idx] = total / (num_classes * counts[idx])
    return weights


def load_image_tensor(path: Path) -> tf.Tensor:
    raw = tf.io.read_file(str(path))
    image = tf.image.decode_image(raw, channels=3, expand_animations=False)
    image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE))
    return tf.cast(image, tf.float32) / 255.0


def augment(image: tf.Tensor) -> tf.Tensor:
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_flip_up_down(image)
    image = tf.image.random_brightness(image, max_delta=0.15)
    image = tf.image.random_contrast(image, 0.85, 1.15)
    image = tf.clip_by_value(image, 0.0, 1.0)
    size = IMG_SIZE
    crop = tf.image.random_crop(image, size=[size, size, 3])
    return crop


def samples_to_dataset(
    samples: list[Sample],
    num_classes: int,
    *,
    training: bool = False,
    batch_size: int = 32,
) -> tf.data.Dataset:
    paths = [str(s.path) for s in samples]
    labels = [s.label_index for s in samples]

    path_ds = tf.data.Dataset.from_tensor_slices(paths)
    label_ds = tf.data.Dataset.from_tensor_slices(labels)

    def _load(path: tf.Tensor, label: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
        raw = tf.io.read_file(path)
        image = tf.image.decode_image(raw, channels=3, expand_animations=False)
        image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE))
        image = tf.cast(image, tf.float32) / 255.0
        if training:
            image = augment(image)
        return image, tf.one_hot(label, num_classes)

    ds = tf.data.Dataset.zip((path_ds, label_ds)).map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.shuffle(min(len(samples), 1024), seed=SEED)
    return ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)


def audit_report(extra_dir: Path | None = None) -> dict:
    samples = iter_extra_image_paths(extra_dir)
    labels = load_labels()
    counts = class_counts(samples)
    report = {
        "total": len(samples),
        "per_class": counts,
        "missing_classes": [label for label in labels if counts.get(label, 0) == 0],
        "min_count": min(counts.values()) if counts else 0,
        "max_count": max(counts.values()) if counts else 0,
    }
    return report


def filter_semilla(samples: list[Sample]) -> list[Sample]:
    return [s for s in samples if "semilla_" in s.path.name.lower()]


def balance_samples(samples: list[Sample]) -> list[Sample]:
    """Oversampling para igualar clases en entrenamiento."""
    rng = np.random.default_rng(SEED)
    by_class: dict[int, list[Sample]] = {}
    for sample in samples:
        by_class.setdefault(sample.label_index, []).append(sample)

    if not by_class:
        return samples

    target = max(len(v) for v in by_class.values())
    balanced: list[Sample] = []
    for class_samples in by_class.values():
        pool = list(class_samples)
        while len(pool) < target:
            pool.extend(class_samples)
        rng.shuffle(pool)
        balanced.extend(pool[:target])
    rng.shuffle(balanced)
    return balanced


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
