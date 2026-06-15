import "package:flutter/material.dart";

import "../../core/severity.dart";

class SeverityBadge extends StatelessWidget {
  final String severity;

  const SeverityBadge({super.key, required this.severity});

  Color _colorFor(int? level) {
    switch (level) {
      case 3:
        return const Color(0xFFC62828);
      case 2:
        return const Color(0xFFFBC02D);
      case 1:
        return const Color(0xFF2E7D32);
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final level = Severity.parseToLevel(severity);
    final label = Severity.labelFor(severity);
    final color = _colorFor(level);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color),
      ),
      child: Text(
        label,
        style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12),
      ),
    );
  }
}
