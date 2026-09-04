import "../api_client.dart";
import "../../models/activity_summary.dart";

class ActivityRepository {
  final ApiClient _client = ApiClient.instance;

  Future<ActivitySummary> fetchSummary() async {
    final json = await _client.get("/api/v1/me/activity-summary");
    return ActivitySummary.fromJson(json);
  }

  Future<List<UserNotificationItem>> fetchNotifications({bool unreadOnly = false}) async {
    final q = unreadOnly ? "?unread_only=true" : "";
    final list = await _client.getList("/api/v1/me/notifications$q");
    return list
        .map((e) => UserNotificationItem.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<void> markSectionRead(String section) async {
    await _client.patchAuth("/api/v1/me/notifications/sections/$section/read", {});
  }

  Future<void> markAllRead() async {
    await _client.patchAuth("/api/v1/me/notifications/read-all", {});
  }
}
