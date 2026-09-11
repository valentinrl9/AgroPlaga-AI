import "package:shared_preferences/shared_preferences.dart";

/// IDs locales de avisos del Inicio marcados como leídos por el agricultor.
class HomeInboxPrefs {
  HomeInboxPrefs._();

  static const _key = "home_inbox_dismissed_ids";

  static Future<Set<String>> dismissedIds() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(_key)?.toSet() ?? {};
  }

  static Future<void> dismiss(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getStringList(_key)?.toSet() ?? {};
    current.add(id);
    await prefs.setStringList(_key, current.toList());
  }

  static Future<void> undismiss(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getStringList(_key)?.toSet() ?? {};
    current.remove(id);
    await prefs.setStringList(_key, current.toList());
  }
}
