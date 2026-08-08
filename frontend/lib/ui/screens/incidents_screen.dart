import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../data/repositories/incident_repository.dart";
import "../../models/pest_incident.dart";

class IncidentsScreen extends StatefulWidget {
  const IncidentsScreen({super.key});

  @override
  State<IncidentsScreen> createState() => _IncidentsScreenState();
}

class _IncidentsScreenState extends State<IncidentsScreen> {
  final _repository = IncidentRepository();
  late Future<List<PestIncident>> _future;
  bool _showClosed = false;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() => _future = _repository.fetchIncidents(activeOnly: !_showClosed));
  }

  Future<void> _openDetail(PestIncident incident) async {
    final changed = await Navigator.pushNamed(
      context,
      Routes.incidentDetail,
      arguments: incident.id,
    );
    if (changed == true) _reload();
  }

  Widget _stageChip(PestIncident incident) {
    return Chip(
      label: Text(incident.stageLabel),
      backgroundColor: NexoColors.bioGreen.withValues(alpha: 0.15),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Mis incidencias"),
        actions: [
          TextButton(
            onPressed: () {
              setState(() => _showClosed = !_showClosed);
              _reload();
            },
            child: Text(_showClosed ? "Activas" : "Historial"),
          ),
        ],
      ),
      body: FutureBuilder<List<PestIncident>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text("Error: ${snapshot.error}"));
          }

          final incidents = snapshot.data ?? [];
          if (incidents.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (_showClosed)
                      const Text(
                        "No hay incidencias cerradas.",
                        textAlign: TextAlign.center,
                      )
                    else
                      const Text(
                        "No tienes incidencias activas.",
                        textAlign: TextAlign.center,
                      ),
                    if (!_showClosed) ...[
                      const SizedBox(height: 16),
                      OutlinedButton(
                        onPressed: () => Navigator.pushNamed(context, Routes.scan),
                        child: const Text("Hacer escaneo"),
                      ),
                    ],
                  ],
                ),
              ),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: incidents.length,
            separatorBuilder: (_, __) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final incident = incidents[index];
              return Card(
                clipBehavior: Clip.antiAlias,
                child: InkWell(
                  onTap: () => _openDetail(incident),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                "${incident.plague} · ${incident.crop}",
                                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                              ),
                            ),
                            _stageChip(incident),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          "${incident.farmName ?? "Unidad"} · ${incident.zoneName ?? "Municipio"}\n"
                          "Severidad: ${incident.severity}",
                          style: const TextStyle(color: NexoColors.textSecondary),
                        ),
                        if (incident.prescriptionProductName != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            "MAPA: ${incident.prescriptionProductName}",
                            style: const TextStyle(fontSize: 13),
                          ),
                        ],
                        if (incident.closureOutcome != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            incident.closureOutcome == "crop_lost" ? "Cosecha perdida" : "Resuelto",
                            style: const TextStyle(color: NexoColors.bioGreen, fontWeight: FontWeight.w600),
                          ),
                        ],
                        const SizedBox(height: 8),
                        Text(
                          "Toca para abrir CRM · ${incident.stageLabel}",
                          style: const TextStyle(fontSize: 12, color: NexoColors.textSecondary),
                        ),
                      ],
                    ),
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
