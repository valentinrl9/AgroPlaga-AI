"""Business Model Canvas — exactamente 1 página A4 horizontal."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

OUTPUT = Path(__file__).resolve().parent / "Business_Model_Canvas_AgroPlaga_AI.pdf"

GREEN = colors.HexColor("#2E7D32")
GREEN_LIGHT = colors.HexColor("#E8F5E9")
HEADER_BG = colors.HexColor("#1B5E20")
COST_BG = colors.HexColor("#FFF3E0")
REV_BG = colors.HexColor("#E3F2FD")
BORDER = colors.HexColor("#9E9E9E")
TEXT = colors.HexColor("#212121")

BLOCKS = {
    "partners": (
        "SOCIOS CLAVE",
        "Ayuntamientos Poniente (El Ejido, Dalías): difusión y asociaciones.\n"
        "Junta de Andalucía: desarrollo rural y subvenciones.\n"
        "Escuelas agrícolas: validación IA y pilotos con peritos.\n"
        "Misión Agrotech, IOE, Cámara Almería: PI, legal y RGPD.",
    ),
    "activities": (
        "ACTIVIDADES CLAVE",
        "IA predictiva: entrenamiento sobre mapa colaborativo.\n"
        "Software multi-perfil: app agricultor, técnico y dashboard coop.\n"
        "Auditoría de datos: filtrado y validación de alertas.",
    ),
    "value": (
        "PROPUESTA DE VALOR",
        "Cooperativas/SAT: dashboard multi-agricultor, mapa SIGPAC validado, informes semanales; menos visitas a ciegas.\n"
        "Técnicos: analítica avanzada, historial por finca, informes PDF.\n"
        "Agricultores: PlagaScan gratis offline, alertas comarcales, red colaborativa.",
    ),
    "relationships": (
        "RELACIÓN CON CLIENTES",
        "Agricultores: base gratuita; confianza y datos de calidad a cambio.\n"
        "B2B: soporte, formación y consultoría bajo licencia.\n"
        "Co-creación: entrevistas piloto (sem. 2 y 4) para medir disposición de pago.",
    ),
    "segments": (
        "SEGMENTOS DE CLIENTES",
        "Cooperativas y SAT (B2B): control fitosanitario territorial.\n"
        "Técnicos y peritos: carteras de fincas e informes en campo.\n"
        "Organismos públicos: datos agregados validados.\n"
        "Agricultores red: usuarios freemium que alimentan el mapa.",
    ),
    "resources": (
        "RECURSOS CLAVE",
        "TFLite: diagnóstico local sin datos en invernadero.\n"
        "Cloud + PostGIS: VPS, dashboards y geo en tiempo real.\n"
        "Datos SIGPAC: base anonimizada comarcal.",
    ),
    "channels": (
        "CANALES",
        "Venta directa: reuniones con gerentes coop/SAT.\n"
        "Ferias agrícolas Almería y eventos AgTech.\n"
        "App Stores: descarga app agricultor.",
    ),
    "costs": (
        "ESTRUCTURA DE COSTES (bootstrap anual)",
        "Tech/infra: 500–800 € (VPS, dominio, SSL, herramientas dev).\n"
        "Marketing Km 0: 1.000–1.500 € (visitas, folletos, eventos).\n"
        "Asesoría legal: 0 € (aceleración pública).",
    ),
    "revenue": (
        "FUENTES DE INGRESOS",
        "Licencia B2B coop/SAT: 200–500 €/año (dashboard, informes, control socios).\n"
        "SaaS técnico: 15–30 €/mes · Premium farmer (F2): 2–5 €/mes.\n"
        "Licitaciones: informes agregados anonimizados.\n"
        "Proyección: A1 ~4.500 € · A2 ~25 k€ · A3 ~75–90 k€.",
    ),
}


def wrap_lines(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            continue
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if pdfmetrics.stringWidth(trial, font, size) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_block(c, x: float, y: float, w: float, h: float, title: str, body: str, bg) -> None:
    c.setFillColor(bg)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.rect(x, y, w, h, fill=1, stroke=1)

    pad = 4
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(x + pad, y + h - 9, title)

    c.setFillColor(TEXT)
    c.setFont("Helvetica", 5.3)
    max_w = w - 2 * pad
    line_h = 6.1
    yy = y + h - 16
    for line in wrap_lines(body, "Helvetica", 5.3, max_w):
        if yy < y + 3:
            break
        c.drawString(x + pad, yy, line)
        yy -= line_h


def main() -> None:
    page_w, page_h = landscape(A4)
    m = 4 * mm
    header_h = 10 * mm

    c = canvas.Canvas(str(OUTPUT), pagesize=landscape(A4))
    c.setTitle("Business Model Canvas — AgroPlaga AI")
    c.setAuthor("Valentín Ruiz León")

    # Cabecera
    c.setFillColor(HEADER_BG)
    c.rect(m, page_h - m - header_h, page_w - 2 * m, header_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(m + 6, page_h - m - header_h + 14, "BUSINESS MODEL CANVAS — AGROPLAGA AI")
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.HexColor("#C8E6C9"))
    c.drawString(
        m + 6,
        page_h - m - header_h + 4,
        "Valentín Ruiz León · Jun 2026 · Híbrido B2B / Lean Km 0 · Freemium agricultor · Licencia coop/técnico",
    )

    # Rejilla BMC
    grid_x = m
    grid_y = m
    grid_w = page_w - 2 * m
    grid_h = page_h - 2 * m - header_h - 1.5 * mm

    col_w = grid_w / 5
    row_top_h = grid_h * 0.36
    row_mid_h = grid_h * 0.34
    row_bot_h = grid_h * 0.30

    y_top = grid_y + row_mid_h + row_bot_h
    y_mid = grid_y + row_bot_h

    # Fila superior
    draw_block(c, grid_x + 0 * col_w, y_top, col_w, row_top_h, *BLOCKS["partners"], GREEN_LIGHT)
    draw_block(c, grid_x + 1 * col_w, y_top, col_w, row_top_h, *BLOCKS["activities"], GREEN_LIGHT)
    draw_block(c, grid_x + 2 * col_w, y_mid, col_w, row_top_h + row_mid_h, *BLOCKS["value"], GREEN_LIGHT)
    draw_block(c, grid_x + 3 * col_w, y_top, col_w, row_top_h, *BLOCKS["relationships"], GREEN_LIGHT)
    draw_block(c, grid_x + 4 * col_w, y_mid, col_w, row_top_h + row_mid_h, *BLOCKS["segments"], GREEN_LIGHT)

    # Fila media
    draw_block(c, grid_x + 0 * col_w, y_mid, col_w, row_mid_h, *BLOCKS["resources"], GREEN_LIGHT)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.setFillColor(GREEN_LIGHT)
    c.rect(grid_x + 1 * col_w, y_mid, col_w, row_mid_h, fill=1, stroke=1)
    draw_block(c, grid_x + 3 * col_w, y_mid, col_w, row_mid_h, *BLOCKS["channels"], GREEN_LIGHT)

    # Fila inferior
    draw_block(c, grid_x, grid_y, col_w * 2, row_bot_h, *BLOCKS["costs"], COST_BG)
    draw_block(c, grid_x + col_w * 2, grid_y, col_w * 3, row_bot_h, *BLOCKS["revenue"], REV_BG)

    c.showPage()
    c.save()
    print(f"PDF generado (1 pagina): {OUTPUT}")


if __name__ == "__main__":
    main()
