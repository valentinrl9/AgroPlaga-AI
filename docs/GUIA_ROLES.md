# AgroPlaga AI — Guía por roles (piloto)

**Versión:** v1.6-core · **URL producción:** `https://agroplaga-ai.farm`  
**Panel B2B:** `https://agroplaga-ai.farm/panel/`

Esta guía explica **qué puede hacer cada rol** en el piloto: agricultor, técnico/perito y cooperativa.

---

## Resumen rápido

| Rol | Código piloto | App móvil (APK) | Panel web |
|-----|---------------|-----------------|-----------|
| **Agricultor** | `PLG-PILOT-F01` … `F07` | ✅ Uso principal | ❌ No accede |
| **Técnico / perito** | `PLG-PILOT-T01`, `T02` | ✅ Opcional (escaneo + validación mapa) | ✅ **Uso principal** |
| **Cooperativa** | `PLG-PILOT-C01` | ✅ Opcional | ✅ **Uso principal** |

> Los tres roles se registran con **código de invitación + email + contraseña**. La APK ya apunta al servidor del piloto.

---

## Acceso común (todos los roles en la app)

1. **Registro:** pantalla *Regístrate* → código personal (1 uso) + nombre + email + contraseña.
2. **Login:** email y contraseña. La sesión se mantiene entre aperturas.
3. **Ajustes:** *Servidor API / Ajustes* — en el piloto no hace falta cambiar nada (URL fija en la APK).
4. **Cerrar sesión:** icono de salir en la barra superior del inicio.

**Conexión:** el escaneo con IA funciona **sin Wi‑Fi** (modelo en el móvil). Historial, mapa, login y guardar escaneos **sí necesitan internet**.

---

# Rol 1 — Agricultor

**Objetivo:** escanear plagas en el invernadero, guardar orientación y, si quiere, colaborar con el mapa comarcal.

**Herramienta:** app móvil (APK). No usa el panel web.

## Inicio

Pantalla principal con acceso a todas las funciones del agricultor. Mensaje de bienvenida con tu nombre.

---

## Escanear (PlagaScan)

**Ruta:** *Nuevo escaneo*

| Paso | Qué hace |
|------|----------|
| 1. Foto | *Tomar foto* o *Elegir de galería*. Enfocar una hoja afectada, buena luz, ~20 cm. |
| 2. Cultivo | Selector: tomate, pimiento, calabacín, etc. |
| 3. Análisis | La IA local (TFLite) propone **plaga**, **confianza** y **severidad sugerida**. Funciona offline. |
| 4. Ajustes | Puedes cambiar severidad (Leve / Moderado / Alto) y vincular una **finca** (opcional). |
| 5. Compartir con técnico | Checkbox **«Compartir foto con mi técnico/cooperativa»** (opt-in). Si lo marcas, la foto y el diagnóstico van a la cola del perito en el panel. **Sin marcar, el técnico no ve nada.** |
| 6. Guardar | *Guardar diagnóstico* → se guarda en tu historial en el servidor. |

**Importante:** la IA es **orientativa**, no un diagnóstico oficial. Si dudas, consulta a tu técnico.

---

## Resultado del escaneo

Tras guardar, ves:

- **Diagnóstico:** plaga, confianza, severidad.
- **¿Te resultó útil?** — *Sí, me orienta* / *No, no me fío* (no se pide corregir la plaga).
- **Recomendaciones personalizadas** según plaga, cultivo y severidad.
- **Contribuir al mapa** — botón para añadir el foco al mapa comunitario (ver abajo).

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

- Crear fincas con **nombre**, **cultivo** y tipo.
- Eliminar fincas.
- Al escanear, puedes **vincular** un escaneo a una finca para la analítica.

No expone la ubicación exacta de la parcela en el mapa público.

---

## Mapa de focos

**Ruta:** *Mapa de focos*

Mapa comarcal con **focos agregados por zona SIGPAC** (municipio/recinto, no parcela concreta):

- Calor según intensidad de reportes.
- Qué plagas se están viendo en la comarca.
- Eventos validados por técnicos tienen más peso en el mapa.

---

## Contribuir al mapa (desde un escaneo)

**Ruta:** *Resultado del escaneo* → *Contribuir al mapa*

| Qué haces | Qué pasa |
|-----------|----------|
| Eliges tu **municipio SIGPAC** | El foco se publica **anonimizado** en el mapa comunitario. |
| Confirmas plaga y severidad | No se sube tu nombre ni la foto al mapa público. |
| Contribuyes | Suma al heatmap y puede generar alertas para la zona. |

Puedes contribuir **sin** haber marcado «compartir con técnico»; son dos cosas distintas:

- **Mapa** = anonimizado, sin foto.
- **Compartir con técnico** = identificado, con foto, solo para el panel B2B.

---

## Alertas

**Ruta:** *Alertas*

Lista de **alertas tempranas** por zona: brotes recientes, picos de severidad, etc. Te ayudan a saber qué se mueve en la comarca (no alertas de tu parcela exacta).

---

## Comunidad

**Ruta:** *Comunidad*

- Tu **perfil colaborativo**: cuántas contribuciones llevas.
- **Insignias** por participación (gamificación ligera).
- Ranking comarcal agregado (sin identificar parcelas).

---

## Lo que el agricultor NO hace

- No accede al panel web B2B.
- No valida escaneos de otros.
- No corrige plagas en nombre del sistema (eso lo hace el técnico en el panel).

---

# Rol 2 — Técnico / perito agrícola

**Objetivo:** revisar escaneos con foto de los agricultores, validar diagnósticos y supervisar el mapa comarcal.

**Herramientas:** **panel web** (principal) + app móvil (complementaria).

**Registro:** código `PLG-PILOT-T01` o `T02` → rol `tech`.

---

## Panel web — acceso

1. Abrir `https://agroplaga-ai.farm/panel/`
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
- **Plaga IA**, confianza, cultivo, severidad.
- **Agricultor** (nombre y email) y finca si la vinculó.
- **Fecha** del escaneo.

**Acciones:**

| Botón | Efecto |
|-------|--------|
| **Confirmar** | El diagnóstico IA es correcto. |
| **Corregir** | Eliges la plaga correcta en el desplegable + opcional notas. |
| **Descartar** | El escaneo no es válido (foto mala, no es plaga, etc.). |

Puedes añadir **notas** en todos los casos.

Este es el flujo profesional principal del piloto B2B: **ver foto + criterio técnico + trazabilidad**.

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
2. **Validar escaneos** — cola con foto de agricultores que optaron por compartir.
3. **Agricultores** — semáforo del piloto.

**Enfoque recomendado para cooperativa:**

| Uso | Pantalla |
|-----|----------|
| «¿Qué pasa en la comarca?» | Dashboard + mapa + alertas |
| «¿Qué me mandan mis agricultores?» | Validar escaneos + Agricultores |
| Informe interno | Exportar CSV |

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
    ├─ Escanea (offline IA)                  │
    ├─ Guarda diagnóstico                    │
    │                                        │
    ├─ [opt-in] Comparte foto ──────────────►│ Validar escaneos (panel)
    │                                        │  Confirmar / Corregir / Descartar
    │                                        │
    └─ [opcional] Contribuye al mapa ───────►│ Dashboard + mapa (anonimizado)
         (sin foto, sin nombre)              │ Validar eventos mapa (app, opcional)
```

---

# Mensajes clave para explicar en campo

**Al agricultor:**  
*«La app te orienta con la cámara. Si quieres que tu técnico vea la foto, marca la casilla al guardar. El mapa de la comarca no enseña tu nombre ni tu parcela.»*

**Al técnico:**  
*«El panel te muestra las fotos que te comparten. Ahí confirmas o corriges. El mapa te da el panorama de zona, pero sin foto.»*

**A la cooperativa:**  
*«El dashboard es la foto de la comarca; la cola de escaneos es el seguimiento fino de quien confía en vosotros.»*

---

# Soporte técnico piloto

- **API caída / login:** comprobar `https://agroplaga-ai.farm/docs`
- **Panel vacío en validación:** ningún agricultor ha marcado aún «Compartir foto con técnico»
- **IA imprecisa:** esperado en piloto; el valor B2B está en la validación del perito, no en la IA sola

**Documentos relacionados:** [PILOTO_CODIGOS.md](../deploy/PILOTO_CODIGOS.md) · [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md) · [PILOTO_EXPERIMENTO.md](PILOTO_EXPERIMENTO.md)
