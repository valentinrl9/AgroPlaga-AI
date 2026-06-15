import "package:flutter/foundation.dart";
import "package:shared_preferences/shared_preferences.dart";

class ApiConfig {
  ApiConfig._();

  static const _prefsKey = "api_base_url";
  static const _apiOverride = String.fromEnvironment("API_BASE_URL");

  static String? _cached;

  static String get baseUrl => _cached ?? _defaultBaseUrl();

  static Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(_prefsKey);
    if (stored != null && stored.isNotEmpty) {
      _cached = normalize(stored);
      return;
    }
    if (_apiOverride.isNotEmpty) {
      _cached = normalize(_apiOverride);
      return;
    }
    _cached = _defaultBaseUrl();
  }

  static Future<void> save(String url) async {
    final normalized = normalize(url);
    _cached = normalized;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefsKey, normalized);
  }

  static Future<void> reset() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_prefsKey);
    _cached = _apiOverride.isNotEmpty ? normalize(_apiOverride) : _defaultBaseUrl();
  }

  static String normalize(String url) {
    var value = url.trim();
    if (value.isEmpty) return _defaultBaseUrl();
    if (!value.startsWith("http://") && !value.startsWith("https://")) {
      value = "http://$value";
    }
    return value.replaceAll(RegExp(r"/+$"), "");
  }

  static String _defaultBaseUrl() {
    if (kIsWeb) return "http://localhost:8000";
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return "http://10.0.2.2:8000";
      default:
        return "http://localhost:8000";
    }
  }
}
