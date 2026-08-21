import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../data/repositories/incident_repository.dart";
import "../../models/pest_incident.dart";
import "../layout/mobile_layout.dart";

class IncidentsScreen extends StatefulWidget {
  const IncidentsScreen({super.key});

  @override
  State<IncidentsScreen> createState() => _IncidentsScreenState();
}

class _IncidentsScreenState extends State<IncidentsScreen> {
  final _repository = IncidentRepository();
  late Future<List<PestIncident>> _future;
  bool _showClosed = false;

  static const _stages = [
    "detection",
    "diagnosis",
    "prescription",
    "treatment",
    "evaluation",
    "closed",
  ];

  static const _stageHints = {
    "detection": "Confirmar diagnóstico",
    "diagnosis": "Prescripción MAPA",
    "prescription": "Registrar tratamiento",
    "treatment": "Iniciar evaluación",
    "evaluation": "Valorar evolución",
    "closed": "Incidencia cerrada",
  };

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() {
      _future = _repository.fetchIncidents(activeOnly: !_showClosed);
    });
  }

  Future<void> _openDetail(PestIncident incident) async {
    final changed = await Navigator.pushNamed(
      context,
      Routes.incidentDetail,
      arguments: incident.id,
    );
    if (changed == true) _reload();
  }

  Widget _stageProgress(PestIncident incident) {
    return Row(
      children: [
        for (var i = 0; i < _stages.length; i++) ...[
          if (i > 0)
            Expanded(
              child: Container(
                height: 3,
                color: i <= incident.stageIndex ? NexoColors.bioGreen : NexoColors.borderSubtle,
              ),
            ),
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: i < incident.stageIndex
                  ? NexoColors.bioGreen
                  : i == incident.stageIndex
                      ? NexoColors.techCyan
                      : NexoColors.borderSubtle,
              border: i == incident.stageIndex
                  ? Border.all(color: NexoColors.bioGreen, width: 2)
                  : null,
            ),
          ),
        ],
      ],
    );
  }

  Color _stageColor(PestIncident incident) {
    if (!incident.isActive) return NexoColors.textSecondary;
    switch (incident.stage) {
      case "detection":
      case "evaluation":
        return NexoColors.techCyan;
      case "diagnosis":
      case "prescription":
        return NexoColors.warningAmber;
      case "treatment":
        return NexoColors.bioGreen;
      default:
        return NexoColors.textSecondary;
    }
  }

  Widget _stageChip(PestIncident incident) {
    final color = _stageColor(incident);
    return Chip(
      label: Text(incident.stageLabel),
      labelStyle: TextStyle(color: color, fontWeight: FontWeight.w600, fontSize: 12),
      backgroundColor: color.withValues(alpha: 0.12),
      side: BorderSide(color: color.withValues(alpha: 0.35)),
      visualDensity: VisualDensity.compact,
      padding: EdgeInsets.zero,
    );
  }

  String _nextAction(PestIncident incident) {
    if (!incident.isActive) {
      return incident.closureOutcome == "crop_lost" ? "Cosecha perdida" : "Resuelta";
    }
    return _stageHints[incident.stage] ?? incident.stageLabel;
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
            return MobileLayout.errorState(error: snapshot.error!, onRetry: _reload);
          }

          final incidents = snapshot.data ?? [];
          if (incidents.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      _showClosed ? Icons.inventory_2_outlined : Icons.bug_report_outlined,
                      size: 48,
                      color: NexoColors.textSecondary.withValues(alpha: 0.6),
                    ),
                    const SizedBox(height: 16),
                    if (_showClosed)
                      const Text(
                        "No hay incidencias cerradas.",
                        textAlign: TextAlign.center,
                      )
                    else
                      const Text(
                        "No tienes incidencias activas.\nAbre una desde un escaneo con plaga detectada.",
                        textAlign: TextAlign.center,
                      ),
                    if (!_showClosed) ...[
                      const SizedBox(height: 20),
                      FilledButton.icon(
                        onPressed: () => Navigator.pushNamed(context, Routes.scan),
                        icon: const Icon(Icons.camera_alt_outlined),
                        label: const Text("Hacer escaneo"),
                      ),
                    ],
                  ],
                ),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async {
              _reload();
              await _future;
            },
            child: ListView.separated(
              physics: const AlwaysScrollableScrollPhysics(),
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
                              const SizedBox(width: 4),
                              Icon(
                                Icons.chevron_right,
                                color: NexoColors.textSecondary.withValues(alpha: 0.7),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          _stageProgress(incident),
                          const SizedBox(height: 10),
                          Text(
                            "${incident.farmName ?? "Unidad"} · ${incident.zoneName ?? "Municipio"}",
                            style: const TextStyle(color: NexoColors.textSecondary, fontSize: 13),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            "Severidad ${incident.severity}",
                            style: const TextStyle(color: NexoColors.textSecondary, fontSize: 13),
                          ),
                          if (incident.prescriptionProductName != null) ...[
                            const SizedBox(height: 6),
                            Text(
                              "MAPA: ${incident.prescriptionProductName}",
                              style: const TextStyle(fontSize: 13),
                            ),
                          ],
                          const SizedBox(height: 10),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            decoration: BoxDecoration(
                              color: NexoColors.surfaceElevated,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  incident.isActive ? Icons.play_arrow_rounded : Icons.check_circle_outline,
                                  size: 16,
                                  color: incident.isActive ? NexoColors.bioGreen : NexoColors.textSecondary,
                                ),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    incident.isActive
                                        ? "Siguiente paso: ${_nextAction(incident)}"
                                        : _nextAction(incident),
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: incident.isActive ? FontWeight.w600 : FontWeight.normal,
                                      color: incident.isActive ? NexoColors.bioGreen : NexoColors.textSecondary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
