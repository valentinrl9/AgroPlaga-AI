import "package:flutter/foundation.dart";
import "package:shared_preferences/shared_preferences.dart";

class ApiConfig {
  ApiConfig._();

  static const _prefsKey = "api_base_url";
  static const _apiOverride = String.fromEnvironment("API_BASE_URL");

  static String? _cached;

  static bool get allowCustomServerUrl => kDebugMode;

  static String get baseUrl => _cached ?? _defaultBaseUrl();

  static Future<void> load() async {
    if (_apiOverride.isNotEmpty) {
      _cached = normalize(_apiOverride);
      return;
    }
    if (!allowCustomServerUrl) {
      _cached = _defaultBaseUrl();
      return;
    }
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(_prefsKey);
    if (stored != null && stored.isNotEmpty) {
      _cached = normalize(stored);
      return;
    }
    _cached = _defaultBaseUrl();
  }

  static Future<void> save(String url) async {
    if (!allowCustomServerUrl) return;
    final normalized = normalize(url);
    _enforceTransportPolicy(normalized);
    _cached = normalized;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefsKey, normalized);
  }

  static Future<void> reset() async {
    if (!allowCustomServerUrl) return;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_prefsKey);
    _cached = _apiOverride.isNotEmpty ? normalize(_apiOverride) : _defaultBaseUrl();
  }

  static String normalize(String url) {
    var value = url.trim();
    if (value.isEmpty) return _defaultBaseUrl();
    if (!value.startsWith("http://") && !value.startsWith("https://")) {
      value = kReleaseMode ? "https://$value" : "http://$value";
    }
    final normalized = value.replaceAll(RegExp(r"/+$"), "");
    _enforceTransportPolicy(normalized);
    return normalized;
  }

  static void _enforceTransportPolicy(String url) {
    if (kReleaseMode && !url.startsWith("https://")) {
      throw ArgumentError("En producción solo se permiten URLs HTTPS.");
    }
  }

  static String _defaultBaseUrl() {
    if (_apiOverride.isNotEmpty) {
      return normalize(_apiOverride);
    }
    if (kReleaseMode) {
      throw StateError(
        "Define API_BASE_URL con HTTPS al compilar release "
        "(flutter build --dart-define=API_BASE_URL=https://tu-dominio)",
      );
    }
    if (kIsWeb) return "http://localhost:8000";
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return "http://10.0.2.2:8000";
      default:
        return "http://localhost:8000";
    }
  }
}
