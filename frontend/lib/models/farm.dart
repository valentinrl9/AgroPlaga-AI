class Farm {
  final int id;
  final String name;
  final String crop;
  final String farmType;
  final int? zoneId;
  final double? surfaceM2;
  final String? sigpacCode;
  final DateTime createdAt;

  Farm({
    required this.id,
    required this.name,
    required this.crop,
    required this.farmType,
    this.zoneId,
    this.surfaceM2,
    this.sigpacCode,
    required this.createdAt,
  });

  factory Farm.fromJson(Map<String, dynamic> json) {
    return Farm(
      id: json["id"] as int,
      name: json["name"] as String,
      crop: json["crop"] as String,
      farmType: json["farm_type"] as String? ?? "farm",
      zoneId: json["zone_id"] as int?,
      surfaceM2: (json["surface_m2"] as num?)?.toDouble(),
      sigpacCode: json["sigpac_code"] as String?,
      createdAt: DateTime.parse(json["created_at"] as String),
    );
  }

  String get typeLabel => farmType == "greenhouse" ? "Invernadero" : "Finca";

  bool get hasSigpac => sigpacCode != null && sigpacCode!.trim().isNotEmpty;
}
