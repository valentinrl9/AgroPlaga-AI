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
    String? nave,
    String? sector,
    String? cropStage,
    String? cropVariant,
    double? surfaceM2,
    String? sigpacCode,
  }) async {
    final json = await _client.postAuth("/api/v1/farms", {
      "name": name,
      "crop": crop,
      "farm_type": farmType,
      if (zoneId != null) "zone_id": zoneId,
      if (nave != null && nave.trim().isNotEmpty) "nave": nave.trim(),
      if (sector != null && sector.trim().isNotEmpty) "sector": sector.trim(),
      if (cropStage != null && cropStage.trim().isNotEmpty) "crop_stage": cropStage.trim(),
      if (cropVariant != null && cropVariant.trim().isNotEmpty) "crop_variant": cropVariant.trim(),
      if (surfaceM2 != null) "surface_m2": surfaceM2,
      if (sigpacCode != null && sigpacCode.trim().isNotEmpty) "sigpac_code": sigpacCode.trim(),
    });
    return Farm.fromJson(json);
  }

  Future<Farm> updateFarm(
    int id, {
    String? name,
    String? crop,
    int? zoneId,
    String? nave,
    String? sector,
    String? cropStage,
    String? cropVariant,
    String? sigpacCode,
    double? surfaceM2,
    int? climateStationId,
    bool clearClimateStation = false,
  }) async {
    final json = await _client.patchAuth("/api/v1/farms/$id", {
      if (name != null) "name": name,
      if (crop != null) "crop": crop,
      if (zoneId != null) "zone_id": zoneId,
      if (nave != null) "nave": nave,
      if (sector != null) "sector": sector,
      if (cropStage != null) "crop_stage": cropStage,
      if (cropVariant != null) "crop_variant": cropVariant,
      if (sigpacCode != null) "sigpac_code": sigpacCode,
      if (surfaceM2 != null) "surface_m2": surfaceM2,
      if (clearClimateStation) "climate_station_id": null,
      if (!clearClimateStation && climateStationId != null) "climate_station_id": climateStationId,
    });
    return Farm.fromJson(json);
  }

  Future<void> deleteFarm(int id) async {
    await _client.deleteAuth("/api/v1/farms/$id");
  }
}
