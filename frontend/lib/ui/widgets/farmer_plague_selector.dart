import "package:flutter/material.dart";

import "../../core/plague_catalog.dart";
import "../../ml/plaga_result.dart";
import "../../models/scan.dart";

/// Lets the farmer pick the plague they believe applies (overrides IA suggestion).
class FarmerPlagueSelector extends StatelessWidget {
  final Scan? scan;
  final String? aiPlague;
  final String? selectedPlague;
  final List<PlagueCandidate>? topCandidates;
  final ValueChanged<String?> onChanged;
  final bool enabled;

  const FarmerPlagueSelector({
    super.key,
    this.scan,
    this.aiPlague,
    required this.selectedPlague,
    this.topCandidates,
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

  List<PlagueCandidate> get _candidates {
    if (topCandidates != null && topCandidates!.isNotEmpty) {
      return topCandidates!;
    }
    final suggested = scan?.plague ?? aiPlague;
    if (suggested == null || suggested.trim().isEmpty) return const [];
    return [
      PlagueCandidate(
        plague: suggested.trim().toLowerCase(),
        confidence: scan?.confidence ?? 0,
      ),
    ];
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
    final candidates = _candidates;
    final showTopSuggestions = candidates.length >= 2;
    final selectedNormalized = selectedPlague?.trim().toLowerCase();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (showTopSuggestions) ...[
          const Text(
            "Plagas más probables según la IA",
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 4),
          const Text(
            "Elige una opción o indica otra plaga abajo si ninguna encaja.",
            style: TextStyle(fontSize: 12, color: Colors.black54),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final candidate in candidates.take(3))
                ChoiceChip(
                  label: Text("${candidate.plague} · ${candidate.confidencePercent}"),
                  selected: selectedNormalized == candidate.plague,
                  onSelected: enabled
                      ? (_) => onChanged(candidate.plague)
                      : null,
                ),
            ],
          ),
          const SizedBox(height: 14),
          const Text(
            "Otra plaga (catálogo completo)",
            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
        ] else if (suggestedPlague != null) ...[
          Text(
            "IA sugiere: $suggestedPlague",
            style: const TextStyle(fontSize: 13, color: Colors.black54),
          ),
          const SizedBox(height: 8),
        ],
        InputDecorator(
          decoration: InputDecoration(
            labelText: showTopSuggestions ? "Plaga según tu criterio" : "Plaga según tu criterio",
            helperText:
                "El tratamiento MAPA y la incidencia usarán esta plaga bajo tu responsabilidad.",
            border: const OutlineInputBorder(),
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
