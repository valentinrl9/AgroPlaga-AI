import "../api_client.dart";
import "../../models/alert.dart";

class AlertRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<PlagaAlert>> fetchAlerts({int? zoneId, bool activeOnly = true}) async {
    final params = <String, String>{"active_only": activeOnly.toString()};
    if (zoneId != null) params["zone_id"] = zoneId.toString();

    final query = params.entries.map((e) => "${e.key}=${Uri.encodeComponent(e.value)}").join("&");
    final result = await _client.getList("/api/v1/alerts?$query");

    return result
        .map((item) => PlagaAlert.fromJson(Map<String, dynamic>.from(item as Map)))
        .toList();
  }

  Future<AlertPreferencesData> fetchPreferences() async {
    final response = await _client.get("/api/v1/alerts/preferences");
    return AlertPreferencesData.fromJson(response);
  }

  Future<AlertPreferencesData> savePreferences(List<AlertPreference> preferences) async {
    final response = await _client.putAuth("/api/v1/alerts/preferences", {
      "preferences": preferences.map((p) => p.toJson()).toList(),
    });
    return AlertPreferencesData.fromJson(response);
  }

  Future<void> dismissAlert(int alertId) async {
    await _client.patchAuth("/api/v1/alerts/$alertId", {"active": false});
  }
}
