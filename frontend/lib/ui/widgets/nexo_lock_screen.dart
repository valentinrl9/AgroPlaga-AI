import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

class NexoLockScreen extends StatelessWidget {
  final String moduleName;
  final bool isB2C;
  final String? message;

  const NexoLockScreen({
    super.key,
    required this.moduleName,
    this.isB2C = true,
    this.message,
  });

  @override
  Widget build(BuildContext context) {
    final displayMessage = message ?? (isB2C
        ? "Desbloquea métricas avanzadas e IA climática predictiva por 9.99€/mes."
        : "Este módulo requiere vinculación oficial con tu Cooperativa o SAT adherida "
            "para la gestión unificada de alertas. Solicita el alta a tu perito técnico.");

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
              const Text(
                "Módulo no activo",
                style: TextStyle(fontSize: 15, color: NexoColors.textSecondary),
              ),
              const SizedBox(height: 20),
              Text(
                displayMessage,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 15,
                  height: 1.45,
                  color: NexoColors.pureWhite,
                ),
              ),
              if (isB2C) ...[
                const SizedBox(height: 28),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: null,
                    style: ElevatedButton.styleFrom(
                      disabledBackgroundColor: NexoColors.bioGreen.withValues(alpha: 0.35),
                      disabledForegroundColor: NexoColors.pureWhite.withValues(alpha: 0.7),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                    ),
                    child: const Text("Activar periodo de prueba de 7 días"),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
