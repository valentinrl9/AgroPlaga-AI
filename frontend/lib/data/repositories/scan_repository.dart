import "../api_client.dart";
import "../../models/scan.dart";

class ScanRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<Scan>> fetchScans() async {
    final result = await _client.getList("/api/v1/scans");
    return result.map((item) => Scan.fromJson(Map<String, dynamic>.from(item as Map))).toList();
  }

  Future<Scan> createScan({
    required String crop,
    required String plague,
    required String severity,
    double confidence = 0.0,
    String? location,
    int? farmId,
  }) async {
    final response = await _client.postAuth("/api/v1/scans", {
      "crop": crop,
      "plague": plague,
      "severity": severity,
      "confidence": confidence,
      if (location != null) "location": location,
      if (farmId != null) "farm_id": farmId,
    });

    return Scan.fromJson(response);
  }
}
