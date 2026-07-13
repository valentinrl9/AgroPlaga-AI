import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../models/scan.dart";

class ScanValidationBanner extends StatelessWidget {
  final Scan scan;

  const ScanValidationBanner({super.key, required this.scan});

  @override
  Widget build(BuildContext context) {
    if (scan.isRejectedByTech) {
      return _box(
        color: NexoColors.errorRed,
        icon: Icons.block,
        title: "Escaneo rechazado por el perito",
        body: scan.techNotes?.isNotEmpty == true
            ? scan.techNotes!
            : "No registres un tratamiento vinculado a este escaneo. Repite el escaneo o consulta con tu técnico.",
      );
    }
    if (scan.isVerifiedByTech) {
      final plague = scan.effectivePlague;
      return _box(
        color: NexoColors.bioGreen,
        icon: Icons.verified_outlined,
        title: "Plaga validada por perito",
        body: scan.correctedPlague != null && scan.correctedPlague != scan.plague
            ? "IA: ${scan.plague} → Perito: $plague"
            : "Diagnóstico confirmado: $plague",
      );
    }
    return _box(
      color: NexoColors.warningAmber,
      icon: Icons.warning_amber_outlined,
      title: "Plaga no verificada por perito",
      body: scan.shareWithTech
          ? "Pendiente de revisión del perito. Puedes registrar tratamiento bajo tu responsabilidad o esperar la validación."
          : "Solo IA de campo. Comparte la foto con tu perito o acepta responsabilidad al registrar un tratamiento.",
    );
  }

  Widget _box({
    required Color color,
    required IconData icon,
    required String title,
    required String body,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.45)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(fontWeight: FontWeight.w700, color: color)),
                const SizedBox(height: 4),
                Text(body, style: const TextStyle(fontSize: 13, height: 1.35)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
