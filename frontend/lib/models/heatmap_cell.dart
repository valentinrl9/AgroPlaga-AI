class HeatmapCell {
  final int zoneId;
  final String sigpacCode;
  final String zoneName;
  final double lat;
  final double lon;
  final int count;
  final int maxSeverity;
  final double intensity;
  final int validatedCount;
  final int pendingCount;

  HeatmapCell({
    required this.zoneId,
    required this.sigpacCode,
    required this.zoneName,
    required this.lat,
    required this.lon,
    required this.count,
    required this.maxSeverity,
    required this.intensity,
    this.validatedCount = 0,
    this.pendingCount = 0,
  });

  factory HeatmapCell.fromJson(Map<String, dynamic> json) {
    return HeatmapCell(
      zoneId: json["zone_id"] as int,
      sigpacCode: json["sigpac_code"] as String,
      zoneName: json["zone_name"] as String,
      lat: (json["lat"] as num).toDouble(),
      lon: (json["lon"] as num).toDouble(),
      count: json["count"] as int,
      maxSeverity: json["max_severity"] as int,
      intensity: (json["intensity"] as num).toDouble(),
      validatedCount: json["validated_count"] as int? ?? 0,
      pendingCount: json["pending_count"] as int? ?? 0,
    );
  }

  bool get hasPendingOnly => pendingCount > 0 && validatedCount == 0;
  bool get hasValidatedOnly => validatedCount > 0 && pendingCount == 0;
  bool get isMixed => validatedCount > 0 && pendingCount > 0;
}
