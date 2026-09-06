import "package:flutter/material.dart";
import "package:flutter/services.dart";

import "../../core/nexo_colors.dart";
import "../../models/official_source.dart";

/// Muestra fuentes oficiales (RAIF, MAPA, etc.) que respaldan o contextualizan un consejo.
class OfficialSourcesPanel extends StatelessWidget {
  final List<OfficialSource> sources;
  final String? heading;

  const OfficialSourcesPanel({
    super.key,
    required this.sources,
    this.heading,
  });

  @override
  Widget build(BuildContext context) {
    if (sources.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F4FD),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF1565C0).withValues(alpha: 0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.account_balance_outlined, size: 18, color: Color(0xFF1565C0)),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  heading ?? "Respaldado o contrastable con fuentes oficiales",
                  style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                    color: Color(0xFF1565C0),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ...sources.map((source) => _SourceTile(source: source)),
        ],
      ),
    );
  }
}

class _SourceTile extends StatelessWidget {
  final OfficialSource source;

  const _SourceTile({required this.source});

  Color get _badgeColor {
    switch (source.kind) {
      case "official_protocol":
        return const Color(0xFF1565C0);
      case "official_registry":
        return NexoColors.bioGreen;
      case "community":
        return NexoColors.warningAmber;
      case "orientation":
        return NexoColors.textSecondary;
      default:
        return const Color(0xFF1565C0);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            spacing: 6,
            runSpacing: 4,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: _badgeColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  source.kindLabel,
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: _badgeColor),
                ),
              ),
              Text(
                source.issuer,
                style: const TextStyle(fontSize: 11, color: NexoColors.textSecondary),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(source.title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
          if (source.note != null && source.note!.isNotEmpty) ...[
            const SizedBox(height: 2),
            Text(source.note!, style: const TextStyle(fontSize: 12, color: NexoColors.textSecondary, height: 1.3)),
          ],
          if (source.url != null && source.url!.isNotEmpty) ...[
            const SizedBox(height: 4),
            InkWell(
              onTap: () async {
                await Clipboard.setData(ClipboardData(text: source.url!));
                if (!context.mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Enlace copiado. Ábrelo en el navegador.")),
                );
              },
              child: Text(
                source.url!,
                style: const TextStyle(fontSize: 11, color: Color(0xFF1565C0), decoration: TextDecoration.underline),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
