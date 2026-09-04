class WeeklyVigilance {
  final int goal;
  final int current;
  final bool completed;
  final DateTime endsAt;
  final int streakWeeks;
  final String description;

  WeeklyVigilance({
    required this.goal,
    required this.current,
    required this.completed,
    required this.endsAt,
    this.streakWeeks = 0,
    required this.description,
  });

  factory WeeklyVigilance.fromJson(Map<String, dynamic> json) {
    return WeeklyVigilance(
      goal: json["goal"] as int,
      current: json["current"] as int,
      completed: json["completed"] as bool? ?? false,
      endsAt: DateTime.parse(json["ends_at"] as String),
      streakWeeks: json["streak_weeks"] as int? ?? 0,
      description: json["description"] as String? ?? "",
    );
  }
}

class PilotCollective {
  final int totalScans;
  final int activeFarmers;
  final int goal;

  PilotCollective({
    required this.totalScans,
    required this.activeFarmers,
    required this.goal,
  });

  factory PilotCollective.fromJson(Map<String, dynamic> json) {
    return PilotCollective(
      totalScans: json["total_scans"] as int? ?? 0,
      activeFarmers: json["active_farmers"] as int? ?? 0,
      goal: json["goal"] as int? ?? 1000,
    );
  }

  double get progress => goal > 0 ? (totalScans / goal).clamp(0.0, 1.0) : 0.0;
}

class ActivitySummary {
  final int unreadCount;
  final Map<String, int> sections;
  final WeeklyVigilance weeklyVigilance;
  final int streakWeeks;
  final int openIncidentsActionCount;
  final PilotCollective pilotCollective;

  ActivitySummary({
    required this.unreadCount,
    required this.sections,
    required this.weeklyVigilance,
    required this.streakWeeks,
    required this.openIncidentsActionCount,
    required this.pilotCollective,
  });

  factory ActivitySummary.fromJson(Map<String, dynamic> json) {
    final sectionsRaw = json["sections"] as Map? ?? {};
    return ActivitySummary(
      unreadCount: json["unread_count"] as int? ?? 0,
      sections: sectionsRaw.map((k, v) => MapEntry(k.toString(), v as int? ?? 0)),
      weeklyVigilance: WeeklyVigilance.fromJson(
        Map<String, dynamic>.from(json["weekly_vigilance"] as Map),
      ),
      streakWeeks: json["streak_weeks"] as int? ?? 0,
      openIncidentsActionCount: json["open_incidents_action_count"] as int? ?? 0,
      pilotCollective: PilotCollective.fromJson(
        Map<String, dynamic>.from(json["pilot_collective"] as Map),
      ),
    );
  }

  int sectionCount(String key) => sections[key] ?? 0;
}

class UserNotificationItem {
  final int id;
  final String notificationType;
  final String section;
  final String title;
  final String body;
  final String? referenceType;
  final int? referenceId;
  final bool isRead;
  final DateTime createdAt;

  UserNotificationItem({
    required this.id,
    required this.notificationType,
    required this.section,
    required this.title,
    required this.body,
    this.referenceType,
    this.referenceId,
    required this.isRead,
    required this.createdAt,
  });

  factory UserNotificationItem.fromJson(Map<String, dynamic> json) {
    return UserNotificationItem(
      id: json["id"] as int,
      notificationType: json["notification_type"] as String,
      section: json["section"] as String? ?? "home",
      title: json["title"] as String,
      body: json["body"] as String,
      referenceType: json["reference_type"] as String?,
      referenceId: json["reference_id"] as int?,
      isRead: json["is_read"] as bool? ?? false,
      createdAt: DateTime.parse(json["created_at"] as String),
    );
  }
}
