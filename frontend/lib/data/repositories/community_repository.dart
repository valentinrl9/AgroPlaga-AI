import "../api_client.dart";
import "../../models/community.dart";

class CommunityRepository {
  final ApiClient _client = ApiClient.instance;

  Future<CommunityProfile> fetchProfile() async {
    final json = await _client.get("/api/v1/community/profile");
    return CommunityProfile.fromJson(json);
  }
}
