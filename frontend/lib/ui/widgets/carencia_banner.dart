import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../data/repositories/treatment_repository.dart";

class CarenciaBanner extends StatefulWidget {
  const CarenciaBanner({super.key});

  @override
  State<CarenciaBanner> createState() => _CarenciaBannerState();
}

class _CarenciaBannerState extends State<CarenciaBanner> {
  final _repo = TreatmentRepository();
  Map<String, dynamic>? _active;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final list = await _repo.fetchActive();
      if (!mounted) return;
      setState(() => _active = list.isNotEmpty ? list.first as Map<String, dynamic> : null);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    if (_active == null) return const SizedBox.shrink();

    final allowed = _active!["harvest_allowed"] as bool? ?? false;
    final hours = (_active!["hours_remaining"] as num?)?.toDouble() ?? 0;
    final product = _active!["product_name"]?.toString() ?? "Tratamiento";

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: (allowed ? NexoColors.successGreen : NexoColors.errorRed).withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: allowed ? NexoColors.successGreen : NexoColors.errorRed),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            allowed ? "APTO PARA CORTE" : "RECOLECCIÓN PROHIBIDA",
            style: TextStyle(
              fontWeight: FontWeight.w800,
              color: allowed ? NexoColors.successGreen : NexoColors.errorRed,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            allowed
                ? "Plazo de carencia cumplido · $product"
                : "$product · ${hours.toStringAsFixed(1)} h restantes",
            style: const TextStyle(fontSize: 13),
          ),
        ],
      ),
    );
  }
}
