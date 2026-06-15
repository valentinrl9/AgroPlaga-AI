import "../api_client.dart";
import "../../models/analytics.dart";

class AnalyticsRepository {
  final ApiClient _client = ApiClient.instance;

  Future<PersonalAnalytics> fetchMyAnalytics({int days = 90}) async {
    final json = await _client.get("/api/v1/analytics/me?days=$days");
    return PersonalAnalytics.fromJson(json);
  }

  Future<PlagaRecommendation> fetchRecommendation({
    required String plague,
    required String crop,
    required String severity,
  }) async {
    final params = {
      "plague": plague,
      "crop": crop,
      "severity": severity,
    };
    final query = params.entries.map((e) => "${e.key}=${Uri.encodeComponent(e.value)}").join("&");
    final json = await _client.get("/api/v1/analytics/recommendations?$query");
    return PlagaRecommendation.fromJson(json);
  }
}
