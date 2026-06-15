# AgroPlaga AI — Panel Web Cooperativas (Fase 7)

Panel B2B para técnicos y administradores. Comparte JWT con la API FastAPI.

## Requisitos

- Node.js 18+
- Backend en `http://localhost:8000` (Docker)

## Arranque

```powershell
cd web-panel
npm install
npm run dev
```

Abre http://localhost:5173

**Login demo:** `admin@example.com` / `admin1234`

## Funciones

- Dashboard: KPIs, mapa de focos, alertas críticas, comparativa por zona
- Evolución histórica (30 días)
- Validación de eventos colaborativos
- Exportación CSV de eventos

## Build producción

```powershell
npm run build
npm run preview
```
