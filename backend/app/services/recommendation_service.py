"""Motor de recomendaciones agronómicas (plaga + cultivo + severidad)."""

SEVERITY_LEVELS = {"leve": 1, "moderado": 2, "moderada": 2, "alto": 3, "alta": 3}

_DEFAULT_RULES = {
    "low": "Monitoriza el cultivo y registra escaneos semanales con PlagaScan.",
    "medium": "Aplica tratamiento según etiqueta y consulta con tu técnico de cooperativa.",
    "high": "Intervención urgente: aisla zona afectada y contacta asesoramiento fitosanitario.",
}


def _severity_level(severity: str) -> int:
    key = severity.strip().lower()
    if key in SEVERITY_LEVELS:
        return SEVERITY_LEVELS[key]
    try:
        return max(1, min(3, int(key)))
    except ValueError:
        return 2


def get_recommendation(plague: str, crop: str, severity: str) -> dict:
    plague_key = plague.strip().lower()
    crop_key = crop.strip().lower()
    level = _severity_level(severity)
    urgency = "alta" if level >= 3 else "media" if level >= 2 else "baja"

    catalog: dict[str, dict[str, dict[str, str]]] = {
        "tuta absoluta": {
            "tomate": {
                "low": "Instala trampas de feromonas y revisa el envés de las hojas 2 veces por semana.",
                "medium": "Aplica Bacillus thuringiensis y elimina hojas con minas visibles.",
                "high": "Tratamiento urgente: rota modo de acción del insecticida y refuerza trampas en bordes.",
            },
            "default": {
                "low": "Monitoriza minas lineales en hojas jóvenes.",
                "medium": "Control biológico + retirada de restos vegetales infectados.",
                "high": "Intervención inmediata con asesoramiento fitosanitario local.",
            },
        },
        "trips": {
            "default": {
                "low": "Coloca cromotrópicos azules y controla malezas en calles.",
                "medium": "Tratamiento dirigido al envés foliar; revisa flores y brotes tiernos.",
                "high": "Umbral superado: tratamiento inmediato por síntomas de plata/bronceado.",
            },
        },
        "mosca blanca": {
            "default": {
                "low": "Trampas amarillas; controla brotes con melaza.",
                "medium": "Jabón potásico o aceite parafínico en brotes afectados.",
                "high": "Rota insecticidas y refuerza biocontrol (Encarsia). Revisa transmisión viral.",
            },
        },
        "pulgón": {
            "default": {
                "low": "Revisa brotes tiernos; favorece auxiliares (mariquitas).",
                "medium": "Tratamiento selectivo en colonias activas.",
                "high": "Tratamiento urgente; revisar transmisión de virus en cultivo.",
            },
        },
        "arañuela roja": {
            "default": {
                "low": "Aumenta humedad relativa puntual y revisa envés con lupa.",
                "medium": "Aplica acaricida específico; elimina hojas muy colonizadas.",
                "high": "Brote activo: tratamiento inmediato y reducir estrés hídrico del cultivo.",
            },
        },
        "minador": {
            "default": {
                "low": "Inspecciona galerías serpenteantes en hojas intermedias.",
                "medium": "Tratamiento en brotes nuevos; trampas cromáticas amarillas.",
                "high": "Población alta: insecticida sistémico según etiqueta y deshoje selectivo.",
            },
        },
        "piojo harinoso": {
            "default": {
                "low": "Revisa tallos y nervios con melaza; limpia con agua a presión suave.",
                "medium": "Aplica criptoléxina o aceite parafínico en colonias.",
                "high": "Infestación generalizada: tratamiento de choque y revisar hormigas vectoras.",
            },
        },
        "oruga": {
            "default": {
                "low": "Busca excrementos en hojas y frutos; trampeo manual al atardecer.",
                "medium": "Bacillus thuringiensis o virus de poliedrosis en larvas activas.",
                "high": "Tratamiento urgente en fruto/hoja; revisar mallas y entradas del invernadero.",
            },
        },
        "mildiu": {
            "tomate": {
                "low": "Mejora ventilación y evita riegos nocturnos.",
                "medium": "Fungicida preventivo; elimina hojas basal con manchas aceitosas.",
                "high": "Fungicida curativo de choque; humedad relativa por debajo del 75%.",
            },
            "default": {
                "low": "Evita condensaciones y mantén densidad de planta adecuada.",
                "medium": "Tratamiento preventivo-curativo; retirar restos afectados.",
                "high": "Alerta fitosanitaria: tratamiento urgente y consulta técnico.",
            },
        },
        "oídio": {
            "default": {
                "low": "Aumenta aireación y evita exceso de nitrógeno.",
                "medium": "Azufre o fungicida específico al primer polvo blanco visible.",
                "high": "Infestación avanzada: tratamiento inmediato y deshoje de hojas afectadas.",
            },
        },
        "botritis": {
            "default": {
                "low": "Elimina restos florales y frutos momificados; mejora ventilación.",
                "medium": "Fungicida contra Botrytis; reduce humedad en floración.",
                "high": "Brote activo: tratamiento de choque y retirada de tejido necrosado.",
            },
        },
        "mancha bacteriana": {
            "default": {
                "low": "Evita mojar follaje al regar; desinfecta herramientas de poda.",
                "medium": "Cobre o antibiótico agrícola según etiqueta; retira hojas con halo amarillo.",
                "high": "Elimina plantas foco y aplica tratamiento bactericida autorizado.",
            },
        },
        "fusarium": {
            "default": {
                "low": "Revisa raíces y conductividad del sustrato; evita estrés salino.",
                "medium": "Tratamiento biológico del sustrato; reduce riego en zonas afectadas.",
                "high": "Marchitez avanzada: arranque de plantas foco y desinfección de suelo/sustrato.",
            },
        },
        "clorosis viral": {
            "tomate": {
                "low": "Controla mosca blanca vectora; elimina plantas con rizado inicial.",
                "medium": "Arranque de plantas sintomáticas; refuerza mallas en ventanas.",
                "high": "Foco viral activo: eliminación masiva de focos y biocontrol de mosca blanca.",
            },
            "default": {
                "low": "Control del vector y uso de variedades tolerantes.",
                "medium": "Elimina plantas con clorosis y deformación foliar.",
                "high": "Consulta técnico: posible foco de virus; actuar sobre vector y focos.",
            },
        },
        "sana": {
            "default": {
                "low": "Mantén vigilancia semanal con PlagaScan aunque no haya síntomas.",
                "medium": "Continúa monitorización; revisa humedad y ventilación.",
                "high": "Sin plaga detectada; refuerza medidas preventivas del cultivo.",
            },
        },
    }

    level_key = "high" if level >= 3 else "medium" if level >= 2 else "low"
    plague_rules = catalog.get(plague_key, catalog["trips"])
    crop_rules = plague_rules.get(crop_key) or plague_rules.get("default", _DEFAULT_RULES)
    action = crop_rules.get(level_key) or crop_rules.get("medium", _DEFAULT_RULES["medium"])

    return {
        "plague": plague_key,
        "crop": crop_key,
        "severity": severity,
        "severity_level": level,
        "urgency": urgency,
        "recommendation": action,
        "prevention_tip": _prevention_tip(plague_key),
    }


def _prevention_tip(plague: str) -> str:
    tips = {
        "tuta absoluta": "Alterna cultivos y usa mallas antiinsectos en ventanas del invernadero.",
        "trips": "Elimina restos vegetales tras cada ciclo y controla malezas hospederas.",
        "mosca blanca": "Inspecciona plantas nuevas antes de introducirlas al invernadero.",
        "pulgón": "Favorece auxiliares reduciendo tratamientos de amplio espectro.",
        "arañuela roja": "Evita estrés hídrico y condiciones secas prolongadas en el invernadero.",
        "minador": "Retira hojas con galerías antiguas antes de que salgan nuevas adultos.",
        "piojo harinoso": "Controla hormigas que protegen la colonia; revisa esquejes entrantes.",
        "oruga": "Cierra entradas con mallas 0,8 mm y revisa frutos al atardecer.",
        "mildiu": "Riega al inicio del día y mantén conductividad equilibrada en fertirrigación.",
        "oídio": "Evita estrés hídrico y no mojar el follaje en aplicaciones foliares.",
        "botritis": "Elimina restos florales y mantén espacio entre plantas en floración.",
        "mancha bacteriana": "No trabajar plantas mojadas; rotar herramientas entre pasillos.",
        "fusarium": "Desinfecta raíces/sustrato entre campañas; evita encharcamientos.",
        "clorosis viral": "Variedades resistentes y control estricto de mosca blanca.",
        "sana": "Un escaneo semanal detecta brotes antes de que se propaguen.",
    }
    return tips.get(plague, "Registra cada escaneo para seguir la evolución de tu finca.")
