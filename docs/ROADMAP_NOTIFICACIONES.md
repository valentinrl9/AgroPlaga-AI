# NEXO Agro — Roadmap notificaciones y badges

**Autor:** Valentín Ruiz León  
**Actualizado:** 4 sep 2026  
**Rama:** `nexoagro`  
**Estado:** ✅ **Fases 1–5 completadas** (in-app + FCM + pulido) — sep 2026  
**Producción:** `https://agroplaga.es` · migración Alembic **`0028_notification_preferences`**

Documento de referencia para **puntos rojos (badges)**, **notificaciones in-app** y **push real (FCM)** en app móvil agricultor y perito + panel web.

---

## Resumen ejecutivo

| Capa | Qué es | Estado actual |
|------|--------|---------------|
| **Notificación in-app** | Registro en BD («tienes 2 sin leer») | Perito: `tech_notifications` ✅ · Agricultor: `user_notifications` ✅ |
| **Punto rojo (badge)** | Indica sección con pendientes no vistos | Panel web perito ✅ · App agricultor (Historial, Incidencias, Comunidad, Alertas) ✅ |
| **Polling + SnackBar** | App pregunta al servidor cada ~30 s | Perito app ✅ · Agricultor ✅ |
| **Gamificación** | Reto semanal, racha, insignias recurrentes, objetivo piloto | ✅ Comunidad + Inicio |
| **Recordatorios incidencias** | Tratar, carencia, foto seguimiento (cron 1 h) | ✅ Scheduler + banner Inicio |
| **Push FCM** | Notificación del sistema con app cerrada | ✅ Fase 4 |

**Principio de diseño:** badge = «hay algo sin mirar»; push = solo si es **accionable**, **urgente** o **esperado** (p. ej. el agricultor pidió validación al perito).

---

## Mapa de fases (ejecución sep 2026)

| Fase | Alcance | Estado |
|------|---------|--------|
| **1** | MVP in-app agricultor (BD, hooks validación perito, badges, polling) | ✅ sep 2026 |
| **2** | Gamificación (reto/racha, toasts, objetivo piloto Comunidad) | ✅ sep 2026 |
| **3** | Recordatorios incidencias CRM (tratar, carencia, evaluación) | ✅ sep 2026 |
| **4** | Push FCM Android (`device_tokens`, Firebase Admin SDK, app cerrada) | ✅ sep 2026 |
| **5** | Pulido: preferencias, alertas comarcal push, anti-spam, horario quieto | ✅ sep 2026 |

*(Las fases 1–3 del plan original de 25 ago se entregaron juntas en commit `ec889f5`.)*

---

## Estimación de esfuerzo (restante)

| Fase | Alcance | Tiempo (1 dev) |
|------|---------|----------------|
| **1–3** | In-app + gamificación + incidencias | ✅ Hecho |
| **4 — FCM Android** | Firebase + `device_tokens` + Admin SDK + Flutter messaging | **3–4 días** |
| **5 — Pulido** | Preferencias, alertas comarcal push, anti-spam, horario quieto | **2–3 días** |

**Recomendación piloto:** Fase 4 en 3 eventos críticos (confirm / correct / reject perito + carencia). Fase 5 tras validar que FCM no spamea.

---

## División de responsabilidades (implementación)

### Agente / código (repo)

- Backend: `user_notifications`, `device_tokens`, endpoints `activity-summary` / `activity-seen`
- Hook en `validate_scan()` → notificar agricultor
- Sustituir stub `send_push_to_user` por Firebase Admin SDK
- Flutter: badges en `NexoActionTile`, polling, registrar FCM token al login, deep links
- Tests + documentación de variables VPS

### Usuario / operaciones (una vez + deploy)

| Paso | Tiempo | Notas |
|------|--------|-------|
| Crear proyecto Firebase + app Android | ~15–30 min | Package name de `frontend/android/app/build.gradle` |
| Descargar `google-services.json` | | → `frontend/android/app/` (idealmente `.gitignore`) |
| JSON cuenta de servicio → VPS | ~10 min | Variable `FIREBASE_CREDENTIALS` — **nunca en git** |
| Deploy backend + migraciones + nueva APK | | `git pull`, restart API, `flutter build apk` |
| Prueba en móvil Android real | ~15 min | Permiso notificaciones + flujo perito valida |

**iOS:** requiere Apple Developer (~99 €/año) — pospuesto; piloto con APK Android.

---

## Arquitectura push (FCM)

```mermaid
sequenceDiagram
  participant P as Perito panel/app
  participant API as FastAPI VPS
  participant DB as PostgreSQL
  participant FCM as Firebase Cloud Messaging
  participant M as Móvil agricultor

  P->>API: POST validar escaneo
  API->>DB: tech_status + user_notification
  API->>DB: device_token del agricultor
  API->>FCM: send(title, body, data)
  FCM->>M: Notificación sistema
  M->>M: Tap → deep link escaneo
```

**Piezas técnicas:**

1. **Firebase Console** — proyecto + app Android + `google-services.json`
2. **Flutter** — `firebase_core`, `firebase_messaging`, `flutter_local_notifications`
3. **Backend** — tabla `device_tokens`, `POST /api/v1/me/device-token`, `firebase-admin`
4. **VPS** — credenciales JSON como secreto de entorno

Hoy: `backend/app/services/notification_service.py` solo hace `print`. Perito ya crea filas en `tech_notifications` al compartir escaneo pero el push no sale.

---

## Eventos — PERITO

### Push + badge (alta prioridad)

| Evento | Mensaje ejemplo | Badge |
|--------|-----------------|-------|
| Nuevo escaneo compartido (`share_with_tech`) | «María compartió escaneo: tomate · trips» | Validar escaneos |
| Agricultor corrige plaga en escaneo en cola | «María cambió la plaga a tuta — revisar» | Validar escaneos |
| Incidencia nueva en cartera de pilotos (si hay asignación) | «Nueva incidencia: mildiu en finca X» | Incidencias |

### Solo badge (sin push)

| Evento | Badge |
|--------|-------|
| Escaneos pendientes en cola (`pending_scans > 0`) | Validar escaneos |
| Entradas SIEX pendientes validación (enterprise) | SIEX |
| Alertas comarcal nuevas (dashboard) | Dashboard / Mapa |

### No notificar (evitar spam)

- Cada foco anónimo nuevo en mapa
- Feedback «¿Te resultó útil?» del agricultor
- Clima rutinario sin umbral crítico

**Canal principal perito:** panel web (`Layout.tsx` ya tiene badge + Notification API). App móvil como complemento.

---

## Eventos — AGRICULTOR

### Push + badge (alta prioridad)

| Evento | Mensaje ejemplo | Badge |
|--------|-----------------|-------|
| Perito **confirma** escaneo | «Tu perito confirmó: trips» | Historial |
| Perito **corrige** plaga | «Tu perito indica: tuta (no trips)» | Historial |
| Perito **rechaza** escaneo | «Escaneo no válido — repite foto o consulta» | Historial |
| **Carencia cumplida** | «APTO PARA CORTE — plazo cumplido» | Inicio |
| Carencia crítica (&lt;24 h, opcional) | «Quedan 18 h de carencia» | Inicio |

### Push + badge (media — comarcal)

| Evento | Mensaje ejemplo | Badge |
|--------|-----------------|-------|
| Alerta nueva en municipio/zona del usuario | «Pico de trips en El Ejido» | Alertas |
| Foco relevante en comarca (incidencia validada) | «Actividad de mildiu en tu comarca» | Mapa |

Respetar `user_alert_preferences` (por plaga).

### Solo badge (sin push)

| Evento | Badge |
|--------|-------|
| Escaneo compartido sin respuesta del perito (X días) | Historial |
| Incidencia: cambio de etapa CRM | Incidencias |
| SIEX pendiente SIGPAC | Mis fincas / SIEX |
| Borrador SIEX tras tratamiento | SIEX |
| Nueva medalla gamificación | Comunidad |

### Banner in-app (ya parcial)

- Carencia activa → `CarenciaBanner` (no push cada hora)
- Confianza baja en último escaneo → recordatorio al abrir app

### No notificar

- «Diagnóstico guardado» tras cada escaneo propio
- Mapa comarcal genérico sin relación con fincas/plagas del usuario
- Onboarding repetitivo (&gt;1/día)

---

## Mapa badge ↔ UI (app agricultor)

| Botón / sección | Punto rojo cuando… |
|-----------------|-------------------|
| **Historial** | Validación perito no vista; escaneo pendiente de revisar |
| **Alertas** | Alerta activa nueva en zona del usuario |
| **Incidencias** | Incidencia abierta con cambio desde última visita |
| **Mapa** | (opcional) foco nuevo en municipio de sus fincas |
| **Mis fincas** | SIGPAC obligatorio pendiente para SIEX |
| **SIEX** | Entrada pendiente validación o `pendiente_sigpac` |
| **Tab Field (inicio)** | Agregado si cualquier sub-sección tiene pendiente |

## Mapa badge ↔ UI (perito app + panel)

| Destino | Punto rojo cuando… |
|---------|-------------------|
| **Validar escaneos** | `pending_scans > 0` o notificaciones unread |
| **Eventos mapa** | Outbreak events pendientes |
| **SIEX (panel)** | Cola enterprise pendiente |
| **Inicio / nav** | Agregado si hay cola en cualquier módulo |

---

## Matriz push vs badge

| Evento | Agricultor push | Agricultor badge | Perito push | Perito badge |
|--------|:---------------:|:----------------:|:-----------:|:------------:|
| Escaneo compartido con perito | — | opcional | ✅ | ✅ |
| Perito confirma / corrige / rechaza | ✅ | ✅ | — | — |
| Alerta comarcal (zona/plaga) | ✅* | ✅ | — | ✅ |
| Carencia cumplida | ✅ | ✅ | — | — |
| Carencia activa | banner | banner | — | — |
| Incidencia: cambio etapa | — | ✅ | — | ✅ |
| SIEX pendiente SIGPAC | — | ✅ | — | — |
| SIEX pendiente validación | — | — | — | ✅ |

\*Solo si preferencia de alerta activa para esa plaga.

---

## Fases de implementación (checklist)

### Fase 1 — MVP in-app (sin FCM) ✅ COMPLETADA (4 sep 2026)

**Backend**

- [x] Migración `0026`: `user_notifications` + `notification_reminder_log`
- [x] Servicio `user_notification_service` (crear, listar, unread, mark read, sections)
- [x] Hook en `tech_scan_service.validate_scan()` → notificar `scan.user_id`
- [x] `GET /api/v1/me/notifications` + `GET /api/v1/me/activity-summary` + `PATCH .../sections/{section}/read`
- [x] Tests: `tests/test_user_notifications.py`

**Flutter agricultor**

- [x] `NexoActionTile`: prop `showBadge`
- [x] `ActivityRepository` + polling en `FieldHomeScreen` (30 s)
- [x] Badge en Historial, Incidencias, Comunidad, Alertas; limpiar al abrir pantalla
- [x] SnackBar cuando sube `unread_count`
- [x] Deep link desde SnackBar → incidencia / historial

**Criterio de done Fase 1:** ✅ agricultor ve badge + SnackBar al validar perito con app abierta.

---

### Fase 2 — Gamificación ✅ COMPLETADA (4 sep 2026)

- [x] Reto semanal + racha en Inicio (`WeeklyVigilanceCard`)
- [x] Insignias semanales recurrentes (`weekly_vigilance_YYYY_Wnn`)
- [x] Toast reto en `ResultScreen` tras escaneo
- [x] Objetivo colectivo piloto en Comunidad (`pilot_collective`)
- [x] Notificación in-app al ganar insignia

---

### Fase 3 — Recordatorios incidencias ✅ COMPLETADA (4 sep 2026)

- [x] Scheduler `notification_reminders` (cada 1 h)
- [x] Avisos por etapa CRM: prescripción, tratamiento, carencia, evaluación foto
- [x] Banner incidencias pendientes en Inicio
- [x] Hook al registrar tratamiento en incidencia
- [x] Deduplicación 24 h (`notification_reminder_log`)

**Criterio de done Fase 3:** ✅ incidencia abierta genera recordatorio in-app deduplicado.

---

### Fase 4 — Push FCM Android ✅ COMPLETADA (6 sep 2026)

**Infra (usuario)**

- [x] Proyecto Firebase + `google-services.json`
- [x] JSON cuenta de servicio en VPS (`FIREBASE_CREDENTIALS`)

**Backend**

- [x] Migración `device_tokens` (`user_id`, `token`, `platform`, `updated_at`)
- [x] `POST /api/v1/me/device-token`
- [x] Sustituir `notification_service.send_push_to_user` por Firebase Admin SDK
- [x] Payload `data`: `type`, `scan_id` para deep link

**Flutter**

- [x] Dependencias Firebase + permiso Android 13+
- [x] Registrar token tras login / refresh token
- [x] Handler foreground (`flutter_local_notifications`)
- [x] Tap notificación → navegar a escaneo

**Criterio de done Fase 4:** ✅ push con app cerrada (pendiente smoke test en móvil piloto).

---

### Fase 5 — Pulido y prevención push ✅ COMPLETADA (6 sep 2026)

**Prevención**

- [x] Push alertas comarcal (filtrar por `user_alert_preferences` + zona finca)
- [x] Push carencia cumplida si app cerrada (refuerzo del banner existente)
- [x] Badge SIEX `pendiente_sigpac` + finca sin SIGPAC

**Pulido**

- [x] Pantalla preferencias en Ajustes (tipo de notificación on/off)
- [x] Agrupación anti-spam («N avisos pendientes» en ventana 10 min)
- [x] Horario quieto 22:00–07:00 (solo push críticos)
- [x] No re-notificar mismo evento sin cambio de estado (dedupe_key)
- [x] Refinar textos perito app (banner validaciones)

**Criterio de done Fase 5:** ✅ agricultor controla spam; alertas comarcal solo si opt-in.

---

## Reglas anti-spam

1. **Agrupar** eventos similares en ventana corta (10 min).
2. **No repetir** si el estado no cambió.
3. **Deep link** siempre al recurso concreto (`scan_id`, `incident_id`).
4. **Marcar leído** al entrar en la pantalla destino, no solo al abrir la app.
5. **Horario quieto** opcional para push no críticos.

---

## Canales por rol y estado de app

| Rol | App abierta | Segundo plano | App cerrada |
|-----|-------------|---------------|-------------|
| Agricultor | Badge + SnackBar | FCM + badge | FCM |
| Perito panel | Badge nav | Notification API | Notification API |
| Perito app | Badge + SnackBar | FCM + badge | FCM |

---

## Preguntas abiertas (cerrar antes de Fase 1b)

- [ ] ¿Perito usa más **panel web** o **app móvil** en piloto? (priorizar canal)
- [ ] ¿Asignación **agricultor ↔ perito** o todos los peritos ven todos los escaneos?
- [ ] ¿Push en **carencia cumplida** siempre o solo badge + `CarenciaBanner`?
- [ ] ¿Alertas comarcal a **todo el municipio** o solo usuarios con finca en esa zona?

---

## Referencias en código

| Pieza | Ubicación |
|-------|-----------|
| Stub push (→ Fase 4) | `backend/app/services/notification_service.py` |
| Notificaciones agricultor | `backend/app/services/user_notification_service.py` |
| Recordatorios incidencias | `backend/app/services/notification_reminder_service.py` |
| API agricultor | `backend/app/api/v1/routes/me_notifications.py` |
| Notificaciones perito | `backend/app/services/tech_notification_service.py` |
| Hook escaneo compartido | `backend/app/api/v1/routes/scans.py` |
| Validación perito | `backend/app/services/tech_scan_service.py` |
| Gamificación | `backend/app/services/gamification_service.py` |
| Badge panel web | `web-panel/src/components/Layout.tsx` |
| Polling + badges app | `frontend/lib/ui/screens/field_home_screen.dart` |
| Preferencias alerta plaga | `backend/app/models/alert_preference.py` |
| Motor alertas comarcal | `backend/app/services/alert_engine.py` |

---

## Registro

| Fecha | Hito |
|-------|------|
| 25 ago 2026 | Plan notificaciones + badges + FCM documentado (este archivo) |
| 25 ago 2026 | UI PlagaScan: top-3 plagas + banner confianza baja (pre-requisito UX) |
| 4 sep 2026 | **Fases 1–3 desplegadas:** `0026`, gamificación, recordatorios incidencias, APK piloto `.es` (`ec889f5`) |
| 5 sep 2026 | **Planificado:** Fase 4 FCM + Fase 5 pulido |

---

*Vinculado desde [ROADMAP_NEXO.md](ROADMAP_NEXO.md). Marcar `[x]` al completar tareas.*
