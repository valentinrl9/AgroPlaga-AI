# AgroPlaga AI — Roadmap de Desarrollo (Edición Lean Startup)

**Autor:** Valentín Ruiz León  
**Actualizado:** 15 jun 2026  
**Estado:** 🚀 **Piloto Lean en campo** — despliegue VPS OK; validaciones con participantes en curso

---

## Alcance por versión

| Versión | Objetivo | Incluye | Estado |
|---------|----------|---------|--------|
| **v1 (MVP-Lean)** | Validar valor central en campo | PlagaScan (offline), consentimiento SIGPAC, agregación anónima, trazabilidad por UUID de dispositivo. | **Listo para despliegue** |
| **v1.5 (Refinamiento)** | Escalar robustez y feedback | Panel B2B completo, analítica personal, reentrenamiento IA con fotos reales de campo. | *Pausado hasta aprendizaje* |
| **v1.6 (Perito móvil)** | Diferenciar rol técnico en app | Centro de mando, validación pro, mapa capas, informes, modo cooperativa | *Tras piloto* |
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

### Fase 4 — Post-piloto: experiencia perito / técnico ⏳ (Pendiente)
> **Gate:** cerrar entrevistas y métricas del piloto → decisión pivotar / perseverar.  
> **Detalle completo:** `docs/ROADMAP.md` → **Fase 11** (v1.6).

Orden de implantación acordado (misma app, flujos distintos por rol):

1. Home “Centro de mando” (KPIs desde `/tech/dashboard`)
2. Cola de validación fullscreen + corregir diagnóstico (solo rol técnico) + segunda opinión del modelo
3. Sello “Validado por técnico” + mapa con capas + modo “Visita a finca”
4. Alertas prioritarias + panel de impacto personal + modo cooperativa (semáforo multi-agricultor)
5. Bitácora de voz en campo + informe PDF de visita

**No iniciar Fase 4** hasta terminar Fase 3.

### Fases en Pausa (Fases 6, 7, 8, 9 y 10 del plan original) ⏸️
- Modificaciones avanzadas de la IA y reentrenamiento masivo (Pausado post-MVP).
- Exportación pesada de PDFs y hardening de seguridad comercial (Cifrados AES-256, k-anonymity estricto).
- Modelos predictivos ARIMA e integración con Open-Meteo (Diferidos explícitamente a la v2).

---

## Orden de Construcción Lean

**Ahora:**
```
Piloto desplegado (HTTPS + invitaciones)
    → Reparto APK + códigos a 10 participantes
        → Medir retención, conversión y frecuencia (semanas 2–6)
            → Entrevistas cualitativas (semana 0, 2, 4)
                → Reunión: ¿Pivotar o perseverar?
```

**Después del piloto (si perseveramos):**
```
Fase 11 / v1.6 — Experiencia perito móvil (ver ROADMAP.md)
    → v1.5 reentrenamiento IA con feedback de validaciones
        → v2 predicción + hardening comercial
```
