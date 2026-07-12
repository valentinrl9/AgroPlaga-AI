import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

/// Panel oscuro con borde sutil para agrupar acciones.
class NexoSectionCard extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const NexoSectionCard({
    super.key,
    required this.title,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: NexoColors.surfaceCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: NexoColors.borderSubtle),
        boxShadow: [
          BoxShadow(
            color: NexoColors.techCyan.withValues(alpha: 0.04),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: NexoColors.techCyan,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 14),
          ...children,
        ],
      ),
    );
  }
}

/// Acción secundaria en rejilla (historial, alertas, etc.).
class NexoActionTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  const NexoActionTile({
    super.key,
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: NexoColors.surfaceElevated,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: NexoColors.borderSubtle),
          ),
          child: Column(
            children: [
              Icon(icon, color: NexoColors.techCyan, size: 22),
              const SizedBox(height: 6),
              Text(
                label,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: NexoColors.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
