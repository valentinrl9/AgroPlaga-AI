import "package:flutter/material.dart";

/// Logo de marca AgroPlaga AI (assets/branding/app_logo.png).
class AppLogo extends StatelessWidget {
  const AppLogo({super.key, this.size = 96, this.borderRadius = 16});

  final double size;
  final double borderRadius;

  static const _assetPath = "assets/branding/app_logo.png";

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: Image.asset(
        _assetPath,
        width: size,
        height: size,
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => Icon(Icons.eco, size: size * 0.7, color: const Color(0xFF2E7D32)),
      ),
    );
  }
}
