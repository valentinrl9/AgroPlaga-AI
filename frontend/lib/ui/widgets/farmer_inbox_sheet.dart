import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../models/activity_summary.dart";

class FarmerInboxItem {
  final String id;
  final String title;
  final String body;
  final IconData icon;
  final Color accentColor;
  final Future<void> Function()? onOpen;

  const FarmerInboxItem({
    required this.id,
    required this.title,
    required this.body,
    required this.icon,
    required this.accentColor,
    this.onOpen,
  });
}

Future<void> showFarmerInboxSheet({
  required BuildContext context,
  required List<FarmerInboxItem> items,
  required Future<void> Function(FarmerInboxItem item) onDismiss,
}) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: NexoColors.surfaceCard,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (ctx) {
      return SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: NexoColors.borderSubtle,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                "Avisos",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: NexoColors.textPrimary),
              ),
              const SizedBox(height: 4),
              Text(
                items.isEmpty ? "No tienes avisos pendientes." : "Toca un aviso para verlo y marcarlo como leído.",
                style: const TextStyle(fontSize: 13, color: NexoColors.textSecondary),
              ),
              const SizedBox(height: 12),
              if (items.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Icon(Icons.notifications_none_outlined, size: 40, color: NexoColors.textSecondary),
                )
              else
                ConstrainedBox(
                  constraints: BoxConstraints(
                    maxHeight: MediaQuery.of(ctx).size.height * 0.55,
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    itemCount: items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (context, index) {
                      final item = items[index];
                      return Material(
                        color: NexoColors.surfaceElevated,
                        borderRadius: BorderRadius.circular(12),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(12),
                          onTap: () async {
                            Navigator.pop(ctx);
                            if (item.onOpen != null) {
                              await item.onOpen!();
                            }
                            await onDismiss(item);
                          },
                          child: Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: item.accentColor.withValues(alpha: 0.45)),
                            ),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Icon(item.icon, color: item.accentColor, size: 22),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        item.title,
                                        style: TextStyle(
                                          fontWeight: FontWeight.w700,
                                          fontSize: 14,
                                          color: item.accentColor,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        item.body,
                                        style: const TextStyle(fontSize: 13, color: NexoColors.textPrimary, height: 1.35),
                                      ),
                                    ],
                                  ),
                                ),
                                const Icon(Icons.chevron_right, color: NexoColors.textSecondary, size: 20),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
            ],
          ),
        ),
      );
    },
  );
}


FarmerInboxItem? carenciaInboxItem(Map<String, dynamic> active) {
  final allowed = active["harvest_allowed"] as bool? ?? false;
  final hours = (active["hours_remaining"] as num?)?.toDouble() ?? 0;
  final product = active["product_name"]?.toString() ?? "Tratamiento";
  final id = active["id"]?.toString() ?? product;

  return FarmerInboxItem(
    id: "carencia:$id:${allowed ? "ok" : "wait"}",
    title: allowed ? "APTO PARA CORTE" : "RECOLECCIÓN PROHIBIDA",
    body: allowed
        ? "Plazo de carencia cumplido · $product"
        : "$product · ${hours.toStringAsFixed(1)} h restantes",
    icon: allowed ? Icons.check_circle_outline : Icons.timer_off_outlined,
    accentColor: allowed ? NexoColors.successGreen : NexoColors.errorRed,
  );
}

FarmerInboxItem vigilanceInboxItem(WeeklyVigilance vigilance, int streakWeeks) {
  final ends = vigilance.endsAt.toIso8601String();
  return FarmerInboxItem(
    id: "vigilance:$ends",
    title: vigilance.completed ? "Reto semanal completado" : "Reto semanal",
    body: vigilance.completed
        ? "${vigilance.current}/${vigilance.goal} escaneo esta semana · "
            "${streakWeeks > 0 ? "Racha $streakWeeks sem." : "Completado"}"
        : "${vigilance.current}/${vigilance.goal} escaneo esta semana · "
            "${vigilance.description.isNotEmpty ? vigilance.description : "Sigue escaneando esta semana"}",
    icon: vigilance.completed ? Icons.emoji_events_outlined : Icons.flag_outlined,
    accentColor: vigilance.completed ? NexoColors.successGreen : NexoColors.techCyan,
  );
}
