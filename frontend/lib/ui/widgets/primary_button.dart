import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;

  const PrimaryButton({super.key, required this.label, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final enabled = onPressed != null;

    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(12),
        child: Ink(
          decoration: BoxDecoration(
            gradient: enabled ? NexoColors.primaryGradient : null,
            color: enabled ? null : NexoColors.bioGreenDisabled,
            borderRadius: BorderRadius.circular(12),
            boxShadow: enabled
                ? [
                    BoxShadow(
                      color: NexoColors.bioGreen.withValues(alpha: 0.35),
                      blurRadius: 18,
                      offset: const Offset(0, 6),
                    ),
                  ]
                : null,
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
            child: Center(
              child: Text(
                label,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: NexoColors.pureWhite,
                  letterSpacing: 0.2,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
