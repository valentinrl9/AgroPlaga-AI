import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

class NexoLockScreen extends StatelessWidget {
  final String moduleName;
  final bool isB2C;

  const NexoLockScreen({
    super.key,
    required this.moduleName,
    this.isB2C = true,
  });

  @override
  Widget build(BuildContext context) {
    final message = isB2C
        ? "Desbloquea métricas avanzadas e IA climática predictiva. "
            "Activa el periodo de prueba de 7 días cuando esté disponible."
        : "Este módulo requiere vinculación oficial con tu Cooperativa o SAT adherida "
            "para la gestión unificada de alertas. Solicita el alta a tu perito técnico.";

    return Container(
      color: NexoColors.deepBlue.withValues(alpha: 0.95),
      width: double.infinity,
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.lock_rounded, size: 72, color: NexoColors.warningAmber),
              const SizedBox(height: 20),
              Text(
                moduleName,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  color: NexoColors.pureWhite,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                "Módulo no activo",
                style: TextStyle(fontSize: 15, color: NexoColors.lightText),
              ),
              const SizedBox(height: 20),
              Text(
                message,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 15,
                  height: 1.45,
                  color: NexoColors.pureWhite,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
