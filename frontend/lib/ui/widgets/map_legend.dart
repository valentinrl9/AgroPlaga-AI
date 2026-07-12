import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

class MapLegend extends StatelessWidget {
  const MapLegend({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Leyenda",
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: NexoColors.textSecondary,
              ),
            ),
            const SizedBox(height: 8),
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _LegendItem(color: NexoColors.severityLow, label: "Leve"),
                _LegendItem(color: NexoColors.severityModerate, label: "Moderado"),
                _LegendItem(color: NexoColors.severityHigh, label: "Alto"),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Container(
                  width: 48,
                  height: 10,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(4),
                    gradient: LinearGradient(
                      colors: [
                        NexoColors.warningAmber.withValues(alpha: 0.5),
                        NexoColors.errorRed.withValues(alpha: 0.85),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    "Calor: ámbar → rojo según intensidad",
                    style: TextStyle(fontSize: 11, color: NexoColors.textSecondary),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Row(
              children: [
                _ValidationBadgeSample(
                  label: "?",
                  fill: NexoColors.warningAmber,
                  border: Color(0xFFEF6C00),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    "Ámbar = aviso IA sin validar por perito",
                    style: TextStyle(fontSize: 11, color: NexoColors.textSecondary),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            const Row(
              children: [
                _ValidationBadgeSample(
                  label: "✓",
                  fill: NexoColors.errorRed,
                  border: NexoColors.bioGreen,
                ),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    "Borde verde = validado por perito (plaga confirmada o corregida)",
                    style: TextStyle(fontSize: 11, color: NexoColors.textSecondary),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ValidationBadgeSample extends StatelessWidget {
  final String label;
  final Color fill;
  final Color border;

  const _ValidationBadgeSample({
    required this.label,
    required this.fill,
    required this.border,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 28,
      height: 28,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: fill,
        shape: BoxShape.circle,
        border: Border.all(color: border, width: 2),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: label == "?" ? NexoColors.deepBlue : NexoColors.pureWhite,
          fontWeight: FontWeight.bold,
          fontSize: 11,
        ),
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 12, color: NexoColors.textPrimary)),
      ],
    );
  }
}
