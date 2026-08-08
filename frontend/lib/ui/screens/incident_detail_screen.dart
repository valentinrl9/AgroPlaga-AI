import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../data/repositories/incident_repository.dart";
import "../../data/repositories/scan_repository.dart";
import "../../data/repositories/treatment_repository.dart";
import "../../models/pest_incident.dart";
import "../../models/scan.dart";
import "../widgets/primary_button.dart";

class IncidentDetailScreen extends StatefulWidget {
  final int incidentId;

  const IncidentDetailScreen({super.key, required this.incidentId});

  @override
  State<IncidentDetailScreen> createState() => _IncidentDetailScreenState();
}

class _IncidentDetailScreenState extends State<IncidentDetailScreen> {
  final _incidentRepo = IncidentRepository();
  final _treatmentRepo = TreatmentRepository();
  final _scanRepo = ScanRepository();

  late Future<PestIncident> _future;
  List<dynamic> _biocides = [];
  List<Scan> _scans = [];
  String? _selectedRegistry;
  final _surfaceController = TextEditingController(text: "5000");
  final _evalScanController = TextEditingController();
  bool _ackUnverified = false;
  bool _loadingBiocides = false;
  bool _busy = false;
  String? _error;
  Map<String, dynamic>? _dosePreview;
  PestIncident? _incident;

  static const _stages = [
    "detection",
    "diagnosis",
    "prescription",
    "treatment",
    "evaluation",
    "closed",
  ];

  static const _stageLabels = {
    "detection": "Detección",
    "diagnosis": "Diagnóstico",
    "prescription": "Prescripción MAPA",
    "treatment": "Tratamiento aplicado",
    "evaluation": "Evaluación comparativa",
    "closed": "Cierre",
  };

  @override
  void initState() {
    super.initState();
    _reload();
  }

  @override
  void dispose() {
    _surfaceController.dispose();
    _evalScanController.dispose();
    super.dispose();
  }

  void _reload() {
    setState(() => _future = _load());
  }

  Future<PestIncident> _load() async {
    final incident = await _incidentRepo.fetchIncident(widget.incidentId);
    if (mounted) setState(() => _incident = incident);
    if (incident.stage == "diagnosis" || incident.stage == "prescription") {
      await _loadBiocides(incident);
    }
    if (incident.stage == "evaluation") {
      _scans = await _scanRepo.fetchScans();
      if (incident.evaluationScanId != null) {
        _evalScanController.text = "${incident.evaluationScanId}";
      }
    }
    return incident;
  }

  Future<void> _loadBiocides(PestIncident incident) async {
    setState(() => _loadingBiocides = true);
    try {
      final list = await _treatmentRepo.fetchBiocides(
        plague: incident.plague,
        crop: incident.crop,
      );
      if (!mounted) return;
      setState(() {
        _biocides = list;
        _loadingBiocides = false;
        if (list.isNotEmpty && _selectedRegistry == null) {
          _selectedRegistry = list.first["registry_no"] as String?;
        }
      });
      await _previewDose(incident);
    } catch (e) {
      if (mounted) {
        setState(() {
          _loadingBiocides = false;
          _error = e.toString();
        });
      }
    }
  }

  Future<void> _previewDose(PestIncident incident) async {
    final registry = _selectedRegistry ?? incident.prescriptionRegistryNumber;
    final surface = double.tryParse(_surfaceController.text.trim());
    if (registry == null || surface == null || surface <= 0) return;
    try {
      final dose = await _treatmentRepo.calculateDose(
        surfaceM2: surface,
        registryNo: registry,
        plague: incident.plague,
        crop: incident.crop,
      );
      if (mounted) setState(() => _dosePreview = dose);
    } catch (_) {}
  }

  Future<void> _run(Future<void> Function() action) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await action();
      _reload();
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  int _stepState(PestIncident incident, String stageKey) {
    final current = _stages.indexOf(incident.stage);
    final step = _stages.indexOf(stageKey);
    if (step < current) return 1;
    if (step == current) return 0;
    return -1;
  }

  Widget _prescriptionPanel(PestIncident incident) {
    if (incident.stage != "diagnosis" && incident.stage != "prescription") {
      if (incident.prescriptionProductName != null) {
        return Text(
          "${incident.prescriptionProductName} · "
          "${incident.prescriptionDoseMl?.toStringAsFixed(1) ?? "—"} ml · "
          "carencia ${incident.prescriptionSafetyHours ?? "—"} h",
        );
      }
      return const SizedBox.shrink();
    }

    if (_loadingBiocides) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 8),
        child: LinearProgressIndicator(),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (_biocides.isNotEmpty)
          DropdownButtonFormField<String>(
            value: _selectedRegistry,
            decoration: const InputDecoration(labelText: "Producto MAPA"),
            items: _biocides
                .map(
                  (b) => DropdownMenuItem(
                    value: b["registry_no"] as String,
                    child: Text(b["name"] as String, overflow: TextOverflow.ellipsis),
                  ),
                )
                .toList(),
            onChanged: _busy
                ? null
                : (v) async {
                    setState(() => _selectedRegistry = v);
                    await _previewDose(incident);
                  },
          )
        else
          Text(
            "Sin productos MAPA para ${incident.plague} / ${incident.crop}",
            style: const TextStyle(color: NexoColors.warningAmber, fontSize: 13),
          ),
        const SizedBox(height: 12),
        TextField(
          controller: _surfaceController,
          enabled: !_busy,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(labelText: "Superficie (m²)"),
          onSubmitted: (_) => _previewDose(incident),
        ),
        if (_dosePreview != null) ...[
          const SizedBox(height: 8),
          Text(
            "Dosis estimada: ${_dosePreview!["dose_ml"]} ml",
            style: const TextStyle(fontSize: 13),
          ),
        ],
        if (incident.stage == "diagnosis") ...[
          const SizedBox(height: 12),
          PrimaryButton(
            label: "Guardar prescripción",
            onPressed: _busy || _selectedRegistry == null
                ? null
                : () => _run(() async {
                      final surface = double.tryParse(_surfaceController.text.trim()) ?? 5000;
                      await _incidentRepo.prescribe(
                        incident.id,
                        registryNo: _selectedRegistry!,
                        surfaceM2: surface,
                      );
                    }),
          ),
        ],
      ],
    );
  }

  Widget _treatmentPanel(PestIncident incident) {
    if (incident.stage == "prescription") {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          CheckboxListTile(
            value: _ackUnverified,
            onChanged: _busy ? null : (v) => setState(() => _ackUnverified = v ?? false),
            controlAffinity: ListTileControlAffinity.leading,
            contentPadding: EdgeInsets.zero,
            title: const Text(
              "Confirmo aplicación bajo mi responsabilidad (plaga no verificada por perito).",
              style: TextStyle(fontSize: 13),
            ),
          ),
          PrimaryButton(
            label: "Registrar tratamiento y activar carencia",
            onPressed: _busy
                ? null
                : () => _run(() => _incidentRepo.applyTreatment(
                      incident.id,
                      ackUnverified: _ackUnverified,
                    )),
          ),
        ],
      );
    }

    final t = incident.treatment;
    if (t != null) {
      return Text(
        "${t.productName} · carencia ${t.safetyHours} h · "
        "${t.harvestAllowed ? "Cosecha permitida" : "${t.hoursRemaining?.toStringAsFixed(0) ?? "—"} h restantes"}",
      );
    }
    return const SizedBox.shrink();
  }

  Widget _evaluationPanel(PestIncident incident) {
    if (incident.stage != "evaluation") {
      if (incident.evaluationScanId != null) {
        return Text("Escaneo comparativo #${incident.evaluationScanId}");
      }
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          "Adjunta un escaneo de seguimiento para comparar la evolución.",
          style: TextStyle(fontSize: 13, color: NexoColors.textSecondary),
        ),
        const SizedBox(height: 8),
        if (_scans.isNotEmpty)
          DropdownButtonFormField<int>(
            value: int.tryParse(_evalScanController.text),
            decoration: const InputDecoration(labelText: "Escaneo comparativo"),
            items: _scans
                .where((s) => s.id != incident.scanId)
                .map(
                  (s) => DropdownMenuItem(
                    value: s.id,
                    child: Text("#${s.id} · ${s.plague} · ${s.createdAt?.toLocal().toString().split(".").first ?? "—"}"),
                  ),
                )
                .toList(),
            onChanged: _busy
                ? null
                : (v) {
                    if (v != null) _evalScanController.text = "$v";
                  },
          ),
        const SizedBox(height: 8),
        OutlinedButton(
          onPressed: _busy
              ? null
              : () => _run(() async {
                    final scanId = int.tryParse(_evalScanController.text.trim());
                    if (scanId == null) throw Exception("Selecciona un escaneo comparativo");
                    await _incidentRepo.attachEvaluationScan(incident.id, scanId);
                  }),
          child: const Text("Adjuntar foto comparativa"),
        ),
        const SizedBox(height: 12),
        OutlinedButton(
          onPressed: _busy
              ? null
              : () => _run(() => _incidentRepo.evaluate(incident.id, improved: false)),
          child: const Text("No hay mejora → volver a tratamiento"),
        ),
        const SizedBox(height: 8),
        PrimaryButton(
          label: "Hay mejora → cerrar resuelto",
          onPressed: _busy
              ? null
              : () => _run(() {
                    final scanId = int.tryParse(_evalScanController.text.trim());
                    return _incidentRepo.evaluate(
                      incident.id,
                      improved: true,
                      evaluationScanId: scanId,
                    );
                  }),
        ),
        const SizedBox(height: 8),
        OutlinedButton(
          onPressed: _busy ? null : () => _run(() => _incidentRepo.close(incident.id, outcome: "crop_lost")),
          child: const Text("Cosecha perdida"),
        ),
      ],
    );
  }

  Widget _stepContent(PestIncident incident, String stageKey) {
    switch (stageKey) {
      case "detection":
        if (incident.stage == "detection") {
          return PrimaryButton(
            label: "Confirmar diagnóstico",
            onPressed: _busy ? null : () => _run(() => _incidentRepo.advance(incident.id)),
          );
        }
        return const Text("Incidencia abierta desde el escaneo inicial.");
      case "diagnosis":
      case "prescription":
        return _prescriptionPanel(incident);
      case "treatment":
        if (incident.stage == "treatment") {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _treatmentPanel(incident),
              const SizedBox(height: 12),
              PrimaryButton(
                label: "Iniciar evaluación",
                onPressed: _busy ? null : () => _run(() => _incidentRepo.startEvaluation(incident.id)),
              ),
              const SizedBox(height: 8),
              OutlinedButton(
                onPressed: _busy ? null : () => _run(() => _incidentRepo.close(incident.id, outcome: "resolved")),
                child: const Text("Cerrar como resuelto"),
              ),
            ],
          );
        }
        return _treatmentPanel(incident);
      case "evaluation":
        return _evaluationPanel(incident);
      case "closed":
        if (incident.closureOutcome != null) {
          return Text(
            incident.closureOutcome == "crop_lost" ? "Resultado: cosecha perdida" : "Resultado: resuelto",
            style: const TextStyle(color: NexoColors.bioGreen, fontWeight: FontWeight.w600),
          );
        }
        return const SizedBox.shrink();
      default:
        return const SizedBox.shrink();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("CRM incidencia")),
      body: FutureBuilder<PestIncident>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || !snapshot.hasData) {
            return Center(child: Text("Error: ${snapshot.error ?? "Incidencia no encontrada"}"));
          }

          final incident = snapshot.data!;
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  "${incident.plague} · ${incident.crop}",
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  "${incident.farmName ?? "Unidad"} · ${incident.zoneName ?? "Municipio"}\n"
                  "Severidad: ${incident.severity}",
                  style: const TextStyle(color: NexoColors.textSecondary),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!, style: const TextStyle(color: NexoColors.errorRed)),
                ],
                const SizedBox(height: 16),
                Stepper(
                  physics: const NeverScrollableScrollPhysics(),
                  currentStep: incident.stageIndex.clamp(0, _stages.length - 1),
                  controlsBuilder: (_, __) => const SizedBox.shrink(),
                  steps: _stages.map((key) {
                    return Step(
                      title: Text(_stageLabels[key] ?? key),
                      content: _stepContent(incident, key),
                      isActive: incident.stage == key,
                      state: _stepState(incident, key) == 1
                          ? StepState.complete
                          : _stepState(incident, key) == 0
                              ? StepState.editing
                              : StepState.indexed,
                    );
                  }).toList(),
                ),
                if (!incident.isActive)
                  OutlinedButton(
                    onPressed: () => Navigator.pop(context, true),
                    child: const Text("Volver al listado"),
                  ),
              ],
            ),
          );
        },
      ),
      floatingActionButton: _incident?.isActive == true
          ? FloatingActionButton.extended(
              onPressed: () => Navigator.pushNamed(context, Routes.scan).then((_) => _reload()),
              label: const Text("Nuevo escaneo"),
              icon: const Icon(Icons.camera_alt_outlined),
            )
          : null,
    );
  }
}
