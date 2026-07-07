# Documentación AgroPlaga AI

Índice de la carpeta `docs/`. Empieza aquí según tu rol o tarea.

**Producción piloto:** `https://agroplaga-ai.farm` · Panel B2B: `https://agroplaga-ai.farm/panel/`

---

## Si vas a…

| Situación | Lee primero |
|-----------|-------------|
| **Hacer un vídeo pitch (~1 min)** | [GUION_VIDEO_1MIN.md](GUION_VIDEO_1MIN.md) |
| **Usar la app o explicarla en campo** | [GUIA_ROLES.md](GUIA_ROLES.md) |
| **Organizar el piloto (métricas, hipótesis)** | [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md) |
| **Entrevistar participantes** | [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md) |
| **Desplegar o mantener el VPS** | [PILOTO_DESPLIEGUE.md](PILOTO_DESPLIEGUE.md) + [../deploy/PILOTO_CODIGOS.md](../deploy/PILOTO_CODIGOS.md) |
| **Ver estado estratégico / piloto Lean** | [ROADMAP_LEAN.md](ROADMAP_LEAN.md) |
| **Ver fases técnicas completas** | [ROADMAP.md](ROADMAP.md) |
| **Consultar plagas del modelo** | [PLAGAS_PONIENTE.md](PLAGAS_PONIENTE.md) → `shared/plague_catalog.json` |

---

## Por rol

### Agricultor
- [GUIA_ROLES.md](GUIA_ROLES.md) — Rol 1: PlagaScan, mapa, fincas, analítica
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
- [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md) — experimento y decisión pivot/perseverar
- [PILOTO_DESPLIEGUE.md](PILOTO_DESPLIEGUE.md) — infraestructura
- [ROADMAP_LEAN.md](ROADMAP_LEAN.md) — estado v1.6-core y fases

---

## Documentos por tema

### Piloto en campo
| Documento | Contenido |
|-----------|-----------|
| [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md) | Hipótesis H1–H4, métricas, onboarding, cierre |
| [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md) | Guiones entrevista por rol |
| [PILOTO_DESPLIEGUE.md](PILOTO_DESPLIEGUE.md) | Docker, Caddy, VPS Hetzner, variables `pilot.env` |
| [GUIA_ROLES.md](GUIA_ROLES.md) | Funcionalidades por rol (app + panel) |

### Producto y roadmap
| Documento | Contenido |
|-----------|-----------|
| [ROADMAP_LEAN.md](ROADMAP_LEAN.md) | Estrategia Lean, estado piloto, v1.6-core ✅ |
| [ROADMAP.md](ROADMAP.md) | Roadmap técnico completo (fases, arquitectura, v2) |
| [PLAGAS_PONIENTE.md](PLAGAS_PONIENTE.md) | 15 clases PlagaScan del Poniente |

### Negocio
| Documento | Contenido |
|-----------|-----------|
| [Business_Model_Canvas_AgroPlaga_AI.pdf](Business_Model_Canvas_AgroPlaga_AI.pdf) | Canvas (PDF) |
| [generate_bmc_pdf.py](generate_bmc_pdf.py) | Regenerar el BMC |

### Fuera de `docs/` (relacionado)
| Ruta | Contenido |
|------|-----------|
| [../deploy/PILOTO_CODIGOS.md](../deploy/PILOTO_CODIGOS.md) | Códigos de invitación del piloto |
| [../README.md](../README.md) | Entrada al repositorio |
| [../web-panel/README.md](../web-panel/README.md) | Panel B2B React |

---

## Estado actual (jul 2026)

- **v1 MVP + piloto Lean:** desplegado en VPS con HTTPS.
- **v1.6-core:** validación perito con foto en panel — implementado y desplegado.
- **v1.5 IA:** pausada hasta fotos verificadas de perito/piloto.
- **Próximo:** piloto H4, v1.6 completo / CEX v1.7.
- **Pendiente (v1.8):** [Registro Oficial de Biocidas](ROADMAP.md#fase-12--integración-con-registro-oficial-de-biocidas-ministerio-de-sanidad--pendiente-v18) — ETL Ministerio + recomendaciones TP18.
- **Futuro (v1.7):** Cuaderno de Campo (CEX) — registro opt-in de tratamientos tras escaneo, plazos de seguridad, export para perito/cooperativa. Ver [ROADMAP.md](ROADMAP.md) → Fase 8.
