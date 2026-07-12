class OutbreakEvent {
  final int id;
  final String plague;
  final int severity;
  final int zoneId;
  final String? zoneName;
  final DateTime reportedAt;
  final String modelVersion;
  final bool validated;
  final String status;
  final String? originalPlague;
  final String? correctedPlague;
  final String displayPlague;
  final int? sourceScanId;

  OutbreakEvent({
    required this.id,
    required this.plague,
    required this.severity,
    required this.zoneId,
    this.zoneName,
    required this.reportedAt,
    required this.modelVersion,
    required this.validated,
    this.status = "pending",
    this.originalPlague,
    this.correctedPlague,
    required this.displayPlague,
    this.sourceScanId,
  });

  factory OutbreakEvent.fromJson(Map<String, dynamic> json) {
    return OutbreakEvent(
      id: json["id"] as int,
      plague: json["plague"] as String,
      severity: json["severity"] as int,
      zoneId: json["zone_id"] as int,
      zoneName: json["zone_name"] as String?,
      reportedAt: DateTime.parse(json["reported_at"] as String),
      modelVersion: json["model_version"] as String,
      validated: json["validated"] as bool? ?? false,
      status: json["status"] as String? ?? (json["validated"] == true ? "validated" : "pending"),
      originalPlague: json["original_plague"] as String?,
      correctedPlague: json["corrected_plague"] as String?,
      displayPlague: json["display_plague"] as String? ?? json["plague"] as String,
      sourceScanId: json["source_scan_id"] as int?,
    );
  }

  bool get isPending => status == "pending";
  bool get isValidated => status == "validated";
  bool get wasCorrected => correctedPlague != null && correctedPlague!.isNotEmpty;

  String get severityLabel {
    switch (severity) {
      case 1:
        return "Leve";
      case 2:
        return "Moderado";
      case 3:
        return "Alto";
      default:
        return "Desconocido";
    }
  }
}
