import "package:flutter_secure_storage/flutter_secure_storage.dart";

/// Almacenamiento seguro de tokens (Keychain / Keystore / cifrado web).
class SecureTokenStorage {
  SecureTokenStorage._();

  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  static Future<void> writeAccessToken(String token) async {
    await _storage.write(key: "auth_token", value: token);
  }

  static Future<void> writeRefreshToken(String? token) async {
    if (token == null || token.isEmpty) {
      await _storage.delete(key: "refresh_token");
      return;
    }
    await _storage.write(key: "refresh_token", value: token);
  }

  static Future<String?> readAccessToken() => _storage.read(key: "auth_token");

  static Future<String?> readRefreshToken() => _storage.read(key: "refresh_token");

  static Future<void> clear() async {
    await _storage.delete(key: "auth_token");
    await _storage.delete(key: "refresh_token");
  }
}
