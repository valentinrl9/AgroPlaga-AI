import "../api_client.dart";
import "../../models/user_profile.dart";

class UserRepository {
  final ApiClient _client = ApiClient.instance;

  Future<UserProfile> fetchProfile() async {
    final json = await _client.get("/api/v1/users/me");
    return UserProfile.fromJson(json);
  }
}
