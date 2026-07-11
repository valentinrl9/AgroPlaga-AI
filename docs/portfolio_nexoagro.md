# PORTFOLIO-SPEC-2026: Ecosistema Modular NEXO Agro
==================================================================================
Versión: 1.0.0-PROD
Estado: Definitivo / Especificación Comercial y Funcional
Autor: Valentín Ruiz León (Julio 2026)
Ámbito: Documentación del Sistema (Docs / Producto)

---

## 1. Módulo Operativo: NEXO Field (AgroPlaga AI)
**Enfoque:** Aplicación móvil nativa orientada a la operación diaria a pie de campo bajo el plástico. Diseñada para usabilidad extrema, diagnóstico ágil y control sanitario.

### 1.1 Funcionalidades Core
*   **Scanner IA Offline (Visión Artificial Local):** Inferencia local en el dispositivo móvil mediante árboles de pesos ligeros optimizados (formato ONNX)[cite: 1]. Permite la detección e identificación de plagas de forma inmediata sin depender de cobertura de red o datos dentro del invernadero[cite: 1].
*   **Vademécum Oficial del MAPA Integrado:** Sincronización semanal automatizada vía ETL con la base de datos pública del Registro de Productos Fitosanitarios del Ministerio de Agricultura de España[cite: 1]. Filtra dinámicamente en base al binomio cultivo/plaga para evitar prescripciones ilegales o revocadas[cite: 1].
*   **Motor de Cálculo Automático de Dosis:** Algoritmo que cruza la superficie real en metros cuadrados de las estructuras del usuario con los rangos autorizados del MAPA[cite: 1]. Toma como base el estándar de caldo del Poniente Almeriense (1000L/ha por defecto) y calcula la dosificación de producto comercial exacta[cite: 1].
*   **Nexo Community (Mapa de Calor Anónimo):** Mapeo de brotes fitosanitarios cercanos en tiempo real[cite: 1]. Para proteger la propiedad e intimidad entre fincas colindantes, calcula el centroide del paraje mediante PostGIS o aplica una máscara aleatoria de dispersión en un radio de 500 metros, ocultando la coordenada exacta[cite: 1].
*   **Registro Inmediato en Borrador de Cuaderno:** Cada acción de escaneo o confirmación de tratamiento genera un asiento estructurado directo en la tabla de borradores, erradicando por completo el uso de anotaciones físicas en papel[cite: 1].

### 1.2 Funcionalidades Premium de Alto Valor Añadido
*   **Contador de Plazo de Carencia y Alerta de Corte:** Asistente visual (semáforo en UI) conectado a la base de datos de tratamientos activos[cite: 1]. Renderiza un cronómetro inverso basado en las horas del plazo de seguridad oficial del producto aplicado[cite: 1]. Bloquea digitalmente la recolección con la alerta "RECOLECCIÓN PROHIBIDA" (#EF4444) y cambia a verde (#10B981) al expirar, evitando rechazos por residuos en el almacén[cite: 1].
*   **Historial de Resistencias Cruzadas:** Motor de validación que analiza el histórico de aplicaciones fitosanitarias de los últimos 48 días. Si detecta el uso reiterado de una misma materia activa o modo de acción química, alerta al usuario y sugiere alternativas con códigos FRAC o IRAC diferentes para evitar mutaciones y resistencias de la plaga.

---

## 2. Módulo Avanzado: NEXO Climate (AgroData Consulting)
**Enfoque:** Software analítico de precisión combinado con servicios de consultoría estratégica. Transforma variables físicas y microclimáticas en decisiones agronómicas de alto rendimiento.

### 2.1 Funcionalidades Core
*   **Integración de Estaciones Meteorológicas:** Ingesta de datos analíticos procedentes de redes de estaciones físicas exteriores y previsiones meteorológicas ultra-locales[cite: 1].
*   **Soporte IoT para Sensores de Interior:** Conexión y lectura en tiempo real de nodos y sondas de suelo, temperatura, humedad relativa y CO2 instalados bajo la cubierta del invernadero[cite: 1].
*   **Dashboard Inteligente Unificado:** Cuadro de mando avanzado que centraliza la telemetría de sensores, alertas críticas del cultivo y previsiones climáticas en una única fuente de la verdad visual[cite: 1].
*   **Digitalización Absoluta de Documentos:** Repositorio en la nube indexado para el almacenamiento y consulta de facturas de insumos, recetas fitosanitarias, análisis de aguas/suelos y albaranes de entrega[cite: 1].
*   **Consultoría Profesional Personalizada:** Bloque de horas de asesoría técnica de ingeniería de datos orientada a la optimización de los recursos hídricos, estrategias nutricionales e históricos de la explotación[cite: 1].

### 2.2 Funcionalidades Premium de Alto Valor Añadido
*   **Motor Automático de Alertas DPV y Punto de Rocío:** Computación en tiempo real de indicadores basados en las variables de Temperatura y Humedad Relativa[cite: 1]:
    *   *Déficit de Presión de Vapor ($DPV$):* Si $DPV < 0.4\text{ kPa}$ (humedad estancada, riesgo fúngico) o $DPV > 1.6\text{ kPa}$ (estrés hídrico), inyecta una alerta visual y push con la ventana óptima de ventilación[cite: 1].
    *   *Temperatura del Punto de Rocío ($T_d$):* Predice con exactitud la condensación en la cubierta plástica para evitar el goteo directo sobre el cultivo[cite: 1].
*   **Simulador de Costes e Insumos por Campaña:** Herramienta analítica de costes de producción que cruza los metros cúbicos de agua consumidos, kg de fertilizantes inyectados y tratamientos aplicados con los kilogramos comerciales recolectados. Devuelve al agricultor su coste financiero real por kilo de producto producido (€/kg).

---

## 3. Módulo B2B: NEXO Enterprise (Panel Cooperativas y SATs)
**Enfoque:** Plataforma web de control de datos masivos orientada a los consejos rectores, peritos agrícolas y directores técnicos de cooperativas o Sociedades Agrarias de Transformación (SAT).

### 3.1 Funcionalidades Core
*   **Cuadro de Mando Multivista de Socios:** Panel supervisor avanzado que unifica y agrega la información operativa (plagas) y climática (sensores) de todos los agricultores adscritos[cite: 1].
*   **Bandeja de Validación de Cuadernos Digitales:** Interfaz pericial donde los técnicos de la cooperativa reciben los borradores de tratamientos de los socios en estado `PENDIENTE_VALIDACION`[cite: 1]. Permite auditar la imagen de la plaga, dosis calculada y visar el documento remotamente mediante firma digital oficial (`VALIDADO_OFICIAL`)[cite: 1].
*   **Módulo de Recomendaciones e IA Colectiva:** Alertas masivas y zonificadas basadas en la agregación de datos meteorológicos y focos detectados de manera anónima en el Paraje o comarca[cite: 1].
*   **Gestión Documental Centralizada:** Módulo de almacenamiento y vinculación automática de certificaciones globales (GlobalGAP, GRASP, Producción Integrada) directamente conectadas al expediente digital de cada socio[cite: 1].
*   **Consultoría e Informes Corporativos:** Reportes analíticos automatizados y auditorías de datos personalizados para los comités de calidad y gerencia de la comercializadora[cite: 1].

### 3.2 Funcionalidades Enterprise de Alto Valor Añadido
*   **Exportador Masivo SIEX en un Clic (JSON Schema Oficial):** Conversor estructurado que recopila los cientos de cuadernos de campo digitales validados por los técnicos y genera el archivo plano unificado bajo el esquema oficial requerido por la API de la administración española para su volcado ministerial automático[cite: 1].
*   **Módulo de Previsión de Entrada de Género (Predictive Supply Chain):** Algoritmo predictivo que cruza las tendencias térmicas acumuladas en los invernaderos de los socios (*AgroData*) con el estado fenológico de los ciclos de cultivo declarados en la app. Proporciona a la dirección comercial una estimación del volumen de kilos (oferta) que entrará en el almacén en las próximas dos semanas, maximizando su poder de negociación frente a las cadenas de distribución europeas.

---
*NEXO Agro — Especificación de Arquitectura de Portfolio de Producto. Documento Confidencial de Uso Interno.*