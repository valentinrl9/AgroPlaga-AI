# Documentación NEXO Agro

Índice de la carpeta `docs/`. Empieza aquí según tu rol o tarea.

**Producción piloto (AgroPlaga, sin cambiar hasta validación Nexo):** `https://agroplaga-ai.farm` · Panel B2B: `https://agroplaga-ai.farm/panel/`  
**Desarrollo unificación:** rama `nexoagro` · ver [ROADMAP_NEXO.md](ROADMAP_NEXO.md)

---

## Si vas a…

| Situación | Lee primero |
|-----------|-------------|
| **Ver qué construir y en qué orden** | [ROADMAP_NEXO.md](ROADMAP_NEXO.md) |
| **Entender arquitectura y módulos** | [NEXO_CONTEXT.md](NEXO_CONTEXT.md) |
| **Catálogo comercial / portfolio** | [portfolio_nexoagro.md](portfolio_nexoagro.md) |
| **Hacer un vídeo pitch (~1 min)** | [GUION_VIDEO_1MIN.md](GUION_VIDEO_1MIN.md) |
| **Usar la app o explicarla en campo** | [GUIA_ROLES.md](GUIA_ROLES.md) |
| **Organizar el piloto (métricas, hipótesis)** | [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md) |
| **Entrevistar participantes** | [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md) |
| **Desplegar o mantener el VPS** | [PILOTO_DESPLIEGUE.md](PILOTO_DESPLIEGUE.md) + [../deploy/PILOTO_CODIGOS.md](../deploy/PILOTO_CODIGOS.md) |
| **Consultar plagas del modelo** | [PLAGAS_PONIENTE.md](PLAGAS_PONIENTE.md) → `shared/plague_catalog.json` |
| **Historial técnico AgroPlaga** | [ROADMAP.md](ROADMAP.md) *(archivado)* |
| **Historial piloto Lean** | [ROADMAP_LEAN.md](ROADMAP_LEAN.md) *(archivado)* |

---

## Por rol

### Agricultor
- [GUIA_ROLES.md](GUIA_ROLES.md) — NEXO Field: PlagaScan, mapa, fincas, analítica
- App Nexo: pestañas Field / Climate / SIEX (Climate y SIEX según licencia)
- Códigos de registro: [../deploy/PILOTO_CODIGOS.md](../deploy/PILOTO_CODIGOS.md) (`PLG-PILOT-F01` … `F07`)

### Técnico / perito
- [GUIA_ROLES.md](GUIA_ROLES.md) — Rol 2: panel *Validar escaneos*, semáforo agricultores
- [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md) — Guion B
- Códigos: `PLG-PILOT-T01`, `T02`

### Cooperativa
- [GUIA_ROLES.md](GUIA_ROLES.md) — Rol 3: dashboard, CSV, validación B2B
- [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md) — Guion C
- Código: `PLG-PILOT-C01`

### Organizador del piloto / admin
- [ROADMAP_NEXO.md](ROADMAP_NEXO.md) — estado unificación y fases
- [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md) — experimento y decisión pivot/perseverar
- [PILOTO_DESPLIEGUE.md](PILOTO_DESPLIEGUE.md) — infraestructura

---

## Documentos por tema

### NEXO Agro (activo)
| Documento | Contenido |
|-----------|-----------|
| [ROADMAP_NEXO.md](ROADMAP_NEXO.md) | Roadmap único de ejecución (Fases 0–4) |
| [NEXO_CONTEXT.md](NEXO_CONTEXT.md) | Arquitectura, RBAC, design tokens, módulos |
| [portfolio_nexoagro.md](portfolio_nexoagro.md) | Especificación comercial Field / Climate / Enterprise |

### Piloto en campo
| Documento | Contenido |
|-----------|-----------|
| [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md) | Hipótesis H1–H4, métricas, onboarding, cierre |
| [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md) | Guiones entrevista por rol |
| [PILOTO_DESPLIEGUE.md](PILOTO_DESPLIEGUE.md) | Docker, Caddy, VPS Hetzner, variables `pilot.env` |
| [GUIA_ROLES.md](GUIA_ROLES.md) | Funcionalidades por rol (app + panel) |

### Archivados (referencia histórica)
| Documento | Contenido |
|-----------|-----------|
| [ROADMAP.md](ROADMAP.md) | Roadmap técnico AgroPlaga pre-unificación |
| [ROADMAP_LEAN.md](ROADMAP_LEAN.md) | Estrategia Lean piloto AgroPlaga |
| [PLAGAS_PONIENTE.md](PLAGAS_PONIENTE.md) | 15 clases PlagaScan del Poniente |

### Negocio
| Documento | Contenido |
|-----------|-----------|
| [ESTUDIO_COMPETENCIA_NEXO.html](ESTUDIO_COMPETENCIA_NEXO.html) | Análisis competencia Nexo |
| [HOJA_RUTA_FINANCIERA_NEXO.html](HOJA_RUTA_FINANCIERA_NEXO.html) | Hoja de ruta financiera |
| [Business_Model_Canvas_AgroPlaga_AI.pdf](Business_Model_Canvas_AgroPlaga_AI.pdf) | Canvas (PDF) |

### Fuera de `docs/` (relacionado)
| Ruta | Contenido |
|------|-----------|
| [../deploy/PILOTO_CODIGOS.md](../deploy/PILOTO_CODIGOS.md) | Códigos de invitación del piloto |
| [../README.md](../README.md) | Entrada al repositorio |
| [../web-panel/README.md](../web-panel/README.md) | Panel B2B React |

---

## Estado actual (jul 2026)

- **Producción VPS:** AgroPlaga piloto (v1.6-core) — sin cambios hasta validación Nexo.
- **Rama `nexoagro`:** unificación Field + Climate + shell SIEX en local.
- **Fase 0:** ~90 % — backend Climate PostgreSQL, UI Climate B+, permisos RBAC.
- **Próximo:** validación local → gaps Climate → deploy con OK explícito.
- **SIEX (Fase 3):** bloqueado — prioridad tras validar Field + Climate.
