    # AgroPlaga AI — Piloto Lean (experimento de campo)

    **Autor:** Valentín Ruiz León  
    **Versión piloto:** APK → `https://agroplaga-ai.farm`  
    **Duración recomendada:** 4–6 semanas  
    **Cohorte objetivo:** 5–6 personas (mix agricultores + técnicos/cooperativa)

    ---

    ## 1. Objetivo del experimento

    Validar si AgroPlaga AI aporta **valor real** antes de seguir invirtiendo en IA (v1.5), producción comercial o predicción (v2).

    Al final del piloto debes poder responder:

    1. ¿Los agricultores **usan** la app en el invernadero sin que tú empujes cada semana?
    2. ¿Confían lo suficiente en el escaneo y las recomendaciones?
    3. ¿La **contribución al mapa** tiene sentido para ellos o para la cooperativa?
    4. ¿**Perseveramos** con el producto actual, **pivotamos** (canal, propuesta o IA) o **paramos**?

    ---

    ## 2. Hipótesis a validar

    | ID | Hipótesis | Se confirma si… | Se invalida si… |
    |----|-----------|-----------------|-----------------|
    | **H1 — Adopción** | El agricultor escanea plagas en campo con el móvil | ≥50% del cohort activo en semana 4; ≥2 escaneos/usuario/semana (media) | &lt;30% activo en semana 4; abandono tras 1 uso |
    | **H2 — Valor IA** | PlagaScan ayuda a decidir o detectar antes | ≥60% entrevistados dice “útil” o “bastante útil”; **confianza** autodeclarada ≥3/5 | Mayoría dice “no confío”; abandono tras ver resultados erróneos |
    | **H3 — Colaboración** | Parte de los diagnósticos alimentan el mapa comarcal | ≥30% escaneos → contribución SIGPAC | Casi nadie contribuye; “no veo para qué” |
    | **H4 — Valor B2B** | Técnico/cooperativa extrae valor de validación con foto | Técnico usa cola v1.6-core ≥1/semana; confirma/corrige diagnósticos reales | Panel ignorado; “no puedo verificar nada” |

    > **Gate H4 (15 jun 2026):** no medir H4 con el panel actual (validación anónima sin foto). Esperar a **v1.6-core** → [PROXIMO_HITO_V16_CORE.md](PROXIMO_HITO_V16_CORE.md).

    **Umbrales orientativos** — ajústalos al tamaño real del cohort (5–6 personas).

    ---

    ## 3. Roles y qué valida cada uno

    | Rol | Qué prueba | Entrevista |
    |-----|------------|------------|
    | **Agricultor** | PlagaScan, guardar, recomendaciones, contribuir (opcional) | [Guion A](PILOTO_ENTREVISTAS.md#rol-1--agricultor) |
    | **Técnico / perito** | Validación eventos, calidad fotos, mapa, alertas | [Guion B](PILOTO_ENTREVISTAS.md#rol-2--técnico--perito-agrícola) |
    | **Cooperativa** | Panel web, focos por zona, export CSV, visión agregada | [Guion C](PILOTO_ENTREVISTAS.md#rol-3--cooperativa--responsable-técnico-sat) |

    Un mismo contacto puede cubrir varios roles; adapta preguntas, no leas el guion entero.

    ---

    ## 4. Antes de empezar (checklist tú)

    - [ ] APK piloto instalada y probada (Wi‑Fi + datos) ✅
    - [ ] Servidor `https://agroplaga-ai.farm` estable 24/7
    - [ ] Lista de 5–6 participantes con nombre, rol, finca/zona, teléfono
    - [ ] Cuenta creada o acordado que se registran solos
    - [ ] **Onboarding 10 min** presencial o videollamada (ver §5)
    - [ ] Fecha inicio piloto anotada (Día 0)
    - [ ] Canal de soporte (WhatsApp contigo) comunicado
    - [ ] Este documento impreso o en móvil para entrevistas

    ---

    ## 5. Onboarding inicial (10 minutos — todos los roles)

    Decir en voz alta, en finca o por videollamada:

    1. **Qué es:** app para escanear plagas en el invernadero (funciona **sin Wi‑Fi** en el escaneo; mapa y login necesitan internet).
    2. **Qué pedimos:** usarla cuando veáis un problema fitosanitario real, no solo “probar una vez”.
    3. **Privacidad:** la parcela exacta no se publica; el mapa usa **zona SIGPAC** (municipio/recinto).
    4. **Contribución:** tras un escaneo podéis decir si queréis **añadir el foco al mapa** comarcal (anonimizado).
    5. **Si la IA falla:** no corrijáis la plaga — **avisad al técnico** o usad el resultado solo como orientación. Los **técnicos validan** lo dudoso. En la app solo os preguntaremos si **os resultó útil o si confiáis** en el resultado.
    6. **Soporte:** [tu WhatsApp] si no arranca, no entra o da error.
    7. **Duración:** 4–6 semanas; luego entrevista corta de cierre.

    **Demo en vivo (3 min):** foto → resultado → guardar → (opcional) contribuir con zona.

    ---

    ## 6. Guiones de entrevista

    **Documento completo (profesional, por rol):** [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md)

    Incluye apertura, preguntas semana 2 y cierre semana 5–6, señales verde/roja y plantilla de notas.  
    **No pidas al agricultor que corrija plagas** en entrevista; pregunta por **confianza y utilidad**.

    Resumen rápido:

    - **Agricultor:** uso real, confianza IA, mapa, retención (15–20 min).
    - **Técnico:** calidad IA, validación profesional, mapa/alertas, disposición de pago B2B (20 min).
    - **Cooperativa:** panel web, datos agregados, modelo freemium + licencia (20 min).

    ---

    ### Entrevista A — Agricultor (referencia; ver guion completo)

    Preguntas clave: ¿cuánto usaste? ¿confías en el resultado? ¿contribuiste al mapa? ¿seguirías usándola?

    ### Entrevista B — Técnico (referencia; ver guion completo)

    Preguntas clave: ¿acierta la IA en plagas del Poniente? ¿validarías/corregirías diagnósticos? ¿valor del mapa?

    ### Entrevista C — Cooperativa (referencia; ver guion completo)

    Preguntas clave: ¿panel útil? ¿licencia 200–500 €/año realista? ¿ampliar piloto?

    ---

    ## 7. Métricas cuantitativas (semanales)

    Anotar cada **lunes** (o al cierre). Fuente: panel admin, BD, o endpoints de stats si los usas.

    ### Tabla de seguimiento por participante

    | Participante | Rol | Zona | S1 escaneos | S2 | S3 | S4 | S5 | S6 | Contrib. | Último uso |
    |--------------|-----|------|-------------|----|----|----|----|-----|----------|------------|
    | | | | | | | | | | | |

    **Definiciones:**
    - **Escaneo:** scan guardado en backend (con o sin contribución).
    - **Contrib.:** n.º de eventos en mapa / n.º escaneos (ratio %).
    - **Activo semana N:** ≥1 escaneo o ≥1 apertura con acción (scan o contribución).

    ### Métricas globales del cohort

    | Métrica | Semana 1 | S2 | S3 | S4 | S5 | S6 |
    |---------|----------|----|----|----|----|-----|
    | Usuarios registrados | | | | | | |
    | Usuarios activos | | | | | | |
    | Total escaneos | | | | | | |
    | Escaneos / usuario activo | | | | | | |
    | % escaneos → contribución | | | | | | |
    | Confianza IA (útil / confía 1-5, entrevista) | | | | | | |
    | Retención S1→S4 (%) | — | | | | | |

    ---

    ## 8. Checklist de evaluación al cierre (semana 6)

    ### Datos cuantitativos

    - [ ] Calculada **retención** semana 1 → semana 4 (objetivo ≥50%)
    - [ ] Calculada **frecuencia** media escaneos/usuario/semana (objetivo ≥2 en semanas activas)
    - [ ] Calculado **% conversión** escaneo → contribución mapa (objetivo ≥30%)
    - [ ] Revisada **confianza/utilidad IA** en entrevistas (objetivo H2 ≥3/5 en mayoría)
    - [ ] Anotados usuarios **nunca activos** y **power users**

    ### Entrevistas cualitativas

    - [ ] Entrevista A completada con ≥3 agricultores
    - [ ] Entrevista B completada con ≥1 técnico/perito
    - [ ] Entrevista C completada con ≥1 contacto cooperativa (si aplica)
    - [ ] Citadas **frases literales** que resuman dolor y valor (para decisión)

    ### Por hipótesis

    | Hipótesis | Evidencia a favor | Evidencia en contra | Veredicto |
    |-----------|-------------------|---------------------|-----------|
    | H1 Adopción | | | ☐ Confirma ☐ Invalida ☐ Inconcluso |
    | H2 Valor IA | | | ☐ Confirma ☐ Invalida ☐ Inconcluso |
    | H3 Colaboración | | | ☐ Confirma ☐ Invalida ☐ Inconcluso |
    | H4 Valor B2B | | | ☐ Confirma ☐ Invalida ☐ Inconcluso |

    ---

    ## 9. Decisión final: perseverar, pivotar o parar

    Reúne los datos y responde por escrito (1 página):

    ### Perseverar ✅
    - H1 y al menos H2 o H3 confirmadas.
    - Entrevistas mayoritariamente positivas.
    - **Siguiente:** ampliar cohorte, v1.5 (fotos + reentrenamiento), mejoras UX concretas listadas.

    ### Pivotar 🔄
    Ejemplos según evidencia:
    - **Pivot canal:** solo técnicos escanean; agricultor solo mira alertas.
    - **Pivot propuesta:** quitar IA del centro; mapa colaborativo + validación técnica.
    - **Pivot segmento:** solo invernadero tomate/pepino; o solo una cooperativa.
    - **Siguiente:** prototipo mínimo del pivot (2 semanas), no reentrenar IA a ciegas.

    ### Parar ⏹️
    - Retención muy baja y entrevistas negativas en valor y usabilidad.
    - **Siguiente:** documentar aprendizajes; no invertir en producción comercial aún.

    ### Plantilla de decisión (rellenar)

    ```
    Fecha cierre piloto: ___________
    Participantes: ___ agricultores, ___ técnicos, ___ cooperativa
    Decisión: ☐ Perseverar  ☐ Pivotar  ☐ Parar

    Resumen en 3 líneas:
    1.
    2.
    3.

    Top 3 mejoras si perseveramos:
    1.
    2.
    3.

    ¿Ampliar piloto a más usuarios? Sí / No — ¿cuántos?
    ```

    ---

    ## 10. Consentimiento y ética (mínimo piloto)

    Informar verbalmente o por WhatsApp:

    - Proyecto en fase **piloto / investigación**; la app puede fallar o cambiar.
    - Datos de escaneos y contribuciones se usan para **mejorar el producto** y mapas agregados.
    - No se publica parcela ni nombre en el mapa comunitario.
    - Pueden **dejar de participar** cuando quieran; contacto para borrar cuenta: [tu email].

    No hace falta comité ético para piloto cerrado informal, pero **no compartas datos personales** de participantes fuera del proyecto.

    ---

    ## 11. Calendario sugerido

    | Cuándo | Acción |
    |--------|--------|
    | **Día 0** | Onboarding + registro + primer escaneo guiado |
    | **Semana 1** | Soporte activo; anotar incidencias |
    | **Semana 2** | Entrevistas A (agricultores) + B (técnico); métricas S1–S2 |
    | **Semana 3** | Entrevista C (cooperativa); métricas S3 |
    | **Semana 4** | Recordatorio suave por WhatsApp si inactivos |
    | **Semana 5** | Segunda ronda entrevistas A/B (retención) |
    | **Semana 6** | Checklist §8 + decisión §9 + reunión contigo mismo |

    ---

    ## 12. Referencias

    - Despliegue técnico: [PILOTO_DESPLIEGUE.md](PILOTO_DESPLIEGUE.md)
    - **Guiones entrevista:** [PILOTO_ENTREVISTAS.md](PILOTO_ENTREVISTAS.md)
    - Roadmap estratégico: [ROADMAP_LEAN.md](ROADMAP_LEAN.md)
    - Roadmap técnico v1: [ROADMAP.md](ROADMAP.md)

    ---

    *Documento listo para imprimir o convertir a PDF. Ajusta nombres, fechas y umbrales cuando cierres el cohort.*
