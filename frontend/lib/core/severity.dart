class Severity {
  static const levels = <int, String>{
    1: "Leve",
    2: "Moderado",
    3: "Alto",
  };

  static int? parseToLevel(String value) {
    final normalized = value.trim().toLowerCase();
    for (final entry in levels.entries) {
      if (entry.value.toLowerCase() == normalized) return entry.key;
    }
    switch (normalized) {
      case "low":
      case "leve":
        return 1;
      case "medium":
      case "moderado":
      case "moderada":
        return 2;
      case "high":
      case "alto":
      case "alta":
        return 3;
      default:
        return int.tryParse(normalized);
    }
  }

  static String labelFor(String value) {
    final level = parseToLevel(value);
    if (level != null) return levels[level] ?? value;
    return value;
  }

  static String labelForLevel(int level) => levels[level] ?? "Desconocido";
}
