# AgroPlaga AI — Roadmap de Desarrollo

**Autor:** Valentín Ruiz León  
**Actualizado:** 18 jun 2026  
**Estado:** ✅ **v1 MVP completado** — Validado en dispositivo Android + backend Docker (LAN)  
**Estrategia Competitiva:** Diferenciación radical frente a Plantix mediante inferencia offline, privacidad por diseño (SIGPAC) y enfoque B2B para cooperativas[cite: 2].

---

## Alcance por versión

| Versión | Objetivo | Incluye | Enfoque frente a Plantix |
|---------|----------|---------|--------------------------|
| **v1 (MVP)** | Escanear y colaborar perfectos | PlagaScan, contribución al mapa, heatmap, alertas reactivas, gamificación, panel B2B, analítica personal[cite: 2]. | **Ventaja Offline y B2B:** Inferencia local sin cobertura en invernadero, protección de datos del agricultor y panel para técnicos[cite: 2]. |
| **v2** | Previsión e inteligencia comarcal | Predicción climática (Open-Meteo), modelos ARIMA/Prophet, capa de riesgo en mapa, KDE/Redis, FCM, integraciones RAIF[cite: 2]. | **Ventaja Predictiva:** Pasar de la diagnosis reactiva a la prevención meteorológica hiperlocal por distritos[cite: 2]. |

**Decisión (jun 2026):** la predicción queda **fuera del MVP**[cite: 2]. Primero consolidar el núcleo offline/colaborativo y la validación técnica en el Poniente Almeriense frente a soluciones globales centralizadas[cite: 2].

---

## Visión del producto y Diferenciación Estratégica

AgroPlaga AI no compite como un catálogo global retail, sino como un **ecosistema de sanidad vegetal hiperlocal y colaborativo**[cite: 2].

### 🥊 Pilares de disrupción frente a Plantix:
1. **Inferencia 100% Offline:** Plantix requiere enviar la imagen a la nube (inviable bajo el plástico de muchos invernaderos sin cobertura)[cite: 2]. AgroPlaga ejecuta **PlagaScan + TFLite** en hilos locales del dispositivo[cite: 2].
2. **Privacidad por Diseño:** Frente al rastreo comercial de datos, AgroPlaga destruye el `user_id` en los eventos públicos y utiliza agregación geográfica mediante códigos **SIGPAC** a nivel de municipio/recinto con *jitter* controlado (~150-400 m)[cite: 2]. El agricultor colabora sin delatar su parcela exacta[cite: 2].
3. **Ecosistema B2B (Cooperativas):** Plantix ignora la estructura agrícola local. AgroPlaga integra a los técnicos agrícolas de las comercializadoras mediante un panel web dedicado para auditar, validar y coordinar tratamientos en la comarca[cite: 2].

---

## Decisiones de arquitectura (v1)

| Tema | Decisión | Justificación Competitiva |
|------|----------|---------------------------|
| `outbreaks` | **Eliminada.** Sustituida por `outbreak_events` (eventos colaborativos anonimizados)[cite: 2]. | Evita filtraciones y simplifica el procesado geoespacial[cite: 2]. |
| Zonas geográficas | Tabla `agri_zones` con códigos SIGPAC municipio (`04-087` = El Ejido)[cite: 2]. Sin parcela exacta en datos públicos. | Garantiza la confianza del agricultor receloso de su competencia local[cite: 2]. |
| Privacidad | Los eventos colaborativos **no almacenan `user_id`**[cite: 2]. Reputación mediante contador interno desacoplado. | Cumplimiento estricto de anonimato y seguridad por diseño[cite: 2]. |
| Severidad | Escala numérica unificada: `1` Leve, `2` Moderado, `3` Alto[cite: 2]. | Estandarización para el motor de alertas y el panel técnico[cite: 2]. |
| Geometría | PostGIS: centroide municipal + *jitter* controlado (~150–400 m) para el mapa[cite: 2]. | Ofrece visualización de calor útil sin comprometer la ubicación real[cite: 2]. |
| Web cooperativas | Panel web separado (React) conectado a la misma API REST compartida[cite: 2]. | Herramienta de valor exclusivo para la gestión técnica de cooperativas locales[cite: 2]. |
| Heurística de Validación | Diagnósticos locales con <65% de confianza se marcan como "Pendientes de revisión técnica"[cite: 2]. | Los técnicos pueden validar o corregir el foco desde el panel web, alimentando el flujo de reentrenamiento[cite: 2]. |

---

## Fases de implementación

### Fase 0 — Diseño y especificación ✅ ~70 %
- [x] Guía técnica integral[cite: 2]
- [x] Anexo comunidad (mapa de calor, alertas, gamificación comarcal)[cite: 2]
- [x] Decisiones de arquitectura de datos y anonimización[cite: 2]
- [ ] Wireframes pantallas críticas (Flujo de consentimiento de datos)
- [x] Catálogo 15 plagas clave del Poniente Almeriense (`shared/plague_catalog.json`)[cite: 2]
- [ ] Importación catálogo SIGPAC de municipios del Poniente Almeriense

---

### Fase 1 — Backend core e infraestructura ✅ COMPLETADA (MVP v1)
- [x] FastAPI + PostgreSQL + Docker[cite: 2]
- [x] JWT auth con almacenamiento seguro[cite: 2]
- [x] Alembic migraciones automáticas al arranque[cite: 2]
- [x] PostGIS habilitado para agregación comarcal[cite: 2]
- [x] Modelos `agri_zones`, `outbreak_events`, `alerts`[cite: 2]
- [x] Endpoints `/zones`, `/outbreak-events`, `/alerts`[cite: 2]
- [x] Servicio geo (antiespionaje: *jitter* e inyección de ruido geográfico)[cite: 2]
- [x] Refresh tokens y Rate limiting activo para robustez productiva[cite: 2]
- [x] Rol `tech` completo en RBAC (validación de alertas dudosas y dashboard B2B)[cite: 2]
- [x] Tests PyTest (auth, events, zones, scans, plagas)[cite: 2]

---

### Fase 2 — Esqueleto Flutter + integración API ✅ COMPLETADA (MVP v1)
- [ ] BLoC/Provider para gestión avanzada de estados de red (v2)
- [x] Splash + auto-login con validación de token[cite: 2]
- [x] Conectar historial offline y login local[cite: 2]
- [x] Selector de zona SIGPAC amigable en flujo de contribución[cite: 2]
- [x] Flujo de consentimiento explícito: "¿Contribuir anónimamente al mapa de tu zona?"[cite: 2]
- [x] Widgets UI optimizados para campo: `severity_badge`, `card_scan`, `map_legend`[cite: 2]
- [x] Pantalla de alertas estructurada por urgencia[cite: 2]
- [x] Refresh token automático en `ApiClient` ante cortes de señal[cite: 2]

---

### Fase 3 — IA local (PlagaScan Offline vs. Nube) ✅ MVP v1 · ⏸️ refinamiento v1.5
- [x] Dataset PlantVillage enriquecido con capturas locales bajo plástico (`ml/extra_data/`)[cite: 2]
- [x] Entrenamiento MobileNetV3 optimizado para CPU móvil (`ml/train_plagascan.py`)[cite: 2]
- [x] Exportación `.tflite` cuantizado a 8-bit para ligereza total (`frontend/assets/ml/plaga_model.tflite`)[cite: 2]
- [x] Pantalla PlagaScan con visor de cámara nativo y guías de iluminación UX[cite: 2]
- [x] Flujo robusto: Captura → Inferencia Local IA → Recomendación Inmediata → Guardar Historial Offline[cite: 2]
- [x] API `GET /api/v1/plagues` con tratamientos biológicos y químicos autorizados para la zona[cite: 2]

---

### Fase 4 — PlagaHub: Mapa Comunitario Vivo ✅ COMPLETADA (MVP)
- [x] Conexión a `MapRepository` con parseo geográfico PostGIS[cite: 2]
- [x] Mapa dinámico con `flutter_map` renderizando centroides municipales SIGPAC[cite: 2]
- [x] Filtros avanzados: tipo de plaga, severidad y ventanas temporales (24 h / 7 d / 30 d)[cite: 2]
- [x] Endpoint `/api/v1/heatmap` con agregación por densidad de infección local[cite: 2]
- [x] Modos de vista: Mapa de Calor / Marcadores Anonimizados / Mixto[cite: 2]

---

### Fase 5 — Motor de alertas tempranas e Inteligencia de Zona ✅ COMPLETADA (MVP v1)
- [x] `alert_engine` matemático: Análisis de picos mediante Z-score y medias móviles[cite: 2]
- [x] Reglas de negocio críticas: Brote repentino (+35% de incidencia), plaga nueva en la zona, acumulación de riesgo[cite: 2]
- [x] Score de prioridad automatizado: `severidad × 0.6 + incremento × 0.4`[cite: 2]
- [x] Job síncrono programado (APScheduler) ejecutándose de fondo[cite: 2]
- [x] Pantalla de alertas e historial de notificaciones por zona de interés[cite: 2]
- [ ] Conexión final con Firebase Cloud Messaging (FCM) para alertas push instantáneas

---

### Fase 6 — Gamificación Cooperativa y Control de Calidad ✅ COMPLETADA (MVP)
- [x] Flujo de validación cruzada: El peso de un foco en el mapa se multiplica por 1.5 si es validado por un usuario con rol `tech`[cite: 2].
- [x] Sistema de incentivos: Insignias, rankings anónimos por zona y misiones ("Vigilancia semanal") para fomentar el uso continuo[cite: 2].
- [x] Endpoints de *Feedback loops* para reportar falsos positivos de la IA y guardar imágenes para reentrenamiento[cite: 2].
- [x] Anti-spam algorítmico activo (máximo 5 escaneos/hora por usuario y control de duplicados en la misma zona)[cite: 2].

---

### Fase 7 — Panel Web Cooperativas (B2B Corporativo) ✅ COMPLETADA (MVP)
- [x] Frontend Web desarrollado en React + TypeScript (`web-panel/`)[cite: 2]
- [x] Dashboard gerencial: Gráficos de evolución histórica de plagas por comarca, comparativas entre distritos y alertas críticas[cite: 2].
- [x] Herramientas de control: Módulo para validar o desestimar incidencias sospechosas reportadas por los usuarios[cite: 2].
- [x] Exportación ágil de informes de salud vegetal en formato CSV[cite: 2].

---

### Fase 8 — Analítica personal y valor agronómico ✅ COMPLETADA (MVP)
- [x] Gráficas cronológicas personalizadas para el agricultor vinculadas a sus fincas (`/api/v1/analytics/me`)[cite: 2].
- [x] Motor de recomendaciones dinámicas basadas en la combinación exacta de: Plaga + Cultivo + Nivel de Severidad[cite: 2].
- [x] Pantalla Flutter "Mi analítica" para contrastar el estado de la finca con la media del municipio[cite: 2].

---

### Fase 9 — Predicción microclimática (Ventaja Preventiva v2) ⏸️ DIFERIDA
- [ ] Integración con la API de Open-Meteo y cruce con sensores IoT de humedad/temperatura interna[cite: 2].
- [ ] Implementación de modelos predictivos ARIMA / Prophet para anticipar brotes con 4 días de margen[cite: 2].
- [ ] Superposición de capas de "Riesgo Futuro" en PlagaHub[cite: 2].
- [ ] Pipeline de conexión con avisos oficiales de la RAIF (Red de Alerta Fitosanitaria de Andalucía).

---

### Fase 10 — Hardening y Despliegue Comercial
- [ ] Protocolo HTTPS forzado y políticas CORS estrictas anti-scraping de mapas[cite: 2].
- [ ] Implementación de *k-anonymity* para asegurar que un foco nunca revele información si hay menos de $N$ invernaderos en una zona[cite: 2].
- [ ] Compilaciones optimizadas para producción y almacenamiento de imágenes de referencia en contenedores S3 blindados[cite: 2].

---

## Stack Tecnológico Consolidado

| Capa | Tecnología | Rol Estratégico Competitivo |
|------|------------|-----------------------------|
| **Móvil** | Flutter, TFLite, flutter_map, FCM[cite: 2] | Interfaz ágil, mapas eficientes e inferencia local offline sin internet[cite: 2]. |
| **Web Panel** | React + TypeScript, Leaflet[cite: 2] | Dashboard corporativo fluido para control de técnicos y cooperativas[cite: 2]. |
| **API** | FastAPI, Pydantic, SQLAlchemy, GeoAlchemy2[cite: 2] | Backend asíncrono de alto rendimiento con documentación OpenAPI nativa[cite: 2]. |
| **BD** | PostgreSQL 16 + PostGIS[cite: 2] | Motor relacional robusto con indexación geoespacial óptima para mapas de calor[cite: 2]. |
| **Cache & Jobs**| Redis, APScheduler[cite: 2] | Optimización de tiempos de carga en mapas y automatización del motor de alertas[cite: 2]. |
| **IA** | TensorFlow, TFLite cuantizado[cite: 2] | Entrenamiento robusto y exportación compacta directa a la memoria del móvil[cite: 2]. |