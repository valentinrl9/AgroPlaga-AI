import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

/// Logotipo tipográfico AgroPlaga.
class NexoWordmark extends StatelessWidget {
  final double fontSize;
  final bool onDark;

  const NexoWordmark({
    super.key,
    this.fontSize = 28,
    this.onDark = false,
  });

  @override
  Widget build(BuildContext context) {
    final brandColor = onDark ? NexoColors.pureWhite : NexoColors.textPrimary;

    return RichText(
      text: TextSpan(
        style: TextStyle(fontSize: fontSize, height: 1.1),
        children: [
          TextSpan(
            text: "Agro",
            style: TextStyle(
              fontWeight: FontWeight.w900,
              color: brandColor,
              letterSpacing: -0.5,
            ),
          ),
          const TextSpan(
            text: "Plaga",
            style: TextStyle(
              fontWeight: FontWeight.w300,
              color: NexoColors.bioGreen,
            ),
          ),
        ],
      ),
    );
  }
}
