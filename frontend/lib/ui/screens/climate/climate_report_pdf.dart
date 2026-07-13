import "package:pdf/pdf.dart";
import "package:pdf/widgets.dart" as pw;
import "package:printing/printing.dart";

Future<void> exportClimateMonthlyPdf({
  required Map<String, dynamic> resumenMensual,
  required Map<String, dynamic> resumenSemanal,
}) async {
  final doc = pw.Document();
  final mesInfo = (resumenMensual["informacion"] as List?)?.cast<String>() ?? [];
  final semInfo = (resumenSemanal["informacion"] as List?)?.cast<String>() ?? [];

  doc.addPage(
    pw.MultiPage(
      pageFormat: PdfPageFormat.a4,
      build: (context) => [
        pw.Header(
          level: 0,
          child: pw.Text("NEXO Climate — Informe mensual", style: pw.TextStyle(fontSize: 22, fontWeight: pw.FontWeight.bold)),
        ),
        pw.Text("Generado: ${DateTime.now().toIso8601String().substring(0, 16)}"),
        pw.SizedBox(height: 16),
        pw.Text("Resumen mensual", style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
        pw.SizedBox(height: 8),
        ...mesInfo.map((line) => pw.Bullet(text: line)),
        if (resumenMensual["nivel_riesgo"] != null)
          pw.Text("Riesgo: ${resumenMensual["nivel_riesgo"]}"),
        if (resumenMensual["recomendacion_general"] != null) ...[
          pw.SizedBox(height: 8),
          pw.Text(resumenMensual["recomendacion_general"].toString()),
        ],
        pw.SizedBox(height: 20),
        pw.Text("Resumen semanal", style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
        pw.SizedBox(height: 8),
        ...semInfo.map((line) => pw.Bullet(text: line)),
        if (resumenSemanal["nivel_riesgo"] != null)
          pw.Text("Riesgo: ${resumenSemanal["nivel_riesgo"]}"),
        pw.SizedBox(height: 20),
        pw.Text(
          "NEXO Agro · Datos Open-Meteo · Uso agronómico orientativo",
          style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700),
        ),
      ],
    ),
  );

  await Printing.layoutPdf(onLayout: (format) async => doc.save());
}
