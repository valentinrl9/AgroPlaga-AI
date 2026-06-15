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
  }) async {
    final json = await _client.postAuth("/api/v1/farms", {
      "name": name,
      "crop": crop,
      "farm_type": farmType,
      if (zoneId != null) "zone_id": zoneId,
    });
    return Farm.fromJson(json);
  }

  Future<void> deleteFarm(int id) async {
    await _client.deleteAuth("/api/v1/farms/$id");
  }
}
