import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

/// Logotipo tipográfico NEXO Agro (NEXO_CONTEXT.md §2.3).
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
    final nexoColor = onDark ? NexoColors.pureWhite : NexoColors.textPrimary;

    return RichText(
      text: TextSpan(
        style: TextStyle(fontSize: fontSize, height: 1.1),
        children: [
          TextSpan(
            text: "NEXO",
            style: TextStyle(
              fontWeight: FontWeight.w900,
              color: nexoColor,
              letterSpacing: -0.5,
            ),
          ),
          const TextSpan(
            text: "Agro",
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
