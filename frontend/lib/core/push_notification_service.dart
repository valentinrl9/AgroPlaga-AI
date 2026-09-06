import "dart:async";

import "package:firebase_core/firebase_core.dart";
import "package:firebase_messaging/firebase_messaging.dart";
import "package:flutter/foundation.dart";
import "package:flutter_local_notifications/flutter_local_notifications.dart";

import "../core/auth_redirect.dart";
import "../core/routes.dart";
import "../core/session.dart";
import "../data/repositories/activity_repository.dart";
import "../data/repositories/scan_repository.dart";
import "../ui/screens/result_screen_args.dart";

@pragma("vm:entry-point")
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  if (Firebase.apps.isEmpty) {
    await Firebase.initializeApp();
  }
}

class PushNotificationService {
  PushNotificationService._();

  static final PushNotificationService instance = PushNotificationService._();

  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  final ActivityRepository _activityRepo = ActivityRepository();
  bool _initialized = false;
  Future<void>? _initFuture;

  static const _androidChannel = AndroidNotificationChannel(
    "agroplaga_alerts",
    "Alertas AgroPlaga",
    description: "Validaciones, incidencias y avisos del piloto",
    importance: Importance.high,
  );

  bool get _firebaseReady => Firebase.apps.isNotEmpty;

  FirebaseMessaging get _messaging {
    if (!_firebaseReady) {
      throw StateError("Firebase no inicializado");
    }
    return FirebaseMessaging.instance;
  }

  Future<void> initialize() async {
    _initFuture ??= _initializeImpl();
    await _initFuture;
  }

  Future<void> _initializeImpl() async {
    if (_initialized) return;

    try {
      if (Firebase.apps.isEmpty) {
        await Firebase.initializeApp();
      }
    } catch (error) {
      debugPrint("FCM: Firebase no configurado ($error)");
      return;
    }

    if (!_firebaseReady) return;

    try {
      FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

      const androidInit = AndroidInitializationSettings("@mipmap/ic_launcher");
      await _localNotifications.initialize(
        const InitializationSettings(android: androidInit),
        onDidReceiveNotificationResponse: (response) {
          final payload = response.payload;
          if (payload != null && payload.isNotEmpty) {
            unawaited(_handlePayload(_payloadToMap(payload)));
          }
        },
      );

      final androidPlugin = _localNotifications
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
      await androidPlugin?.createNotificationChannel(_androidChannel);

      FirebaseMessaging.onMessage.listen(_onForegroundMessage);
      FirebaseMessaging.onMessageOpenedApp.listen((message) {
        unawaited(_handlePayload(_stringifyData(message.data)));
      });

      final initial = await _messaging.getInitialMessage();
      if (initial != null) {
        unawaited(_handlePayload(_stringifyData(initial.data)));
      }

      _messaging.onTokenRefresh.listen((token) {
        unawaited(_registerToken(token));
      });

      _initialized = true;
    } catch (error, stack) {
      debugPrint("FCM: init parcial fallida ($error)\n$stack");
    }
  }

  Future<void> ensurePermissionsAndToken() async {
    try {
      await initialize();
      if (!_initialized || !_firebaseReady) return;

      final androidPlugin = _localNotifications
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
      await androidPlugin?.requestNotificationsPermission();
      await _messaging.requestPermission(alert: true, badge: true, sound: true);
      await syncTokenWithBackend();
    } catch (error) {
      debugPrint("FCM: permisos/token ($error)");
    }
  }

  Future<void> syncTokenWithBackend() async {
    try {
      if (!_initialized || !_firebaseReady) return;
      if (!await Session.hasToken()) return;

      final token = await _messaging.getToken();
      if (token == null || token.isEmpty) return;
      await _registerToken(token);
    } catch (error) {
      debugPrint("FCM: no se pudo registrar token ($error)");
    }
  }

  Future<void> _registerToken(String token) async {
    if (!await Session.hasToken()) return;
    try {
      await _activityRepo.registerDeviceToken(token);
    } catch (error) {
      debugPrint("FCM: error enviando token al backend ($error)");
    }
  }

  Future<void> _onForegroundMessage(RemoteMessage message) async {
    final notification = message.notification;
    if (notification == null) return;

    final payload = _mapToPayload(_stringifyData(message.data));
    await _localNotifications.show(
      notification.hashCode,
      notification.title,
      notification.body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          _androidChannel.id,
          _androidChannel.name,
          channelDescription: _androidChannel.description,
          importance: Importance.high,
          priority: Priority.high,
        ),
      ),
      payload: payload,
    );
  }

  Future<void> _handlePayload(Map<String, String> data) async {
    if (data.isEmpty) return;

    final nav = AuthRedirect.navigatorKey.currentState;
    if (nav == null) return;

    if (!await Session.hasToken()) {
      nav.pushNamedAndRemoveUntil(Routes.login, (_) => false);
      return;
    }

    if (data["type"] == "grouped") {
      nav.pushNamed(Routes.home);
      return;
    }

    final section = data["section"] ?? "";
    final referenceType = data["reference_type"];
    final referenceIdRaw = data["reference_id"];

    if (referenceType == "scan" && referenceIdRaw != null) {
      final scanId = int.tryParse(referenceIdRaw);
      if (scanId != null) {
        try {
          final scan = await ScanRepository().fetchScan(scanId);
          nav.pushNamed(Routes.result, arguments: ResultScreenArgs(scan: scan));
          return;
        } catch (_) {
          nav.pushNamed(Routes.history);
          return;
        }
      }
    }

    switch (section) {
      case "incidents":
        nav.pushNamed(Routes.incidents);
        break;
      case "community":
        nav.pushNamed(Routes.community);
        break;
      case "alerts":
        nav.pushNamed(Routes.alerts);
        break;
      case "tech":
        nav.pushNamed(Routes.techValidation);
        break;
      case "history":
        nav.pushNamed(Routes.history);
        break;
      default:
        nav.pushNamed(Routes.home);
    }
  }

  String _mapToPayload(Map<String, String> data) {
    return data.entries.map((e) => "${e.key}=${e.value}").join("&");
  }

  Map<String, String> _stringifyData(Map<String, dynamic> data) {
    return data.map((key, value) => MapEntry(key, value?.toString() ?? ""));
  }

  Map<String, String> _payloadToMap(String payload) {
    final out = <String, String>{};
    for (final part in payload.split("&")) {
      final idx = part.indexOf("=");
      if (idx <= 0) continue;
      out[part.substring(0, idx)] = part.substring(idx + 1);
    }
    return out;
  }
}
