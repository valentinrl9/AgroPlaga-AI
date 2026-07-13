import "../api_client.dart";

class SiexRepository {
  final ApiClient _client = ApiClient.instance;

  Future<bool> hasAccess() async {
    final data = await _client.get("/api/v1/siex/access");
    return data["has_access"] as bool? ?? false;
  }

  Future<List<dynamic>> fetchEntries() async {
    return await _client.getList("/api/v1/siex/entries");
  }
}
