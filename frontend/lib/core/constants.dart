import "api_config.dart";

class ApiConstants {
  static String get baseUrl => ApiConfig.baseUrl;

  static const authPath = "/api/v1/auth";
}

/// Umbrales de UI para PlagaScan (orientación IA).
class ScanUiConstants {
  ScanUiConstants._();

  /// Por debajo de este valor se muestra aviso de confianza baja.
  static const lowConfidenceThreshold = 0.40;
}
