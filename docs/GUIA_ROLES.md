# NEXO Agro — Guía por roles (piloto V2)

**Versión:** NEXO Field Pro 2.0 · **URL producción:** `https://agroplaga.es`  
**Panel B2B:** `https://agroplaga.es/panel/`  
**Legacy:** `agroplaga-ai.farm` redirige a `.es` (la API en `.farm` sigue para APK antigua).

Esta guía explica **qué puede hacer cada rol** en el piloto: agricultor, técnico/perito y cooperativa.

---

## Resumen rápido

| Rol | Código piloto | App móvil (APK) | Panel web |
|-----|---------------|-----------------|-----------|
| **Agricultor** | `PLG-PILOT-F01` … `F07` | ✅ Uso principal | ❌ No accede |
| **Técnico / perito** | `PLG-PILOT-T01`, `T02` | ✅ Opcional (validación escaneos + mapa) | ✅ **Uso principal** |
| **Cooperativa** | `PLG-PILOT-C01` | ✅ Opcional | ✅ **Uso principal** |

> Registro con **código de invitación + email + contraseña**. Al registrarse, el agricultor **acepta el mapa comunitario anónimo** (obligatorio). La APK piloto apunta a `https://agroplaga.es`.

---

## Acceso común (todos los roles en la app)

1. **Registro:** pantalla *Regístrate* → código personal (1 uso) + nombre + email + contraseña.
2. **Login:** email y contraseña. La sesión se mantiene entre aperturas.
3. **Ajustes:** *Servidor API / Ajustes* — en el piloto no hace falta cambiar nada (URL fija en la APK).
4. **Cerrar sesión:** icono de salir en la barra superior del inicio.

**Conexión:** el escaneo con IA funciona **sin Wi‑Fi** (modelo en el móvil). Historial, mapa, login y guardar escaneos **sí necesitan internet**.

---

# Rol 1 — Agricultor

**Objetivo:** escanear plagas, gestionar fincas e incidencias fitosanitarias, colaborar con el mapa comunitario y (opcional) cuaderno SIEX.

**Herramienta:** app móvil (APK). No usa el panel web.

## Primer acceso (V2)

1. **Registro** con código piloto + aceptación del **mapa comunitario anónimo**.
2. **Onboarding obligatorio:** crear al menos una finca/invernadero (municipio Almería, cultivo, fase fenológica, nave/sector, superficie).
3. **SIGPAC recinto:** opcional al alta; **obligatorio solo** si usa el cuaderno SIEX (se indica en «Mis fincas»).

## Inicio

Pantalla principal Field con acceso a escaneo, historial, mapa, incidencias, fincas, clima (si licencia) y SIEX (si licencia/preview).

---

## Escanear (PlagaScan)

**Ruta:** *Nuevo escaneo*

| Paso | Qué hace |
|------|----------|
| 1. Foto | *Tomar foto* o *Elegir de galería*. Enfocar una hoja afectada, buena luz, ~20 cm. |
| 2. Cultivo | Selector: tomate, pimiento, calabacín, etc. |
| 3. Análisis | La IA local (TFLite) propone **plaga**, **confianza** y **severidad sugerida**. Funciona offline. |
| 4. Ajustes | Puedes cambiar severidad, vincular **finca** y **corregir la plaga** si no coincide con lo que ves en campo. |
| 5. Compartir con técnico | Checkbox **«Compartir foto con mi técnico/cooperativa»** (opt-in). Sin marcar, el perito no ve la foto. |
| 6. Guardar | *Guardar diagnóstico* → historial en servidor. |

**Importante:** la IA es **orientativa**. Si corriges la plaga, esa corrección se usa en tratamientos e incidencias; el perito la verá en su cola de validación.

---

## Resultado del escaneo

Tras guardar:

- **Diagnóstico** y selector para **corregir plaga** (si difiere de la IA).
- **Abrir incidencia** — inicia el CRM fitosanitario y publica foco anónimo en el mapa del municipio (sin volver a preguntar consentimiento).
- **Registrar tratamiento** / recomendaciones MAPA.
- **¿Te resultó útil?** — feedback.

Ya **no** hace falta pulsar «Contribuir al mapa» por separado: las **incidencias abiertas** alimentan el mapa comunitario.

---

## Historial

**Ruta:** *Historial*

Lista de todos tus escaneos guardados (fecha, plaga, cultivo, severidad). Puedes volver a abrir uno para ver recomendaciones o contribuir al mapa si aún no lo hiciste.

*Nota:* las fotos no se guardan en el historial de la app para consulta posterior; solo el texto del diagnóstico. Si compartiste foto con el técnico, él la ve en el panel.

---

## Mi analítica

**Ruta:** *Mi analítica*

Estadísticas **solo tuyas**:

- Resumen de escaneos (total, por plaga, por severidad).
- Evolución en el tiempo.
- Desglose por finca (si vinculaste escaneos a fincas).

Sirve para ver patrones en tus propias parcelas, no datos de otros agricultores.

---

## Mis fincas

**Ruta:** *Mis fincas*

- Listado de fincas registradas (tocar para editar cultivo, fase y **SIGPAC recinto**).
- Botón **«Añadir finca»** para nuevas unidades.
- **SIGPAC:** manual, consulta el visor SIGPAC del MAPA; necesario para cuaderno SIEX completo.

---

## Incidencias (CRM fitosanitario)

**Ruta:** *Incidencias*

Ciclo en 6 etapas: Detección → Diagnóstico → Prescripción MAPA → Tratamiento → Evaluación (foto comparativa) → Cierre.

- Al **abrir incidencia** desde un escaneo relevante, el foco entra en el mapa comunitario del municipio.
- Al **cerrar** (resuelto / cosecha perdida), el foco **sale del mapa**.
- Tratamientos generan carencia y, si aplica, entrada SIEX borrador.

---

## Mapa de focos

**Ruta:** *Mapa de focos*

- **Freemium:** vista **24 h** (tiempo real).
- **Premium (`has_field_premium`):** histórico **7 y 30 días**.
- Focos de **incidencias activas** agregados por municipio SIGPAC (sin parcela ni nombre).

---

## NEXO Climate / SIEX (si licencia o preview piloto)

- **Climate:** estación meteorológica según finca/municipio; alertas, riesgo, informe PDF.
- **SIEX:** cuaderno borrador automático al registrar tratamientos. Requiere **SIGPAC del recinto** en la finca; hasta entonces las entradas quedan «Pendiente SIGPAC».

---

## Lo que el agricultor NO hace

- No accede al panel web B2B.
- No valida escaneos de otros agricultores.
- No valida entradas SIEX de cooperativa (eso es rol perito en panel, modo enterprise).

---

# Rol 2 — Técnico / perito agrícola

**Objetivo:** revisar escaneos con foto de los agricultores, validar diagnósticos y supervisar el mapa comarcal.

**Herramientas:** **panel web** (principal) + app móvil (complementaria).

**Registro:** código `PLG-PILOT-T01` o `T02` → rol `tech`.

---

## Panel web — acceso

1. Abrir `https://agroplaga.es/panel/`
2. Mismo **email y contraseña** que en la app.
3. Solo entran roles `tech` y `admin`.

---

## Dashboard

**Ruta panel:** *Dashboard*

| Funcionalidad | Descripción |
|---------------|-------------|
| **KPIs** | Eventos recientes, % validados, alertas activas, zonas con actividad. |
| **Ventana temporal** | 24 h / 7 días / 30 días. |
| **Mapa de focos** | Heatmap por zona SIGPAC (vista agregada). |
| **Focos críticos** | Alertas prioritarias con plaga y zona. |
| **Comparativa por zona** | Tabla: reportes, validados, severidad máxima, intensidad. |
| **Evolución 30 días** | Gráfico de actividad diaria. |
| **Exportar CSV** | Descarga eventos del mapa para informes o Excel. |

Todo es **vista comarcal agregada** — no sustituye la cola de escaneos con foto.

---

## Validar escaneos (v1.6-core) ⭐

**Ruta panel:** *Validar escaneos*

Cola de escaneos que el agricultor marcó **«Compartir foto con mi técnico»**.

Por cada escaneo ves:

- **Foto** de la hoja.
- **Plaga efectiva** (prioridad: corrección perito → corrección agricultor → IA).
- Si el agricultor **corrigió la plaga**, verás **IA sugirió … · Agricultor indica …**
- Cultivo, severidad, agricultor, finca, fecha.

**Acciones:**

| Botón | Efecto |
|-------|--------|
| **Confirmar** | Validas la plaga efectiva mostrada (IA o corrección del agricultor). |
| **Corregir** | Eliges la plaga correcta en el desplegable + opcional notas. |
| **Descartar** | Escaneo no válido (foto mala, no es plaga, etc.). |

---

## Incidencias activas (CRM) — solo lectura

**Ruta panel:** *Incidencias*

Listado de incidencias fitosanitarias que gestionan los agricultores en la app:

- Etapa actual (detección … evaluación).
- Agricultor, finca, municipio, plaga, cultivo, severidad.
- Prescripción/tratamiento si ya existe.

**No editable desde panel** — supervisión y priorización de llamadas. Las incidencias cerradas pueden ocultarse con el filtro «Solo abiertas».

---

## Cuaderno SIEX

**Ruta panel:** *Cuaderno SIEX*

Cola de entradas en **`pendiente_validacion`** (modo cooperativa enterprise). Las entradas **`pendiente_sigpac`** las resuelve el agricultor añadiendo SIGPAC en «Mis fincas»; no aparecen aquí.

---

## Agricultores del piloto

**Ruta panel:** *Agricultores*

Semáforo por agricultor registrado:

| Estado | Significado |
|--------|-------------|
| Gris — *Sin escaneos compartidos* | Aún no ha compartido nada con el técnico. |
| Ámbar — *Pendientes de validar* | Tiene escaneos en cola sin revisar. |
| Verde — *Al día* | Compartió escaneos y no quedan pendientes. |

Sirve para priorizar a quién seguir o llamar.

---

## App móvil — funciones extra del técnico

El técnico **también** tiene todo lo del agricultor en la app (puede escanear en campo si quiere).

**Extra solo rol `tech`:**

### Validar eventos (mapa)

**Ruta app:** *Validar eventos (técnico)*

Lista de **contribuciones anónimas al mapa** pendientes de validar (plaga + zona SIGPAC + severidad, **sin foto ni agricultor**).

- Pulsar ✓ marca el evento como validado → más peso en el heatmap.
- Complemento al panel; **no sustituye** *Validar escaneos* con foto.

---

# Rol 3 — Cooperativa / responsable técnico SAT

**Objetivo:** visión agregada de la comarca, seguimiento de agricultores del piloto y validación profesional de escaneos.

**Herramientas:** **panel web** (principal). La app móvil es opcional.

**Registro:** código `PLG-PILOT-C01` → rol `tech` (mismas capacidades técnicas que T01/T02 en el sistema).

---

## Qué hace la cooperativa en el panel

Tiene **las mismas pantallas** que el técnico:

1. **Dashboard** — panorama comarcal, mapa, alertas, CSV.
2. **Validar escaneos** — cola con foto (plaga IA + corrección agricultor si aplica).
3. **Incidencias** — seguimiento CRM de solo lectura.
4. **Cuaderno SIEX** — validación enterprise (cuando aplique licencia).
5. **Agricultores** — semáforo del piloto.

**Enfoque recomendado para cooperativa:**

| Uso | Pantalla |
|-----|----------|
| «¿Qué pasa en la comarca?» | Dashboard + mapa + alertas |
| «¿Qué me mandan mis agricultores?» | Validar escaneos + Incidencias + Agricultores |
| Cuaderno de campo cooperativa | SIEX (enterprise) |
| Informe interno | Exportar CSV / export SIEX JSON |

---

## Privacidad (cooperativa vs agricultor)

| Dato | Mapa público | Panel B2B |
|------|--------------|-----------|
| Parcela exacta | ❌ No | ❌ No (solo finca nominal si el agricultor la creó) |
| Nombre agricultor | ❌ No | ✅ Solo si compartió escaneo con técnico |
| Foto de hoja | ❌ No | ✅ Solo con opt-in explícito |
| Zona SIGPAC | ✅ Sí (agregada) | ✅ Sí |

---

## App móvil (cooperativa)

Opcional: registrar con `PLG-PILOT-C01` e instalar la APK para escanear o validar eventos del mapa en campo. Para la demo B2B del piloto, **prioriza el panel web**.

---

# Cuenta admin (solo organizador del piloto)

No es un rol de campo, pero existe para ti:

- **Email demo:** `admin@example.com` / `admin1234` (o tu `MASTER_*` en `pilot.env`).
- **Panel web:** acceso completo igual que `tech`.
- **API admin:** `/api/v1/admin/invites`, `/api/v1/admin/users` — auditoría de códigos y registros.

---

# Flujos que conectan los tres roles

```
AGRICULTOR                          TÉCNICO / COOPERATIVA
    │                                        │
    ├─ Onboarding + fincas (SIGPAC manual)   │
    ├─ Escanea (offline IA)                  │
    ├─ Corrige plaga (opcional)              │
    ├─ Guarda diagnóstico                    │
    │                                        │
    ├─ [opt-in] Comparte foto ──────────────►│ Validar escaneos (panel/app)
    │         (ve plaga efectiva)            │  Confirmar / Corregir / Descartar
    │                                        │
    ├─ Abre incidencia CRM ─────────────────►│ Incidencias (panel, lectura)
    │    → mapa anónimo municipio            │  Dashboard + mapa
    │                                        │
    └─ Tratamiento → SIEX borrador ────────►│ SIEX (enterprise, validación)
         (SIGPAC en finca si cuaderno)      │
```

---

# Mensajes clave para explicar en campo

**Al agricultor:**  
*«La app te orienta con la cámara. Puedes corregir la plaga si no cuadra. Si quieres que tu técnico vea la foto, marca la casilla al guardar. Al abrir una incidencia, tu municipio entra en el mapa sin enseñar tu parcela.»*

**Al técnico:**  
*«El panel te muestra las fotos compartidas con la plaga que usa el agricultor (no solo la IA). Ahí confirmas o corriges. Incidencias te deja ver en qué etapa va cada caso.»*

**A la cooperativa:**  
*«El dashboard es la foto de la comarca; la cola de escaneos es el seguimiento fino; Incidencias y SIEX completan el cuaderno de campo.»*

---

# Soporte técnico piloto

- **API caída / login:** comprobar `https://agroplaga.es/docs`
- **Panel vacío en validación:** ningún agricultor ha marcado aún «Compartir foto con técnico»
- **IA imprecisa:** esperado en piloto; el valor B2B está en la validación del perito, no en la IA sola

**Documentos relacionados:** [PILOTO_CODIGOS.md](../deploy/PILOTO_CODIGOS.md) · [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md) · [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md)
