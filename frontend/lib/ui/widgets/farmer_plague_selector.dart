import "package:flutter/material.dart";

import "../../core/plague_catalog.dart";
import "../../models/scan.dart";

/// Lets the farmer pick the plague they believe applies (overrides IA suggestion).
class FarmerPlagueSelector extends StatelessWidget {
  final Scan? scan;
  final String? aiPlague;
  final String? selectedPlague;
  final ValueChanged<String?> onChanged;
  final bool enabled;

  const FarmerPlagueSelector({
    super.key,
    this.scan,
    this.aiPlague,
    required this.selectedPlague,
    required this.onChanged,
    this.enabled = true,
  });

  static List<String> optionsFor({Scan? scan, String? aiPlague}) {
    final ai = (scan?.plague ?? aiPlague ?? "").trim().toLowerCase();
    final labels = PlagueCatalog.labels.where((l) => l != "sana").toList();
    if (ai.isNotEmpty && !labels.any((l) => l.toLowerCase() == ai)) {
      return [ai, ...labels];
    }
    return labels;
  }

  @override
  Widget build(BuildContext context) {
    final suggestedPlague = scan?.plague ?? aiPlague;
    final options = optionsFor(scan: scan, aiPlague: suggestedPlague);
    final value = selectedPlague ?? scan?.effectivePlague ?? suggestedPlague;
    final normalizedValue = value?.trim().toLowerCase();
    final effectiveValue = options.any((o) => o.toLowerCase() == normalizedValue)
        ? options.firstWhere((o) => o.toLowerCase() == normalizedValue)
        : options.first;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (suggestedPlague != null) ...[
          Text(
            "IA sugiere: $suggestedPlague",
            style: const TextStyle(fontSize: 13, color: Colors.black54),
          ),
          const SizedBox(height: 8),
        ],
        InputDecorator(
          decoration: const InputDecoration(
            labelText: "Plaga según tu criterio",
            helperText: "El tratamiento MAPA y la incidencia usarán esta plaga bajo tu responsabilidad.",
            border: OutlineInputBorder(),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              isExpanded: true,
              value: effectiveValue,
              items: options
                  .map(
                    (plague) => DropdownMenuItem(
                      value: plague,
                      child: Text(
                        plague == suggestedPlague?.trim().toLowerCase() ? "$plague (IA)" : plague,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  )
                  .toList(),
              onChanged: enabled ? (v) => onChanged(v) : null,
            ),
          ),
        ),
      ],
    );
  }
}

bool farmerPlagueDiffersFromAi({required String aiPlague, String? selectedPlague}) {
  final selected = selectedPlague?.trim().toLowerCase();
  if (selected == null || selected.isEmpty) return false;
  return selected != aiPlague.trim().toLowerCase();
}

String? farmerPlaguePayload({required String aiPlague, String? selectedPlague}) {
  if (!farmerPlagueDiffersFromAi(aiPlague: aiPlague, selectedPlague: selectedPlague)) {
    return null;
  }
  return selectedPlague!.trim().toLowerCase();
}
