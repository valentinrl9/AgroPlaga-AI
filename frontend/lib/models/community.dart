import "../../models/activity_summary.dart";

export "../../models/activity_summary.dart" show WeeklyVigilance, PilotCollective;

class UserBadge {
  final String code;
  final String label;
  final DateTime earnedAt;

  UserBadge({required this.code, required this.label, required this.earnedAt});

  factory UserBadge.fromJson(Map<String, dynamic> json) {
    return UserBadge(
      code: json["code"] as String,
      label: json["label"] as String,
      earnedAt: DateTime.parse(json["earned_at"] as String),
    );
  }
}

class ZoneRankingEntry {
  final int zoneId;
  final String zoneName;
  final int contributions;
  final int validatedCount;

  ZoneRankingEntry({
    required this.zoneId,
    required this.zoneName,
    required this.contributions,
    required this.validatedCount,
  });

  factory ZoneRankingEntry.fromJson(Map<String, dynamic> json) {
    return ZoneRankingEntry(
      zoneId: json["zone_id"] as int,
      zoneName: json["zone_name"] as String,
      contributions: json["contributions"] as int,
      validatedCount: json["validated_count"] as int? ?? 0,
    );
  }
}

class CommunityProfile {
  final int contributionCount;
  final List<UserBadge> badges;
  final WeeklyVigilance weeklyVigilance;
  final List<ZoneRankingEntry> zoneRanking;
  final PilotCollective pilotCollective;

  CommunityProfile({
    required this.contributionCount,
    required this.badges,
    required this.weeklyVigilance,
    required this.zoneRanking,
    required this.pilotCollective,
  });

  factory CommunityProfile.fromJson(Map<String, dynamic> json) {
    return CommunityProfile(
      contributionCount: json["contribution_count"] as int? ?? 0,
      badges: (json["badges"] as List? ?? [])
          .map((e) => UserBadge.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      weeklyVigilance: WeeklyVigilance.fromJson(
        Map<String, dynamic>.from(json["weekly_vigilance"] as Map),
      ),
      zoneRanking: (json["zone_ranking"] as List? ?? [])
          .map((e) => ZoneRankingEntry.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      pilotCollective: PilotCollective.fromJson(
        Map<String, dynamic>.from(json["pilot_collective"] as Map? ?? {"total_scans": 0, "active_farmers": 0, "goal": 1000}),
      ),
    );
  }
}
