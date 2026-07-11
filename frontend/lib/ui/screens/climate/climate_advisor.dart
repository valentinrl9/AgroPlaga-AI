/// Consejos agronómicos (portado de AgroData main.js).
class ClimateAdvisor {
  static Map<String, String> generate({
    required Map<String, dynamic> actual,
    required Map<String, dynamic> recomendaciones,
  }) {
    final diario = (recomendaciones["diario"] as List?) ?? [];
    final hoy = diario.isNotEmpty ? diario.first as Map<String, dynamic> : <String, dynamic>{};

    final et0Hoy = (actual["et0_dia"] as num?)?.toDouble() ?? 0;
    final estres = (actual["estres_termico"] as num?)?.toDouble() ?? 0;
    final humedadHoy = (actual["humedad_dia"] as num?)?.toDouble() ??
        (actual["humedad"] as num?)?.toDouble() ??
        0;
    final temp = (actual["temperatura"] as num?)?.toDouble() ?? 0;

    double et0PredMax = et0Hoy;
    double lluviaSemana = 0;
    for (final d in diario) {
      final map = d as Map<String, dynamic>;
      final et0 = (map["et0"] as num?)?.toDouble() ?? 0;
      if (et0 > et0PredMax) et0PredMax = et0;
      lluviaSemana += (map["lluvia"] as num?)?.toDouble() ?? 0;
    }

    final hoyEstres = (hoy["estres"] as num?)?.toDouble() ?? 0;

    String riego;
    if (lluviaSemana > 8) {
      riego =
          "Se previenen ${lluviaSemana.toStringAsFixed(1)} mm esta semana. Reduce riego y revisa drenaje.";
    } else if (et0PredMax > 4 || et0Hoy > 3.5) {
      riego =
          "ET0 hoy ${et0Hoy.toStringAsFixed(1)} mm/día. Programa riego en la tarde (18-20 h).";
    } else if (et0Hoy > 2) {
      riego = "Demanda hídrica moderada (${et0Hoy.toStringAsFixed(1)} mm/día). Riego normal.";
    } else {
      riego = "Baja evapotranspiración. Riego ligero; prioriza ventilación si humedad > 85%.";
    }

    String ventilacion;
    if (estres > 110) {
      ventilacion =
          "Estrés ${estres.toStringAsFixed(0)} (alto). Abre ventilaciones entre 11 h y 16 h.";
    } else if (estres > 95) {
      ventilacion = "Estrés en subida. Aumenta ventilación en horas centrales.";
    } else if (hoyEstres > estres + 5) {
      ventilacion = "El estrés subirá (hasta ~${hoyEstres.toStringAsFixed(0)}). Prepasa ventilación.";
    } else {
      ventilacion = "Estrés controlado (${estres.toStringAsFixed(0)}). Mantén ventilación programada.";
    }

    String humedad;
    if (humedadHoy > 90 || (humedadHoy > 85 && lluviaSemana > 3)) {
      humedad = "Humedad ${humedadHoy.toStringAsFixed(0)}% + lluvia. Ventila al amanecer; vigila hongos.";
    } else if (humedadHoy > 85) {
      humedad = "Humedad alta (${humedadHoy.toStringAsFixed(0)}%). Evita riego foliar al atardecer.";
    } else if (humedadHoy < 45) {
      humedad = "Ambiente seco (${humedadHoy.toStringAsFixed(0)}%). Riesgo en brotes tiernos.";
    } else {
      humedad = "Humedad adecuada (${humedadHoy.toStringAsFixed(0)}%). Ventila al atardecer.";
    }

    return {"riego": riego, "ventilacion": ventilacion, "humedad": humedad};
  }
}
