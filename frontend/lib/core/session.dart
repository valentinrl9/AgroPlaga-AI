import "package:shared_preferences/shared_preferences.dart";

import "../data/api_client.dart";

class Session {
  static const String tokenKey = "auth_token";
  static const String refreshTokenKey = "refresh_token";
  static const String roleKey = "user_role";
  static const String nameKey = "user_name";
  static const String fieldPremiumKey = "has_field_premium";
  static const String climateModuleKey = "has_climate_module";
  static const String siexModuleKey = "has_siex_module";
  static const String siexEnterpriseKey = "has_siex_enterprise";
  static const String contributedScansKey = "contributed_scan_ids";

  static Future<bool> restore() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(tokenKey);
    if (token != null && token.isNotEmpty) {
      ApiClient.instance.setToken(token);
      return true;
    }
    ApiClient.instance.setToken(null);
    return false;
  }

  static Future<void> saveTokens({required String accessToken, String? refreshToken}) async {
    ApiClient.instance.setToken(accessToken);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(tokenKey, accessToken);
    if (refreshToken != null && refreshToken.isNotEmpty) {
      await prefs.setString(refreshTokenKey, refreshToken);
    }
  }

  static Future<void> saveToken(String token) async {
    await saveTokens(accessToken: token);
  }

  static Future<String?> get refreshToken async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(refreshTokenKey);
  }

  static Future<bool> tryRefreshToken() async {
    final refresh = await refreshToken;
    if (refresh == null || refresh.isEmpty) return false;
    try {
      final response = await ApiClient.instance.post(
        "/api/v1/auth/refresh",
        {"refresh_token": refresh},
      );
      final access = response["access_token"] as String?;
      final nextRefresh = response["refresh_token"] as String?;
      if (access == null || access.isEmpty) return false;
      await saveTokens(accessToken: access, refreshToken: nextRefresh ?? refresh);
      return true;
    } catch (_) {
      return false;
    }
  }

  static Future<void> saveUserInfo({
    required String role,
    required String name,
    bool hasFieldPremium = false,
    bool hasClimateModule = false,
    bool hasSiexModule = false,
    bool hasSiexEnterprise = false,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(roleKey, role);
    await prefs.setString(nameKey, name);
    await prefs.setBool(fieldPremiumKey, hasFieldPremium);
    await prefs.setBool(climateModuleKey, hasClimateModule);
    await prefs.setBool(siexModuleKey, hasSiexModule);
    await prefs.setBool(siexEnterpriseKey, hasSiexEnterprise);
  }

  static Future<String?> get role async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(roleKey);
  }

  static Future<String?> get name async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(nameKey);
  }

  static Future<bool> hasContributed(int scanId) async {
    final ids = await contributedScanIds;
    return ids.contains(scanId);
  }

  static Future<Set<int>> get contributedScanIds async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(contributedScansKey) ?? [];
    return raw.map(int.parse).toSet();
  }

  static Future<void> markContributed(int scanId) async {
    final prefs = await SharedPreferences.getInstance();
    final list = prefs.getStringList(contributedScansKey) ?? [];
    final id = scanId.toString();
    if (!list.contains(id)) {
      list.add(id);
      await prefs.setStringList(contributedScansKey, list);
    }
  }

  static Future<bool> get hasFieldPremium async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(fieldPremiumKey) ?? false;
  }

  static Future<bool> get hasClimateModule async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(climateModuleKey) ?? false;
  }

  static Future<bool> get hasSiexModule async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(siexModuleKey) ?? false;
  }

  static Future<bool> get hasSiexEnterprise async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(siexEnterpriseKey) ?? false;
  }

  static Future<bool> get hasSiexAccess async {
    if (await hasSiexModule || await hasSiexEnterprise) return true;
    return await isTechOrAdmin;
  }

  static Future<bool> get isTechOrAdmin async {
    final r = await role;
    return r == "tech" || r == "admin";
  }

  static Future<void> clear() async {
    ApiClient.instance.setToken(null);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(tokenKey);
    await prefs.remove(refreshTokenKey);
    await prefs.remove(roleKey);
    await prefs.remove(nameKey);
    await prefs.remove(fieldPremiumKey);
    await prefs.remove(climateModuleKey);
    await prefs.remove(siexModuleKey);
    await prefs.remove(siexEnterpriseKey);
  }

  static Future<bool> hasToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey(tokenKey);
  }
}
