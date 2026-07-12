import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

import "../../models/scan.dart";
import "severity_badge.dart";

class CardScan extends StatelessWidget {
  final Scan? scan;
  final String? plague;
  final String? crop;
  final String? severity;
  final double? confidence;
  final String? title;
  final List<Widget>? extra;

  const CardScan({
    super.key,
    this.scan,
    this.plague,
    this.crop,
    this.severity,
    this.confidence,
    this.title,
    this.extra,
  });

  factory CardScan.fromScan(Scan scan, {String? title, List<Widget>? extra}) {
    return CardScan(
      scan: scan,
      plague: scan.plague,
      crop: scan.crop,
      severity: scan.severity,
      confidence: scan.confidence,
      title: title,
      extra: extra,
    );
  }

  @override
  Widget build(BuildContext context) {
    final plagueLabel = plague ?? scan?.plague ?? "—";
    final cropLabel = crop ?? scan?.crop;
    final severityLabel = severity ?? scan?.severity;
    final confidenceValue = confidence ?? scan?.confidence;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (title != null) ...[
              Text(title!, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
            ],
            if (cropLabel != null) ...[
              Text("Cultivo: $cropLabel", style: const TextStyle(fontSize: 16)),
              const SizedBox(height: 8),
            ],
            Text(
              plagueLabel,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: NexoColors.errorRed),
            ),
            if (severityLabel != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Text("Severidad: "),
                  SeverityBadge(severity: severityLabel),
                ],
              ),
            ],
            if (confidenceValue != null) ...[
              const SizedBox(height: 8),
              Text("Confianza: ${(confidenceValue * 100).toStringAsFixed(confidenceValue <= 1 ? 1 : 0)}%"),
            ],
            if (extra != null) ...[
              const SizedBox(height: 8),
              ...extra!,
            ],
          ],
        ),
      ),
    );
  }
}
