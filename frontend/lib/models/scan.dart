class Scan {
  final int id;
  final String crop;
  final String plague;
  final String severity;
  final double confidence;
  final String? location;
  final int? farmId;
  final DateTime? createdAt;

  Scan({
    required this.id,
    required this.crop,
    required this.plague,
    required this.severity,
    this.confidence = 0.0,
    this.location,
    this.farmId,
    this.createdAt,
  });

  factory Scan.fromJson(Map<String, dynamic> json) {
    return Scan(
      id: json["id"] as int,
      crop: json["crop"] as String,
      plague: json["plague"] as String,
      severity: json["severity"] as String,
      confidence: (json["confidence"] as num?)?.toDouble() ?? 0.0,
      location: json["location"] as String?,
      farmId: json["farm_id"] as int?,
      createdAt: json["created_at"] != null ? DateTime.parse(json["created_at"] as String) : null,
    );
  }
}
