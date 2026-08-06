"""Genera PDF comercial NEXO Field Pro 1.B — funcionalidades, instrucciones y guía de venta."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path(__file__).resolve().parent / "NEXO_Field_Pro_1B_Comercial.pdf"

NAVY = colors.HexColor("#0B192C")
GREEN = colors.HexColor("#10B981")
GREEN_DARK = colors.HexColor("#059669")
MUTED = colors.HexColor("#64748B")
LIGHT_BG = colors.HexColor("#F1F5F9")
WHITE = colors.white


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=NAVY,
            spaceAfter=6,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=GREEN_DARK,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1E293B"),
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=12,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=14,
            textColor=NAVY,
            leftIndent=14,
            rightIndent=14,
            spaceBefore=8,
            spaceAfter=8,
            backColor=LIGHT_BG,
            borderPadding=8,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=MUTED,
        ),
    }


def bullet_list(items: list[str], styles) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, styles["bullet"]), leftIndent=6) for item in items],
        bulletType="bullet",
        start="•",
        leftIndent=12,
    )


def cover_block(styles) -> list:
    url = "https://agroplaga-ai.farm"
    return [
        Spacer(1, 28 * mm),
        Paragraph("NEXO Field Pro", styles["title"]),
        Paragraph("Versión 1.B — Paquete comercial listo para piloto", styles["subtitle"]),
        Spacer(1, 4 * mm),
        Table(
            [[Paragraph(f"<b>API y landing:</b> {url}", styles["body"])]],
            colWidths=[170 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
                    ("BOX", (0, 0), (-1, -1), 0.5, GREEN),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        ),
        Spacer(1, 6 * mm),
        Table(
            [[Paragraph(f"<b>Panel B2B peritos:</b> {url}/panel/", styles["body"])]],
            colWidths=[170 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
                    ("BOX", (0, 0), (-1, -1), 0.5, GREEN),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        ),
        Spacer(1, 10 * mm),
        Paragraph(
            "<b>Propuesta en una frase:</b> PlagaScan orientativo en el móvil + validación del perito "
            "con aviso automático + mapa comarcal + tratamientos MAPA + cuaderno SIEX borrador + módulo clima.",
            styles["body"],
        ),
        Spacer(1, 6 * mm),
        Paragraph(
            "<b>Autor:</b> Valentín Ruiz León · <b>Fecha:</b> agosto 2026 · Documento para venta piloto cooperativas/SAT",
            styles["small"],
        ),
        PageBreak(),
    ]


def section_product(styles) -> list:
    return [
        Paragraph("1. Qué incluye el paquete 1.B", styles["h1"]),
        Paragraph(
            "Producto unificado desplegado en producción. Tres capas: app móvil Flutter (agricultor y perito), "
            "API FastAPI en la nube y panel web React para técnicos y cooperativas.",
            styles["body"],
        ),
        Paragraph("Módulos incluidos", styles["h2"]),
        bullet_list(
            [
                "<b>NEXO Field (base):</b> PlagaScan offline, historial, fincas, mapa de focos SIGPAC, alertas, comunidad.",
                "<b>Validación perito:</b> cola con foto, confirmar/corregir/descartar, notificación al perito (polling 30 s).",
                "<b>Field Premium:</b> registro tratamientos, carencia, catálogo biocidas MAPA (ETL), cálculo de dosis.",
                "<b>NEXO Climate:</b> métricas Open-Meteo, DPV, punto de rocío, riesgo semanal, informe PDF.",
                "<b>SIEX borrador:</b> compilación automática desde tratamientos con SIGPAC; bandeja validación en panel.",
                "<b>Panel Enterprise:</b> dashboard KPIs, validación escaneos, cuaderno SIEX, export preview JSON.",
            ],
            styles,
        ),
        Spacer(1, 4 * mm),
        Paragraph("Límites honestos (decírselo al cliente)", styles["h2"]),
        bullet_list(
            [
                "La IA identifica ~15 plagas prioritarias con precisión <b>orientativa</b> (~10 % en validación interna). "
                "El valor comercial es la <b>validación del perito</b>, no el diagnóstico automático.",
                "SIEX es <b>borrador interno</b> — no export oficial al ministerio (fase posterior).",
                "Notificaciones perito: aviso en app y panel (polling); push nativo FCM pendiente.",
                "Climate usa Open-Meteo (paraje configurable); sensores IoT propios en roadmap.",
            ],
            styles,
        ),
        PageBreak(),
    ]


def section_features(styles) -> list:
    rows = [
        ["Rol", "Funcionalidad clave", "Dónde"],
        [
            "Agricultor",
            "PlagaScan: foto → orientación IA offline → guardar → compartir con perito",
            "App móvil",
        ],
        ["Agricultor", "Mapa comarcal anonimizado (SIGPAC), alertas, analítica propia", "App móvil"],
        ["Agricultor", "Registrar tratamiento, ver carencia, consultar biocidas MAPA", "App móvil *"],
        ["Perito", "Recibe aviso de nuevo escaneo pendiente", "App + panel"],
        ["Perito", "Validar escaneos con foto (confirmar / corregir / descartar)", "Panel /panel/"],
        ["Perito", "Dashboard KPIs, mapa calor, export CSV eventos", "Panel"],
        ["Perito", "Validar entradas SIEX de socios", "Panel /siex"],
        ["Cooperativa", "Vista agregada comarcal + gestión peritos (licencias RBAC)", "Panel + admin"],
    ]
    t = Table(rows, colWidths=[28 * mm, 95 * mm, 42 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [
        Paragraph("2. Funcionalidades por rol", styles["h1"]),
        t,
        Spacer(1, 4 * mm),
        Paragraph("* Field Premium, Climate y SIEX requieren flags de licencia activados por cooperativa.", styles["small"]),
        Spacer(1, 6 * mm),
        Paragraph("Plagas cubiertas por la IA (orientación)", styles["h2"]),
        Paragraph(
            "sana, tuta absoluta, trips, mosca blanca, pulgón, arañuela roja, minador, piojo harinoso, oruga, "
            "mildiu, oídio, botritis, mancha bacteriana, fusarium, clorosis viral.",
            styles["body"],
        ),
        Paragraph("Flujo estrella (demostración en 3 minutos)", styles["h2"]),
        bullet_list(
            [
                "Agricultor escanea hoja → marca «Compartir con mi perito» → guarda.",
                "Perito recibe aviso en panel (badge + notificación navegador) → abre Validar escaneos.",
                "Perito confirma o corrige → agricultor ve estado «validado por perito» en la app.",
                "Opcional: registrar tratamiento MAPA → carencia activa → borrador SIEX generado.",
            ],
            styles,
        ),
        PageBreak(),
    ]


def section_instructions(styles) -> list:
    return [
        Paragraph("3. Instrucciones de uso (piloto)", styles["h1"]),
        Paragraph("Acceso y registro", styles["h2"]),
        bullet_list(
            [
                "Instalar APK release (API: https://agroplaga-ai.farm).",
                "Registro con <b>código de invitación</b> (1 uso) + email + contraseña. Modo piloto: invite_only.",
                "Perito/cooperativa: mismo usuario en app y en https://agroplaga-ai.farm/panel/",
            ],
            styles,
        ),
        Paragraph("Agricultor — pasos", styles["h2"]),
        bullet_list(
            [
                "Inicio → <b>Nuevo escaneo</b> → foto → elegir cultivo → revisar sugerencia IA.",
                "Marcar <b>Compartir foto con mi técnico/cooperativa</b> si quiere validación.",
                "Historial, fincas, mapa de focos, alertas y analítica desde el menú Field.",
                "Tratamientos (Premium): elegir producto MAPA, dosis calculada, semáforo carencia.",
            ],
            styles,
        ),
        Paragraph("Perito — pasos", styles["h2"]),
        bullet_list(
            [
                "Entrar en panel → pestaña <b>Validar escaneos</b> (badge con pendientes).",
                "Por escaneo: ver foto, plaga IA, agricultor → Confirmar / Corregir / Descartar.",
                "Dashboard: KPIs comarcales, mapa, export CSV.",
                "SIEX: revisar entradas pendientes de socios con SIGPAC en finca.",
            ],
            styles,
        ),
        Paragraph("Administrador cooperativa (post-venta)", styles["h2"]),
        bullet_list(
            [
                "Activar licencias en BD: has_field_premium, has_climate_module, has_siex_module, has_siex_enterprise.",
                "Crear códigos invite (admin) para agricultores y peritos.",
                "Ejecutar ETL MAPA tras deploy: POST /api/v1/treatments/etl/run (token admin).",
                "Documentación técnica: docs/MVP_1B_DEPLOY.md y docs/GUIA_ROLES.md.",
            ],
            styles,
        ),
        PageBreak(),
    ]


def section_sales(styles) -> list:
    return [
        Paragraph("4. Cómo venderlo — guía comercial", styles["h1"]),
        Paragraph("A quién vender primero", styles["h2"]),
        bullet_list(
            [
                "<b>Cooperativas y SAT</b> del Poniente (control fitosanitario territorial, menos visitas a ciegas).",
                "<b>Peritos independientes</b> con cartera de fincas (validación remota + informe de actividad).",
                "<b>Agricultores socios</b> como usuarios finales — entrada por la coop, no venta directa masiva al inicio.",
            ],
            styles,
        ),
        Paragraph("Elevator pitch (30 segundos)", styles["h2"]),
        Paragraph(
            "«NEXO Field Pro pone en el bolsillo del agricultor un escáner de orientación fitosanitaria que funciona "
            "sin cobertura dentro del invernadero. Cuando comparte una sospecha, su perito recibe un aviso al instante "
            "y la valida con foto desde el móvil o el panel. La cooperativa ve el mapa comarcal, los tratamientos con "
            "carencia MAPA y un borrador de cuaderno de campo — todo en una sola plataforma, desplegada ya en piloto.»",
            styles["quote"],
        ),
        Paragraph("Argumentos por dolor del cliente", styles["h2"]),
        bullet_list(
            [
                "<b>«No llego a todas las fincas»</b> → Cola de validación remota; el agricultor manda foto antes de tu visita.",
                "<b>«La IA no me fío»</b> → Correcto: vendemos validación perito + trazabilidad, no diagnóstico automático.",
                "<b>«SIEX 2027 me agobia»</b> → Borrador automático desde tratamientos registrados; el perito valida antes de cerrar.",
                "<b>«¿Y si aplico mal un producto?»</b> → Catálogo MAPA + dosis + alerta carencia en pantalla.",
                "<b>«Quiero saber qué pasa en la comarca»</b> → Mapa SIGPAC anonimizado + alertas agregadas.",
            ],
            styles,
        ),
        Paragraph("Objeciones frecuentes — respuesta", styles["h2"]),
        bullet_list(
            [
                "«¿Sustituye al agrónomo?» → No. Amplifica su capacidad de supervisión; él sigue siendo quien valida.",
                "«¿Funciona sin internet?» → El escaneo IA sí; compartir, mapa y panel requieren conexión.",
                "«¿Es oficial SIEX?» → Borrador interno hoy; export ministerial en hoja de ruta 2027.",
                "«¿Cuánto cuesta?» → Piloto coop: licencia anual 200–500 €/año (dashboard + N socios). Perito: 15–30 €/mes. Consultar paquete piloto 5–6 agricultores.",
            ],
            styles,
        ),
        PageBreak(),
    ]


def section_closing(styles) -> list:
    return [
        Paragraph("5. Checklist antes de la demo comercial", styles["h1"]),
        bullet_list(
            [
                "APK instalada en móvil demo (agricultor + perito).",
                "Usuarios de prueba con licencias activas.",
                "ETL MAPA ejecutado (catálogo biocidas cargado).",
                "1 escaneo de prueba compartido → perito recibe notificación en panel.",
                "Explicar disclaimer IA en pantalla de resultado.",
            ],
            styles,
        ),
        Spacer(1, 8 * mm),
        Paragraph("Frase de cierre recomendada", styles["h2"]),
        Paragraph(
            "«Proponemos un piloto de 4 semanas con 5 agricultores de la cooperativa: ustedes ponen el perito, "
            "nosotros la plataforma y la formación. Medimos cuántos escaneos se validan y cuánto tiempo ahorra "
            "el técnico. Si no aporta valor, no seguimos.»",
            styles["quote"],
        ),
        Spacer(1, 10 * mm),
        HRFlowable(width="100%", thickness=0.5, color=GREEN),
        Spacer(1, 4 * mm),
        Paragraph(
            "NEXO Agro · NEXO Field Pro 1.B · https://agroplaga-ai.farm · Confidencial uso comercial interno",
            styles["footer"],
        ),
    ]


def main() -> None:
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=14 * mm,
        title="NEXO Field Pro 1.B — Guía comercial",
        author="Valentín Ruiz León",
    )
    story = []
    story.extend(cover_block(styles))
    story.extend(section_product(styles))
    story.extend(section_features(styles))
    story.extend(section_instructions(styles))
    story.extend(section_sales(styles))
    story.extend(section_closing(styles))
    doc.build(story)
    print(f"PDF generado: {OUTPUT}")


if __name__ == "__main__":
    main()
