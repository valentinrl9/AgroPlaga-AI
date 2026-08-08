import "../api_client.dart";

class ClimateRepository {
  final ApiClient _client = ApiClient.instance;

  String _zoneSuffix(int? zoneId) => zoneId != null ? "&zone_id=$zoneId" : "";

  Future<Map<String, dynamic>> fetchAccess() async {
    return await _client.get("/api/v1/climate/access");
  }

  Future<List<dynamic>> fetchStations() async {
    return await _client.getList("/api/v1/climate/stations");
  }

  Future<Map<String, dynamic>> fetchActual({int? zoneId}) async {
    final q = zoneId != null ? "?zone_id=$zoneId" : "";
    return await _client.get("/api/v1/climate/actual$q");
  }

  Future<Map<String, dynamic>> fetchAlertas({int? zoneId}) async {
    final q = zoneId != null ? "?zone_id=$zoneId" : "";
    return await _client.get("/api/v1/climate/alertas$q");
  }

  Future<Map<String, dynamic>> fetchRecomendaciones({int dias = 7, int? zoneId}) async {
    return await _client.get("/api/v1/climate/recomendaciones?dias=$dias${_zoneSuffix(zoneId)}");
  }

  Future<Map<String, dynamic>> fetchEtlStatus() async {
    return await _client.get("/api/v1/climate/etl/status");
  }

  Future<List<dynamic>> fetchPrediccion({int dias = 7, int? zoneId}) async {
    return await _client.getList("/api/v1/climate/prediccion?dias=$dias${_zoneSuffix(zoneId)}");
  }

  Future<Map<String, dynamic>> fetchRiesgo({int dias = 7, int? zoneId}) async {
    return await _client.get("/api/v1/climate/riesgo?dias=$dias${_zoneSuffix(zoneId)}");
  }
}
