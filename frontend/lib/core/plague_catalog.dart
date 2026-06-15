/// 15 plagas prioritarias del Poniente Almeriense (v1.5).
class PlagueCatalog {
  PlagueCatalog._();

  static const version = "v1.5";
  static const region = "Poniente Almeriense (invernaderos)";

  static const labels = [
    "sana",
    "tuta absoluta",
    "trips",
    "mosca blanca",
    "pulgón",
    "arañuela roja",
    "minador",
    "piojo harinoso",
    "oruga",
    "mildiu",
    "oídio",
    "botritis",
    "mancha bacteriana",
    "fusarium",
    "clorosis viral",
  ];

  static bool isKnown(String plague) {
    final key = plague.trim().toLowerCase();
    return labels.any((l) => l.toLowerCase() == key);
  }
}
