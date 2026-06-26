# AgroPlaga AI — Roadmap de Desarrollo (Edición Lean Startup)

**Autor:** Valentín Ruiz León  
**Actualizado:** 26 jun 2026  
**Estado:** ✅ **v1.6-core desplegado en VPS** — piloto en campo (APK con opt-in foto pendiente en móviles)

---

## Alcance por versión

| Versión | Objetivo | Incluye | Estado |
|---------|----------|---------|--------|
| **v1 (MVP-Lean)** | Validar valor central en campo | PlagaScan (offline), consentimiento SIGPAC, agregación anónima, trazabilidad por UUID de dispositivo. | **Listo para despliegue** |
| **v1.5 (Refinamiento)** | Escalar robustez y feedback | Panel B2B completo, analítica personal, reentrenamiento IA con fotos reales de campo. | *Pausado hasta aprendizaje* |
| **v1.6-core** | Validación perito vendible | Foto opt-in, cola panel, corregir plaga, semáforo agricultores piloto | **✅ Implementado** |
| **v1.6 (completo)** | Diferenciar rol técnico en app | Centro de mando móvil, mapa capas, informes PDF, modo cooperativa | *Tras v1.6-core* |
| **v1.7 (CEX)** | Cuaderno de campo digital | Tratamientos opt-in, plazos seguridad, export PDF/CSV perito/cooperativa | *Post-piloto* |
| **v2 (Escalabilidad)** | Previsión y hardening comercial | Modelos ARIMA/Prophet, k-anonymity masivo, Redis, FCM Push, subida a tiendas. | *Diferido* |

**Decisión estratégica (jun 2026):** Se congela el desarrollo de nuevas funciones (predicción, optimización de infraestructura) para evitar el desperdicio (*waste*). Todo el foco se desplaza a conseguir aprendizaje validado con un grupo piloto de 5-6 agricultores.

---

## Visión Lean del Producto

AgroPlaga AI combina **diagnóstico fitosanitario offline** con una **red colaborativa comunitaria** anonimizada por SIGPAC. En lugar de construir la plataforma perfecta a ciegas, la versión actual actúa como un experimento científico controlado para validar las dos hipótesis de fe principales: si el agricultor adopta la tecnología en el invernadero y si la cooperativa extrae valor real de los datos agregados.

---

## Modificaciones de Arquitectura para el Experimento

| Tema | Decisión Lean | Objetivo |
|------|----------------|----------|
| **Identidad de Usuario** | **UUID de dispositivo desacoplado** | Sustituye cualquier `user_id` real. Permite medir la retención y frecuencia de uso sin comprometer la privacidad. |
| **Infraestructura** | **VPS Mínimo Viable (Docker Compose)** | Evita configuraciones pesadas de producción (S3, Vault). Servidor básico 24/7 para el piloto. |
| **Seguridad de Red** | **Túnel HTTPS Automático (Caddy/Cloudflare)** | Requisito mínimo viable para que Android permita conexiones seguras externas de la APK. |
| **Distribución** | **Instalación Directa ("Conserje")** | Entrega de la APK por canales directos (Drive/WhatsApp) a los early adopters, omitiendo Google Play. |

---

## Fases de Implementación Actualizadas

### Fase 1 — Ajuste de Métricas y Anonimato 🔄 (En progreso)
- [x] Catálogo de 15 plagas del Poniente Almeriense.
- [ ] **Generación de UUID local:** Implementar lógica en Flutter para almacenar un identificador único aleatorio en el dispositivo.
- [ ] **Trazabilidad anónima en API:** Adaptar endpoints `/outbreak-events` para recibir y agrupar interacciones según el UUID del dispositivo.
- [x] `get_db` centralizado y lógica geoespacial con jitter base.

### Fase 2 — Despliegue de Infraestructura Ágil ✅ (Completada en piloto)
- [x] **Migración a VPS:** Ubuntu + Docker Compose en Hetzner (`167.233.129.193`).
- [x] **Capa SSL obligatoria:** Caddy + Let's Encrypt en `agroplaga-ai.farm`.
- [x] **Compilación Release:** APK con `--dart-define=API_BASE_URL=https://agroplaga-ai.farm`.
- [x] **Registro cerrado:** invitaciones piloto (`REGISTRATION_MODE=invite_only`).

### Fase 3 — El Experimento de Campo (Semanas 2 a 6) 👥 (En curso)
- [ ] **Captación de Early Adopters:** Seleccionar de 5 a 6 agricultores y técnicos entre El Ejido y Dalías para la prueba directa de la APK.
- [ ] **Auditoría de Métricas Accionables:**
    - *Frecuencia:* ¿Cuántos escaneos realiza cada UUID de forma semanal?
    - *Conversión:* ¿Qué porcentaje de diagnósticos offline terminan en contribuciones reales al mapa comarcal?
    - *Retención:* ¿Los usuarios de la semana 1 siguen utilizando la herramienta en la semana 4?
- [ ] **Validación cualitativa:** Entrevistas de campo para analizar la calidad de las fotos y usabilidad bajo el plástico del invernadero.

### Fase 3b — v1.6-core (validación perito) ✅ **COMPLETADA**

La validación anterior del perito (botón ✓ sobre eventos anónimos del mapa, sin foto) era testimonial. v1.6-core añade **escaneos con foto opt-in** y **cola de validación B2B** en el panel.

**Backend**
- [x] Migración `0008_scan_tech_validation`
- [x] `POST /api/v1/scans/with-image` (multipart)
- [x] `GET /api/v1/scans/{id}/image`
- [x] `GET /api/v1/tech/pending-scans`
- [x] `PATCH /api/v1/scans/{id}/validate` (confirm / correct / reject)
- [x] `GET /api/v1/tech/farmers` (semáforo piloto)
- [x] Almacenamiento local `SCAN_IMAGES_DIR` (volumen Docker en piloto)

**Panel web** (`/panel`)
- [x] Validación de escaneos con foto
- [x] Vista Agricultores del piloto

**App Flutter**
- [x] Checkbox opt-in al guardar
- [x] Subida multipart con foto

**Despliegue**
- [x] VPS + backend + panel (`docker compose … up -d --build`)
- [ ] APK release en móviles del piloto (`flutter build apk --release --dart-define=API_BASE_URL=https://agroplaga-ai.farm`)

```bash
# VPS (desde ~/AgroPlaga-AI)
git pull origin main
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env -p agroplaga up -d --build
```

```powershell
# APK local
cd frontend
flutter build apk --release --dart-define=API_BASE_URL=https://agroplaga-ai.farm
```

### Fase 4 — v1.6 completo (post v1.6-core) ⏳
> **Detalle:** `docs/ROADMAP.md` → **Fase 11**.

Centro de mando móvil, mapa capas, informes PDF, bitácora de voz, etc.

### Fases en Pausa (Fases 6, 7, 8, 9 y 10 del plan original) ⏸️
- Modificaciones avanzadas de la IA y reentrenamiento masivo (Pausado post-MVP).
- Exportación pesada de PDFs y hardening de seguridad comercial (Cifrados AES-256, k-anonymity estricto).
- Modelos predictivos ARIMA e integración con Open-Meteo (Diferidos explícitamente a la v2).

---

## Orden de Construcción Lean

**Ahora (orden acordado):**
```
v1.6-core desplegado en VPS
    → APK agricultor con opt-in foto en móviles piloto
        → Piloto H1–H3 (agricultores) + H4 (técnicos/cooperativa en panel)
            → Entrevistas + métricas → ¿Pivotar o perseverar?
```

**Después (si perseveramos):**
```
v1.6 completo (móvil perito, mapa capas, informes)
    → v1.5 reentrenamiento IA con fotos validadas por perito
        → v1.7 Cuaderno de Campo (CEX): tratamientos opt-in + export perito/cooperativa
            → v2 predicción + hardening comercial
```
