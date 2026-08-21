import "package:flutter/material.dart";

import "../../core/user_friendly_error.dart";

/// Utilidades compartidas para UX móvil (scroll, teclado, errores).
class MobileLayout {
  MobileLayout._();
  static EdgeInsets scrollPadding(
    BuildContext context, {
    double base = 16,
    double extraBottom = 16,
  }) {
    final viewInsets = MediaQuery.viewInsetsOf(context);
    return EdgeInsets.fromLTRB(
      base,
      base,
      base,
      base + extraBottom + viewInsets.bottom,
    );
  }

  static Widget dismissKeyboardOnTap({
    required BuildContext context,
    required Widget child,
  }) {
    return GestureDetector(
      onTap: () => FocusManager.instance.primaryFocus?.unfocus(),
      behavior: HitTestBehavior.translucent,
      child: child,
    );
  }

  static Widget errorState({
    required Object error,
    required VoidCallback onRetry,
    IconData icon = Icons.cloud_off_outlined,
  }) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 48, color: Colors.grey),
            const SizedBox(height: 12),
            Text(
              UserFriendlyError.from(error),
              textAlign: TextAlign.center,
              style: const TextStyle(height: 1.4),
            ),
            const SizedBox(height: 16),
            OutlinedButton(onPressed: onRetry, child: const Text("Reintentar")),
          ],
        ),
      ),
    );
  }
}
