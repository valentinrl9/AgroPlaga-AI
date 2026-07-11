import "../api_client.dart";

class ClimateRepository {
  final ApiClient _client = ApiClient.instance;

  Future<Map<String, dynamic>> fetchAccess() async {
    return await _client.get("/api/v1/climate/access");
  }

  Future<Map<String, dynamic>> fetchActual() async {
    return await _client.get("/api/v1/climate/actual");
  }

  Future<Map<String, dynamic>> fetchAlertas() async {
    return await _client.get("/api/v1/climate/alertas");
  }

  Future<Map<String, dynamic>> fetchRecomendaciones({int dias = 7}) async {
    return await _client.get("/api/v1/climate/recomendaciones?dias=$dias");
  }

  Future<Map<String, dynamic>> fetchEtlStatus() async {
    return await _client.get("/api/v1/climate/etl/status");
  }

  Future<List<dynamic>> fetchPrediccion({int dias = 7}) async {
    return await _client.getList("/api/v1/climate/prediccion?dias=$dias");
  }
}
