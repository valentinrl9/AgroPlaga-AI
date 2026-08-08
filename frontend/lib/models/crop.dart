class CropCatalogEntry {
  final String id;
  final String name;
  final List<String> aliases;
  final String category;
  final List<String> stages;

  CropCatalogEntry({
    required this.id,
    required this.name,
    required this.aliases,
    required this.category,
    required this.stages,
  });

  factory CropCatalogEntry.fromJson(Map<String, dynamic> json) {
    return CropCatalogEntry(
      id: json["id"] as String,
      name: json["name"] as String,
      aliases: (json["aliases"] as List<dynamic>? ?? const [])
          .map((e) => e.toString())
          .toList(),
      category: json["category"] as String? ?? "",
      stages: (json["stages"] as List<dynamic>? ?? const [])
          .map((e) => e.toString())
          .toList(),
    );
  }
}
