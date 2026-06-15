import "dart:async";

import "package:flutter/material.dart";

import "routes.dart";
import "session.dart";

class AuthRedirect {
  AuthRedirect._();

  static final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  static bool isUnauthorized(Object error) => error.toString().contains("401");

  static Future<void> onUnauthorized() async {
    await Session.clear();
    navigatorKey.currentState?.pushNamedAndRemoveUntil(Routes.login, (_) => false);
  }

  static void redirectIfUnauthorized(BuildContext context, Object error) {
    if (!isUnauthorized(error)) return;
    unawaited(onUnauthorized());
  }
}
