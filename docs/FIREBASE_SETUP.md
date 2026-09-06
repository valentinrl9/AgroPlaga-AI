# Firebase Cloud Messaging — AgroPlaga / NEXO Field Pro

Guía paso a paso para activar **push Android (Fase 4)** en piloto y producción.

## Resumen

| Pieza | Dónde va | ¿En git? |
|-------|----------|----------|
| `google-services.json` | `frontend/android/app/` | **No** |
| Cuenta de servicio JSON | VPS (`deploy/firebase-service-account.json` o ruta custom) | **No** |
| Código FCM | Repo (ya integrado) | Sí |

**Package name Android (obligatorio coincidir):** `com.example.agro_plaga_ai`

---

## 1. Crear proyecto Firebase

1. Entra en [Firebase Console](https://console.firebase.google.com/).
2. **Añadir proyecto** → nombre sugerido: `AgroPlaga` o `NEXO Field Pro`.
3. Desactiva Google Analytics si no lo necesitas (opcional en piloto).

---

## 2. Registrar app Android

1. En el proyecto → **Añadir app** → icono **Android**.
2. **Nombre del paquete Android:** `com.example.agro_plaga_ai`
3. Apodo opcional: `AgroPlaga Field`.
4. **Registrar app**.
5. Descarga **`google-services.json`**.
6. Colócalo en:

   ```
   frontend/android/app/google-services.json
   ```

7. **Siguiente** hasta terminar (no hace falta añadir el SDK manualmente; Flutter ya lo hace).

> Sin este archivo la app compila igual (Gradle lo detecta), pero **FCM no funcionará** hasta que lo copies.

---

## 3. Cuenta de servicio (backend / VPS)

El backend envía push con **Firebase Admin SDK**.

1. Firebase Console → **Configuración del proyecto** (engranaje) → pestaña **Cuentas de servicio**.
2. **Generar nueva clave privada** → descarga el JSON.
3. En el VPS, sube el archivo fuera del repo git, por ejemplo:

   ```bash
   scp firebase-adminsdk-xxxxx.json root@167.233.129.193:/opt/agroplaga/secrets/firebase-service-account.json
   ```

4. En `deploy/pilot.env` añade:

   ```env
   NOTIFICATIONS_ENABLED=true
   FCM_ENABLED=true
   FIREBASE_CREDENTIALS=/secrets/firebase-service-account.json
   ```

5. Monta el secreto en Docker (`docker-compose.pilot.yml` ya incluye el volumen):

   ```yaml
   volumes:
     - /opt/agroplaga/secrets/firebase-service-account.json:/secrets/firebase-service-account.json:ro
   ```

6. Redeploy:

   ```bash
   docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env -p agroplaga up -d --build
   alembic upgrade head   # dentro del contenedor backend → migración 0027_device_tokens
   ```

---

## 4. Build APK con FCM

Con `google-services.json` en su sitio:

```bash
cd frontend
flutter pub get
flutter build apk --release --dart-define=API_BASE_URL=https://agroplaga.es
```

Instala el APK en el móvil piloto. Tras **login**, la app registra el token en `POST /api/v1/me/device-token`.

---

## 5. Probar push

### A) Desde Firebase Console (smoke test)

1. **Messaging** → **Nueva campaña** → **Notificaciones**.
2. Título/cuerpo de prueba → **Enviar mensaje de prueba**.
3. Pega el **token FCM** del dispositivo (logcat o endpoint backend).

### B) Flujo real piloto

1. Agricultor escanea y comparte con perito.
2. Perito valida (confirm / correct / reject).
3. Debe llegar:
   - Notificación **in-app** (badge) — ya funciona.
   - **Push sistema** con app cerrada — Fase 4.

Eventos push prioritarios:

- Validación perito (`scan_confirmed`, `scan_corrected`, `scan_rejected`)
- Carencia cumplida (`incident_carencia_done`)
- Recordatorio incidencia (`incident_reminder`)

---

## 6. Variables de entorno

### Local / `.env`

```env
NOTIFICATIONS_ENABLED=true
PILOT_SCAN_GOAL=1000
FCM_ENABLED=false
# FIREBASE_CREDENTIALS=/ruta/local/firebase-service-account.json
```

Con `FCM_ENABLED=false` el backend sigue creando notificaciones in-app y solo hace log del push (stub).

### Piloto VPS

```env
NOTIFICATIONS_ENABLED=true
FCM_ENABLED=true
FIREBASE_CREDENTIALS=/secrets/firebase-service-account.json
PILOT_SCAN_GOAL=1000
```

---

## 7. Troubleshooting

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| App compila pero no hay push | Falta `google-services.json` | Descargar de Firebase Console |
| Backend log `[notification] push stub` | `FCM_ENABLED=false` o sin JSON | Activar env + montar credenciales |
| Push no llega tras login | Token no registrado | Re-login; revisar `device_tokens` en BD |
| `UnregisteredError` en logs | Token viejo | Normal; se borra automáticamente |
| Permiso denegado Android 13+ | Usuario rechazó notificaciones | Ajustes del sistema → AgroPlaga → Notificaciones |

---

## 8. Seguridad

- **Nunca** commitear `google-services.json` ni la cuenta de servicio.
- Rotar clave de servicio si se filtra.
- En producción comercial, cambiar `applicationId` de `com.example.*` a un ID definitivo (`es.agroplaga.field`) y re-registrar en Firebase.

---

## Referencias en código

- Backend push: `backend/app/services/notification_service.py`
- Tokens: `backend/app/services/device_token_service.py`, migración `0027_device_tokens`
- API: `POST /api/v1/me/device-token`
- Flutter: `frontend/lib/core/push_notification_service.dart`
