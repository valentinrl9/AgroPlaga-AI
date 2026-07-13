import "../api_client.dart";
import "../../models/farm.dart";

class FarmRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<Farm>> fetchFarms() async {
    final list = await _client.getList("/api/v1/farms");
    return list.map((e) => Farm.fromJson(Map<String, dynamic>.from(e as Map))).toList();
  }

  Future<Farm> createFarm({
    required String name,
    required String crop,
    required String farmType,
    int? zoneId,
    double? surfaceM2,
    String? sigpacCode,
  }) async {
    final json = await _client.postAuth("/api/v1/farms", {
      "name": name,
      "crop": crop,
      "farm_type": farmType,
      if (zoneId != null) "zone_id": zoneId,
      if (surfaceM2 != null) "surface_m2": surfaceM2,
      if (sigpacCode != null && sigpacCode.trim().isNotEmpty) "sigpac_code": sigpacCode.trim(),
    });
    return Farm.fromJson(json);
  }

  Future<Farm> updateFarm(int id, {String? sigpacCode, double? surfaceM2}) async {
    final json = await _client.patchAuth("/api/v1/farms/$id", {
      if (sigpacCode != null) "sigpac_code": sigpacCode,
      if (surfaceM2 != null) "surface_m2": surfaceM2,
    });
    return Farm.fromJson(json);
  }

  Future<void> deleteFarm(int id) async {
    await _client.deleteAuth("/api/v1/farms/$id");
  }
}
