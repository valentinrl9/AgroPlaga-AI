class CountItem {
  final String name;
  final int count;

  CountItem({required this.name, required this.count});

  factory CountItem.fromJson(Map<String, dynamic> json) {
    return CountItem(name: json["name"] as String, count: json["count"] as int);
  }
}

class TimelinePoint {
  final String date;
  final int count;

  TimelinePoint({required this.date, required this.count});

  factory TimelinePoint.fromJson(Map<String, dynamic> json) {
    return TimelinePoint(date: json["date"] as String, count: json["count"] as int);
  }
}

class FarmBreakdown {
  final int farmId;
  final String name;
  final String crop;
  final String farmType;
  final int scanCount;

  FarmBreakdown({
    required this.farmId,
    required this.name,
    required this.crop,
    required this.farmType,
    required this.scanCount,
  });

  factory FarmBreakdown.fromJson(Map<String, dynamic> json) {
    return FarmBreakdown(
      farmId: json["farm_id"] as int,
      name: json["name"] as String,
      crop: json["crop"] as String,
      farmType: json["farm_type"] as String? ?? "farm",
      scanCount: json["scan_count"] as int? ?? 0,
    );
  }
}

class AnalyticsSummary {
  final int days;
  final int totalScans;
  final int highSeverityCount;
  final List<CountItem> crops;
  final List<CountItem> plagues;

  AnalyticsSummary({
    required this.days,
    required this.totalScans,
    required this.highSeverityCount,
    required this.crops,
    required this.plagues,
  });

  factory AnalyticsSummary.fromJson(Map<String, dynamic> json) {
    return AnalyticsSummary(
      days: json["days"] as int,
      totalScans: json["total_scans"] as int,
      highSeverityCount: json["high_severity_count"] as int? ?? 0,
      crops: (json["crops"] as List? ?? [])
          .map((e) => CountItem.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      plagues: (json["plagues"] as List? ?? [])
          .map((e) => CountItem.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
    );
  }
}

class ScanHistoryItem {
  final int id;
  final String crop;
  final String plague;
  final double confidence;
  final String severity;
  final DateTime? createdAt;

  ScanHistoryItem({
    required this.id,
    required this.crop,
    required this.plague,
    required this.confidence,
    required this.severity,
    this.createdAt,
  });

  factory ScanHistoryItem.fromJson(Map<String, dynamic> json) {
    return ScanHistoryItem(
      id: json["id"] as int,
      crop: json["crop"] as String,
      plague: json["plague"] as String,
      confidence: (json["confidence"] as num?)?.toDouble() ?? 0.0,
      severity: json["severity"] as String,
      createdAt: json["created_at"] != null ? DateTime.parse(json["created_at"] as String) : null,
    );
  }
}

class PersonalAnalytics {
  final AnalyticsSummary summary;
  final List<TimelinePoint> timeline;
  final List<FarmBreakdown> farms;
  final List<ScanHistoryItem> recentScans;

  PersonalAnalytics({
    required this.summary,
    required this.timeline,
    required this.farms,
    required this.recentScans,
  });

  factory PersonalAnalytics.fromJson(Map<String, dynamic> json) {
    return PersonalAnalytics(
      summary: AnalyticsSummary.fromJson(Map<String, dynamic>.from(json["summary"] as Map)),
      timeline: (json["timeline"] as List? ?? [])
          .map((e) => TimelinePoint.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      farms: (json["farms"] as List? ?? [])
          .map((e) => FarmBreakdown.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      recentScans: (json["recent_scans"] as List? ?? [])
          .map((e) => ScanHistoryItem.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
    );
  }
}

class PlagaRecommendation {
  final String plague;
  final String crop;
  final String severity;
  final int severityLevel;
  final String urgency;
  final String recommendation;
  final String preventionTip;

  PlagaRecommendation({
    required this.plague,
    required this.crop,
    required this.severity,
    required this.severityLevel,
    required this.urgency,
    required this.recommendation,
    required this.preventionTip,
  });

  factory PlagaRecommendation.fromJson(Map<String, dynamic> json) {
    return PlagaRecommendation(
      plague: json["plague"] as String,
      crop: json["crop"] as String,
      severity: json["severity"] as String,
      severityLevel: json["severity_level"] as int? ?? 2,
      urgency: json["urgency"] as String? ?? "media",
      recommendation: json["recommendation"] as String,
      preventionTip: json["prevention_tip"] as String,
    );
  }
}
