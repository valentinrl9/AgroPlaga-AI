import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";

/// Aviso: SIGPAC del recinto lo indica el agricultor; necesario para cuaderno SIEX.
class SigpacSiexBanner extends StatelessWidget {
  final String? message;
  final bool compact;
  final bool showAction;

  const SigpacSiexBanner({
    super.key,
    this.message,
    this.compact = false,
    this.showAction = true,
  });

  static const defaultMessage =
      "El cuaderno SIEX necesita el código SIGPAC del recinto invernadero. "
      "Indícalo manualmente en «Mis fincas» (consulta el visor SIGPAC del MAPA). "
      "Diagnóstico, incidencias y tratamientos funcionan sin él.";

  void _openFarms(BuildContext context) {
    Navigator.pushNamed(context, Routes.farms);
  }

  @override
  Widget build(BuildContext context) {
    final text = message ?? defaultMessage;
    return Card(
      margin: EdgeInsets.zero,
      color: NexoColors.techCyan.withValues(alpha: 0.08),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.map_outlined,
              color: NexoColors.techCyan,
              size: compact ? 20 : 22,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (!compact)
                    const Text(
                      "SIGPAC para cuaderno SIEX",
                      style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                    ),
                  if (!compact) const SizedBox(height: 4),
                  Text(
                    text,
                    style: TextStyle(
                      fontSize: compact ? 12 : 13,
                      color: NexoColors.textSecondary,
                      height: 1.35,
                    ),
                  ),
                  if (showAction && !compact) ...[
                    const SizedBox(height: 4),
                    Align(
                      alignment: Alignment.centerLeft,
                      child: TextButton(
                        onPressed: () => _openFarms(context),
                        child: const Text("Ir a Mis fincas"),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
