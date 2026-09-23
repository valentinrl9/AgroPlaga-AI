import "dart:convert";

import "package:flutter/foundation.dart";
import "package:http/http.dart" as http;

import "app_version.dart";

class AppUpdateOffer {
  final String versionName;
  final String apkUrl;

  const AppUpdateOffer({required this.versionName, required this.apkUrl});
}

class AppUpdate {
  static Future<AppUpdateOffer?> check() async {
    if (kIsWeb) return null;
    try {
      final response = await http
          .get(Uri.parse(appUpdateManifestUrl))
          .timeout(const Duration(seconds: 6));
      if (response.statusCode < 200 || response.statusCode >= 300) return null;
      final data = jsonDecode(response.body);
      if (data is! Map<String, dynamic>) return null;
      final code = data["version_code"];
      final url = data["apk_url"];
      if (code is! int || url is! String || url.isEmpty) return null;
      if (code <= appVersionCode) return null;
      final name = data["version_name"];
      return AppUpdateOffer(
        versionName: name is String && name.isNotEmpty ? name : "$code",
        apkUrl: url,
      );
    } catch (_) {
      return null;
    }
  }
}
