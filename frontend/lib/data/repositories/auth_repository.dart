import "../api_client.dart";
import "../../core/session.dart";
import "../../models/user_profile.dart";
import "user_repository.dart";

class AuthRepository {
  final ApiClient _client = ApiClient.instance;
  final _users = UserRepository();

  static Future<bool> restoreSession() => Session.restore();

  Future<void> _storeProfile() async {
    try {
      final profile = await _users.fetchProfile();
      await Session.saveUserInfo(role: profile.role, name: profile.name);
    } catch (_) {}
  }

  Future<bool> login(String email, String password) async {
    if (email.isEmpty || password.isEmpty) {
      return false;
    }

    final response = await _client.post(
      "/api/v1/auth/login",
      {"email": email, "password": password},
    );

    final token = response["access_token"] as String?;
    final refresh = response["refresh_token"] as String?;
    if (token == null || token.isEmpty) {
      return false;
    }

    await Session.saveTokens(accessToken: token, refreshToken: refresh);
    await _storeProfile();
    return true;
  }

  Future<bool> register(String name, String email, String password, {String? inviteCode}) async {
    if (name.isEmpty || email.isEmpty || password.isEmpty) {
      return false;
    }

    final body = <String, dynamic>{
      "name": name,
      "email": email,
      "password": password,
    };
    if (inviteCode != null && inviteCode.trim().isNotEmpty) {
      body["invite_code"] = inviteCode.trim();
    }

    final response = await _client.post(
      "/api/v1/auth/register",
      body,
    );

    final token = response["access_token"] as String?;
    final refresh = response["refresh_token"] as String?;
    if (token == null || token.isEmpty) {
      return false;
    }

    await Session.saveTokens(accessToken: token, refreshToken: refresh);
    await _storeProfile();
    return true;
  }

  Future<UserProfile?> currentProfile() => _users.fetchProfile();

  Future<void> logout() async {
    await Session.clear();
  }

  Future<bool> hasStoredSession() => Session.hasToken();
}
