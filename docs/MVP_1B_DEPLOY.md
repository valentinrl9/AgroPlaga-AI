# Deploy MVP 1.B — NEXO Field Pro

**Producto comercial:** Field + Climate + SIEX borrador + Field Premium (tratamientos MAPA) + notificaciones perito.

**Dominio piloto:** `https://agroplaga-ai.farm`

---

## Checklist pre-deploy

- [ ] Backup PostgreSQL producción
- [ ] `deploy/pilot.env` actualizado (sin `DEMO_SEED_USERS`, previews en `false`)
- [ ] Panel compilado: `bash deploy/build-panel.sh`
- [ ] APK Nexo: `flutter build apk --release --dart-define=API_BASE_URL=https://TU_DOMINIO`

---

## 1. Backup BD (obligatorio)

```bash
ssh tu-vps
cd /ruta/proyecto
docker compose -f docker-compose.pilot.yml exec db \
  pg_dump -U plagaia plagaia_db > backup_pre_nexo_$(date +%Y%m%d).sql
```

---

## 2. Desplegar backend Nexo

En el VPS, con la rama `nexoagro`:

```bash
git pull origin nexoagro
bash deploy/build-panel.sh
bash deploy/setup-pilot.sh
```

El `docker-compose.pilot.yml` incluye volúmenes **climate** y **mapa**. Al arrancar, Alembic aplica migraciones hasta `0016_tech_notifications`.

Comprobar:

```bash
curl -sI https://agroplaga-ai.farm/docs | head -n 1
curl -sI https://agroplaga-ai.farm/panel/ | head -n 1
```

---

## 3. Post-deploy (admin)

1. **ETL MAPA** (catálogo biocidas):
   ```bash
   curl -X POST https://agroplaga-ai.farm/api/v1/treatments/etl/run \
     -H "Authorization: Bearer TOKEN_ADMIN"
   ```

2. **Licencias cooperativa** — activar flags en BD o vía seed master:
   - `has_field_premium = true`
   - `has_climate_module = true`
   - `has_siex_module = true` (agricultor)
   - `has_siex_enterprise = true` (cooperativa)

3. **Usuarios perito** — rol `tech` o `admin`

---

## 4. Notificaciones perito (nuevo)

Cuando un agricultor comparte escaneo (`POST /scans/with-image` con `share_with_tech=true`):

- Se crea registro en `tech_notifications` para cada perito/admin
- **Panel web:** badge en «Validar escaneos» + polling 30 s + notificación navegador (si el perito acepta permisos)
- **App móvil perito:** banner + SnackBar al detectar nuevos pendientes (polling 30 s)

API:

- `GET /api/v1/tech/notifications/unread-count`
- `GET /api/v1/tech/notifications`
- `PATCH /api/v1/tech/notifications/read-all`

Al validar un escaneo, las notificaciones asociadas se marcan leídas.

**FCM push nativo:** pendiente fase posterior (requiere Firebase). El polling cubre MVP 1.B.

---

## 5. Mensaje comercial honesto (UI)

- PlagaScan = **orientación IA**, no diagnóstico certificado
- Validación perito = valor principal del producto
- SIEX = borrador interno, no export ministerial oficial

---

## 6. Smoke test

```bash
python backend/scripts/smoke_test_nexo.py --base-url https://agroplaga-ai.farm
pytest backend/tests/test_tech_scans.py -q
```

---

## Rollback

```bash
docker compose -f docker-compose.pilot.yml down
# restaurar backup SQL si necesario
git checkout <commit-anterior>
bash deploy/setup-pilot.sh
```

---

*MVP 1.B — AgroPlaga / NEXO Field Pro · 2026*
