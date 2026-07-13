import "dart:typed_data";

import "../api_client.dart";

class TechDashboardRepository {
  final ApiClient _client = ApiClient.instance;

  Future<Map<String, dynamic>> fetchDashboard({int hours = 168}) async {
    return await _client.get("/api/v1/tech/dashboard?hours=$hours");
  }

  Future<List<dynamic>> fetchPendingScans() async {
    return await _client.getList("/api/v1/tech/pending-scans");
  }

  Future<List<dynamic>> fetchFarmers() async {
    return await _client.getList("/api/v1/tech/farmers");
  }
}

class TechScanRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<dynamic>> fetchPending() async {
    return await _client.getList("/api/v1/tech/pending-scans");
  }

  Future<Uint8List> fetchImage(int scanId) async {
    return await _client.getBytesAuth("/api/v1/scans/$scanId/image");
  }

  Future<void> validate({
    required int scanId,
    required String action,
    String? correctedPlague,
    String? techNotes,
  }) async {
    await _client.patchAuth("/api/v1/scans/$scanId/validate", {
      "action": action,
      if (correctedPlague != null) "corrected_plague": correctedPlague,
      if (techNotes != null) "tech_notes": techNotes,
    });
  }
}
