class HeatmapCell {
  final int zoneId;
  final String sigpacCode;
  final String zoneName;
  final double lat;
  final double lon;
  final int count;
  final int maxSeverity;
  final double intensity;

  HeatmapCell({
    required this.zoneId,
    required this.sigpacCode,
    required this.zoneName,
    required this.lat,
    required this.lon,
    required this.count,
    required this.maxSeverity,
    required this.intensity,
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
    );
  }
}
