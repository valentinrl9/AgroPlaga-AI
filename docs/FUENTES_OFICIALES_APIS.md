# Fuentes oficiales y APIs fitosanitarias

> Qué existe hoy en internet, qué usa NEXO, y cómo se muestra al agricultor.

---

## Resumen ejecutivo

| Fuente | API REST de protocolos | Qué usa NEXO hoy |
|--------|------------------------|------------------|
| **RAIF (Junta Andalucía)** | No hay API de protocolos en JSON | Catálogo local `shared/official_sources.json` + enlaces RAIF/BOJA |
| **Portal Datos Abiertos Andalucía** | CKAN `datastore_search` (datos TRIANA/parcelas, no protocolos) | No integrado |
| **MAPA Registro Fitosanitarios** | Export JSON CEX (ya en ETL biocidas) | Tratamientos + cita en recomendaciones |
| **MAPA alertas nacionales** | Sin API unificada pública | Enlace informativo |
| **EPPO Global Database** | API con clave (fotos/metadata) | Enlace por plaga |
| **Alertas NEXO** | Motor propio (`alert_engine`) | Etiquetadas como dato comunitario + RAIF de contexto |

---

## RAIF — qué hay y qué no

**RAIF** publica boletines, PDFs de protocolos (p. ej. control biológico invernadero, *Thrips parvispinus*) y situación fitosanitaria de Almería en web. **No existe un endpoint REST documentado** del tipo “dame protocolo por plaga”.

**Alternativa parcial:** [Portal de Datos Abiertos](https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif) — dataset TRIANA (muestreos ATRIA/API), consultable vía:

```text
GET https://www.juntadeandalucia.es/datosabiertos/portal/api/3/action/datastore_search?resource_id=...&limit=5
```

Útil para **tendencias regionales**, no para textos de protocolo.

**Enfoque NEXO:** mantener `shared/official_sources.json` curado (RAIF, BOJA, MAPA, EPPO) y servirlo en API.

---

## MAPA — qué ya tenéis

- **Registro productos:** `backend/app/mapa/client.py` → export CEX JSON semanal.
- **Recomendaciones de producto:** cruce plaga/cultivo con catálogo local.
- **Disclaimer:** visible en endpoints de tratamientos.

No hay API MAPA de “alertas fitosanitarias” en tiempo real; sanidad vegetal es principalmente web/PDF.

---

## API NEXO (implementado)

```http
GET /api/v1/plagues/official-sources?plague=trips&crop=pimiento&context=recommendation
GET /api/v1/analytics/recommendations?plague=trips&crop=Tomate&severity=Moderado
GET /api/v1/alerts
```

Respuesta incluye `official_sources[]`:

```json
{
  "id": "raif-horticolas-almeria",
  "kind": "official_bulletin",
  "kind_label": "Documento oficial",
  "issuer": "Junta de Andalucía · RAIF",
  "title": "Situación fitosanitaria hortícolas protegidos — Almería",
  "url": "https://...",
  "note": null
}
```

**Tipos (`kind`):**

| kind | Significado en UI |
|------|-------------------|
| `official_protocol` | Protocolo oficial (BOJA, IFAPA/RAIF) |
| `official_bulletin` | Boletín / web RAIF o MAPA |
| `official_registry` | Registro MAPA productos |
| `community` | Alerta derivada del mapa NEXO |
| `orientation` | Texto orientativo de la app (contrastar con RAIF) |

---

## UI Flutter

- `OfficialSourcesPanel` en **ResultScreen** (recomendaciones) y **AlertsScreen**.
- Badge por tipo + emisor + enlace (copiar al portapapeles).

---

## Mantenimiento del catálogo

Editar `shared/official_sources.json` cuando RAIF publique:

- Nuevo protocolo (p. ej. otra plaga obligatoria).
- Nuevo boletín Almería invernadero.
- Resolución BOJA.

Revisión recomendada: **mensual** o tras alerta RAIF relevante.

---

## Próximos pasos (opcional)

1. Scraper/admin panel para pegar URL RAIF → entrada JSON (sin API oficial).
2. Sincronizar titulares RAIF vía RSS si la Junta lo expone.
3. Mostrar fuentes MAPA en pantalla de tratamiento con n.º registro concreto.
4. Integrar CKAN TRIANA para capa “situación regional” en mapa (no sustituye protocolo).
