class NotificationPreferences {
  final bool pushScanValidation;
  final bool pushIncidents;
  final bool pushCarencia;
  final bool pushAlertsComarcal;
  final bool pushBadges;
  final bool pushWeekly;
  final bool pushTechPending;
  final bool quietHoursEnabled;
  final int quietHoursStart;
  final int quietHoursEnd;

  NotificationPreferences({
    required this.pushScanValidation,
    required this.pushIncidents,
    required this.pushCarencia,
    required this.pushAlertsComarcal,
    required this.pushBadges,
    required this.pushWeekly,
    required this.pushTechPending,
    required this.quietHoursEnabled,
    required this.quietHoursStart,
    required this.quietHoursEnd,
  });

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) {
    return NotificationPreferences(
      pushScanValidation: json["push_scan_validation"] as bool? ?? true,
      pushIncidents: json["push_incidents"] as bool? ?? true,
      pushCarencia: json["push_carencia"] as bool? ?? true,
      pushAlertsComarcal: json["push_alerts_comarcal"] as bool? ?? false,
      pushBadges: json["push_badges"] as bool? ?? true,
      pushWeekly: json["push_weekly"] as bool? ?? true,
      pushTechPending: json["push_tech_pending"] as bool? ?? true,
      quietHoursEnabled: json["quiet_hours_enabled"] as bool? ?? true,
      quietHoursStart: json["quiet_hours_start"] as int? ?? 22,
      quietHoursEnd: json["quiet_hours_end"] as int? ?? 7,
    );
  }

  Map<String, dynamic> toJson() => {
        "push_scan_validation": pushScanValidation,
        "push_incidents": pushIncidents,
        "push_carencia": pushCarencia,
        "push_alerts_comarcal": pushAlertsComarcal,
        "push_badges": pushBadges,
        "push_weekly": pushWeekly,
        "push_tech_pending": pushTechPending,
        "quiet_hours_enabled": quietHoursEnabled,
        "quiet_hours_start": quietHoursStart,
        "quiet_hours_end": quietHoursEnd,
      };

  NotificationPreferences copyWith({
    bool? pushScanValidation,
    bool? pushIncidents,
    bool? pushCarencia,
    bool? pushAlertsComarcal,
    bool? pushBadges,
    bool? pushWeekly,
    bool? pushTechPending,
    bool? quietHoursEnabled,
    int? quietHoursStart,
    int? quietHoursEnd,
  }) {
    return NotificationPreferences(
      pushScanValidation: pushScanValidation ?? this.pushScanValidation,
      pushIncidents: pushIncidents ?? this.pushIncidents,
      pushCarencia: pushCarencia ?? this.pushCarencia,
      pushAlertsComarcal: pushAlertsComarcal ?? this.pushAlertsComarcal,
      pushBadges: pushBadges ?? this.pushBadges,
      pushWeekly: pushWeekly ?? this.pushWeekly,
      pushTechPending: pushTechPending ?? this.pushTechPending,
      quietHoursEnabled: quietHoursEnabled ?? this.quietHoursEnabled,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
    );
  }
}
