# AgroPlaga AI — Roadmap de Desarrollo

**Autor:** Valentín Ruiz León  
**Actualizado:** 15 jun 2026  
**Estado:** ✅ **v1 MVP completado** — validado en dispositivo Android + backend Docker (LAN)

---

## Alcance por versión

| Versión | Objetivo | Incluye |
|---------|----------|---------|
| **v1 (MVP)** | Escanear y colaborar perfectos | PlagaScan, contribución al mapa, heatmap, alertas reactivas, gamificación, panel B2B, analítica personal |
| **v2** | Previsión y refinamiento avanzado | Predicción climática, modelos ARIMA/Prophet, capa de riesgo en mapa, KDE/Redis, FCM, PDF, hardening producción |

**Decisión (jun 2026):** la predicción queda **fuera del MVP**. Primero cerrar v1 redondo; estudiar previsión cuando haya datos y uso real.

---

## Visión del producto

AgroPlaga AI combina **diagnóstico fitosanitario offline** (PlagaScan + TFLite) con una **red colaborativa comunitaria** que genera mapas de calor y alertas tempranas. La **predicción de brotes** (clima + series temporales) es objetivo de **v2**, cuando el núcleo escaneo/colaboración esté validado. Las zonas geográficas usan referencias **SIGPAC** a nivel municipio/recinto, familiares para el agricultor y sin exponer parcelas concretas.

**Clientes:** agricultor (móvil), técnico de cooperativa (móvil + web), administrador (web).

---

## Decisiones de arquitectura (v1)

| Tema | Decisión |
|------|----------|
| `outbreaks` (tabla antigua) | **Eliminada.** Sustituida por `outbreak_events` (eventos colaborativos anonimizados). |
| Zonas geográficas | Tabla `agri_zones` con códigos SIGPAC municipio (`04-087` = Almería–El Ejido). Sin parcela ni polígono exacto en datos públicos. |
| Privacidad | Los eventos colaborativos **no almacenan `user_id`**. La reputación del usuario se gestiona con contador interno desacoplado. |
| Severidad | Escala numérica unificada: `1` Leve, `2` Moderado, `3` Alto. |
| Geometría | PostGIS: centroide municipal + jitter controlado (~150–400 m) para el mapa. |
| Web cooperativas | API REST compartida. Panel web separado (React) en fase posterior; misma API que el móvil. |
| Heatmap / alertas | Servicios desacoplados (`heatmap_service`, `alert_engine`) con precomputación y cache (Redis en producción). |

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
- [ ] Reentrenamiento con `ml/extra_data/` (insectos de invernadero) — **pausado post-MVP**

**Entregable:** diagnóstico offline en tiempo real. ✅ Validado en Android release.

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

### Fase 8 — Analítica personal y recomendaciones ✅ COMPLETADA (MVP)
- [x] Gráficas cronológicas por finca/cultivo (`/api/v1/analytics/me`)
- [x] Motor de recomendaciones (plaga + cultivo + severidad)
- [x] Historial avanzado con badges de severidad y fechas
- [x] Stats endpoints para usuario y zona (`/analytics/zones/{id}`)
- [x] Pantalla Flutter "Mi analítica" + recomendaciones en resultado
- [x] Selector de finca opcional al guardar escaneo (`farm_id` en scans)

**Entregable:** valor agronómico personalizado.

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

**v2 (siguiente horizonte):**
```
Datos acumulados + feedback IA
    → Open-Meteo + modelos por zona/plaga
        → Capa de riesgo predictivo en mapa
```

---

## Stack por capa

| Capa | Tecnología |
|------|------------|
| Móvil | Flutter, TFLite, flutter_map, FCM |
| Web cooperativas | React + TypeScript, Leaflet |
| API | FastAPI, Pydantic, SQLAlchemy, GeoAlchemy2 |
| BD | PostgreSQL 16 + PostGIS |
| Cache | Redis (fase 4+) |
| Jobs | APScheduler / Celery (fase 5+) |
| IA entrenamiento | TensorFlow/Keras, Colab |
| IA inferencia | TFLite en dispositivo |
| Infra | Docker Compose → VPS, S3, TLS |

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

## Próximo sprint — post-MVP

**Opción A — v1.5 IA:** reentrenamiento con capturas locales + feedback usuarios  
**Opción B — Fase 10:** despliegue VPS, TLS, hardening para mercado  
**Opción C — v2:** predicción climática cuando haya volumen de datos (Fase 9)

**Explícitamente fuera del MVP cerrado:** Fase 9 (predicción) hasta decidir v2.
