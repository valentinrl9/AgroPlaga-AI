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
# PlantDoc (~2500 img campo, GitHub automático)
python ml/import_extra_data.py --plantdoc --max-per-class 80

# PlantVillage (~54k img, enfermedades + sana; primera vez ~1 GB)
python ml/import_extra_data.py --plantvillage --max-per-class 80

# IP102 (descarga manual primero — ver abajo)
python ml/import_extra_data.py --ip102 --max-per-class 50

# Los tres
python ml/import_extra_data.py --all
```

### IP102 — descarga manual (una vez)

1. Abre https://github.com/xpwu95/IP102 → Google Drive
2. Descarga el dataset de clasificación (v1.1)
3. Descomprime en `ml/datasets/ip102/` (debe haber `train.txt` o carpetas `1/`…`102/`)

Licencia IP102: uso académico. PlantDoc: CC BY 4.0.

Otras fuentes: feedback de usuarios en la app (plaga corregida).

### Paso 5 automático (presupuesto 0 €)

```powershell
python ml/scripts/run_paso5_zero_budget.py
```

Importa PlantDoc + IP102 + EPPO + iNaturalist, sincroniza semilla, reentrena en
`ml/models/experiments/paso5/` (no pisa el `.tflite` del APK) y guarda informes en
`ml/reports/eval_baseline_paso5.json` y `eval_paso5.json`.

Mendeley (manual): descarga ZIP desde data.mendeley.com y colócalo en
`ml/datasets/s62zm6djd2/tomato_pests_8.zip`, luego:

```powershell
python ml/scripts/import_public_datasets.py --mendeley8 --mendeley8-zip ml/datasets/s62zm6djd2/tomato_pests_8.zip
```

### Roboflow Universe (detección → recortes clasificación)

1. API key gratis en [Roboflow Settings](https://app.roboflow.com/settings/api) → `ROBOFLOW_API_KEY` en `.env`
2. Catálogo curado: `ml/datasets/roboflow/catalog.json` (tomate, pulgón/mosca, arañuela)
3. Importar recortes:

```powershell
python ml/scripts/import_roboflow.py --project tomato-pest --max-per-class 80
python ml/scripts/import_roboflow.py --all-catalog --max-per-class 60
```

4. Experimento completo (import + train + eval, **no pisa producción**):

```powershell
python ml/scripts/run_roboflow_experiment.py --projects tomato-pest
```

Entrena con `--roboflow-only` (solo archivos `roboflow_*`). Comparar `ml/reports/eval_roboflow.json` vs baseline antes de desplegar.

## Entrenar tras importar

```bash
python ml/train_plagascan.py --epochs 10 --max-per-class 150
```
