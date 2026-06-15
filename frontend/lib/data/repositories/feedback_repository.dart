import "../api_client.dart";

class FeedbackRepository {
  final ApiClient _client = ApiClient.instance;

  Future<void> submit({
    required int scanId,
    required bool isCorrect,
    String? correctedPlague,
    String? comment,
  }) async {
    await _client.postAuth("/api/v1/feedback", {
      "scan_id": scanId,
      "is_correct": isCorrect,
      if (correctedPlague != null) "corrected_plague": correctedPlague,
      if (comment != null) "comment": comment,
    });
  }
}
