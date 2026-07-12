import "package:fl_chart/fl_chart.dart";
import "package:flutter/material.dart";

import "../../../core/nexo_colors.dart";

class ClimateLineChart extends StatelessWidget {
  final String title;
  final List<String> labels;
  final List<double> values;
  final Color color;

  const ClimateLineChart({
    super.key,
    required this.title,
    required this.labels,
    required this.values,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final axisColor = Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.55);
    final gridColor = NexoColors.borderSubtle.withValues(alpha: 0.6);

    if (values.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text("$title — sin datos"),
        ),
      );
    }

    final spots = <FlSpot>[];
    for (var i = 0; i < values.length; i++) {
      spots.add(FlSpot(i.toDouble(), values[i]));
    }

    final maxY = values.reduce((a, b) => a > b ? a : b) * 1.2 + 0.1;

    return Card(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 16, 16, 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            SizedBox(
              height: 180,
              child: LineChart(
                LineChartData(
                  minY: 0,
                  maxY: maxY,
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    getDrawingHorizontalLine: (_) => FlLine(color: gridColor, strokeWidth: 1),
                  ),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 36,
                        getTitlesWidget: (value, meta) => Text(
                          value.toStringAsFixed(0),
                          style: TextStyle(fontSize: 10, color: axisColor),
                        ),
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 28,
                        getTitlesWidget: (value, meta) {
                          final i = value.toInt();
                          if (i < 0 || i >= labels.length) return const SizedBox.shrink();
                          final label = labels[i];
                          final short = label.length > 6 ? label.substring(5) : label;
                          return Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text(short, style: TextStyle(fontSize: 10, color: axisColor)),
                          );
                        },
                      ),
                    ),
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      color: color,
                      barWidth: 3,
                      dotData: const FlDotData(show: true),
                      belowBarData: BarAreaData(show: true, color: color.withValues(alpha: 0.12)),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ClimateMetricCard extends StatelessWidget {
  final String title;
  final String value;
  final String emoji;
  final String? hint;
  final Color? accent;

  const ClimateMetricCard({
    super.key,
    required this.title,
    required this.value,
    required this.emoji,
    this.hint,
    this.accent,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: NexoColors.surfaceElevated,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 4,
                  height: 36,
                  decoration: BoxDecoration(
                    color: accent ?? NexoColors.bioGreen,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("$emoji $title", style: const TextStyle(fontWeight: FontWeight.w600)),
                      const SizedBox(height: 4),
                      Text(
                        value,
                        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            if (hint != null) ...[
              const SizedBox(height: 8),
              Text(hint!, style: TextStyle(fontSize: 12, color: NexoColors.textSecondary)),
            ],
          ],
        ),
      ),
    );
  }
}

class ClimateIaPanel extends StatelessWidget {
  final Map<String, String> consejos;

  const ClimateIaPanel({super.key, required this.consejos});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _tile("💧", "Riego", consejos["riego"] ?? ""),
        const SizedBox(height: 8),
        _tile("🌡️", "Ventilación y calor", consejos["ventilacion"] ?? ""),
        const SizedBox(height: 8),
        _tile("🍃", "Humedad y sanidad", consejos["humedad"] ?? ""),
      ],
    );
  }

  Widget _tile(String emoji, String title, String body) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("$emoji $title", style: const TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            Text(body, style: const TextStyle(height: 1.35)),
          ],
        ),
      ),
    );
  }
}
