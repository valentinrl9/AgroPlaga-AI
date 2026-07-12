# NEXO Agro — Roadmap de Desarrollo

**Autor:** Valentín Ruiz León  
**Actualizado:** 11 jul 2026  
**Rama:** `nexoagro`  
**Estado:** 🔄 **Fase 0 ~90 %** — unificación base en local · producción sigue en AgroPlaga piloto

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
| **NEXO SIEX** | CEX / cumplimiento 2027 | `has_siex_enterprise` | 🔒 Lock screen — Fase 3 |

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

## Fase 0 — Consolidación unificada 🔄 ~90 %

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
- [x] Login → 3 pestañas visibles *(confirmado en `flutter run` Chrome)*
- [ ] Field: PlagaScan, mapa, alertas sin regresiones
- [x] Climate: métricas y gráficos con Docker local *(confirmado en `flutter run`)*
- [ ] SIEX: lock screen correcto
- [ ] Panel `/panel`: login operativo
- [x] Mapa: avisos IA pendientes vs validados por perito (jul 2026)

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
- [ ] Home "Centro de mando" para rol `tech`
- [ ] Cola validación fullscreen con foto
- [ ] Mapa técnico con capas (calor, pendientes, validados)
- [ ] Modo visita a finca + informe PDF

### Field Premium (ex v1.7 parcial + v1.8)
- [ ] Modelo `farm_treatments` + flujo opt-in tras escaneo
- [ ] Contador plazo de carencia (semáforo recolección)
- [ ] ETL catálogo biocidas MAPA / Ministerio (TP18)
- [ ] Motor dosis automática por superficie invernadero
- [ ] Historial resistencias cruzadas (48 días)

### IA (ex v1.5 — pausado)
- [ ] Reentrenamiento TFLite con fotos validadas por perito
- [ ] Mensaje honesto en UI: IA orientativa, perito valida

### Infra
- [ ] FCM push alertas
- [ ] APK release Nexo para agricultores piloto

---

## Fase 2 — NEXO Climate productivo ⏳

> Paridad con dashboard AgroData original + monetización B2C.

### Paridad funcional AgroData
- [ ] Informe mensual exportable PDF
- [ ] Auto-refresh cada 15 min en app
- [ ] Pestaña Riesgo con lógica completa (`api_prediccion.py` original)
- [ ] Semáforos DPV / punto de rocío en UI con tokens NEXO
- [ ] Copiar histórico CSV AgroData → `backend/data/climate/` (arranque rápido ETL)

### Futuro IoT / B2B
- [ ] Ingesta estaciones meteorológicas locales
- [ ] Sensores interior (temp, HR, CO2, suelo)
- [ ] Paywall B2C: trial 7 días, `has_climate_module`
- [ ] Dashboard web Climate (React) para consultoría

---

## Fase 3 — NEXO SIEX + Enterprise ⏳

> Cumplimiento legal SIEX (obligatorio enero 2027) + panel cooperativa.

- [ ] Tabla `siex_cuaderno_borrador` + pipeline eventos Field/Climate
- [ ] Justificación climática automática en tratamientos
- [ ] Bandeja validación perito B2B (web)
- [ ] Firma digital cooperativa → `VALIDADO_OFICIAL`
- [ ] Exportador JSON schema ministerial (un clic)
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
Fase 0 (ahora)
    Validación local Field + Climate
        Gaps Climate (PDF, riesgo, refresh)
            Deploy staging VPS (con OK)
                Piloto Nexo unificado
                    Fase 1 Field (perito + premium)
                        Fase 3 SIEX (deadline 2027)
                            Fase 4 comercial
```

**Regla:** no desplegar a producción hasta validar Fase 0 + gaps Climate críticos.

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
| jul 2026 | `ROADMAP_NEXO.md` — roadmap único, roadmaps AgroPlaga archivados |

---

*Mantener este archivo como única fuente de verdad de ejecución. Marcar `[x]` al completar tareas.*
