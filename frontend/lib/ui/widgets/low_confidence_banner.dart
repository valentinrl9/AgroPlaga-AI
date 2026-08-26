import "package:flutter/material.dart";

import "../../core/constants.dart";
import "../../core/nexo_colors.dart";

class LowConfidenceBanner extends StatelessWidget {
  final double confidence;

  const LowConfidenceBanner({super.key, required this.confidence});

  bool get isLow => confidence < ScanUiConstants.lowConfidenceThreshold;

  @override
  Widget build(BuildContext context) {
    if (!isLow) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: NexoColors.warningAmber.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: NexoColors.warningAmber.withValues(alpha: 0.55)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.info_outline, color: NexoColors.warningAmber, size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Confianza baja",
                  style: TextStyle(fontWeight: FontWeight.w700, color: NexoColors.warningAmber),
                ),
                const SizedBox(height: 4),
                Text(
                  "La IA no está segura (${(confidence * 100).toStringAsFixed(0)}%). "
                  "Confirma tú la plaga antes de guardar o tratar.",
                  style: const TextStyle(fontSize: 13, height: 1.35, color: NexoColors.textPrimary),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Resalta el bloque de selección de plaga cuando la confianza es baja.
class PlagueSelectionHighlight extends StatelessWidget {
  final double confidence;
  final Widget child;

  const PlagueSelectionHighlight({
    super.key,
    required this.confidence,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final highlight = confidence < ScanUiConstants.lowConfidenceThreshold;
    if (!highlight) return child;

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: NexoColors.warningAmber.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: NexoColors.warningAmber.withValues(alpha: 0.45)),
      ),
      child: child,
    );
  }
}
