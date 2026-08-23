# Roadmap ML — PlagaScan (detección de plaga)

> **Prioridad:** alta post-piloto B2B. Sin mejora de modelo, la app sigue siendo útil (CRM, SIEX, perito), pero la IA no genera confianza real en campo.
>
> **Versión objetivo del modelo en app:** `v1.6-tflite` (APK Field Pro con modelo reentrenado).

---

## Línea base (ago 2026)

| Métrica | Valor |
|---------|-------|
| Arquitectura | MobileNetV3Small → TFLite float16 (~1,9 MB) |
| Clases | 15 (`shared/plague_catalog.json`) |
| Inferencia | On-device (`frontend/lib/ml/tflite_runner.dart`) |
| **val_accuracy último entreno** | **10,58%** (jul 2026, `model_metadata.json`) |
| Datos `extra_data/` | ~3.000 img (PlantDoc/IP102); **tuta absoluta = 1** |
| Datos `dataset_semilla/` | 786 plagas + 240 sanas curadas |
| PlantVillage | Descarga rota (HTTP 403) |
| Bucle perito → dataset | **No implementado** |
| Evaluación por clase | **No implementada** |

> **Versión desplegada en app (ago 2026):** `v1.6-tflite-b2` · top-1 hold-out **~14%** (+4 pp vs v1.5).

---

## Reentreno ago 2026 (datos internet + semilla)

| Métrica | v1.5 baseline | v1.6-b2 desplegado |
|---------|---------------|---------------------|
| Top-1 hold-out (648 img) | 9,6% | **13,9%** |
| Top-3 hold-out | 31,0% | 30,1% |
| Top-6 top-1 | 0,4% | 0,4% |

**Hecho:** sync semilla→extra_data (3.476 img), pipeline eval/train, modelo en APK.  
**Pendiente:** export escaneos perito, top-3 UI, fotos campo para ≥65% top-6.

---

## Definición de «precisión aceptable»

| Hito | Métrica (fotos **reales invernadero**, hold-out piloto) | Rol en producto |
|------|--------------------------------------------------------|-----------------|
| **MVP ML v1.6** | ≥**55%** top-1 global; ≥**65%** top-1 en **top 6 plagas**; ≥**85%** top-3 en top 6 | Asistente que acierta a menudo; agricultor/perito corrigen el resto |
| **Field Pro ML v2.0** | ≥**70%** top-1 top 6; ≥**50%** top-1 resto; F1 ≥0,6 en trips/tuta/minador | Marketing «detección IA» creíble en piloto |
| **Producción ML v2.5** | ≥**80%** top-1 top 6; reentreno mensual automatizado | Ventaja competitiva clara |

**Top 6 plagas piloto (Poniente):** tuta absoluta, trips, mosca blanca, arañuela roja, mildiu, botritis.

**No usar solo `val_accuracy` del train mixto** (PlantDoc ≠ invernadero). El criterio de release es un **benchmark fijo** `ml/benchmarks/pilot_holdout/` que no entra en entrenamiento.

---

## Fases y orden de ejecución

```text
Fase 0 ──► Fase 1 ──► Fase 2 ──► Fase 3 ──► Release APK v1.6
  infra      datos       entreno      producto
  2-3 sem    4-8 sem     2 sem        1 sem
```

---

## Fase 0 — Infraestructura ML (2–3 semanas)

> Sin esto, cualquier reentreno es a ciegas.

### Scripts a implementar

| # | Script | Descripción |
|---|--------|-------------|
| 0.1 | `ml/scripts/sync_semilla_to_extra.py` | Copia `dataset_semilla/` → `extra_data/` (mapeo 19 carpetas → 15 labels). Corrige desbalance (p.ej. tuta=1). |
| 0.2 | `ml/scripts/export_validated_scans.py` | Lee BD (o export JSON admin): escaneos `tech_status ∈ {confirmed, corrected}` → `ml/extra_data/{plaga}/` + `manifest.csv`. Etiqueta = `corrected_plague` o `effective_plague`. |
| 0.3 | `ml/scripts/build_benchmark.py` | Crea/valida `ml/benchmarks/pilot_holdout/` (split estratificado, mín. 10 img/clase piloto). |
| 0.4 | `ml/evaluate_plagascan.py` | Carga `.tflite` + benchmark → accuracy, F1, matriz confusión, informe `ml/reports/eval_YYYYMMDD.html`. |
| 0.5 | Mejoras `ml/train_plagascan.py` | Class weights, augmentación (flip/brightness/crop), split estratificado, `--fine-tune` (descongelar últimas capas MobileNet), early stopping. |

### Tareas manuales (paralelo)

- [ ] Corregir códigos EPPO erróneos en `plague_registry.json` (minador, spodoptera, mancha).
- [ ] Unificar versión modelo en app: `tflite_runner.dart` → leer de `model_metadata.json`.
- [ ] Documentar en `ml/extra_data/README.md` regla: **no entrenar sin audit de balance** (`ml/scripts/audit_extra_data.py` — nuevo, opcional en 0.1).

### Criterio de salida Fase 0

- [ ] `python ml/scripts/sync_semilla_to_extra.py` deja **≥30 img/clase** en top 6 (excepto las ya piloto-ready).
- [ ] `python ml/evaluate_plagascan.py` genera informe del modelo actual (~11% baseline documentado).
- [ ] Entreno de prueba con datos balanceados supera **35% val** (sanity check técnico, no release).

---

## Fase 1 — Datos de campo validados (4–8 semanas, durante piloto)

> **Esta fase es el cuello de botella.** Depende de agricultores + perito en producción.

### Fuentes de datos (prioridad)

1. **Escaneos validados por perito** (automático vía 0.2) — máxima calidad.
2. **`dataset_semilla/`** — completar ~359 fotos daño pendientes (`FOTOS_PENDIENTES.md`).
3. **PlantDoc/IP102** — solo como complemento, cap `--max-per-class 80`, nunca como única fuente.

### Objetivos numéricos antes de Fase 2

| Clase | Mínimo img validadas/campo | Objetivo |
|-------|---------------------------|----------|
| tuta absoluta | 80 | 150 |
| trips | 80 | 150 |
| minador | 50 | 100 |
| mosca blanca | 50 | 100 |
| arañuela roja | 50 | 100 |
| mildiu | 50 | 100 |
| botritis | 50 | 100 |
| sana | 100 | 200 |
| Resto (8 clases) | 30 c/u | 50 c/u |

### Operativa piloto

- [ ] Briefing perito: corregir plaga siempre que difiera; descartar fotos borrosas/lejanas.
- [ ] Briefing agricultor: foto macro hoja/fruto afectado, luz natural si es posible.
- [ ] Job semanal (cron o manual): `export_validated_scans.py` + `audit_extra_data.py`.
- [ ] Revisión quincenal: informe eval vs benchmark; decidir si hay datos suficientes para Fase 2.

### Criterio de salida Fase 1

- [ ] Benchmark hold-out con **≥10 fotos/clase** en top 6 (fotos que **no** se usaron en train).
- [ ] Total **≥600 imágenes** de origen piloto/semilla (excl. PlantDoc puro).
- [ ] Al menos **50 escaneos** exportados desde validación perito real.

---

## Fase 2 — Reentrenamiento v1.6 (2 semanas)

### Pipeline de entreno (orden)

```powershell
cd "c:\Proyecto PlagaIA"

# 1. Sincronizar semilla + escaneos validados
python ml/scripts/sync_semilla_to_extra.py
python ml/scripts/export_validated_scans.py --database-url $env:DATABASE_URL

# 2. Auditar balance
python ml/scripts/audit_extra_data.py

# 3. Entrenar (Colab o PC con GPU recomendado)
python ml/train_plagascan.py --epochs 25 --max-per-class 200 --fine-tune --extra-only

# 4. Evaluar SIEMPRE contra benchmark hold-out
python ml/evaluate_plagascan.py --benchmark ml/benchmarks/pilot_holdout

# 5. Si pasa gates → export ya hecho en train a frontend/assets/ml/
```

### Hiperparámetros iniciales v1.6

| Parámetro | Valor |
|-----------|-------|
| Backbone | MobileNetV3Small (ImageNet) |
| Fine-tune | Últimas 30 capas tras 5 épocas cabeza congelada |
| Augmentación | flip H/V, ±20% brightness, random crop 80–100% |
| Class weights | Inversamente proporcional a frecuencia |
| Optimizer | Adam 1e-4 (fine-tune), 1e-3 (cabecera) |
| Early stopping | patience=5 sobre val_loss |

### Gates de calidad (obligatorios para release)

| Gate | Umbral |
|------|--------|
| G1 — Benchmark top-6 top-1 | ≥ **65%** |
| G2 — Benchmark top-6 top-3 | ≥ **85%** |
| G3 — Benchmark global top-1 | ≥ **55%** |
| G4 — Recall tuta + trips | ≥ **60%** cada una (no confundir entre sí) |
| G5 — Tamaño TFLite | ≤ **2,5 MB** (móviles gama media piloto) |
| G6 — Regresión manual | 20 fotos manuales del equipo: ≥15/20 «aceptable» en top-3 |

Si falla un gate: iterar datos (Fase 1) o reducir a **modelo top-6 + «otra/desconocida»** (ver Fase 3 alternativa).

---

## Fase 3 — Producto app v1.6 (1 semana)

### Cambios Flutter

| # | Cambio | Archivo |
|---|--------|---------|
| 3.1 | Mostrar **top-3** plagas + % (no solo top-1) | `plaga_classifier_mobile.dart`, `result_screen.dart` |
| 3.2 | Umbral confianza: &lt;40% → mensaje «Foto poco clara — confirma manualmente» | `result_screen.dart` |
| 3.3 | Versión modelo desde metadata | `tflite_runner.dart` |
| 3.4 | Enviar `top3` opcional al backend (futuro analytics) | `scan_repository.dart` + schema (opcional v1.6.1) |

### Release

```powershell
# Tras copiar plaga_model.tflite + model_metadata.json (model_version: v1.6-tflite)
cd frontend
flutter build apk --release --dart-define=API_BASE_URL=https://agroplaga-ai.farm
```

- [ ] APK: `releases/NEXO-Field-Pro-2.0.0-v1.6-plagascan-*.apk`
- [ ] Notas release: métricas benchmark (honestas), top-3, plagas mejor soportadas.
- [ ] **No** cambiar copy legal: sigue siendo orientativa; perito valida lo compartido.

---

## Fase 4 — Mejora continua (post v1.6)

| Item | Descripción |
|------|-------------|
| 4.1 | `build_cromos.py` + `synthesize_dataset.py` — insectos sobre hojas sanas |
| 4.2 | Reentreno mensual: script `ml/scripts/monthly_retrain.sh` (export → train → eval → tag git) |
| 4.3 | Modelo binario previo: «sano vs afectado» → reduce falsos en hojas sanas |
| 4.4 | Clases extendidas perito → cola admin → dataset (roadmap B2B catálogo EPPO) |
| 4.5 | v2.5: EfficientNet-Lite o modelo híbrido edge+cloud para casos &lt;40% confianza |

---

## Checklist «Listo para APK v1.6 con modelo nuevo»

Copiar y marcar antes de compilar APK de release:

```
[ ] export_validated_scans ejecutado (≥50 escaneos perito en extra_data)
[ ] sync_semilla_to_extra ejecutado (sin clases <30 img en top 6)
[ ] benchmark hold-out creado y excluido del train
[ ] train_plagascan con --fine-tune completado
[ ] evaluate_plagascan: G1–G6 PASS (informe en ml/reports/)
[ ] model_metadata.json → "model_version": "v1.6-tflite"
[ ] labels.txt coherente con catálogo
[ ] Top-3 visible en ResultScreen
[ ] Prueba manual 20 fotos campo (≥15/20 top-3 OK)
[ ] APK release + notas para agricultores/perito
```

---

## Cronograma orientativo

| Mes | Hito |
|-----|------|
| **Sep 2026** | Fase 0 completa; baseline eval automatizado |
| **Oct–Nov 2026** | Fase 1 durante piloto; acumular 600+ fotos campo |
| **Dic 2026** | Fase 2–3 → **APK v1.6 PlagaScan** si gates PASS |
| **2027 Q1** | Fase 4 síntesis + reentreno mensual |

*Ajustar según ritmo real del piloto (escaneos/semana, perito activo).*

---

## Dependencias con resto de Nexo

| Dependencia | Estado |
|-------------|--------|
| Cola validación perito (panel + app) | ✅ Hecho |
| `farmer_plague` + `effective_plague` | ✅ Hecho |
| Almacenamiento imágenes escaneo en backend | ✅ Hecho |
| Export imágenes validadas → ML | ❌ Fase 0.2 |
| Top-N predicciones en UI | ❌ Fase 3.1 |

---

## Referencias en repo

| Recurso | Ruta |
|---------|------|
| Entrenamiento | `ml/train_plagascan.py` |
| Datos entreno | `ml/extra_data/` |
| Semilla curada | `ml/dataset_semilla/` |
| Checklist fotos | `ml/dataset_semilla/FOTOS_PENDIENTES.md` |
| Modelo en app | `frontend/assets/ml/plaga_model.tflite` |
| Inferencia móvil | `frontend/lib/ml/tflite_runner.dart` |
| Roadmap producto | `docs/ROADMAP_NEXO.md` |

---

*Última actualización: ago 2026 — PlagaScan priorizado post-piloto B2B.*
