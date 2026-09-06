import "official_source.dart";

class PlagaAlert {
  final int id;
  final int zoneId;
  final String? zoneName;
  final String plague;
  final String alertType;
  final String description;
  final double? priorityScore;
  final DateTime createdAt;
  final bool active;
  final List<OfficialSource> officialSources;
  final String officialAttribution;

  PlagaAlert({
    required this.id,
    required this.zoneId,
    this.zoneName,
    required this.plague,
    required this.alertType,
    required this.description,
    this.priorityScore,
    required this.createdAt,
    required this.active,
    this.officialSources = const [],
    this.officialAttribution = "",
  });

  factory PlagaAlert.fromJson(Map<String, dynamic> json) {
    final sources = (json["official_sources"] as List? ?? [])
        .map((item) => OfficialSource.fromJson(Map<String, dynamic>.from(item as Map)))
        .toList();
    return PlagaAlert(
      id: json["id"] as int,
      zoneId: json["zone_id"] as int,
      zoneName: json["zone_name"] as String?,
      plague: json["plague"] as String,
      alertType: json["alert_type"] as String,
      description: json["description"] as String,
      priorityScore: (json["priority_score"] as num?)?.toDouble(),
      createdAt: DateTime.parse(json["created_at"] as String),
      active: json["active"] as bool? ?? true,
      officialSources: sources,
      officialAttribution: json["official_attribution"] as String? ?? "",
    );
  }

  String get displayAttribution {
    if (officialAttribution.trim().isNotEmpty) return officialAttribution;
    final official = officialSources.where((source) => source.isOfficial).toList();
    if (official.isNotEmpty) {
      return "Para medidas oficiales en tu zona, consulta ${official.first.issuer}.";
    }
    return "Alerta automática del mapa comunitario AgroPlaga (no emitida por RAIF).";
  }
}

class AlertPreference {
  final String plague;
  final bool enabled;

  AlertPreference({required this.plague, required this.enabled});

  factory AlertPreference.fromJson(Map<String, dynamic> json) {
    return AlertPreference(
      plague: json["plague"] as String,
      enabled: json["enabled"] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {"plague": plague, "enabled": enabled};
}

class AlertPreferencesData {
  final List<AlertPreference> preferences;
  final List<String> availablePlagues;

  AlertPreferencesData({
    required this.preferences,
    required this.availablePlagues,
  });

  factory AlertPreferencesData.fromJson(Map<String, dynamic> json) {
    final prefs = (json["preferences"] as List? ?? [])
        .map((item) => AlertPreference.fromJson(Map<String, dynamic>.from(item as Map)))
        .toList();
    final available = (json["available_plagues"] as List? ?? [])
        .map((item) => item as String)
        .toList();
    return AlertPreferencesData(preferences: prefs, availablePlagues: available);
  }
}
