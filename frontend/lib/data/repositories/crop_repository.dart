import "../api_client.dart";
import "../../models/crop.dart";

class CropRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<CropCatalogEntry>> search({String? query, int limit = 20}) async {
    final path = query == null || query.trim().isEmpty
        ? "/api/v1/crops?limit=$limit"
        : "/api/v1/crops?q=${Uri.encodeQueryComponent(query.trim())}&limit=$limit";
    final list = await _client.getList(path);
    return list
        .map((item) => CropCatalogEntry.fromJson(Map<String, dynamic>.from(item as Map)))
        .toList();
  }
}
