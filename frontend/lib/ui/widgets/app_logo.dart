import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

/// Logo de marca NEXO Agro (assets/branding/app_logo.png).
class AppLogo extends StatelessWidget {
  final double size;
  final double borderRadius;

  const AppLogo({super.key, this.size = 72, this.borderRadius = 14});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: Image.asset(
        "assets/branding/app_logo.png",
        width: size,
        height: size,
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => Icon(
          Icons.eco,
          size: size * 0.7,
          color: NexoColors.bioGreen,
        ),
      ),
    );
  }
}
