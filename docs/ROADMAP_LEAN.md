# AgroPlaga AI — Roadmap de Desarrollo (Edición Lean Startup)

**Autor:** Valentín Ruiz León  
**Actualizado:** 18 jun 2026  
**Estado:** 🚀 **Fase de Experimento de Campo** — MVP v1 adaptado para captura de métricas y validación con Early Adopters.

---

## Alcance por versión

| Versión | Objetivo | Incluye | Estado |
|---------|----------|---------|--------|
| **v1 (MVP-Lean)** | Validar valor central en campo | PlagaScan (offline), consentimiento SIGPAC, agregación anónima, trazabilidad por UUID de dispositivo. | **Listo para despliegue** |
| **v1.5 (Refinamiento)** | Escalar robustez y feedback | Panel B2B completo, analítica personal, reentrenamiento IA con fotos reales de campo. | *Pausado hasta aprendizaje* |
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

### Fase 2 — Despliegue de Infraestructura Ágil 🚀 (Inmediato)
- [ ] **Migración a VPS:** Configurar una instancia básica de Ubuntu con Docker y desplegar el entorno actual mediante `docker-compose up -d`.
- [ ] **Capa SSL obligatoria:** Configurar un túnel seguro HTTPS hacia el puerto expuesto de FastAPI.
- [ ] **Compilación Release:** Generar la APK apuntando de forma fija a la nueva dirección pública del servidor.

### Fase 3 — El Experimento de Campo (Semanas 2 a 6) 👥 (Inmediato)
- [ ] **Captación de Early Adopters:** Seleccionar de 5 a 6 agricultores y técnicos entre El Ejido y Dalías para la prueba directa de la APK.
- [ ] **Auditoría de Métricas Accionables:**
    - *Frecuencia:* ¿Cuántos escaneos realiza cada UUID de forma semanal?
    - *Conversión:* ¿Qué porcentaje de diagnósticos offline terminan en contribuciones reales al mapa comarcal?
    - *Retención:* ¿Los usuarios de la semana 1 siguen utilizando la herramienta en la semana 4?
- [ ] **Validación cualitativa:** Entrevistas de campo para analizar la calidad de las fotos y usabilidad bajo el plástico del invernadero.

### Fases en Pausa (Fases 6, 7, 8, 9 y 10 del plan original) ⏸️
- Modificaciones avanzadas de la IA y reentrenamiento masivo (Pausado post-MVP).
- Exportación pesada de PDFs y hardening de seguridad comercial (Cifrados AES-256, k-anonymity estricto).
- Modelos predictivos ARIMA e integración con Open-Meteo (Diferidos explícitamente a la v2).

---

## Orden de Construcción Lean

```
Generación de UUID anónimo e integraciones de métricas en API
    → Mudar Docker Compose a un VPS básico con túnel HTTPS
        → Compilar APK release e instalar directamente a los Early Adopters
            → Medir Retención, Conversión y Frecuencia de uso por dispositivo
                → Reunión de evaluación de métricas: ¿Pivotar o Perseverar?
```
