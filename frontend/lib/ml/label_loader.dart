import "package:flutter/services.dart";

class LabelLoader {
  static List<String>? _cache;

  static Future<List<String>> load() async {
    if (_cache != null) return _cache!;

    final raw = await rootBundle.loadString("assets/ml/labels.txt");
    _cache = raw
        .split("\n")
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        .toList();

    return _cache!;
  }
}
