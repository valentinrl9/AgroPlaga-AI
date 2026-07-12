import "package:flutter/material.dart";

import "../../data/repositories/outbreak_event_repository.dart";
import "../../models/outbreak_event.dart";
import "../widgets/severity_badge.dart";

class TechValidationScreen extends StatefulWidget {
  const TechValidationScreen({super.key});

  @override
  State<TechValidationScreen> createState() => _TechValidationScreenState();
}

class _TechValidationScreenState extends State<TechValidationScreen> {
  final _repository = OutbreakEventRepository();
  late Future<List<OutbreakEvent>> _future;

  @override
  void initState() {
    super.initState();
    _future = _repository.fetchEvents(hours: 168);
  }

  void _reload() {
    final newFuture = _repository.fetchEvents(hours: 168);
    setState(() {
      _future = newFuture;
    });
  }

  Future<void> _validate(OutbreakEvent event) async {
    await _repository.setValidation(event.id, action: "confirm");
    _reload();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Validar eventos"),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _reload)],
      ),
      body: FutureBuilder<List<OutbreakEvent>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text("Error: ${snapshot.error}"));
          }

          final pending = (snapshot.data ?? []).where((e) => e.isPending).toList();
          if (pending.isEmpty) {
            return const Center(child: Text("No hay eventos pendientes de validar."));
          }

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: pending.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final event = pending[index];
              return Card(
                child: ListTile(
                  title: Text("${event.displayPlague} · ${event.zoneName ?? "Zona ${event.zoneId}"}"),
                  subtitle: Text(
                    "Severidad ${event.severity} · IA sin validar"
                    "${event.originalPlague != null && event.originalPlague != event.displayPlague ? " · original: ${event.originalPlague}" : ""}",
                  ),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFFB200).withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Text("Pendiente", style: TextStyle(fontSize: 11, color: Color(0xFFEF6C00))),
                      ),
                      const SizedBox(width: 4),
                      SeverityBadge(severity: event.severity.toString()),
                      IconButton(
                        icon: const Icon(Icons.check_circle, color: Color(0xFF00A86B)),
                        onPressed: () => _validate(event),
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
