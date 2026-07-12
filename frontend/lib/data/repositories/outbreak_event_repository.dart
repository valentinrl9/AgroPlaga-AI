import "../api_client.dart";
import "../../models/outbreak_event.dart";

class OutbreakEventRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<OutbreakEvent>> fetchEvents({
    int? zoneId,
    String? plague,
    int? hours,
    int? minSeverity,
    bool validatedOnly = false,
  }) async {
    final params = <String, String>{};
    if (zoneId != null) params["zone_id"] = zoneId.toString();
    if (plague != null && plague.isNotEmpty) params["plague"] = plague;
    if (hours != null) params["hours"] = hours.toString();
    if (minSeverity != null) {
      params["min_severity"] = minSeverity.toString();
    }
    if (validatedOnly) params["validated_only"] = "true";

    final query = params.entries.map((e) => "${e.key}=${Uri.encodeComponent(e.value)}").join("&");
    final path = query.isEmpty ? "/api/v1/outbreak-events" : "/api/v1/outbreak-events?$query";

    final result = await _client.getList(path);
    return result
        .map((item) => OutbreakEvent.fromJson(Map<String, dynamic>.from(item as Map)))
        .toList();
  }

  Future<OutbreakEvent> contribute({
    required String plague,
    required int severity,
    required int zoneId,
    String modelVersion = "v0.0",
    int? sourceScanId,
  }) async {
    final response = await _client.postAuth("/api/v1/outbreak-events", {
      "plague": plague,
      "severity": severity,
      "zone_id": zoneId,
      "model_version": modelVersion,
      if (sourceScanId != null) "source_scan_id": sourceScanId,
    });
    return OutbreakEvent.fromJson(response);
  }

  Future<OutbreakEvent> setValidation(
    int eventId, {
    required String action,
    String? correctedPlague,
  }) async {
    final response = await _client.patchAuth("/api/v1/outbreak-events/$eventId/validate", {
      "action": action,
      if (correctedPlague != null) "corrected_plague": correctedPlague,
    });
    return OutbreakEvent.fromJson(response);
  }
}
