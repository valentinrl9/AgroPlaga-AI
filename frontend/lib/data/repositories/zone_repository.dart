import "../api_client.dart";
import "../../models/zone.dart";

class ZoneRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<AgriZone>> fetchZones() async {
    final result = await _client.getList("/api/v1/zones");
    return result
        .map((item) => AgriZone.fromJson(Map<String, dynamic>.from(item as Map)))
        .toList();
  }
}
