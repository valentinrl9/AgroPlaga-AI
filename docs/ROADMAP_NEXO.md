# NEXO Agro — Roadmap de Desarrollo

**Autor:** Valentín Ruiz León  
**Actualizado:** 22 ago 2026  
**Rama:** `nexoagro`  
**Estado:** ✅ **NEXO Field Pro 2.0** desplegado en `https://agroplaga-ai.farm` — versión piloto **aceptable para campo**  
**Siguiente hito:** Piloto ampliado sur Almería + gaps comerciales (FCM, dominio `.es`, SIEX cooperativa)  
**TODO infra (más adelante):** dominio `agroplaga.es` + Workspace · seguridad avanzada (pinning, Redis, WAF)

---

## Resumen ejecutivo — V2 (ago 2026)

### Lo que tenemos operativo

| Área | Entregado |
|------|-----------|
| **Field base** | PlagaScan offline, historial, alertas, mapa comunitario, registro con consentimiento mapa anónimo |
| **Field Pro / Premium** | Tratamientos MAPA, dosis automática, carencia, catálogo biocidas ETL semanal |
| **Fincas** | Wizard onboarding + «Mis fincas» (103 municipios Almería, cultivo/fase/nave/sector, SIGPAC manual para SIEX) |
| **CRM incidencias** | Ciclo 1→6 (detección → cierre), prescripción MAPA, evaluación con foto cámara/galería, bucle tratamiento↔evaluación |
| **Mapa comercial** | Freemium 24 h; Premium 7 d / 30 d; focos ligados a incidencias activas; cierre retira del heatmap |
| **Perito** | Cola validación foto, corrección plaga, agricultor puede corregir plaga IA, notificaciones polling |
| **Climate** | 11 estaciones sur Almería, ETL multi-estación, selector por finca/estación, informe PDF, loading UX |
| **SIEX** | Cuaderno borrador automático desde tratamientos; SIGPAC manual por finca; refresh al completar recinto; preview abierto en piloto |
| **Producción** | VPS + Docker + Caddy, migraciones hasta `0025`, APK release `2.0.0+3` |

### Planificado para más adelante (no bloquea piloto V2)

- GPS automático en escaneos / SIGPAC por coordenadas (**descartado** por cobertura invernadero y permisos; SIGPAC manual acordado)
- Push FCM, catálogo plagas extendido perito, informes PDF visita, firma SIEX cooperativa, export JSON ministerial
- Reentrenamiento IA con fotos validadas, IoT sensores, dashboard Climate web, dominio `agroplaga.es`, hardening Redis/WAF/pinning
- Historial rotaciones/fases, recordatorios push carencia/reevaluación, resistencias cruzadas 48 d

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
| **NEXO Field** | AgroPlaga AI | base (todos) + `has_field_premium` | ✅ V2 operativo (piloto VPS + APK) |
| **NEXO Climate** | AgroData Consulting | `has_climate_module` | ✅ Multi-estación sur Almería (11 puntos) + UI Flutter |
| **NEXO SIEX** | CEX / cumplimiento 2027 | `has_siex_module` / `has_siex_enterprise` | 🟡 Cuaderno borrador automático; SIGPAC manual; validación cooperativa pendiente |

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
- [x] Actualizar `GUIA_ROLES.md` con módulos Nexo V2

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

## Fase 1 — NEXO Field completo 🟡 (gaps menores)

> Cerrar lo pendiente del piloto AgroPlaga y Field Premium. **Núcleo V2 ya integrado** — quedan mejoras perito/comercial.

### Experiencia perito móvil (ex v1.6 / Fase 11)
- [x] Home "Centro de mando" para rol `tech` (KPIs + CTAs)
- [x] Cola validación con foto (`TechScanValidationScreen` → `/api/v1/tech/pending-scans`)
- [x] Notificaciones in-app perito al compartir escaneo (polling panel + app; migración `0016`)
- [ ] **Catálogo extendido perito:** autocomplete EPPO + `plague_registry`; «otra plaga»; cola sugerencias admin → dataset
- [ ] Mapa técnico con capas (calor, pendientes, validados) — presets parciales vía mapa existente
- [ ] Modo visita a finca + informe PDF

### Field Premium (ex v1.7 parcial + v1.8)
- [x] Modelo `farm_treatments` + API `/api/v1/treatments` (migración `0013`)
- [x] Contador plazo de carencia (`CarenciaBanner` + semáforo recolección)
- [x] Catálogo biocidas MAPA piloto + **ETL real MAPA CEX** (`ExportJsonProductosAutorizados`)
- [x] Motor dosis automática (`POST /api/v1/treatments/dose/calculate`)
- [x] API catálogo: `GET /treatments/catalog/status` + `POST /treatments/etl/run` (admin)
- [x] Scheduler ETL MAPA semanal (domingos 03:00 UTC)
- [x] **Mapa histórico 7 / 30 días** para `has_field_premium` (`heatmap_access.py` + `MapScreen`)
- [ ] Historial resistencias cruzadas (48 días)

### IA (ex v1.5 — pausado)
- [ ] Reentrenamiento TFLite con fotos validadas por perito
- [x] Mensaje honesto en UI: IA orientativa, perito valida (`ScanValidationBanner`, corrección agricultor)

### Infra
- [ ] FCM push alertas
- [x] APK release Nexo 2.0 (`flutter build apk --dart-define=API_BASE_URL=https://agroplaga-ai.farm`)

---

## Versión 2 — NEXO Field 2.0 ✅ COMPLETADA (piloto ago 2026)

> Experiencia comercializable en **todo el sur de Almería**: registro con fincas, mapa comunitario, CRM incidencias, clima multi-zona y SIEX borrador.

### 2.1 Registro, fincas y mapa comunitario

**Principios acordados:**
- Consentimiento mapa anónimo **obligatorio** al registrarse (`consent_map_anonymous`; backfill legacy `0025`).
- Contribución al mapa **automática** al abrir incidencia relevante.
- Compartir con **perito** opt-in por escaneo (`share_with_tech`).
- **SIGPAC recinto manual** en finca (obligatorio solo para SIEX). GPS/EXIF **descartado** por cobertura invernadero y fiabilidad.

**Wizard de registro (obligatorio ≥1 unidad):**
- [x] Paso cuenta: código invitación, nombre, email, contraseña (`RegisterScreen`)
- [x] Paso legal: aceptación condiciones + mapa comunitario anónimo (obligatorio en registro)
- [x] Paso unidades (`OnboardingWizardScreen` + gate si no hay fincas):
  - [x] Finca, nave, sector (nombres libres)
  - [x] **Municipio:** autocomplete **103 municipios** Almería (`almeria_municipalities.json` + `GET /zones`)
  - [x] **Cultivo + variante:** autocompletado (`GET /crops?q=` + `crop_catalog.json`)
  - [x] **Estado fenológico** (catálogo por cultivo)
  - [x] Superficie m²
  - [x] SIGPAC recinto opcional (obligatorio solo para cuaderno SIEX)
- [x] Backend: `Farm` con `nave`, `sector`, `crop_stage`, `crop_variant`, `zone_id`, `sigpac_code` (migraciones `0017+`)
- [x] Backend: `User.consent_accepted_at` + `ensure_map_consent()` para cuentas legacy

**Edición continua:**
- [x] «Mis fincas»: editar cultivo, fase y SIGPAC; lista primero + botón «Añadir finca»
- [ ] Historial opcional de cambios de fase (futuro IA / predicciones)

**Escaneo:**
- [ ] GPS automático al escanear (`latitude`/`longitude` en modelo; **no enviado desde app** — pospuesto)
- [x] Vincular escaneo a finca (`farm_id`); selector finca en escaneo/tratamiento
- [x] Sin prompt repetido «¿contribuir al mapa?» — consentimiento registro + incidencia (`ResultScreen`)
- [x] Agricultor puede corregir plaga IA (`farmer_plague`, migración `0024`)

### 2.2 CRM fitosanitario — ciclo de vida de incidencias ✅

**Bifurcación tras escaneo:**
- [x] Escaneo sin relevancia → historial
- [x] Escaneo relevante → **incidencia** (`PestIncident`, migraciones `0018`/`0019`)

**Etapas:**
- [x] **1 Detección** — foto, finca, cultivo, plaga IA
- [x] **2 Diagnóstico** — avance etapa + productos MAPA
- [x] **3 Prescripción** — producto, dosis, superficie parcial/total (`prescription_surface_m2`)
- [x] **4 Tratamiento** — registro + carencia + entrada SIEX borrador
- [x] **5 Evaluación** — foto comparativa (cámara/galería), mejora sí/no
- [x] **6 Cierre** — `RESUELTO` / `COSECHA PERDIDA` + export SIEX si aplica

**Reglas de flujo:**
- [x] Si **no mejora** → vuelve a **tratamiento** (no a prescripción)
- [x] Bucle tratamiento ↔ evaluación hasta mejora o cierre
- [ ] Recordatorios in-app/push: carencia activa, fecha reevaluación

**Backend / Flutter:**
- [x] Modelo + API CRUD/transiciones (`/api/v1/incidents`)
- [x] Pantalla timeline + detalle por etapas (`IncidentsScreen`, `IncidentDetailScreen`)
- [x] Enlace `Scan`, `FarmTreatment`, `OutbreakEvent`, validación perito
- [x] Cierre → `OutbreakEvent.status = closed` (excluido del heatmap)

### 2.3 Mapa de calor — Freemium vs Premium ✅

- [x] Incidencia activa → `OutbreakEvent` en municipio SIGPAC
- [x] Cierre incidencia → evento `closed`, excluido de `get_heatmap_grid`
- [x] Heatmap solo incidencias no cerradas
- [x] Backend: `enforce_map_hours` — freemium 24 h; premium 7 d / 30 d
- [x] Flutter `MapScreen`: selector histórico + chips bloqueados + CTA Premium
- [x] Panel perito/cooperativa sin restricción freemium (rol B2B)
- [ ] Copy landing comercial alineado con paywall (marketing)

### 2.4 Criterio de done Versión 2 (Field) ✅

- [x] Registro obligatorio con unidades + municipios Almería completos
- [x] Mapa auto-contribuye con consentimiento registro (sin GPS escaneo)
- [x] Incidencia completa 1→6 con bucle evaluación → tratamiento
- [x] Perito y mapa desacoplados; share_with_tech opt-in
- [x] Freemium: mapa 24 h; Premium: histórico 7 y 30 días
- [ ] Landing + piloto sur Almería alineados comercialmente (copy/marketing)

---

## Fase 2 — NEXO Climate productivo 🟡 (operativo piloto)

> Paridad con dashboard AgroData original + monetización B2C.

### Paridad funcional AgroData
- [x] Informe mensual exportable PDF (Flutter `pdf` + `printing`)
- [x] Auto-refresh cada 15 min en app (`Timer.periodic` + ETL status)
- [x] Pestaña Riesgo (`GET /api/v1/climate/riesgo` + barra semanal)
- [x] Semáforos DPV / punto de rocío en UI (`punto_rocio_status`)
- [x] Loading UX al cambiar estación meteorológica (banner + skeletons)
- [ ] Copiar histórico CSV AgroData → `backend/data/climate/` (arranque rápido ETL)

### Estaciones meteorológicas — sur de Almería ✅ (piloto)

**Implementado:** ETL Open-Meteo **multi-estación** — **11 puntos** sur almeriense (`climate_stations_sur.json`, migración `0020`).

- [x] Modelo `climate_stations` (id, slug, municipio/zone_id, lat, lon, fuente, activa)
- [x] Seed estaciones: Poniente, Roquetas, Adra, Almería capital, Níjar, Levante, etc.
- [x] ETL multi-estación → `climate_daily` / weekly / monthly con `station_id`
- [x] API Climate: métricas según estación vinculada a finca (`farm.climate_station_id`, migración `0022`)
- [x] Flutter: selector finca + estación; fallback estación más cercana al municipio
- [x] Recomendaciones y alertas DPV por estación activa
- [ ] Inventario formal fuentes (Hidrosur/AEMET/cooperativas) documentado por estación
- [ ] Ampliar rejilla si faltan microclimas (Cabezo, Tabernas…)

### Futuro IoT / B2B
- [ ] Ingesta estaciones meteorológicas locales (hardware propio)
- [ ] Sensores interior (temp, HR, CO2, suelo)
- [ ] Paywall B2C: trial 7 días, `has_climate_module` (preview abierto en piloto)
- [ ] Dashboard web Climate (React) para consultoría

---

## Fase 3 — NEXO SIEX + Enterprise 🟡 (borrador operativo — deadline 2027)

> Cumplimiento legal SIEX + panel cooperativa.

- [x] Tabla `siex_cuaderno_borrador` + compilación automática desde tratamientos/incidencias
- [x] SIGPAC recinto en finca (`farms.sigpac_code`) — **manual**; refresh entradas `pendiente_sigpac` al completar
- [x] Justificación automática (plaga/escaneo/MAPA + contexto Climate si activo)
- [x] API `/api/v1/siex/*` + hook post-tratamiento; sync entradas faltantes al listar
- [x] Flutter: pestaña SIEX + banners SIGPAC + selector finca en tratamiento
- [x] Bandeja validación perito B2B (panel web `/siex`)
- [x] Export preview JSON entradas validadas
- [x] `SIEX_PREVIEW_OPEN` en piloto (acceso agricultor sin licencia cooperativa)
- [ ] Firma digital cooperativa → `VALIDADO_OFICIAL`
- [ ] Exportador JSON schema ministerial definitivo (un clic)
- [ ] Panel multivista socios (plagas + clima agregado)
- [ ] Gestión documental (GlobalGAP, certificaciones)

---

## Fase 4 — Producción y comercial ⏳

> Cutover VPS, piloto unificado, monetización.

- [x] Backup PostgreSQL antes de deploy (protocolo jul–ago 2026)
- [x] Deploy rama `nexoagro` a VPS producción (`deploy/vps-deploy-v2.sh`, `agroplaga-ai.farm`)
- [ ] Apagar stack legacy AgroData en VPS (`agrodata-*`)
- [ ] Piloto 5–6 agricultores con app Nexo unificada (ampliación sur Almería)
- [ ] Métricas Lean → pivotar o perseverar
- [ ] Repo definitivo `NexoAgro` (rebrand GitHub opcional)
- [ ] Paquete comercial implantación cooperativas

---

## TODO — Dominio principal `agroplaga.es` + Google Workspace

> **Prioridad:** cuando V2 esté validada en local / antes de escalar comercial.  
> **Situación actual:** producción en `https://agroplaga-ai.farm` (Namecheap).  
> **Objetivo:** `https://agroplaga.es` (IONOS) como dominio principal.  
> **SSL web/API:** Caddy + Let's Encrypt en el VPS (no Google Workspace).

### Checklist DNS (IONOS)

- [ ] Registro **A** `@` → IP del VPS
- [ ] Registro **A** `www` → misma IP (o CNAME `www` → `@`)
- [ ] Verificar propagación: `nslookup agroplaga.es`
- [ ] Registros **MX** → Google Workspace (cuando el correo esté listo)
- [ ] Registros **TXT** → verificación Google + SPF + DKIM

### Checklist Google Workspace (solo correo)

- [ ] Alta Google Workspace con dominio `agroplaga.es`
- [ ] Verificar dominio (TXT en IONOS)
- [ ] MX + SPF + DKIM según asistente Google Admin
- [ ] Crear buzones (`hola@`, `piloto@`, `soporte@`, etc.)

### Checklist VPS / despliegue

- [ ] `API_DOMAIN=agroplaga.es` en `deploy/pilot.env`
- [ ] Actualizar `deploy/pilot.env.example` con `agroplaga.es` como ejemplo
- [ ] Añadir bloque **redirect 301** `agroplaga-ai.farm` → `agroplaga.es` en `deploy/Caddyfile`
- [ ] Redeploy: `docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env -p agroplaga up -d --build`
- [ ] Probar HTTPS: `https://agroplaga.es/`, `/panel/`, `/api/v1/climate/health`
- [ ] Mantener `agroplaga-ai.farm` en Namecheap apuntando al mismo VPS (redirect legacy)

### Checklist app y comunicación

- [ ] APK release: `flutter build apk --dart-define=API_BASE_URL=https://agroplaga.es`
- [ ] Actualizar landing, `docs/`, guías piloto y enlaces comerciales al dominio `.es`
- [ ] Avisar a pilotos / repartir nueva APK

### Orden recomendado (sin cortar servicio)

1. DNS `agroplaga.es` → VPS (convive con `.farm`)
2. Probar HTTPS en `.es` (Caddy emite cert cuando DNS resuelve)
3. Google Workspace en paralelo (MX no afecta la web)
4. Redirect `.farm` → `.es`
5. Nueva APK y comunicación a usuarios

---

## Seguridad — IMPORTANTE (post-V2 / pre-comercialización)

> **Estado ago 2026:** aplicado hardening P0+P1 en código (JWT, alertas, heatmap, secure storage, HTTPS release, etc.). **70/70 tests backend.** Pendiente infra y capa avanzada.

- [ ] **Certificate pinning** (Flutter release) — fijar certificado/clave pública del API `agroplaga.es` para bloquear MITM incluso con HTTPS
- [ ] **Rate limiting distribuido** (Redis) — sustituir buckets en memoria cuando haya >1 worker o varias instancias
- [ ] **WAF / firewall VPS** — reglas en Hetzner/Cloudflare (solo 80/443, geo opcional, bloqueo brute-force)
- [ ] **Auditoría externa** — pentest ligero antes de registro abierto o cooperativas de pago
- [ ] **Rotación de secretos** — procedimiento documentado para `SECRET_KEY`, DB, SMTP

*(Ver también: [TODO — Dominio `agroplaga.es`](#todo--dominio-principal-agroplagaes--google-workspace) arriba.)*

---

## Orden de construcción

```
Fase 0 ✅
    MVP 1.B ✅ (Field Pro + notificaciones perito)
        Versión 2 Field ✅ (registro + incidencias + mapa premium)
            Versión 2 Climate ✅ piloto (11 estaciones sur Almería)
                SIEX borrador ✅ (SIGPAC manual + refresh)
                    Piloto ampliado sur Almería + métricas Lean
                        Fase 1 gaps (catálogo perito, FCM, PDF visita)
                            Fase 3 SIEX cooperativa (deadline 2027)
                                Fase 4 comercial + dominio agroplaga.es
```

**Enfoque actual:** validar V2 en campo; priorizar FCM, copy comercial y SIEX cooperativa según feedback piloto.

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
| ago 2026 | Hardening seguridad P0+P1 (JWT, RBAC alertas, secure storage, HTTPS release) |
| ago 2026 | Spec **Versión 2** acordada (registro, CRM incidencias, clima sur Almería) |
| ago 2026 | **V2 Field:** onboarding, CRM incidencias 1→6, mapa premium, fincas, `farmer_plague`, consent legacy |
| ago 2026 | **V2 Climate:** 11 estaciones, selector finca/estación, loading UX |
| ago 2026 | **SIEX borrador:** SIGPAC manual, `pendiente_sigpac` + refresh retroactivo, banners UX |
| ago 2026 | APK `NEXO-Field-Pro-2.0.0` + commits `c525f14`–`fe0ce2b` en `nexoagro` |

---

*Mantener este archivo como única fuente de verdad de ejecución. Marcar `[x]` al completar tareas.*
