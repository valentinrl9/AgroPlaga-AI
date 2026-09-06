import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

/// Línea breve bajo consejos al agricultor: «Según información oficial de …».
class OfficialAttributionLine extends StatelessWidget {
  final String text;

  const OfficialAttributionLine({
    super.key,
    required this.text,
  });

  static const mapaRegistry =
      "Según información oficial del Ministerio de Agricultura (Registro de Productos Fitosanitarios MAPA).";

  @override
  Widget build(BuildContext context) {
    final trimmed = text.trim();
    if (trimmed.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.verified_outlined, size: 14, color: NexoColors.textSecondary),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              trimmed,
              style: const TextStyle(
                fontSize: 12,
                fontStyle: FontStyle.italic,
                color: NexoColors.textSecondary,
                height: 1.35,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
