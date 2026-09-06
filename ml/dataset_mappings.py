"""Mapeo de clases externas → etiquetas AgroPlaga (15 clases Poniente)."""

from __future__ import annotations

# PlantDoc (carpetas train/ y test/) — CC BY 4.0
PLANTDOC_TO_LABEL: dict[str, str] = {
    "Tomato leaf": "sana",
    "Bell_pepper leaf": "sana",
    "Blueberry leaf": "sana",
    "Cherry leaf": "sana",
    "Peach leaf": "sana",
    "Raspberry leaf": "sana",
    "Soyabean leaf": "sana",
    "Strawberry leaf": "sana",
    "grape leaf": "sana",
    "Tomato two spotted spider mites leaf": "arañuela roja",
    "Tomato Early blight leaf": "mildiu",
    "Tomato Septoria leaf spot": "mildiu",
    "Tomato leaf late blight": "mildiu",
    "Potato leaf early blight": "mildiu",
    "Potato leaf late blight": "mildiu",
    "Corn Gray leaf spot": "mildiu",
    "Corn leaf blight": "mildiu",
    "Corn rust leaf": "mildiu",
    "Tomato leaf bacterial spot": "mancha bacteriana",
    "Bell_pepper leaf spot": "mancha bacteriana",
    "Apple Scab Leaf": "mancha bacteriana",
    "Tomato leaf yellow virus": "clorosis viral",
    "Tomato leaf mosaic virus": "clorosis viral",
    "Tomato mold leaf": "botritis",
    "Squash Powdery mildew leaf": "oídio",
    "grape leaf black rot": "botritis",
    "Apple rust leaf": "oídio",
    "Apple Black rot": "botritis",
}

# IP102: índice 1-based (classes.txt) → etiqueta AgroPlaga
IP102_CLASS_TO_LABEL: dict[int, str] = {
    13: "trips",  # grain spreader thrips
    22: "arañuela roja",  # red spider
    24: "oruga",  # army worm
    25: "pulgón",  # aphids
    28: "pulgón",  # english grain aphid
    30: "pulgón",  # bird cherry-oataphid
    33: "arañuela roja",  # longlegged spider mite
    39: "oruga",  # cabbage army worm
    40: "oruga",  # beet army worm
    55: "trips",  # Thrips
    65: "piojo harinoso",  # Pseudococcus comstocki
    72: "mosca blanca",  # Trialeurodes vaporariorum
    77: "piojo harinoso",  # Icerya purchasi
    82: "piojo harinoso",  # Nipaecoccus vastator
    84: "mosca blanca",  # Aleurocanthus spiniferus
    87: "oruga",  # Prodenia litura
    89: "minador",  # Phyllocnistis citrella (minador hoja)
    90: "pulgón",  # Toxoptera citricidus
    91: "pulgón",  # Toxoptera aurantii
    92: "pulgón",  # Aphis citricola
    93: "trips",  # Scirtothrips dorsalis
}

# Mendeley s62zm6djd2 — 8 plagas tomate (nombres de carpeta normalizados)
MENDELEY8_TO_LABEL: dict[str, str] = {
    "tetranychus urticae": "arañuela roja",
    "bemisia argentifolii": "mosca blanca",
    "bemisia tabaci": "mosca blanca",
    "silverleaf whitefly": "mosca blanca",
    "thrips palmi": "trips",
    "thrips": "trips",
    "myzus persicae": "pulgón",
    "peach aphid": "pulgón",
    "spodoptera litura": "oruga",
    "spodoptera exigua": "oruga",
    "helicoverpa armigera": "oruga",
    "cotton bollworm": "oruga",
}

# Mendeley ysk546n9np — 6 plagas tomate
MENDELEY6_TO_LABEL: dict[str, str] = {
    "two-spotted spider mite": "arañuela roja",
    "two spotted spider mite": "arañuela roja",
    "tetranychus urticae": "arañuela roja",
    "silverleaf whitefly": "mosca blanca",
    "bemisia tabaci": "mosca blanca",
    "thrips": "trips",
    "peach aphid": "pulgón",
    "cotton bollworm": "oruga",
    "oriental fruit fly": "oruga",
}

# Roboflow Universe — nombres de clase (normalizados) → etiqueta AgroPlaga
ROBOFLOW_CLASS_TO_LABEL: dict[str, str] = {
    # Tomato Pest (pesto/tomato-pest-35mqs)
    "silverleaf whitefly": "mosca blanca",
    "whitefly": "mosca blanca",
    "mosca blanca": "mosca blanca",
    "wh": "mosca blanca",
    "melon thrips": "trips",
    "melon fly": "oruga",
    "thrips": "trips",
    "trips": "trips",
    "spider mite": "arañuela roja",
    "two spotted spider mite": "arañuela roja",
    "two-spotted spider mite": "arañuela roja",
    "tssm": "arañuela roja",
    "araña roja": "arañuela roja",
    "green peach aphid": "pulgón",
    "aphid": "pulgón",
    "aphids": "pulgón",
    "pulgon verde": "pulgón",
    "pulgon": "pulgón",
    "ap": "pulgón",
    "beet armyworm": "oruga",
    "cotton bollworm": "oruga",
    "tobacco cutworm": "oruga",
    "armyworm": "oruga",
    "oruga": "oruga",
    # TSSM Detection v2 (gent-lab) — todas las etapas → arañuela
    "adult female": "arañuela roja",
    "adult male": "arañuela roja",
    "immature": "arañuela roja",
    "dead mite": "arañuela roja",
    "viable egg": "arañuela roja",
}


def normalize_roboflow_class(name: str) -> str:
    return name.strip().lower().replace("-", " ").replace("_", " ")


def map_roboflow_class(name: str) -> str | None:
    """Resuelve clase Roboflow → etiqueta AgroPlaga (15 clases)."""
    normalized = normalize_roboflow_class(name)
    if normalized in ROBOFLOW_CLASS_TO_LABEL:
        return ROBOFLOW_CLASS_TO_LABEL[normalized]
    for key, label in ROBOFLOW_CLASS_TO_LABEL.items():
        if key in normalized or normalized in key:
            return label
    return None
