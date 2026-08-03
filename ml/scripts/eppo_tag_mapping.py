"""Mapeo de tags EPPO → subcarpetas de dataset_semilla."""

from __future__ import annotations

ORG_ALIASES: dict[str, tuple[str, ...]] = {
    "adulto": ("adult", "adults", "imago", "adulto"),
    "larva": ("larva", "larvae", "caterpillar", "larva"),
    "huevo": ("egg", "eggs", "huevo", "ovum", "oviposition"),
    "pupa": ("pupa", "pupae", "pupation"),
    "ninfa": ("nymph", "nymphs", "ninfa"),
    "ninfa_pupa": ("nymph", "pupa", "scale", "crawler"),
    "acaro_adulto": ("adult mite", "mite", "adult", "spider mite", "acarus"),
    "formas_aladas": ("winged", "alate", "alata", "aladas"),
    "formas_apteras": ("apterous", "wingless", "aptera", "apteras"),
    "adulto_ninfa": ("adult", "nymph", "female", "male", "mealybug", "scale"),
}

DANO_ALIASES: dict[str, tuple[str, ...]] = {
    "dano_plateado": ("silver", "silvering", "silvering damage"),
    "dano_galeria_hoja": ("gallery", "leaf mine", "mine", "serpentine", "blotch"),
    "dano_fruto": ("fruit", "tomato fruit", "berry"),
    "dano_melaza": ("honeydew", "sooty", "molasses"),
    "dano_amarilleo": ("yellowing", "yellow leaf", "chlorosis"),
    "dano_enrollamiento": ("curl", "curling", "rolled", "leaf curl"),
    "dano_punteado": ("stippling", "speckling", "spotting", "punctate"),
    "dano_telarana": ("webbing", "web", "silk"),
    "dano_mina_serpiente": ("serpentine", "leaf mine", "mine"),
    "dano_brote": ("shoot", "bud", "terminal", "brote"),
    "dano_defoliacion": ("defoliation", "feeding damage", "leaf damage", "holes"),
    "dano_necrosis_fruto": ("necrosis", "fruit damage", "fruit spot"),
    "dano_necrosis_hoja": ("necrosis", "leaf blight", "blight", "water-soaked"),
    "dano_tallo": ("stem", "tallo", "stalk"),
    "dano_micelio": ("mycelium", "powdery", "white mold"),
    "dano_mancha_clorotica": ("chlorotic", "chlorosis", "yellow spot", "powdery mildew"),
    "dano_moho_gris": ("grey mold", "gray mold", "botrytis", "mold"),
    "dano_flor": ("flower", "blossom", "flor"),
    "dano_mancha_foliar": ("leaf spot", "bacterial spot", "spot", "foliar"),
    "dano_marchitez": ("wilt", "wilting", "marchitez"),
    "dano_vascular": ("vascular", "discoloration", "xylem"),
    "dano_tallo_algodon": ("cottony", "sclerotia", "white mold", "stem rot"),
    "dano_moho_blanco": ("white mold", "mycelium", "cottony"),
    "dano_sintoma_foliar": ("symptom", "leaf symptom", "mosaic", "curl", "virus"),
    "dano_planta_entera": ("plant", "whole plant", "stunting", "field"),
}

DAMAGE_HINTS = (
    "damage",
    "symptom",
    "injury",
    "disease",
    "infestation sign",
    "feeding",
    "blight",
    "rot",
    "spot",
    "lesion",
)

# Códigos EPPO corregidos respecto a plague_registry.json
EPPO_CODE_OVERRIDES: dict[str, str] = {
    "01_trips": "FRANOC",
}
