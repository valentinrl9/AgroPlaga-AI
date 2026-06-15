# Capturas locales para PlagaScan (v1.5)

Coloca imágenes por carpeta, una por cada etiqueta del catálogo:

```
extra_data/
  sana/
  tuta absoluta/
  trips/
  mosca blanca/
  pulgón/
  arañuela roja/
  minador/
  piojo harinoso/
  oruga/
  mildiu/
  oídio/
  botritis/
  mancha bacteriana/
  fusarium/
  clorosis viral/
```

**Prioridad para el Poniente:** tuta absoluta, trips, mosca blanca, arañuela roja, mildiu, botritis.

Formatos: `.jpg`, `.jpeg`, `.png`, `.webp`

Objetivo: **≥50 imágenes por clase** de invernadero real antes del próximo entrenamiento.

## Importación automática

```powershell
# PlantDoc (clona desde GitHub, ~2500 img en campo)
python ml/import_extra_data.py --plantdoc --max-per-class 80

# IP102 (descarga manual primero — ver abajo)
python ml/import_extra_data.py --ip102 --max-per-class 50

# Ambos
python ml/import_extra_data.py --all
```

### IP102 — descarga manual (una vez)

1. Abre https://github.com/xpwu95/IP102 → Google Drive
2. Descarga el dataset de clasificación (v1.1)
3. Descomprime en `ml/datasets/ip102/` (debe haber `train.txt` o carpetas `1/`…`102/`)

Licencia IP102: uso académico. PlantDoc: CC BY 4.0.

Otras fuentes: feedback de usuarios en la app (plaga corregida).

## Entrenar tras importar

```bash
python ml/train_plagascan.py --epochs 10 --max-per-class 150
```
