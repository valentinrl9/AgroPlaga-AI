# Catálogo v1.5 — 15 plagas del Poniente Almeriense

**Región:** invernaderos del Poniente (El Ejido, Roquetas, Adra, Berja…)  
**Cultivos:** tomate, pimiento, pepino, calabacín, berenjena, lechuga  
**Fuente canónica:** `shared/plague_catalog.json`

---

## Las 15 clases de PlagaScan

| # | Plaga | Tipo | Prioridad | Notas |
|---|-------|------|-----------|-------|
| 1 | sana | — | vigilancia | Hoja sin síntomas claros |
| 2 | tuta absoluta | insecto | crítica | Minador #1 en tomate |
| 3 | trips | insecto | crítica | Frankliniella, daño plateado |
| 4 | mosca blanca | insecto | crítica | Vector de virus (TYLCV) |
| 5 | pulgón | insecto | alta | Colonias en brotes tiernos |
| 6 | arañuela roja | ácaro | crítica | Telarañas en envés, clorosis |
| 7 | minador | insecto | alta | Liriomyza, galerías serpenteantes |
| 8 | piojo harinoso | insecto | alta | Colonias algodonosas, melaza |
| 9 | oruga | insecto | alta | Spodoptera, daño en hoja/fruto |
| 10 | mildiu | hongo | crítica | Manchas aceitosas, Peronospora |
| 11 | oídio | hongo | alta | Polvo blanco en haz |
| 12 | botritis | hongo | crítica | Moho gris, flor/fruto |
| 13 | mancha bacteriana | bacteria | alta | Halo amarillo, manchas necróticas |
| 14 | fusarium | hongo | alta | Marchitez vascular |
| 15 | clorosis viral | virus | crítica | Rizado, amarilleo (TYLCV) |

---

## API

```
GET /api/v1/plagues
```

Devuelve etiquetas, metadatos (nombre científico, EPPO, cultivos).

---

## Entrenamiento IA

1. PlantVillage (proxy fúngico/viral) — ver `ml/plague_catalog.py`
2. `ml/extra_data/` — capturas de invernadero (imprescindible para insectos)
3. `python ml/train_plagascan.py` — exporta TFLite a `frontend/assets/ml/`

**Importante:** el modelo con 15 clases necesita reentrenamiento; hasta entonces la heurística web y el TFLite stub usan las nuevas etiquetas.

---

## Próximo paso (datos)

Importar datasets externos:

```powershell
python ml/import_extra_data.py --plantdoc
python ml/import_extra_data.py --ip102   # tras descargar IP102 manualmente
```

Prioridad manual: **trips, mosca blanca, tuta, arañuela** (pocas en PlantVillage; IP102 cubre insectos).
