import "dart:async";
import "dart:convert";
import "dart:typed_data";

import "package:http/http.dart" as http;

import "../core/auth_redirect.dart";
import "../core/constants.dart";
import "../core/session.dart";

class ApiClient {
  ApiClient._();

  static final ApiClient instance = ApiClient._();

  final http.Client client = http.Client();
  String? _token;

  void setToken(String? token) {
    _token = token;
  }

  String? get token => _token;

  Future<void> ensureAuth() async {
    if (_token != null && _token!.isNotEmpty) return;
    await Session.restore();
  }

  Map<String, String> get _headers {
    final headers = {"Content-Type": "application/json"};
    if (_token != null && _token!.isNotEmpty) {
      headers["Authorization"] = "Bearer $_token";
    }
    return headers;
  }

  Uri _uri(String path) {
    return Uri.parse(ApiConstants.baseUrl + path);
  }

  Future<http.Response> _send(Future<http.Response> Function() request, {bool retryOn401 = true}) async {
    var response = await request();
    if (retryOn401 && response.statusCode == 401 && await Session.tryRefreshToken()) {
      response = await request();
    }
    return response;
  }

  Future<Map<String, dynamic>> get(String path) async {
    await ensureAuth();
    final response = await _send(() => client.get(_uri(path), headers: _headers));
    return _parseResponse(response);
  }

  Future<List<dynamic>> getList(String path) async {
    await ensureAuth();
    final response = await _send(() => client.get(_uri(path), headers: _headers));
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as List<dynamic>;
    }
    _parseResponse(response);
    return [];
  }

  Future<Uint8List> getBytesAuth(String path) async {
    await ensureAuth();
    final headers = <String, String>{};
    if (_token != null && _token!.isNotEmpty) {
      headers["Authorization"] = "Bearer $_token";
    }
    final response = await _send(() => client.get(_uri(path), headers: headers));
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response.bodyBytes;
    }
    _parseResponse(response);
    return Uint8List(0);
  }

  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body, {bool retryOn401 = false}) async {
    final response = await _send(
      () => client.post(_uri(path), headers: _headers, body: jsonEncode(body)),
      retryOn401: retryOn401,
    );
    return _parseResponse(response);
  }

  Future<Map<String, dynamic>> postAuth(String path, Map<String, dynamic> body) async {
    await ensureAuth();
    return post(path, body, retryOn401: true);
  }

  Future<Map<String, dynamic>> putAuth(String path, Map<String, dynamic> body) async {
    await ensureAuth();
    final response = await _send(
      () => client.put(_uri(path), headers: _headers, body: jsonEncode(body)),
    );
    return _parseResponse(response);
  }

  Future<void> deleteAuth(String path) async {
    await ensureAuth();
    final response = await _send(() => client.delete(_uri(path), headers: _headers));
    if (response.statusCode < 200 || response.statusCode >= 300) {
      _parseResponse(response);
    }
  }

  Future<Map<String, dynamic>> patchAuth(String path, Map<String, dynamic> body) async {
    await ensureAuth();
    final response = await _send(
      () => client.patch(_uri(path), headers: _headers, body: jsonEncode(body)),
    );
    return _parseResponse(response);
  }

  Future<Map<String, dynamic>> postMultipartAuth(
    String path,
    Map<String, String> fields,
    String fileField,
    List<int> fileBytes,
    String filename,
  ) async {
    await ensureAuth();

    Future<http.Response> sendOnce() async {
      final request = http.MultipartRequest("POST", _uri(path));
      if (_token != null && _token!.isNotEmpty) {
        request.headers["Authorization"] = "Bearer $_token";
      }
      request.fields.addAll(fields);
      request.files.add(
        http.MultipartFile.fromBytes(
          fileField,
          fileBytes,
          filename: filename,
        ),
      );
      final streamed = await request.send();
      return http.Response.fromStream(streamed);
    }

    var response = await sendOnce();
    if (response.statusCode == 401 && await Session.tryRefreshToken()) {
      response = await sendOnce();
    }
    return _parseResponse(response);
  }

  Map<String, dynamic> _parseResponse(http.Response response) {
    final body = response.body.isEmpty ? "{}" : response.body;
    final decoded = jsonDecode(body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded as Map<String, dynamic>;
    }

    if (response.statusCode == 401) {
      unawaited(AuthRedirect.onUnauthorized());
    }

    final message = decoded is Map<String, dynamic> && decoded.containsKey("detail")
        ? decoded["detail"].toString()
        : response.reasonPhrase ?? "Error desconocido";
    throw Exception("${response.statusCode}: $message");
  }
}
