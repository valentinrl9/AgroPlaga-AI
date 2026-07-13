import "../api_client.dart";

class TreatmentRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<dynamic>> fetchBiocides({required String plague, required String crop}) async {
    final p = Uri.encodeQueryComponent(plague);
    final c = Uri.encodeQueryComponent(crop);
    return await _client.getList("/api/v1/treatments/biocides?plague=$p&crop=$c");
  }

  Future<Map<String, dynamic>> calculateDose({
    required double surfaceM2,
    required String registryNo,
    String? plague,
    String? crop,
  }) async {
    return await _client.postAuth("/api/v1/treatments/dose/calculate", {
      "surface_m2": surfaceM2,
      "registry_no": registryNo,
      if (plague != null) "plague": plague,
      if (crop != null) "crop": crop,
    });
  }

  Future<Map<String, dynamic>> createTreatment(Map<String, dynamic> body) async {
    return await _client.postAuth("/api/v1/treatments", body);
  }

  Future<List<dynamic>> fetchActive({int? farmId}) async {
    final q = farmId != null ? "?farm_id=$farmId" : "";
    return await _client.getList("/api/v1/treatments/active$q");
  }
}
