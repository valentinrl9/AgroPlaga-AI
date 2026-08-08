class IncidentTreatmentSummary {
  final int id;
  final String productName;
  final int safetyHours;
  final double? hoursRemaining;
  final bool harvestAllowed;

  IncidentTreatmentSummary({
    required this.id,
    required this.productName,
    required this.safetyHours,
    this.hoursRemaining,
    required this.harvestAllowed,
  });

  factory IncidentTreatmentSummary.fromJson(Map<String, dynamic> json) {
    return IncidentTreatmentSummary(
      id: json["id"] as int,
      productName: json["product_name"] as String,
      safetyHours: json["safety_hours"] as int,
      hoursRemaining: (json["hours_remaining"] as num?)?.toDouble(),
      harvestAllowed: json["harvest_allowed"] as bool? ?? false,
    );
  }
}

class PestIncident {
  final int id;
  final int scanId;
  final int? farmId;
  final String? farmName;
  final int zoneId;
  final String? zoneName;
  final int? outbreakEventId;
  final String plague;
  final String crop;
  final int severity;
  final String stage;
  final String? closureOutcome;
  final String? notes;
  final String? prescriptionProductName;
  final String? prescriptionRegistryNumber;
  final double? prescriptionDoseMl;
  final int? prescriptionSafetyHours;
  final IncidentTreatmentSummary? treatment;
  final int? evaluationScanId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? closedAt;

  PestIncident({
    required this.id,
    required this.scanId,
    this.farmId,
    this.farmName,
    required this.zoneId,
    this.zoneName,
    this.outbreakEventId,
    required this.plague,
    required this.crop,
    required this.severity,
    required this.stage,
    this.closureOutcome,
    this.notes,
    this.prescriptionProductName,
    this.prescriptionRegistryNumber,
    this.prescriptionDoseMl,
    this.prescriptionSafetyHours,
    this.treatment,
    this.evaluationScanId,
    required this.createdAt,
    required this.updatedAt,
    this.closedAt,
  });

  factory PestIncident.fromJson(Map<String, dynamic> json) {
    return PestIncident(
      id: json["id"] as int,
      scanId: json["scan_id"] as int,
      farmId: json["farm_id"] as int?,
      farmName: json["farm_name"] as String?,
      zoneId: json["zone_id"] as int,
      zoneName: json["zone_name"] as String?,
      outbreakEventId: json["outbreak_event_id"] as int?,
      plague: json["plague"] as String,
      crop: json["crop"] as String,
      severity: json["severity"] as int,
      stage: json["stage"] as String,
      closureOutcome: json["closure_outcome"] as String?,
      notes: json["notes"] as String?,
      prescriptionProductName: json["prescription_product_name"] as String?,
      prescriptionRegistryNumber: json["prescription_registry_number"] as String?,
      prescriptionDoseMl: (json["prescription_dose_ml"] as num?)?.toDouble(),
      prescriptionSafetyHours: json["prescription_safety_hours"] as int?,
      treatment: json["treatment"] != null
          ? IncidentTreatmentSummary.fromJson(Map<String, dynamic>.from(json["treatment"] as Map))
          : null,
      evaluationScanId: json["evaluation_scan_id"] as int?,
      createdAt: DateTime.parse(json["created_at"] as String),
      updatedAt: DateTime.parse(json["updated_at"] as String),
      closedAt: json["closed_at"] != null ? DateTime.parse(json["closed_at"] as String) : null,
    );
  }

  bool get isActive => stage != "closed";

  String get stageLabel {
    const labels = {
      "detection": "Detección",
      "diagnosis": "Diagnóstico",
      "prescription": "Prescripción",
      "treatment": "Tratamiento",
      "evaluation": "Evaluación",
      "closed": "Cierre",
    };
    return labels[stage] ?? stage;
  }

  int get stageIndex {
    const order = ["detection", "diagnosis", "prescription", "treatment", "evaluation", "closed"];
    return order.indexOf(stage).clamp(0, order.length - 1);
  }
}
