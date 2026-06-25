# Próximo hito — v1.6-core (validación perito con foto)

**Autor:** Valentín Ruiz León  
**Fecha decisión:** 15 jun 2026  
**Estado:** ✅ **IMPLEMENTADO** (pendiente deploy VPS + rebuild panel + APK)

---

## Por qué este hito

La validación anterior del perito (botón ✓ sobre eventos anónimos del mapa, sin foto) era testimonial. v1.6-core añade **escaneos con foto opt-in** y **cola de validación B2B**.

---

## Alcance v1.6-core — checklist

### Backend
- [x] Migración `0008_scan_tech_validation`
- [x] `POST /api/v1/scans/with-image` (multipart)
- [x] `GET /api/v1/scans/{id}/image`
- [x] `GET /api/v1/tech/pending-scans`
- [x] `PATCH /api/v1/scans/{id}/validate` (confirm / correct / reject)
- [x] `GET /api/v1/tech/farmers` (semáforo piloto)
- [x] Almacenamiento local `SCAN_IMAGES_DIR` (volumen Docker en piloto)

### Panel web (`/panel`)
- [x] Validación de escaneos con foto
- [x] Vista Agricultores del piloto

### App Flutter
- [x] Checkbox opt-in al guardar
- [x] Subida multipart con foto

### Despliegue (manual)
- [ ] `git pull` + rebuild en VPS
- [ ] `npm run build` en `web-panel/` y copiar `dist/`
- [ ] APK release con `--dart-define=API_BASE_URL=https://agroplaga-ai.farm`

---

## Deploy rápido (VPS)

```bash
cd ~/AgroPlaga-AI
git pull origin main
cd web-panel && npm ci && npm run build && cd ..
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env -p agroplaga up -d --build
```

APK local:

```powershell
cd frontend
flutter build apk --release --dart-define=API_BASE_URL=https://agroplaga-ai.farm
```

---

## Referencias

- [ROADMAP.md](ROADMAP.md) → Fase 11 (v1.6 completo, pendiente)
- [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md)
