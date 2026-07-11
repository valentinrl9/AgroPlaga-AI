# SPEC-2026-PROD: NEXO Agro — Enterprise Core Architecture & Brand Identity
==================================================================================
Version: 2.0.0-RELEASE
Classification: Proprietary / Core Business Infrastructure
System Owner: Valentín Ruiz León (Mayo-Julio 2026)
Target Engines: Cursor AI, Cline Ecosystem, Core Engineering & Design Teams

---

## 1. Misión, Visión y Posicionamiento de Marca (Ecosistema Único)

### 1.1 Declaración de Misión
NEXO Agro es el Ecosistema de Inteligencia Agrícola Unificado diseñado para eliminar por completo la fricción operativa, técnica y burocrática en la agricultura intensiva. Conectamos algoritmos de Inteligencia Artificial offline, telemetría IoT microclimática y las regulaciones legales del Sistema de Información de Explotaciones (SIEX) en una infraestructura de software unificada, modular y de alta fiabilidad.

### 1.2 Posicionamiento de Marca e Impacto
* **Magnitud e Integración:** NEXO Agro no se presenta al mercado como una herramienta aislada; es el tejido conector de la explotación agraria. Engloba el todo, centralizando datos dispersos en una única fuente de la verdad.
* **Fiabilidad Institucional:** Transmite la solidez, robustez jurídica y seguridad de datos que exigen los consejos rectores de las grandes cooperativas agrarias ante las inspecciones y normativas europeas.
* **Simplicidad de Campo (Cero Fricción):** Diseñado bajo la premisa de usabilidad extrema a pie de campo. El agricultor ejecuta acciones de ingeniería de datos complejas mediante un solo clic bajo el plástico del invernadero.

### 1.3 Estrategia de Retención y Monetización Asimétrica (Freemium UX)
El sistema opera bajo una arquitectura de Plataforma como Servicio (SaaS). Las aplicaciones cliente se segmentan dinámicamente mediante un Control de Accesos Basado en Roles (RBAC) que inyecta componentes visuales basándose en tres banderas booleanas del modelo de usuario del backend: `has_field_premium`, `has_climate_module` y `has_siex_enterprise`.

* **Agricultor Free:** Habilitado Módulo Field Base (Scanner). Bloqueado Módulo Field Premium, Climate y SIEX por Paywall.
* **Agricultor Premium:** Habilitado Módulo Field Base, Field Premium, Climate y SIEX (Modo Lectura/Historial).
* **Socio Cooperativa:** Habilitado Módulo Field Base, Field Premium, Climate y SIEX (Modo Auto-compilación y envío). Licenciado vía cooperativa.
* **Técnico / Perito:** Habilitado Panel Supervisor Web, Módulo SIEX Completo (Firma, validación y exportación ministerial).

#### Reglas Estrictas para Interfaces Bloqueadas (LockScreen Protocol)
* **Pestañas Persistentes:** Ningún elemento de navegación o pestaña del menú inferior (móvil) o lateral (web) debe ocultarse si el usuario carece del módulo contratado. Esto maximiza la conversión orgánica y el deseo de uso.
* **Inyección del Componente NexoLockScreen:** Al pulsar sobre un módulo sin licencia activa, la interfaz interceptará la ruta y renderizará un contenedor de pantalla completa con fondo `#0B192C` (opacidad 95%), icono del candado en `#FFB200` y textos parametrizados:
  * *Módulos B2B (SIEX):* "Este módulo requiere vinculación oficial con tu Cooperativa o SAT adherida para la gestión unificada de alertas. Solicita el alta a tu perito técnico."
  * *Módulos B2C (Climate/Premium):* "Desbloquea métricas avanzadas e IA climática predictiva por 9.99€/mes. [Botón: Activar Periodo de Prueba de 7 días]".

---

## 2. Sistema de Identidad Visual Avanzado (Design System Tokens)

Este sistema de diseño debe mapearse de forma nativa en configuraciones de estilos del frontend (`tailwind.config.js` o esquemas de temas de React Native Paper).

### 2.1 Especificación Exactas de Color (Design Tokens)
* **Colores Primarios (Identidad y Dominancia):**
  * **NEXO Deep Blue (`#0B192C`):** Azul noche corporativo de máxima profundidad. Representa la base tecnológica, el almacenamiento masivo de datos (PostgreSQL) y la seguridad empresarial. Usado en fondos web, tipografías principales y cabeceras.
  * **NEXO Bio Green (`#00A86B`):** Verde esmeralda vivo y orgánico. Representa la sanidad vegetal, el cultivo sano y la acción biológica. Usado en botones de éxito, confirmaciones y elementos interactivos clave de la IA.
* **Colores Secundarios (Soporte Analítico e IoT):**
  * **NEXO Tech Cyan (`#00D2C4`):** Turquesa tecnológico. Representa la telemetría, los datos de sensores IoT y las alertas predictivas climáticas.
  * **NEXO Warning Amber (`#FFB200`):** Ámbar de alta visibilidad. Usado para mapas de calor de plagas, alertas de riesgo de esporas fúngicas y umbrales críticos de seguridad fitosanitaria.
* **Colores Neutros y de Interfaz:**
  * **NEXO Pure White (`#FFFFFF`):** Fondos de tarjetas, paneles y espacios limpios de lectura.
  * **NEXO Slate Gray (`#F4F6F9`):** Fondo base para interfaces móviles y paneles web secundarios.
  * **NEXO Dark Text (`#1E293B`):** Gris oscuro de alta legibilidad para textos extensos de datos.
  * **NEXO Light Text (`#94A3B8`):** Gris claro para etiquetas de metadatos e informaciones secundarias.

### 2.2 Arquitectura Tipográfica y Adaptación al Entorno
* **Interfaces Web (NEXO Climate & NEXO SIEX):** Fuente primaria *Plus Jakarta Sans*. Diseñada para visualización de cuadros de mando masivos y tablas densas del cuaderno digital.
  * `H1`: Bold / 32px / Tracking -0.02em
  * `H2`: SemiBold / 24px
  * `Body`: Regular / 14px o 16px / Leading 1.5
* **Interfaces Móviles de Campo (NEXO Field):** Fuente primaria *Roboto* o *SF Pro Display* para legibilidad crítica bajo estrés lumínico.
* **Filtro Automático de Alto Contraste:** Cuando el hardware del móvil detecte mediante el sensor de luz ambiental un flujo superior a 10.000 lux (sol directo bajo el plástico del invernadero), los textos en `#94A3B8` conmutarán a negro absoluto (`#000000`) y los botones primarios duplicarán su borde exterior a `3px solid #FFFFFF`.

### 2.3 Isologo y Logotipo (Construcción de Marca)
* **Imagotipo:** Tres líneas vectoriales fluidas en degradado lineal exacto desde `#00D2C4` (Tech Cyan) hasta `#00A86B` (Bio Green) que convergen en un nodo simétrico central (Nexo). Emula tanto la estructura estructural de un invernadero de raspa y amagado visto desde el cielo como los nodos de una red neuronal de IA.
* **Logotipo:** La palabra **NEXO** en tipografía geométrica ultra-gruesa (*Heavy*) en color `#0B192C`, seguida inmediatamente de la palabra **Agro** en tipografía fina (*Light*) en color `#00A86B`.

---

## 3. Especificación Técnica de Módulos y Funcionalidades

El backend de FastAPI centraliza la lógica de negocio y las llamadas de API mediante una estructura limpia, conectada a una base de datos PostgreSQL con extensión espacial PostGIS.

### 3.1 Módulo: NEXO Field (ID de Permiso: `module_field`)
* **Propósito:** Herramienta operativa diaria a pie de campo para detección, prescripción y control fitosanitario del agricultor.
* **Scanner IA Offline (Visión Artificial Local):** El backend expone el endpoint `/api/v1/field/sync-models` para servir el árbol de pesos ligero (formato ONNX optimizado). Cuando el dispositivo carece de cobertura, el cliente móvil ejecuta la inferencia de manera local, genera un UUID de captura y almacena el JSON en SQLite local con la plaga detectada (ej. `TUTA_ABSOLUTA`), tasa de confianza, timestamp UTC y coordenadas `(lat, lng)` nativas del GPS.
* **Vademécum Activo del Ministerio (Cruce de Datos MAPA):** Sincronización semanal mediante un script ETL interno de FastAPI que descarga e indexa la base de datos pública del Registro de Productos Fitosanitarios del Ministerio de Agricultura (MAPA) de España. La API filtra en base a la plaga detectada y el cultivo del recinto, impidiendo el uso de productos ilegales o revocados.
* **Motor de Cálculo Automático de Dosis:** Cruza los metros cuadrados reales de la estructura del usuario (obtenidos de la tabla `recintos_usuario`) con los rangos de dosis oficiales del MAPA. Tomando como base el estándar de caldo del Poniente Almeriense (1000 litros por hectárea por defecto), calcula la dosificación exacta de forma automática mediante la fórmula: 
  $$\text{Cantidad de Producto Comercial} = \left(\frac{\text{Superficie Invernadero en m}^2}{10000}\right) \times \text{Dosis Máxima por Hectárea}$$
* **Contador de Residuos Fitosanitarios (Control del Estrés Financiero):** Al confirmar una aplicación, el sistema inserta el registro en la tabla `tratamientos_activos`. La interfaz móvil renderiza un cronómetro inverso visual y bloquea la recolección con la alerta `#EF4444` (**"RECOLECCIÓN PROHIBIDA"**). Al expirar las horas del plazo de seguridad, la interfaz cambia a `#10B981` (**"PLAZO DE CARENCIA CUMPLIDO - APTO PARA CORTE"**), garantizando cero rechazos en el almacén de la cooperativa.
* **Nexo Community (Mapa de Calor de Plagas Anónimo):** Mapeo de brotes cercanos en tiempo real. Para evitar conflictos de privacidad entre fincas colindantes, el backend oculta la coordenada exacta utilizando funciones geométricas de PostGIS para calcular el centroide del paraje completo o aplicar una máscara aleatoria de dispersión en un radio de 500 metros, evitando servir puntos exactos.

### 3.2 Módulo: NEXO Climate (ID de Permiso: `module_climate`)
* **Propósito:** Ingesta masiva de telemetría IoT y procesamiento de indicadores macro y microclimáticos bajo el plástico.
* **Algoritmia Agroclimática del Panel de Indicadores Fundamentales:** El backend computa en tiempo real métricas críticas basándose en las variables de Temperatura Interna ($T$) y Humedad Relativa ($HR$):
  1. **Déficit de Presión de Vapor ($DPV$):** Mide la tasa de transpiración y estrés vegetal de la planta.
     * Presión de Vapor de Saturación ($e_s$) = $0.61078 \times e^{\left(\frac{17.27 \times T}{T + 237.3}\right)}$
     * Presión de Vapor Real ($e_a$) = $e_s \times \left(\frac{HR}{100}\right)$
     * $DPV = e_s - e_a$
     * *Lógica de Estado UI:* Si $DPV < 0.4\text{ kPa}$ (Estancamiento de humedad, esporas activas) se usa el color `#FFB200`. Si $DPV > 1.6\text{ kPa}$ (Estrés hídrico, estomas cerrados) se usa el color `#EF4444`. El rango óptimo es entre $0.8$ y $1.2\text{ kPa}$ marcándose en color `#10B981`.
  2. **Temperatura del Punto de Rocío ($T_d$):** Predicción milimétrica de condensación de agua en la cubierta plástica para evitar el goteo directo sobre la planta. Se calcula usando el logaritmo neperiano de la relación de humedad sobre el diferencial térmico estandarizado.
  3. **Contador de Horas Críticas de Humedad:** Un cronógrafo suma el valor `horas_humedad_critica` cuando un nodo reporta lecturas continuadas de Humedad Relativa superior al 85% durante 60 minutos, activando las alarmas visuales de desarrollo fúngico.
* **Predictor IA Fúngico:** Algoritmo predictivo que analiza el histórico climatológico acumulado en las últimas 48 horas y cruza las tendencias para alertar de riesgos de brotes de Mildiu, Ceniza (Oídio) o Botritis.
* **Ventana Horaria Óptima para Ventilar:** Motor de reglas que compara el microclima interno con los sensores exteriores de la estación para automatizar alertas push indicando el momento exacto para abrir o cerrar las bandas laterales del invernadero basándose en si la humedad exterior es menor que la interior y la temperatura supera los 28 grados.

### 3.3 Módulo: NEXO SIEX (ID de Permiso: `module_siex`)
* **Propósito:** Motor automatizado B2B de cumplimiento legal estricto de la normativa digital agraria española (obligatoriedad a partir del 1 de enero de 2027).
* **Cuaderno de Campo Digital Auto-compilado (Data Pipelines):** Arquitectura orientada a eventos. Al pulsar "Aplicar tratamiento" en NEXO Field o detectarse un riego/fertilización en NEXO Climate, el backend unifica los datos del MAPA, el nitrógeno aportado, el pH, la conductividad eléctrica y el código SIGPAC, inyectándolo directamente en la tabla `siex_cuaderno_borrador`, erradicando las libretas de papel.
* **Justificación Climática Automatizada:** El sistema asocia el ID de alerta fúngica generado por NEXO Climate al tratamiento, autocompilando la sección legal de "Justificación técnica del tratamiento fitosanitario" requerida en las inspecciones de la administración.
* **Bandeja de Validación Pericial B2B (Panel de Cooperativa):** Interfaz exclusiva web para los peritos y técnicos de la cooperativa. Reciben los reportes de campo de los socios en estado `PENDIENTE_VALIDACION`. El perito visualiza la imagen en alta definición de la plaga, el paraje y el cálculo de dosis. Cuenta con dos acciones atómicas:
  * **Botón  Rechazar (`#EF4444`):** Abre un modal técnico para modificar o corregir el diagnóstico de la plaga.
  * **Botón Aprobar y Firmar (`#00A86B`):** Firma el cuaderno del socio de forma remota utilizando el certificado digital de la cooperativa, mutando el estado a `VALIDADO_OFICIAL`.
* **Exportador SIEX Enterprise (JSON Schema de Envío Masivo):** Conversor estructurado que transforma la base de datos al esquema del lote de cuadernos exigido por la API del Ministerio de Agricultura de España para su volcado masivo en un solo clic.

---

## 4. Reglas del Sistema y Restricciones Técnicas Críticas (AI Guardrails)

* **Estrategia Offline-First de Sincronización:** El almacenamiento en SQLite local (móvil) sincronizará con la base de datos central en base al parámetro `last_pulled_at`. En caso de conflicto de datos directo (ej. modificación simultánea de un tratamiento en campo y en la web de la cooperativa), la base de datos centralizada de PostgreSQL tendrá siempre prioridad absoluta de sobreescritura.
* **Seguridad de Datos Sensibles:** Los NIF, números de carné de aplicador y teléfonos de los usuarios deben encriptarse en reposo en la base de datos utilizando la extensión `pgcrypto` mediante algoritmos AES-256. Queda estrictamente prohibido el uso de SQL plano concatenado en funciones espaciales de PostGIS para prevenir vectores de inyección.
* **Retrocompatibilidad Obligatoria de Endpoints:** Durante los procesos de unificación y refactorización, los endpoints antiguos del MVP piloto (ej. `/api/scan_plaga`) no deben borrarse; se mantendrán como envoltorios funcionales redirigiendo internamente a la nueva ruta REST estructurada `/api/v1/field/scan` para evitar corrupciones en las APKs instaladas en el campo.

---
*NEXO Agro Enterprise Core Architectural Specifications — Propiedad Exclusiva de Valentín Ruiz León. Mayo-Julio 2026.*