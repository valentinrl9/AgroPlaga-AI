"""Catálogo compartido de plagas del Poniente Almeriense (v1.5 — 15 clases)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILE = ROOT / "shared" / "plague_catalog.json"


def load_catalog() -> dict:
    return json.loads(CATALOG_FILE.read_text(encoding="utf-8"))


def plague_labels() -> list[str]:
    return load_catalog()["labels"]


LABELS = plague_labels()

# PlantVillage → etiqueta AgroPlaga (proxy; insectos reales vía ml/extra_data/)
PLANT_VILLAGE_TO_LABEL: dict[str, str] = {
    "Apple___healthy": "sana",
    "Blueberry___healthy": "sana",
    "Cherry_(including_sour)___healthy": "sana",
    "Corn_(maize)___healthy": "sana",
    "Grape___healthy": "sana",
    "Orange___Haunglongbing_(Citrus_greening)": "clorosis viral",
    "Peach___healthy": "sana",
    "Pepper,_bell___healthy": "sana",
    "Potato___healthy": "sana",
    "Raspberry___healthy": "sana",
    "Soybean___healthy": "sana",
    "Squash___Powdery_mildew": "oídio",
    "Strawberry___healthy": "sana",
    "Tomato___healthy": "sana",
    "Tomato___Bacterial_spot": "mancha bacteriana",
    "Pepper,_bell___Bacterial_spot": "mancha bacteriana",
    "Peach___Bacterial_spot": "mancha bacteriana",
    "Tomato___Early_blight": "mildiu",
    "Tomato___Late_blight": "mildiu",
    "Tomato___Septoria_leaf_spot": "mildiu",
    "Potato___Early_blight": "mildiu",
    "Potato___Late_blight": "mildiu",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "mildiu",
    "Corn_(maize)___Common_rust_": "mildiu",
    "Corn_(maize)___Northern_Leaf_Blight": "mildiu",
    "Grape___Esca_(Black_Measles)": "fusarium",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "botritis",
    "Grape___Black_rot": "botritis",
    "Apple___Apple_scab": "mancha bacteriana",
    "Apple___Black_rot": "botritis",
    "Cherry_(including_sour)___Powdery_mildew": "oídio",
    "Tomato___Leaf_Mold": "oídio",
    "Tomato___Spider_mites Two-spotted_spider_mite": "arañuela roja",
    "Tomato___Target_Spot": "botritis",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "clorosis viral",
    "Tomato___Tomato_mosaic_virus": "clorosis viral",
    "Strawberry___Leaf_scorch": "botritis",
}
