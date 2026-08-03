# dataset_semilla — Fotos fuente para entrenamiento sintético PlagaScan

Banco de imágenes **reales** descargadas (p. ej. [EPPO Global Database](https://gd.eppo.int/)) que alimentan el pipeline:

```
dataset_semilla  →  cromos (recortes)  →  composición en hojas sanas  →  ml/extra_data  →  train_plagascan.py
```

## Crear / regenerar carpetas

```powershell
python ml/scripts/init_dataset_semilla.py
```

## Estructura

```
dataset_semilla/
├── manifest.csv                 # Trazabilidad de cada foto descargada
├── plague_registry.json         # Definición de plagas, EPPO y subcarpetas
├── 00_hojas_sanas/              # Fondos (tomate, pimiento, pepino…)
│   ├── tomate/
│   └── …
├── 01_trips/
│   ├── _meta.json               # URL EPPO, etiqueta de entreno, notas
│   ├── cromo/                   # PNG recortado con alpha (tú o script build_cromos.py)
│   ├── adulto/
│   ├── ninfa/
│   └── dano_plateado/
├── 02_tuta/                     # Ej: https://gd.eppo.int/taxon/GNORAB/photos
│   ├── cromo/
│   ├── huevo/
│   ├── larva/
│   ├── pupa/
│   ├── adulto/
│   ├── dano_galeria_hoja/
│   └── dano_fruto/
└── … (18 plagas, ver plague_registry.json)
```

## Cómo descargar desde EPPO (trabajo manual)

1. Abre `_meta.json` de la plaga → campo `eppo_photos_url`.
2. Filtra por tag EPPO: **Larva**, **Adult**, **Damage**, **Egg**, **Pupa**.
3. Guarda con nombre descriptivo:
   ```
   {eppo}_{tag}_{nnn}.jpg
   ```
   Ejemplo: `GNORAB_larva_001.jpg` en `02_tuta/larva/`.
4. Anota en `manifest.csv`: carpeta, archivo, URL, courtesy (obligatorio EPPO).

### Descarga automática EPPO (API)

Registro gratuito: [EPPO Data Portal](https://data.eppo.int/) → clave API en `EPPO_API_KEY`.

```powershell
$env:EPPO_API_KEY = "tu_clave"
python ml/scripts/fetch_eppo_photos.py --dry-run --all
python ml/scripts/fetch_eppo_photos.py --all --max-per-subfolder 30 --skip-existing
python ml/scripts/fetch_eppo_photos.py --plague 04_pulgon --plague 14_botritis
```

El script clasifica tags EPPO → subcarpetas (`larva`, `dano_fruto`, etc.) y actualiza `manifest.csv`.
Trips usa código **FRANOC** (corregido respecto al registry).

**Licencia EPPO:** las fotos son para **uso educativo**. Para el piloto interno registra autor en `manifest.csv`. Publicación externa requiere permiso del fotógrafo ([EPPO](https://gd.eppo.int/taxon/GNORAB/photos)).

## Carpeta `cromo/`

- Recortes del insecto/hongo **aislado** (ideal PNG con transparencia).
- Los generará `ml/scripts/build_cromos.py` (segmentación) o puedes recortar a mano desde fotos de adulto/larva.
- El script de síntesis pegará cromos sobre `00_hojas_sanas/`.

## Mapeo a etiquetas de entreno

| Carpetas semilla | Etiqueta `train_plagascan` |
|------------------|---------------------------|
| 02_tuta | tuta absoluta |
| 08–10 oruga_* | oruga (3 especies → 1 clase por ahora) |
| 11_chinche_verde, 17_esclerotinia | clases nuevas v2 (ampliación) |
| Resto | 1:1 con `label_train` en `_meta.json` |

Catálogo app actual: `shared/plague_catalog.json` (15 clases). Tras ampliar, actualizaremos catálogo + `labels.txt`.

## Objetivos mínimos antes de sintetizar

| Tipo subcarpeta | Mínimo recomendado |
|-----------------|-------------------|
| cromo | 5–15 recortes limpios |
| adulto / larva | 10–30 fotos |
| dano_* | 20–50 fotos |
| 00_hojas_sanas/cultivo | 30+ fotos por cultivo |

## Pipeline (lo implementamos nosotros)

| Fase | Script | Estado |
|------|--------|--------|
| 0. Fotos EPPO API | `ml/scripts/fetch_eppo_photos.py` | Listo |
| 1. Cromos | `ml/scripts/build_cromos.py` | Pendiente |
| 2. Síntesis + mezcla | `ml/scripts/synthesize_dataset.py` | Pendiente |
| 3. Export | → `ml/extra_data/{label}/` | Pendiente |
| 4. Entreno | `ml/train_plagascan.py` | Existe |

Cuando tengas **≥30 fotos reales** en al menos tuta + trips, avisa y arrancamos fase 1.
