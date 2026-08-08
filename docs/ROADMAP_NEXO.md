# NEXO Agro — Roadmap de Desarrollo

**Autor:** Valentín Ruiz León  
**Actualizado:** 7 ago 2026  
**Rama:** `nexoagro`  
**Estado:** ✅ **MVP 1.B desplegado** en `https://agroplaga-ai.farm` (Field Pro + notificaciones perito)  
**Siguiente hito:** **Versión 2** — registro comunitario, CRM incidencias, clima sur Almería

---

## Documentos de referencia

| Documento | Rol |
|-----------|-----|
| [portfolio_nexoagro.md](portfolio_nexoagro.md) | Catálogo comercial (qué vendemos) |
| [NEXO_CONTEXT.md](NEXO_CONTEXT.md) | Arquitectura, RBAC, diseño (cómo se construye) |
| [ROADMAP.md](ROADMAP.md) | ⚠️ Archivado — historial técnico AgroPlaga |
| [ROADMAP_LEAN.md](ROADMAP_LEAN.md) | ⚠️ Archivado — historial piloto Lean |

**Producción actual (sin cambiar hasta validación):** `https://agroplaga-ai.farm`  
**Desarrollo local:** `docker compose up -d --build` → `flutter run`

---

## Módulos del ecosistema

| Módulo | Origen | Permiso RBAC | Estado |
|--------|--------|--------------|--------|
| **NEXO Field** | AgroPlaga AI | base (todos) + `has_field_premium` | ✅ Operativo (piloto VPS) |
| **NEXO Climate** | AgroData Consulting | `has_climate_module` | 🟡 Portado a PostgreSQL + UI Flutter B+ |
| **NEXO SIEX** | CEX / cumplimiento 2027 | `has_siex_enterprise` | 🟡 MVP local — Fase 3 |

### Mapeo versiones antiguas → NEXO

| Antes | Ahora |
|-------|-------|
| v1 MVP + v1.6-core | NEXO Field (base) |
| v1.6 completo (Fase 11) | Field + panel B2B mejorado |
| v1.7 CEX | NEXO SIEX |
| v1.8 Biocidas + dosis MAPA | NEXO Field Premium |
| AgroData ETL + dashboard | NEXO Climate |
| Fase 9 predicción (diferida) | NEXO Climate (en alcance) |

---

## Fase 0 — Consolidación unificada ✅ COMPLETADA (12 jul 2026)

> Unificar AgroPlaga + AgroData en una sola infraestructura PostgreSQL, shell Nexo y permisos por módulo.

### Backend
- [x] Migración `0010_nexo_module_permissions` (`has_field_premium`, `has_climate_module`, `has_siex_enterprise`)
- [x] Flags expuestos en `GET /api/v1/users/me`
- [x] `CLIMATE_PREVIEW_OPEN` para preview sin licencia
- [x] Migración `0011_climate_tables` (`climate_daily`, `climate_weekly`, `climate_monthly`)
- [x] Módulo `backend/app/climate/` (ETL Open-Meteo, métricas DPV, servicio)
- [x] API `/api/v1/climate/*` (actual, predicción, recomendaciones, alertas, access, ETL)
- [x] Scheduler ETL climate cada 15 min
- [x] Docker: volumen `backend/data/climate`, dependencias pandas/numpy/sklearn

### Flutter
- [x] Rebrand NEXO Agro (theme, splash, login, manifest)
- [x] `NexoShellScreen`: navegación Field / Climate / SIEX
- [x] `FieldHomeScreen`: funcionalidades AgroPlaga existentes
- [x] `NexoLockScreen` para módulos sin licencia
- [x] `ClimateModuleScreen` con 4 pestañas (Inicio, Recomendaciones, Alertas, Informe)
- [x] Gráficos y consejos IA (`climate_charts.dart`, `climate_advisor.dart`)
- [x] `ClimateRepository` conectado a API

### Panel web
- [x] Rebrand parcial NEXO (`Layout.tsx`, `LoginPage.tsx`)

### Documentación
- [x] `NEXO_CONTEXT.md` + `portfolio_nexoagro.md`
- [x] `ROADMAP_NEXO.md` (este documento)
- [x] Archivar roadmaps AgroPlaga
- [ ] Actualizar `GUIA_ROLES.md` con módulos Nexo

### Validación local (checklist)
- [x] Login → 3 pestañas visibles
- [x] Field: PlagaScan, mapa, alertas sin regresiones
- [x] Climate: métricas y gráficos con Docker local
- [x] SIEX: lock screen correcto
- [x] Panel `/panel`: login y validación perito operativos
- [x] Mapa: avisos IA pendientes vs validados por perito

### Validación automatizada (11 jul 2026)
- [x] `flutter analyze lib/` — 0 errores (2 warnings menores)
- [x] Docker backend + PostgreSQL activos (`localhost:8000`)
- [x] OpenAPI `/docs` — rutas `/api/v1/climate/*` registradas
- [x] `pytest` backend — 25 tests passed

**Criterio de done Fase 0:** checklist validado + commit en `nexoagro` + sin tocar producción VPS.

---

## Fase 1 — NEXO Field completo ⏳

> Cerrar lo pendiente del piloto AgroPlaga y Field Premium.

### Experiencia perito móvil (ex v1.6 / Fase 11)
- [x] Home "Centro de mando" para rol `tech` (KPIs + CTAs)
- [x] Cola validación con foto (`TechScanValidationScreen` → `/api/v1/tech/pending-scans`)
- [x] Notificaciones in-app perito al compartir escaneo (polling panel + app; migración `0016`)
- [ ] **Catálogo extendido perito:** autocomplete con filtro al escribir sobre catálogo amplio (EPPO + `plague_registry`), no limitado a las 15 plagas de la IA; opción «otra plaga»; cola de sugerencias revisable por admin → alimentar catálogo y dataset semilla
- [ ] Mapa técnico con capas (calor, pendientes, validados) — presets parciales vía mapa existente
- [ ] Modo visita a finca + informe PDF

### Field Premium (ex v1.7 parcial + v1.8)
- [x] Modelo `farm_treatments` + API `/api/v1/treatments` (migración `0013`)
- [x] Contador plazo de carencia (`CarenciaBanner` + semáforo recolección)
- [x] Catálogo biocidas MAPA piloto (seed `biocide_products`, 5 productos)
- [x] **ETL real MAPA CEX** (`ExportJsonProductosAutorizados` — cuaderno digital ministerial)
- [x] Motor dosis automática (`POST /api/v1/treatments/dose/calculate`)
- [x] API catálogo: `GET /treatments/catalog/status` + `POST /treatments/etl/run` (admin)
- [x] Scheduler ETL MAPA semanal (domingos 03:00 UTC)
- [ ] **Mapa histórico 7 / 30 días** (freemium solo tiempo real — ver V2 §2.3)
- [ ] Historial resistencias cruzadas (48 días)

### IA (ex v1.5 — pausado)
- [ ] Reentrenamiento TFLite con fotos validadas por perito
- [ ] Mensaje honesto en UI: IA orientativa, perito valida

### Infra
- [ ] FCM push alertas
- [ ] APK release Nexo para agricultores piloto

---

## Versión 2 — NEXO Field 2.0 ⏳ (próximo gran hito)

> Experiencia completa para comercializar en **todo el sur de Almería**: registro con fincas, mapa comunitario obligatorio, seguimiento fitosanitario por incidencias y clima multi-zona.

### 2.1 Registro, fincas y mapa comunitario

**Principios acordados:**
- El valor de la app depende de la comunidad → **consentimiento de mapa anónimo obligatorio** al registrarse (condiciones de uso; sin aceptar, no hay cuenta).
- Contribución al mapa de calor **automática** al abrir una incidencia relevante (sin preguntar cada vez).
- Compartir con **perito** sigue siendo **opt-in por escaneo** (`share_with_tech`).
- **Coordenadas GPS solo en escaneos**, no en la finca/unidad de producción.

**Wizard de registro (obligatorio ≥1 unidad):**
- [ ] Paso cuenta: código invitación, nombre, email, contraseña
- [ ] Paso legal: aceptación condiciones + mapa comunitario anónimo (obligatorio)
- [ ] Paso unidades de producción (estructura libre del agricultor):
  - [ ] Finca, nave, sector (nombres que el agricultor elija)
  - [ ] **Municipio:** desplegable con **todos los municipios SIGPAC de Almería** (~102; ampliar `agri_zones` / seed actual solo Poniente)
  - [ ] **Cultivo + variedad:** autocompletado con filtro dinámico al escribir; guardar valor **normalizado** (catálogo MAPA + variantes en `shared/crop_catalog.json`)
  - [ ] **Estado fenológico:** siembra → germinación → crecimiento → floración → fructificación → maduración → cosecha
  - [ ] Superficie m² (dosis MAPA)
  - [ ] SIGPAC recinto: opcional en registro; obligatorio solo cuando cooperativa use SIEX
- [ ] Backend: ampliar modelo `Farm` (o `ProductionUnit`) con `nave`, `sector`, `crop_stage`, `crop_variant`, `zone_id`
- [ ] Backend: `User.consent_accepted_at` + mapa implícito activo
- [ ] API: `GET /api/v1/crops?q=` autocomplete normalizado
- [ ] API: `GET /api/v1/zones` con catálogo completo provincia 04

**Edición continua:**
- [ ] Pantalla «Mis fincas/unidades»: cambiar cultivo (rotación) y fase fenológica en cualquier momento
- [ ] Historial opcional de cambios de fase (futuro IA / predicciones)

**Escaneo:**
- [ ] GPS automático al escanear (`latitude`, `longitude` en `Scan`; permiso ubicación en app)
- [ ] Vincular escaneo a nave/sector; heredar cultivo/fase de la unidad (editable antes de guardar)
- [ ] Quitar prompt repetido «¿contribuir al mapa?» en `ResultScreen` (sustituido por consentimiento registro + incidencia)

### 2.2 CRM fitosanitario — ciclo de vida de incidencias

Referencia: diagrama *CRM Fitosanitario AgroPlaga — Ciclo de Vida* (Detección → Diagnóstico → Prescripción → Tratamiento → Evaluación → Cierre).

**Bifurcación tras escaneo:**
- [ ] Escaneo sin relevancia → solo **historial** (comportamiento actual)
- [ ] Escaneo = plaga a seguir → abrir **incidencia** (`PestIncident` / ticket fitosanitario)

**Etapas y requisitos:**
- [ ] **1 Detección** — foto, unidad (nave/sector), cultivo, fase, GPS del escaneo, plaga IA
- [ ] **2 Diagnóstico** — verificación gravedad; validación perito opcional; plaga confirmada
- [ ] **3 Prescripción** — producto MAPA, dosis, plazo seguridad (reutilizar `register_treatment` + catálogo)
- [ ] **4 Tratamiento** — registro aplicación + contador carencia + alertas (`FarmTreatment`, `CarenciaBanner`)
- [ ] **5 Evaluación** — foto comparativa; decisión «¿mejora?»
- [ ] **6 Cierre** — `RESUELTO` o `COSECHA PERDIDA` → export SIEX si cooperativa enterprise

**Reglas de flujo:**
- [ ] Si **no mejora** en evaluación → volver a **paso 4 (Tratamiento)**, no a prescripción (plaga ya confirmada; solo cambiar producto/dosis)
- [ ] Bucle tratamiento ↔ evaluación hasta mejora o cierre
- [ ] Recordatorios: carencia activa, fecha reevaluación (in-app; push FCM en sprint posterior)

**Backend / Flutter:**
- [ ] Modelo `PestIncident` + estados + API CRUD y transiciones
- [ ] Pantalla timeline «Mis incidencias activas»
- [ ] Enlazar `Scan`, `FarmTreatment`, `OutbreakEvent` (mapa), validación perito
- [ ] Cierre incidencia → retirar foco del mapa comarcal (sync `OutbreakEvent.status = closed`)

### 2.3 Mapa de calor — Freemium vs Premium (`has_field_premium`)

**Fuente de datos (acordado V2):**
- El mapa de calor se alimenta de las **incidencias fitosanitarias abiertas** que generan los agricultores (al declarar una plaga relevante, con consentimiento de mapa al registrarse).
- Cada incidencia activa publica un `OutbreakEvent` anónimo en su **municipio/zona SIGPAC** (sin parcela ni identidad).
- Cuando el agricultor **cierra** la incidencia (controlada → `RESUELTO`, o `COSECHA PERDIDA`), el foco **desaparece del mapa de calor** de inmediato (estado `closed` / excluido de la agregación).
- Incidencias en historial del agricultor ≠ incidencias visibles en mapa comarcal.

**Estado actual (1.B):** el heatmap usa `outbreak_events` con ventana temporal (`hours`); no hay cierre de incidencia ni retirada automática al resolver — **cambiar en V2** al enlazar mapa ↔ `PestIncident`.

**Modelo comercial acordado:**
- **Freemium (Field base):** solo mapa de calor en **tiempo real** (ventana corta, p. ej. últimas 24 h o «ahora»).
- **Premium (`has_field_premium`):** histórico **7 días** y **30 días** en el selector del mapa.

**Implementación prevista (V2):**
- [ ] Al abrir incidencia → crear/activar `OutbreakEvent` en zona del municipio de la unidad
- [ ] Al cerrar incidencia → marcar evento mapa como `closed` y **excluir** de `get_heatmap_grid`
- [ ] Heatmap solo agrega incidencias **activas** (estados 1–5 del CRM; no `closed`)
- [ ] Backend: en `GET /api/v1/heatmap` validar `hours` según licencia (`has_field_premium`); freemium → solo vista tiempo real (incidencias activas ahora); premium → histórico **7 días** y **30 días** (evolución / agregación temporal de focos activos en esa ventana)
- [ ] Flutter `MapScreen`: selector 7 d / 30 d visible solo con premium; freemium sin selector histórico (o CTA «Contratar Premium»)
- [ ] Contribución al mapa: **todos** los agricultores (consentimiento registro); la diferencia es **visualización**, no aportar datos
- [ ] Panel perito/cooperativa: sin restricción freemium (rol B2B)
- [ ] Copy en app y landing alineado con paywall

### 2.4 Criterio de done Versión 2 (Field)

- [ ] Registro obligatorio con unidades + municipios Almería completos
- [ ] GPS en escaneos; mapa auto-contribuye con consentimiento registro
- [ ] Incidencia completa 1→6 con bucle evaluación → tratamiento
- [ ] Perito y mapa siguen desacoplados
- [ ] Freemium: mapa tiempo real; Premium: histórico 7 y 30 días
- [ ] Landing + piloto sur Almería alineados comercialmente

---

## Fase 2 — NEXO Climate productivo ⏳

> Paridad con dashboard AgroData original + monetización B2C.

### Paridad funcional AgroData
- [x] Informe mensual exportable PDF (Flutter `pdf` + `printing`)
- [x] Auto-refresh cada 15 min en app (`Timer.periodic` + ETL status)
- [x] Pestaña Riesgo (`GET /api/v1/climate/riesgo` + barra semanal)
- [x] Semáforos DPV / punto de rocío en UI (`punto_rocio_status`)
- [ ] Copiar histórico CSV AgroData → `backend/data/climate/` (arranque rápido ETL)

### Estaciones meteorológicas — sur de Almería (V2 Climate) 🎯

**Situación actual:** ETL Open-Meteo con **un solo punto** (`OPENMETEO_LAT/LON` ≈ La Mojonera, 36.77 / -2.81), válido para El Ejido / Poniente pero **insuficiente** para comercializar en todo el sur almeriense.

**Objetivo V2:** datos climáticos alineados con la **zona de la finca del agricultor** (municipio / estación más cercana), no solo Poniente.

- [ ] Inventariar estaciones disponibles sur Almería (Red Hidrosur, AEMET, cooperativas, Open-Meteo grid por municipio)
- [ ] Modelo `climate_stations` (id, nombre, municipio/zone_id, lat, lon, fuente, activa)
- [ ] Seed estaciones: Poniente (La Mojonera/Ejido), Roquetas, Adra, Almería, Níjar, Cabo de Gata, Carboneras, Levante (Mojácar, Garrucha, Vera…)
- [ ] ETL multi-estación: ingesta por estación → `climate_daily` / weekly / monthly con `station_id`
- [ ] API Climate: métricas según `zone_id` o estación vinculada a la unidad de producción del usuario
- [ ] Flutter: Climate usa estación de la finca seleccionada (fallback estación más cercana al municipio)
- [ ] Recomendaciones y alertas DPV contextualizadas por zona (no solo El Ejido)
- [ ] Documentar fuentes y cadencia de actualización por estación

### Futuro IoT / B2B
- [ ] Ingesta estaciones meteorológicas locales
- [ ] Sensores interior (temp, HR, CO2, suelo)
- [ ] Paywall B2C: trial 7 días, `has_climate_module`
- [ ] Dashboard web Climate (React) para consultoría

---

## Fase 3 — NEXO SIEX + Enterprise 🟡 (MVP local)

> Cumplimiento legal SIEX (obligatorio enero 2027) + panel cooperativa.

- [x] Tabla `siex_cuaderno_borrador` + compilación automática desde tratamientos Field
- [x] SIGPAC obligatorio en finca (`farms.sigpac_code`) para validez del cuaderno
- [x] Justificación automática (plaga/escaneo/MAPA + contexto Climate si activo)
- [x] API `/api/v1/siex/*` + hook post-`create_treatment`
- [x] Flutter: pestaña SIEX + selector finca en registro tratamiento
- [x] Bandeja validación perito B2B (panel web `/siex`)
- [x] Export preview JSON entradas validadas
- [ ] Firma digital cooperativa → `VALIDADO_OFICIAL`
- [ ] Exportador JSON schema ministerial definitivo (un clic)
- [ ] Panel multivista socios (plagas + clima agregado)
- [ ] Gestión documental (GlobalGAP, certificaciones)

---

## Fase 4 — Producción y comercial ⏳

> Cutover VPS, piloto unificado, monetización.

- [ ] Backup PostgreSQL antes de deploy (protocolo ya usado jul 2026)
- [ ] Deploy rama `nexoagro` a VPS (staging o producción con OK explícito)
- [ ] Apagar stack legacy AgroData en VPS (`agrodata-*`)
- [ ] Piloto 5–6 agricultores con app Nexo unificada
- [ ] Métricas Lean → pivotar o perseverar
- [ ] Repo definitivo `NexoAgro`
- [ ] Paquete comercial implantación cooperativas

---

## Orden de construcción

```
Fase 0 ✅
    MVP 1.B ✅ (Field Pro + notificaciones perito)
        Versión 2 Field (registro + incidencias + GPS escaneos)
            Versión 2 Climate (estaciones sur Almería)
                Piloto sur Almería completo
                    Fase 1 gaps (catálogo perito, FCM, APK release)
                        Fase 3 SIEX (deadline 2027)
                            Fase 4 comercial
```

**Regla V2:** Field 2.0 (registro + CRM incidencias) y Climate multi-estación pueden desarrollarse en paralelo; ambos necesarios antes de escalar comercialización fuera del Poniente.

---

## Stack unificado

| Capa | Tecnología |
|------|------------|
| Móvil | Flutter, TFLite, fl_chart |
| Panel B2B | React + TypeScript |
| API | FastAPI + PostgreSQL 16 + PostGIS |
| Climate ETL | Python (Open-Meteo) + APScheduler |
| IA campo | TFLite ONNX en dispositivo |
| Infra | Docker Compose → VPS + Caddy TLS |

---

## Registro de hitos

| Fecha | Hito |
|-------|------|
| jun 2026 | v1 MVP + v1.6-core AgroPlaga en VPS piloto |
| jul 2026 | Decisión unificación → rama `nexoagro` |
| jul 2026 | Fase 0: backend Climate PostgreSQL + shell Nexo + UI Climate B+ |
| jul 2026 | Fase 0 validada: checklist manual E2E + commit `14947d9` (mapa validado, migración 0012) |
| ago 2026 | MVP 1.B (Field Pro) en producción: notificaciones perito, SIEX/Climate/MAPA, migración `0016` |
| ago 2026 | Landing rediseñada + formulario contacto email; spec **Versión 2** acordada (registro, CRM incidencias, clima sur Almería) |

---

*Mantener este archivo como única fuente de verdad de ejecución. Marcar `[x]` al completar tareas.*
