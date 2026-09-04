import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../models/activity_summary.dart";

class WeeklyVigilanceCard extends StatelessWidget {
  final WeeklyVigilance vigilance;
  final int streakWeeks;

  const WeeklyVigilanceCard({
    super.key,
    required this.vigilance,
    this.streakWeeks = 0,
  });

  @override
  Widget build(BuildContext context) {
    final progress = vigilance.goal > 0
        ? (vigilance.current / vigilance.goal).clamp(0.0, 1.0)
        : 0.0;

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: NexoColors.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: vigilance.completed ? NexoColors.successGreen : NexoColors.techCyan.withValues(alpha: 0.4),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                vigilance.completed ? Icons.check_circle : Icons.flag_outlined,
                color: vigilance.completed ? NexoColors.successGreen : NexoColors.techCyan,
                size: 20,
              ),
              const SizedBox(width: 8),
              const Text(
                "Reto semanal",
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
              ),
              const Spacer(),
              if (streakWeeks > 0)
                Text(
                  "Racha $streakWeeks sem.",
                  style: const TextStyle(fontSize: 12, color: NexoColors.warningAmber, fontWeight: FontWeight.w600),
                ),
            ],
          ),
          const SizedBox(height: 10),
          LinearProgressIndicator(
            value: progress,
            backgroundColor: NexoColors.borderSubtle,
            color: vigilance.completed ? NexoColors.successGreen : NexoColors.techCyan,
            minHeight: 6,
            borderRadius: BorderRadius.circular(4),
          ),
          const SizedBox(height: 8),
          Text(
            vigilance.completed
                ? "${vigilance.current}/${vigilance.goal} escaneo esta semana · Completado"
                : "${vigilance.current}/${vigilance.goal} escaneo esta semana",
            style: const TextStyle(fontSize: 13, color: NexoColors.textSecondary),
          ),
        ],
      ),
    );
  }
}
