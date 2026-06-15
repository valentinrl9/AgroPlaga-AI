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
