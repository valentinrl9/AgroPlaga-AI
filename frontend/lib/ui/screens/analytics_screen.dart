import "package:flutter/material.dart";

import "../../data/repositories/analytics_repository.dart";
import "../../models/analytics.dart";
import "../widgets/severity_badge.dart";

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  final _repository = AnalyticsRepository();
  late Future<PersonalAnalytics> _future;
  int _days = 90;

  @override
  void initState() {
    super.initState();
    _future = _repository.fetchMyAnalytics(days: _days);
  }

  void _reload() {
    final newFuture = _repository.fetchMyAnalytics(days: _days);
    setState(() {
      _future = newFuture;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Mi analítica"),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _reload)],
      ),
      body: FutureBuilder<PersonalAnalytics>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text("Error: ${snapshot.error}"));
          }

          final data = snapshot.data!;
          final summary = data.summary;
          final maxTimeline = data.timeline.isEmpty
              ? 1
              : data.timeline.map((p) => p.count).reduce((a, b) => a > b ? a : b);

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Row(
                children: [
                  const Text("Periodo:", style: TextStyle(fontWeight: FontWeight.w600)),
                  const SizedBox(width: 8),
                  DropdownButton<int>(
                    value: _days,
                    items: const [
                      DropdownMenuItem(value: 30, child: Text("30 días")),
                      DropdownMenuItem(value: 90, child: Text("90 días")),
                      DropdownMenuItem(value: 180, child: Text("180 días")),
                    ],
                    onChanged: (v) {
                      if (v == null) return;
                      setState(() => _days = v);
                      _reload();
                    },
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  _KpiCard(label: "Escaneos", value: "${summary.totalScans}"),
                  _KpiCard(label: "Severidad alta", value: "${summary.highSeverityCount}"),
                  _KpiCard(label: "Cultivos", value: "${summary.crops.length}"),
                  _KpiCard(label: "Plagas distintas", value: "${summary.plagues.length}"),
                ],
              ),
              const SizedBox(height: 20),
              const Text("Evolución de escaneos", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              SizedBox(
                height: 120,
                child: data.timeline.isEmpty
                    ? const Center(child: Text("Sin datos en este periodo"))
                    : Row(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: data.timeline.map((point) {
                          final h = (point.count / maxTimeline) * 90;
                          return Expanded(
                            child: Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 2),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.end,
                                children: [
                                  Container(
                                    height: h.clamp(4, 90),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF2E7D32),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(point.date.substring(5), style: const TextStyle(fontSize: 9)),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      ),
              ),
              const SizedBox(height: 20),
              const Text("Por cultivo", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ...summary.crops.map((c) => _BarRow(label: c.name, count: c.count, max: summary.totalScans)),
              const SizedBox(height: 16),
              const Text("Por plaga", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ...summary.plagues.map((p) => _BarRow(label: p.name, count: p.count, max: summary.totalScans)),
              if (data.farms.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text("Por finca / invernadero", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ...data.farms.map(
                  (f) => ListTile(
                    title: Text(f.name),
                    subtitle: Text("${f.farmType == "greenhouse" ? "Invernadero" : "Finca"} · ${f.crop}"),
                    trailing: Text("${f.scanCount} esc."),
                  ),
                ),
              ],
              const SizedBox(height: 16),
              const Text("Últimos escaneos", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ...data.recentScans.map(
                (scan) => Card(
                  child: ListTile(
                    title: Text("${scan.crop} · ${scan.plague}"),
                    subtitle: Text(
                      "${scan.createdAt != null ? _formatDate(scan.createdAt!) : "—"} · "
                      "${(scan.confidence * 100).toStringAsFixed(0)}% conf.",
                    ),
                    trailing: SeverityBadge(severity: scan.severity),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  String _formatDate(DateTime date) {
    return "${date.day}/${date.month}/${date.year}";
  }
}

class _KpiCard extends StatelessWidget {
  final String label;
  final String value;

  const _KpiCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF757575))),
            Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}

class _BarRow extends StatelessWidget {
  final String label;
  final int count;
  final int max;

  const _BarRow({required this.label, required this.count, required this.max});

  @override
  Widget build(BuildContext context) {
    final width = max > 0 ? count / max : 0.0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("$label ($count)"),
          const SizedBox(height: 4),
          LinearProgressIndicator(value: width.clamp(0.0, 1.0)),
        ],
      ),
    );
  }
}
