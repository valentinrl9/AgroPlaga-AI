# AgroPlaga AI — Roadmap de Desarrollo

**Autor:** Valentín Ruiz León  
**Actualizado:** 4 jul 2026  
**Estado:** ✅ **v1 MVP + v1.6-core** — piloto Lean en campo

---

## Alcance por versión

| Versión | Objetivo | Incluye |
|---------|----------|---------|
| **v1 (MVP)** | Escanear y colaborar | PlagaScan, mapa SIGPAC, alertas, panel B2B, analítica personal ✅ |
| **v1.6-core** | Validación perito con foto | Cola panel, corregir plaga, opt-in agricultor ✅ |
| **v1.6 (completo)** | Experiencia móvil perito/técnico | Centro de mando, mapa capas, informes, modo cooperativa |
| **v1.7 (CEX)** | Cuaderno de campo digital | `farm_treatments`, plazos de seguridad, export PDF/CSV perito/cooperativa |
| **v1.8 (Biocidas)** | Recomendaciones con validez normativa | Catálogo local productos autorizados (Ministerio), cruce plaga → TP18 |
| **v1.5 IA** | Reentrenamiento con campo real | Fotos validadas por perito → nuevo TFLite *(pausado hasta fotos piloto)* |
| **v2** | Previsión y refinamiento avanzado | Predicción climática, ARIMA/Prophet, KDE/Redis, FCM, hardening producción |

**Decisión (jun 2026):** la predicción queda **fuera del MVP**. Primero cerrar v1 redondo; estudiar previsión cuando haya datos y uso real.

---

## Visión del producto

AgroPlaga AI combina **diagnóstico fitosanitario offline** (PlagaScan + TFLite) con una **red colaborativa comunitaria** que genera mapas de calor y alertas tempranas. La **predicción de brotes** (clima + series temporales) es objetivo de **v2**, cuando el núcleo escaneo/colaboración esté validado. Las zonas geográficas usan referencias **SIGPAC** a nivel municipio/recinto, familiares para el agricultor y sin exponer parcelas concretas.

**Clientes:** agricultor (móvil), técnico de cooperativa (móvil + web), administrador (web).

---

## Decisiones de arquitectura (v1)

| Tema | Decisión | Justificación |
|------|----------|---------------|
| `outbreaks` (tabla antigua) | **Eliminada.** Sustituida por `outbreak_events` (eventos colaborativos anonimizados). | |
| Zonas geográficas | Tabla `agri_zones` con códigos SIGPAC municipio (`04-087` = Almería–El Ejido). Sin parcela ni polígono exacto en datos públicos. | |
| Privacidad | Los eventos colaborativos **no almacenan `user_id`**. La reputación del usuario se gestiona con contador interno desacoplado. | |
| Severidad | Escala numérica unificada: `1` Leve, `2` Moderado, `3` Alto. | |
| Geometría | PostGIS: centroide municipal + jitter controlado (~150–400 m) para el mapa. | |
| Web cooperativas | API REST compartida. Panel web separado (React) en fase posterior; misma API que el móvil. | |
| Heatmap / alertas | Servicios desacoplados (`heatmap_service`, `alert_engine`) con precomputación y cache (Redis en producción). | |
| **Cuaderno de Campo (CEX)** | Integrar tabla `farm_treatments` vinculada a `scans`, `farms` y `agri_zones`. Exportación estructurada (PDF/CSV) para perito y cooperativa. Registro **opt-in** del agricultor tras decidir aplicar tratamiento. | Transforma una obligación burocrática tediosa en un automatismo derivado del propio escaneo con IA offline. El perito y la cooperativa reciben borrador en tiempo casi real. |
| **Registro Oficial de Biocidas** | Réplica local en PostgreSQL del catálogo del Ministerio de Sanidad; actualización ETL periódica. Consulta offline en app/panel sin depender del portal en tiempo real. | Recomendaciones fitosanitarias alineadas con productos **TP18** (insecticidas/acaricidas) autorizados en España. Complementa CEX y el motor de recomendaciones actual. |

---

## Fases de implementación

### Fase 0 — Diseño y especificación ✅ ~70 %
- [x] Guía técnica integral
- [x] Anexo comunidad (mapa de calor, alertas, gamificación)
- [x] Decisiones de arquitectura de datos
- [ ] Wireframes pantallas críticas
- [x] Catálogo 15 plagas Poniente Almeriense (`shared/plague_catalog.json`)
- [ ] Importación catálogo SIGPAC municipios Poniente Almeriense

**Entregable:** documento funcional cerrado.

---

### Fase 1 — Backend core e infraestructura ✅ COMPLETADA (MVP v1)
- [x] FastAPI + PostgreSQL + Docker
- [x] JWT auth (register, login)
- [x] Alembic migraciones automáticas al arranque
- [x] PostGIS habilitado
- [x] Modelos `agri_zones`, `outbreak_events`, `alerts`
- [x] Endpoints `/zones`, `/outbreak-events`, `/alerts`
- [x] Servicio geo (jitter, validación anti-GPS exacto)
- [x] Refresh tokens (`POST /auth/refresh`)
- [x] Rate limiting en `/auth`
- [x] Rol `tech` completo en RBAC (validación, dashboard B2B)
- [x] Tests PyTest (auth, events, zones, scans, plagas) — `backend/tests/`
- [x] `get_db` centralizado en `api/deps.py`

**Entregable:** API colaborativa funcional y testeada.

---

### Fase 2 — Esqueleto Flutter + integración API ✅ COMPLETADA (MVP v1)
- [ ] BLoC/Provider para auth y scans (v2)
- [x] Splash + auto-login con validación de token
- [ ] Onboarding, profile (v2)
- [x] Conectar historial y login
- [x] Selector de zona SIGPAC en flujo de contribución
- [x] Flujo consentimiento: "¿Contribuir al mapa?" → POST evento
- [x] Widget `severity_badge`
- [x] Pantalla alertas + mapa con datos reales (lista)
- [x] Widgets: `card_scan`, `map_legend`
- [x] Persistencia de token y auto-login
- [x] Ajustes → URL del API (`ApiConfig`) + acceso desde login en móvil físico
- [x] Refresh token automático en `ApiClient` (retry 401)

**Entregable:** app navegable con contribución colaborativa real.

---

### Fase 3 — IA local (PlagaScan) ✅ MVP v1 · ⏸️ refinamiento v1.5
- [x] Dataset PlantVillage + carpeta `ml/extra_data/` para capturas locales
- [x] Entrenamiento MobileNetV3 (`ml/train_plagascan.py`)
- [x] Exportación `.tflite` cuantizado → `frontend/assets/ml/plaga_model.tflite`
- [x] Integración image_picker (cámara/galería)
- [x] Pantalla PlagaScan con preview y guías UX
- [x] Módulo ML (`plaga_classifier`) con labels desde assets
- [x] Flujo: imagen → IA → guardar scan → contribuir
- [x] Inferencia TFLite en Android/iOS + heurística web
- [x] Catálogo ampliado a 15 plagas Poniente (`docs/PLAGAS_PONIENTE.md`)
- [x] API `GET /api/v1/plagues` + recomendaciones para las 15 clases
- [ ] Reentrenamiento con `ml/extra_data/` (insectos de invernadero) — **⏸️ pausado** hasta fotos verificadas de perito/piloto

#### v1.5 — Feedback IA y roles (decisión post-piloto, jun 2026)
> **Decisión de producto:** el agricultor **no corrige** la plaga detectada (no es experto; genera desconfianza si la IA falla a menudo).  
> El agricultor solo indica **confianza / utilidad** del resultado («¿te ha sido útil?» / «¿te fías lo suficiente para actuar?»).  
> La **validación y corrección** de diagnósticos para mapa y reentrenamiento corresponde al **técnico/perito** (app + panel web).

- [x] **Quitar** botón «No, corregir plaga» del flujo agricultor (`result_screen.dart`).
- [x] **Sustituir** por pregunta de confianza/utilidad (sin pedir nombre de plaga); comentario en API feedback (`util_orientacion` / `no_confianza_utilidad`).
- [ ] **Mensaje honesto en UI:** la IA es orientativa; el técnico valida lo dudoso; mejoras del modelo en versiones futuras.
- [ ] **Validación técnica de escaneos** (v1.6): perito corrige plaga/severidad; auditado (`validated_by`, `corrected_plague`).
- [ ] **Pipeline reentrenamiento:** exportar solo pares imagen+etiqueta **validados por técnico** → `ml/extra_data/` → `train_plagascan.py`.
- [ ] Deprecar o restringir `corrected_plague` en feedback de rol `farmer` (mantener API para migración).

**Entregable v1.5:** circuito de mejora IA **credibile** (experto valida → datos → nuevo TFLite), sin cargar al agricultor.

**Entregable MVP:** diagnóstico offline en tiempo real. ✅ Validado en Android release.

---

### Fase 4 — PlagaHub: mapa y heatmap ✅ COMPLETADA (MVP)
- [x] `MapRepository` conectado a API real
- [x] Mapa con `flutter_map` + marcadores por zona SIGPAC
- [x] Filtro por tipo de plaga
- [x] Leyenda de severidad + detalle al tocar zona
- [x] Zonas API con coordenadas (centroide municipal)
- [x] Endpoint `/api/v1/heatmap` con agregación por zona e intensidad
- [x] Filtros: severidad, ventana temporal (24 h / 7 d / 30 d)
- [x] Modos de vista: Calor / Marcadores / Ambos
- [ ] Cache Redis de tiles (producción)
- [ ] KDE gaussiano / grid 500 m (refinamiento v2)

**Entregable:** mapa colaborativo operativo.

---

### Fase 5 — Motor de alertas tempranas ✅ COMPLETADA (MVP v1)
- [x] `alert_engine`: Z-score, media móvil, comparación ventanas
- [x] Reglas: spike +35 %, plaga nueva, severidad acumulada
- [x] Score prioridad: `severidad × 0.6 + incremento × 0.4`
- [x] Job programado (APScheduler cada 30 min + escaneo al arranque)
- [x] API preferencias por plaga + descartar alerta + scan manual (admin)
- [x] Pantalla alertas en app + preferencias por plaga
- [ ] Notificaciones push (FCM) — stub listo, pendiente Firebase

**Entregable:** alertas automáticas por zona.

---

### Fase 6 — Calidad, validación y gamificación ✅ COMPLETADA (MVP)
- [x] Validación de eventos por rol `tech` / `admin` (API + pantalla Flutter)
- [x] Peso mayor de eventos validados en heatmap (×1.5)
- [x] Insignias, ranking por zona, vigilancia semanal (1 escaneo/semana)
- [x] API feedback para reentrenamiento IA (correcto / plaga corregida)
- [x] Anti-spam por usuario (5/h, 2 repetidos zona+plaga/día)
- [x] Tabla `farms` con tipo finca/invernadero

**Entregable:** red colaborativa fiable e incentivada.

---

### Fase 7 — Panel web cooperativas (B2B) ✅ COMPLETADA (MVP)
- [x] Frontend web React + TypeScript (`web-panel/`)
- [x] Login JWT compartido con API (OAuth2 `/auth/token`)
- [x] Dashboard: comparativa zonas, evolución histórica, focos críticos
- [x] Validación de eventos desde web
- [x] Exportación informes CSV (`/api/v1/tech/export/events.csv`)
- [x] Vista agregada rol `tech` / `admin` (sin datos de parcela)
- [ ] Exportación PDF (pendiente)

**Entregable:** herramienta de oficina para cooperativas.

---

### Fase 8 — Analítica personal, recomendaciones y Cuaderno de Campo (CEX) ✅ MVP v1 · 🔄 Expansión CEX (v1.7)

- [x] Gráficas cronológicas por finca/cultivo (`/api/v1/analytics/me`)
- [x] Motor de recomendaciones (plaga + cultivo + severidad)
- [x] Historial avanzado con badges de severidad y fechas
- [x] Stats endpoints para usuario y zona (`/analytics/zones/{id}`)
- [x] Pantalla Flutter "Mi analítica" + recomendaciones en resultado
- [x] Selector de finca opcional al guardar escaneo (`farm_id` en scans)
- [ ] **[CEX v1.7]** Crear modelo `FarmTreatment` (materia activa, n.º registro Ministerio, dosis, plazo de seguridad, fecha aplicación, producto fitosanitario).
- [ ] **[CEX v1.7]** Flujo en app: tras la inferencia IA, opción **«Registrar tratamiento»** (opt-in del agricultor) que pre-rellena datos fitosanitarios a partir del escaneo y la recomendación.
- [ ] **[CEX v1.7]** Alertas en UI: aviso/bloqueo visual si el cultivo está dentro del **plazo de seguridad** obligatorio para recolección.
- [ ] **[CEX v1.7]** Vista tiempo real en panel cooperativa/perito: apuntes de tratamiento por agricultor/finca (solo los compartidos explícitamente).
- [ ] **[CEX v1.7]** Módulo de exportación de borrador CEX (PDF/CSV) desde perfil del agricultor y panel de la cooperativa.

**Entregable MVP v1:** valor agronómico personalizado.  
**Entregable v1.7 (CEX):** cuaderno de campo digital vinculado al flujo de escaneo → tratamiento → exportación para cumplimiento y asesoramiento técnico.

---

### Fase 12 — Integración con Registro Oficial de Biocidas (Ministerio de Sanidad) ⏳ PENDIENTE (v1.8)

> **Estado:** PENDIENTE — retomar tras v1.7 CEX y/o cuando el motor de recomendaciones deba ofrecer productos con **validez normativa** en España.  
> **Objetivo:** Cruzar los diagnósticos visuales del motor de IA (y las correcciones del perito) con el catálogo legal de productos autorizados, para recomendaciones fitosanitarias/biocidas útiles a técnicos y cooperativas.

#### Especificaciones técnicas

- [ ] **Módulo ETL (Python / FastAPI backend):** *cron job* mensual (o flujo automatizado) que ejecute scraping programático sobre el portal de Sanidad:  
  `https://www.sanidad.gob.es/ciudadanos/productos.do?tipo=biocidas`
- [ ] **Estrategia de extracción:** Sin API pública — interceptar el formulario dinámico mediante peticiones HTTP (`POST`/`GET` al método `realizarBusqueda`) y parsear el árbol HTML con **BeautifulSoup** o **Selectolax**.
- [ ] **Data warehouse local (PostgreSQL):** Tabla(s) dedicada(s), p. ej. `biocide_products`, con al menos:
  - Nombre comercial y **número de registro oficial**
  - Clasificación de usuarios (profesional, especializado, público)
  - Composición química (sustancias activas y porcentajes)
  - Tipo de producto — foco **TP18** (insecticidas y acaricidas)
  - Metadatos de sincronización (`synced_at`, hash de versión del catálogo)
- [ ] **Mapeo plaga → producto:** Tabla de relación `plague_biocide` (EPPO / etiqueta AgroPlaga ↔ materias activas / registros TP18), mantenida por perito o seed inicial + revisión técnica.
- [ ] **API interna:** `GET /api/v1/biocides?plague=…` (y variantes panel B2B) sirviendo **solo datos locales** — latencia mínima, disponibilidad 100 % sin depender de servidores externos en tiempo real.
- [ ] **Consumo en app:** Enriquecer pantalla de resultado y flujo CEX v1.7 con productos TP18 autorizados sugeridos (siempre como **orientación**; decisión final del técnico).
- [ ] **Panel B2B:** Vista de catálogo local, fecha última sync y alerta si el ETL falla o el catálogo lleva >30 días sin actualizar.
- [ ] **Cumplimiento legal:** Atribución fuente Ministerio; disclaimer en UI («consulte ficha oficial y legislación vigente»).

**Dependencias:** v1.7 CEX (`farm_treatments` con n.º registro) · catálogo 15 plagas (`shared/plague_catalog.json`) · recomendaciones actuales (Fase 8 MVP).

**Entregable v1.8:** recomendaciones fitosanitarias cruzadas con biocidas autorizados en España, consultables offline desde la app y el panel.

---

### Fase 9 — Predicción y clima ⏸️ DIFERIDA (v2)
> No forma parte del MVP. Requiere volumen de datos históricos y v1 estable.

- [ ] Integración Open-Meteo
- [ ] Modelos ARIMA / Prophet por zona y plaga
- [ ] Predicción probabilística en mapa
- [ ] Clasificador secundario anti falsos positivos
- [ ] Pipeline reentrenamiento semanal

**Entregable v2:** herramienta predictiva, no solo reactiva.

---

### Fase 11 — Experiencia móvil perito / técnico ⏳ PENDIENTE (post-piloto)
> **Cuándo:** tras cerrar las validaciones del piloto Lean (`docs/PILOTO_EXPERIMENTO.md`).  
> **Problema:** hoy agricultor y perito comparten casi la misma app; el rol `tech` solo añade “Validar eventos”. El panel B2B web ya existe; falta **diferenciar la app móvil** para que el perito sienta una herramienta profesional propia.  
> **Principio:** misma app, **home y flujos distintos por rol**; reutilizar API existente (`/tech/dashboard`, heatmap, outbreak-events, farms, alerts).

#### Bloque A — Identidad de rol (base, semana 1)
- [ ] **Home “Centro de mando”** para `tech` / `admin`: KPIs grandes (pendientes de validar, % validados, zonas activas, alertas abiertas) consumiendo `GET /api/v1/tech/dashboard`.
- [ ] Navegación inferior o menú distinto al del agricultor (priorizar validación, mapa técnico, informes).
- [ ] Ocultar o relegar flujos de consumo (PlagaScan como acción secundaria, no hero del home técnico).

#### Bloque B — Validación profesional (semana 1–2)
- [ ] **Cola de validación fullscreen** (“swipe técnico”): un evento a pantalla completa con foto del scan, plaga, confianza del modelo, mapa mini y acciones **Confirmar / Corregir / Descartar**.
- [ ] **Corregir diagnóstico** al validar: campos `corrected_plague`, `corrected_severity`, `tech_notes` + auditoría (`validated_by`, `validated_at`).
- [ ] **Segunda opinión del modelo**: mostrar predicción IA + top alternativas con %; el perito elige la correcta o “ninguna” (requiere exponer top-N del clasificador o stub inicial en API).

#### Bloque C — Visibilidad en el territorio (semana 2–3)
- [ ] **Sello “Validado por técnico”** en mapa y comunidad cuando `validated=true` (nombre o rol del validador, sin parcela).
- [ ] **Mapa técnico con capas** (toggles): calor IA, solo pendientes, solo validados por mí, alertas activas (reutilizar `/heatmap` + filtros en `outbreak-events`).
- [ ] **Modo “Visita a finca”**: seleccionar finca/zona → últimos scans del agricultor, alertas activas e historial de la zona (filtros sobre endpoints existentes).

#### Bloque D — Priorización e impacto (semana 3–4)
- [ ] **Alertas prioritarias para peritos**: bandeja o push in-app de eventos `validated=false` con severidad alta en zonas activas (FCM opcional en v2; in-app suficiente al inicio).
- [ ] **Panel de impacto personal**: eventos validados esta semana, tasa de corrección al modelo, zonas cubiertas (agregaciones SQL por `validated_by`).
- [ ] **Modo cooperativa (multi-agricultor)**: lista de agricultores del piloto con semáforo verde/ámbar/rojo (sin alertas / pendientes / severidad alta).

#### Bloque E — Entregables de campo (semana 4–5)
- [ ] **Bitácora de campo con voz**: nota de audio (30–60 s) adjunta al validar; upload + `tech_audio_url` (transcripción diferida).
- [ ] **Informe PDF de visita** (1 página): mapa, eventos, validaciones y recomendaciones; botón desde “Visita a finca” o dashboard (Flutter PDF o reutilizar lógica del export CSV del panel web).

**Entregable v1.6:** app móvil donde el perito tiene **centro de mando, validación pro, mapa con capas e informe**, claramente diferenciada del flujo agricultor.

**Dependencias:** piloto Lean cerrado · datos reales de validación · APK piloto estable en producción.

---

### Fase 10 — Producción y auditoría (v1 cierre / v2 hardening)
- [ ] HTTPS, CORS estricto, secretos en vault
- [ ] Cifrado backups AES-256
- [ ] k-anonymity en agregaciones públicas
- [ ] Pruebas de carga
- [ ] Builds Android/iOS + despliegue VPS
- [ ] S3 para imágenes de referencia

**Entregable:** producto listo para mercado e inversores.

---

## Orden de construcción (lógica de proyecto)

**v1 — cerrado (jun 2026):**
```
PlagaScan (IA + guardar + finca)
    → Contribución al mapa (consentimiento + zona SIGPAC)
        → Heatmap + alertas reactivas
            → Comunidad (validación, gamificación)
                → Panel B2B + analítica personal
                    → APK release + checklist E2E en dispositivo ✅
```

**Post-piloto — v1.6 Experiencia perito (tras validaciones de campo):**
```
Piloto Lean cerrado + métricas cualitativas
    → Home “Centro de mando” (tech dashboard en móvil)
        → Validación pro (fullscreen + corregir + segunda opinión)
            → Mapa con capas + sello “Validado por técnico”
                → Visita a finca + alertas prioritarias + impacto personal
                    → Modo cooperativa + bitácora voz + informe PDF
```

**Post-piloto — v1.7 CEX + v1.8 Biocidas:**
```
v1.7 farm_treatments + plazos seguridad + export CEX
    → v1.8 ETL catálogo Ministerio (biocidas TP18) en PostgreSQL
        → Cruce plaga AgroPlaga ↔ productos autorizados (app + panel, consulta local)
```

**v2 (siguiente horizonte):**
```
Datos acumulados + feedback IA + v1.6 en producción
    → Open-Meteo + modelos por zona/plaga
        → Capa de riesgo predictivo en mapa
            → FCM push, Redis, hardening comercial
```

---

## Stack por capa

| Capa | Tecnología | Rol / notas |
|------|------------|-------------|
| Móvil | Flutter, TFLite, flutter_map, FCM | Inferencia offline + flujos campo |
| Web cooperativas | React + TypeScript, Leaflet | Panel B2B, validación, dashboard |
| API | FastAPI, Pydantic, SQLAlchemy, GeoAlchemy2 | REST + PostGIS |
| **Exportación CEX** | ReportLab + Pandas (Python) | Borrador estructurado del Cuaderno de Campo (PDF/CSV) para perito y cooperativa *(v1.7)* |
| **ETL Biocidas** | BeautifulSoup / Selectolax + APScheduler | Sincronización mensual catálogo Ministerio → PostgreSQL *(v1.8)* |
| BD | PostgreSQL 16 + PostGIS | Datos transaccionales + geo + catálogo biocidas local |
| Cache | Redis (fase 4+) | Heatmap / alertas |
| Jobs | APScheduler / Celery (fase 5+) | Precomputación + cron ETL biocidas |
| IA entrenamiento | TensorFlow/Keras, Colab | Reentrenamiento v1.5 |
| IA inferencia | TFLite en dispositivo | PlagaScan offline |
| Infra | Docker Compose → VPS, S3, TLS | Piloto y producción |

---

## v1 MVP — cierre (15 jun 2026) ✅

**Validación E2E en dispositivo Android** (APK release + Docker LAN `192.168.x.x:8000`):

| Flujo | Estado |
|-------|--------|
| Login / registro | ✅ |
| Auto-login al reabrir app | ✅ |
| PlagaScan → guardar → recomendaciones | ✅ |
| Contribución al mapa (SIGPAC) | ✅ |
| Mapa + heatmap + filtros | ✅ |
| Alertas + preferencias | ✅ |
| Comunidad / analítica | ✅ |

**Build release:**
```bash
cd frontend
flutter build apk --release --dart-define=API_BASE_URL=http://<IP_PC>:8000
```
APK: `frontend/build/app/outputs/flutter-apk/app-release.apk`

**Pendiente fuera del MVP (no bloquea demo/piloto):**
- Pulir precisión IA (`ml/extra_data/`) — v1.5
- FCM push, export PDF panel, catálogo SIGPAC ampliado, Redis cache
- Fase 10 producción (HTTPS, VPS, store)

---

## v1.6-core ✅ (completado)

**Decisión 15 jun 2026:** adelantar validación perito con foto **antes** de demos B2B.

Checklist, despliegue y estado del piloto: [ROADMAP_LEAN.md](ROADMAP_LEAN.md) → Fase 3b.

| Orden | Fase | Objetivo |
|-------|------|----------|
| ~~1~~ | ~~**v1.6-core**~~ | ✅ Foto opt-in, cola panel, corregir plaga, semáforo agricultores |
| **2 (ahora)** | Piloto H4 | Entrevistas técnicos/cooperativa con panel v1.6-core |
| 3 | **v1.6 completo** (Fase 11) | Centro de mando móvil, mapa capas, informes PDF |
| 4 | **v1.5 IA** | Reentrenamiento con fotos validadas por perito |
| 5 | **v1.7 CEX** | Cuaderno de campo: `farm_treatments`, plazos seguridad, export perito/cooperativa |
| 6 | **v1.8 Biocidas** | ETL catálogo Ministerio + recomendaciones TP18 con validez normativa |
| 7 | **Fase 10 / v2** | Hardening + predicción |

**Explícitamente fuera del MVP cerrado:** Fase 9 (predicción) hasta decidir v2.
