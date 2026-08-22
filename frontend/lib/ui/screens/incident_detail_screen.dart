import "package:flutter/foundation.dart";
import "package:flutter/material.dart";
import "package:image_picker/image_picker.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../data/repositories/farm_repository.dart";
import "../../data/repositories/incident_repository.dart";
import "../../data/repositories/scan_repository.dart";
import "../../data/repositories/siex_repository.dart";
import "../../data/repositories/treatment_repository.dart";
import "../../ml/plaga_classifier.dart";
import "../../models/pest_incident.dart";
import "../../models/scan.dart";
import "../widgets/primary_button.dart";
import "../widgets/sigpac_siex_banner.dart";

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
  final _farmRepo = FarmRepository();
  final _siexRepo = SiexRepository();
  final _imagePicker = ImagePicker();

  late Future<PestIncident> _future;
  List<dynamic> _biocides = [];
  List<Scan> _scans = [];
  String? _selectedRegistry;
  final _surfaceController = TextEditingController();
  final _evalScanController = TextEditingController();
  bool _ackUnverified = false;
  bool _treatFullFarm = true;
  double _affectedPercent = 30;
  bool _loadingBiocides = false;
  bool _loadingScans = false;
  bool _capturingEvalPhoto = false;
  bool _busy = false;
  bool _hasSiexAccess = false;
  bool _farmMissingSigpac = false;
  String? _error;
  Map<String, dynamic>? _dosePreview;
  String? _viewStage;
  final _stageBarScroll = ScrollController();

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
    "prescription": "Prescripción",
    "treatment": "Tratamiento",
    "evaluation": "Evaluación",
    "closed": "Cierre",
  };

  static const _stageHints = {
    "detection": "Confirma el diagnóstico del escaneo inicial.",
    "diagnosis": "Elige producto MAPA y calcula la dosis.",
    "prescription": "Registra la aplicación en campo y activa carencia.",
    "treatment": "Seguimiento del tratamiento aplicado.",
    "evaluation": "Compara con un nuevo escaneo y valora la evolución.",
    "closed": "Resumen final de la incidencia.",
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
    _stageBarScroll.dispose();
    super.dispose();
  }

  void _reload() {
    setState(() {
      _future = _load();
    });
  }

  Future<PestIncident> _load() async {
    final incident = await _incidentRepo.fetchIncident(widget.incidentId);
    if (!mounted) return incident;

    final hasSiex = await _siexRepo.hasAccess();
    var farmMissingSigpac = false;
    if (hasSiex && incident.farmId != null) {
      try {
        final farms = await _farmRepo.fetchFarms();
        for (final farm in farms) {
          if (farm.id == incident.farmId) {
            farmMissingSigpac = !farm.hasSigpac;
            break;
          }
        }
      } catch (_) {}
    }

    setState(() {
      _hasSiexAccess = hasSiex;
      _farmMissingSigpac = farmMissingSigpac;
      _viewStage ??= incident.stage;
      if (_viewStage != null && _stages.indexOf(_viewStage!) > incident.stageIndex) {
        _viewStage = incident.stage;
      }
      _initSurfaceFromIncident(incident);
    });
    _scrollStageBarTo(_viewStage ?? incident.stage);

    await _ensureStageData(incident, _viewStage ?? incident.stage);
    return incident;
  }

  Future<void> _ensureStageData(PestIncident incident, String stage) async {
    if (stage == "diagnosis" || stage == "prescription") {
      if (_biocides.isEmpty && !_loadingBiocides) {
        await _loadBiocides(incident);
      }
    }
    if (stage == "evaluation" && !_loadingScans) {
      await _loadScans(incident);
    }
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
        _selectedRegistry ??= incident.prescriptionRegistryNumber;
        if (_selectedRegistry == null && list.isNotEmpty) {
          final biological = list.cast<Map<String, dynamic>>().where((b) => b["is_biological"] == true);
          _selectedRegistry = biological.isNotEmpty
              ? biological.first["registry_no"] as String?
              : list.first["registry_no"] as String?;
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

  static const _severityLabels = {1: "Leve", 2: "Moderado", 3: "Alto"};

  String _severityLabel(int level) => _severityLabels[level.clamp(1, 3)] ?? "Moderado";

  Future<void> _captureEvaluationPhoto(PestIncident incident, ImageSource source) async {
    final file = await _imagePicker.pickImage(source: source, imageQuality: 85, maxWidth: 1024);
    if (file == null || !mounted) return;

    setState(() {
      _capturingEvalPhoto = true;
      _error = null;
    });

    try {
      final bytes = await file.readAsBytes();
      final diagnosis = await classifyPlaga(bytes);
      final scan = await _scanRepo.createScan(
        crop: incident.crop,
        plague: incident.plague,
        severity: _severityLabel(diagnosis.suggestedSeverity),
        confidence: diagnosis.confidence,
        farmId: incident.farmId,
      );
      await _incidentRepo.attachEvaluationScan(incident.id, scan.id);
      if (!mounted) return;
      setState(() {
        _evalScanController.text = "${scan.id}";
        _scans = [scan, ..._scans.where((s) => s.id != scan.id)];
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Foto comparativa guardada y adjunta a la incidencia."),
          backgroundColor: NexoColors.bioGreen,
        ),
      );
      _reload();
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _capturingEvalPhoto = false);
    }
  }

  Future<void> _loadScans(PestIncident incident) async {
    setState(() => _loadingScans = true);
    try {
      final list = await _scanRepo.fetchScans();
      if (!mounted) return;
      setState(() {
        _scans = list;
        _loadingScans = false;
        if (incident.evaluationScanId != null) {
          _evalScanController.text = "${incident.evaluationScanId}";
        }
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          _loadingScans = false;
          _error = e.toString();
        });
      }
    }
  }

  void _initSurfaceFromIncident(PestIncident incident) {
    if (incident.prescriptionSurfaceM2 != null) {
      _surfaceController.text = incident.prescriptionSurfaceM2!.toStringAsFixed(0);
      if (incident.farmSurfaceM2 != null && incident.prescriptionSurfaceM2! < incident.farmSurfaceM2!) {
        _treatFullFarm = false;
        _affectedPercent = (incident.prescriptionSurfaceM2! / incident.farmSurfaceM2! * 100).clamp(5, 100);
      }
      return;
    }
    if (incident.farmSurfaceM2 != null && _surfaceController.text.trim().isEmpty) {
      _surfaceController.text = incident.farmSurfaceM2!.toStringAsFixed(0);
    }
  }

  void _applySurfaceMode(PestIncident incident, {required bool fullFarm}) {
    setState(() {
      _treatFullFarm = fullFarm;
      final farmSurface = incident.farmSurfaceM2;
      if (fullFarm && farmSurface != null) {
        _surfaceController.text = farmSurface.toStringAsFixed(0);
      } else if (!fullFarm && farmSurface != null) {
        final partial = farmSurface * (_affectedPercent / 100);
        _surfaceController.text = partial.toStringAsFixed(0);
      }
    });
    _previewDose(incident);
  }

  void _updateAffectedPercent(PestIncident incident, double percent) {
    setState(() {
      _affectedPercent = percent;
      final farmSurface = incident.farmSurfaceM2;
      if (!_treatFullFarm && farmSurface != null) {
        _surfaceController.text = (farmSurface * (percent / 100)).toStringAsFixed(0);
      }
    });
    _previewDose(incident);
  }

  Widget _productTypeChip(Map<String, dynamic> product) {
    final biological = product["is_biological"] == true;
    final color = biological ? NexoColors.bioGreen : NexoColors.warningAmber;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        biological ? "Biológico" : "Químico",
        style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w600),
      ),
    );
  }

  Widget _buildProductOptions(PestIncident incident, {required bool editable}) {
    if (_loadingBiocides) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 12),
        child: LinearProgressIndicator(),
      );
    }
    if (_biocides.isEmpty) {
      return Text(
        "Sin productos MAPA para ${incident.plague} / ${incident.crop}. "
        "Revisa el catálogo o sincroniza MAPA.",
        style: const TextStyle(color: NexoColors.warningAmber),
      );
    }

    final biological = _biocides.where((b) => b["is_biological"] == true).toList();
    final chemical = _biocides.where((b) => b["is_biological"] != true).toList();

    Widget section(String title, List<dynamic> items) {
      if (items.isEmpty) return const SizedBox.shrink();
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: NexoColors.textSecondary)),
          const SizedBox(height: 8),
          ...items.map((raw) {
            final product = Map<String, dynamic>.from(raw as Map);
            final registry = product["registry_no"] as String;
            final selected = _selectedRegistry == registry;
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: !editable || _busy
                      ? null
                      : () async {
                          setState(() => _selectedRegistry = registry);
                          await _previewDose(incident);
                        },
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: selected ? NexoColors.bioGreen : NexoColors.borderSubtle,
                        width: selected ? 2 : 1,
                      ),
                      color: selected ? NexoColors.bioGreen.withValues(alpha: 0.08) : NexoColors.surfaceElevated,
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(
                          selected ? Icons.radio_button_checked : Icons.radio_button_off,
                          color: selected ? NexoColors.bioGreen : NexoColors.textSecondary,
                          size: 20,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(product["name"] as String, style: const TextStyle(fontWeight: FontWeight.w600)),
                              const SizedBox(height: 4),
                              Text(
                                "${product["active_substance"] ?? "—"} · ${product["dose_min_l_ha"]}-${product["dose_max_l_ha"]} L/ha",
                                style: const TextStyle(fontSize: 12, color: NexoColors.textSecondary),
                              ),
                              const SizedBox(height: 6),
                              Row(
                                children: [
                                  _productTypeChip(product),
                                  const SizedBox(width: 8),
                                  Text(
                                    "Carencia ${product["safety_hours"] ?? "—"} h",
                                    style: const TextStyle(fontSize: 11, color: NexoColors.textSecondary),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          }),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          "Elige entre las opciones autorizadas MAPA para esta plaga y cultivo. "
          "Las biológicas aparecen primero.",
          style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
        ),
        const SizedBox(height: 12),
        section("Tratamientos biológicos", biological),
        if (biological.isNotEmpty && chemical.isNotEmpty) const SizedBox(height: 12),
        section("Tratamientos químicos", chemical),
      ],
    );
  }

  Widget _buildSurfaceSection(PestIncident incident, {required bool editable}) {
    final farmSurface = incident.farmSurfaceM2;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (farmSurface != null) ...[
          _infoRow("Superficie finca", "${farmSurface.toStringAsFixed(0)} m²"),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              ChoiceChip(
                label: const Text("Toda la finca"),
                selected: _treatFullFarm,
                onSelected: !editable || _busy
                    ? null
                    : (_) => _applySurfaceMode(incident, fullFarm: true),
              ),
              ChoiceChip(
                label: const Text("Solo zona afectada"),
                selected: !_treatFullFarm,
                onSelected: !editable || _busy
                    ? null
                    : (_) => _applySurfaceMode(incident, fullFarm: false),
              ),
            ],
          ),
          if (!_treatFullFarm) ...[
            const SizedBox(height: 8),
            Text(
              "Zona afectada estimada: ${_affectedPercent.toStringAsFixed(0)} % "
              "(${((farmSurface * _affectedPercent) / 100).toStringAsFixed(0)} m²)",
              style: const TextStyle(fontSize: 12, color: NexoColors.textSecondary),
            ),
            Slider(
              value: _affectedPercent,
              min: 5,
              max: 100,
              divisions: 19,
              label: "${_affectedPercent.toStringAsFixed(0)} %",
              onChanged: !editable || _busy ? null : (v) => _updateAffectedPercent(incident, v),
            ),
          ],
          const SizedBox(height: 12),
        ] else ...[
          const Text(
            "No hay superficie registrada en la finca. Indícala abajo o actualiza «Mis fincas».",
            style: TextStyle(color: NexoColors.warningAmber, fontSize: 12),
          ),
          const SizedBox(height: 8),
        ],
        TextField(
          controller: _surfaceController,
          enabled: editable && !_busy,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: "Superficie a tratar (m²)",
            helperText: farmSurface != null
                ? "Puedes ajustar manualmente si el foco es parcial"
                : "Usada para calcular la dosis en ml",
          ),
          onChanged: (_) => _previewDose(incident),
        ),
      ],
    );
  }

  Widget _buildDosePreview() {
    if (_dosePreview == null) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: NexoColors.techCyan.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        "Dosis estimada: ${_dosePreview!["dose_ml"]} ml · "
        "${_dosePreview!["dose_l_ha"]} L/ha · "
        "Carencia ${_dosePreview!["safety_hours"] ?? "—"} h",
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
    );
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
      setState(() => _viewStage = null);
      _reload();
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _selectStage(PestIncident incident, String stage) async {
    if (_stages.indexOf(stage) > incident.stageIndex) return;
    setState(() => _viewStage = stage);
    await _ensureStageData(incident, stage);
    _scrollStageBarTo(stage);
  }

  void _scrollStageBarTo(String stage) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_stageBarScroll.hasClients) return;
      final index = _stages.indexOf(stage);
      if (index < 0) return;
      const chipWidth = 118.0;
      final target = (index * chipWidth).clamp(0.0, _stageBarScroll.position.maxScrollExtent);
      _stageBarScroll.animateTo(
        target,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    });
  }

  bool _isStageUnlocked(PestIncident incident, String stage) {
    return _stages.indexOf(stage) <= incident.stageIndex;
  }

  bool _isCurrentStage(PestIncident incident, String stage) {
    return incident.stage == stage;
  }

  bool _canAct(PestIncident incident, String stage) {
    return incident.isActive && _isCurrentStage(incident, stage);
  }

  Widget _infoCard({required String title, required List<Widget> children}) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: const TextStyle(color: NexoColors.textSecondary, fontSize: 13)),
          ),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 14))),
        ],
      ),
    );
  }

  Widget _stageBar(PestIncident incident) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: NexoColors.surfaceCard,
        border: Border(bottom: BorderSide(color: NexoColors.borderSubtle.withValues(alpha: 0.5))),
      ),
      child: SingleChildScrollView(
        controller: _stageBarScroll,
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            for (var i = 0; i < _stages.length; i++) ...[
              if (i > 0)
                Container(
                  width: 20,
                  height: 2,
                  margin: const EdgeInsets.symmetric(horizontal: 2),
                  color: _stages.indexOf(_stages[i]) <= incident.stageIndex
                      ? NexoColors.bioGreen
                      : NexoColors.borderSubtle,
                ),
              _stageChip(incident, _stages[i]),
            ],
          ],
        ),
      ),
    );
  }

  Widget _stageChip(PestIncident incident, String stage) {
    final unlocked = _isStageUnlocked(incident, stage);
    final selected = (_viewStage ?? incident.stage) == stage;
    final current = _isCurrentStage(incident, stage);
    final done = _stages.indexOf(stage) < incident.stageIndex || incident.stage == "closed";

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: unlocked ? () => _selectStage(incident, stage) : null,
        borderRadius: BorderRadius.circular(20),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: selected
                ? NexoColors.bioGreen.withValues(alpha: 0.2)
                : unlocked
                    ? NexoColors.surfaceElevated
                    : NexoColors.surfaceBase,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: current
                  ? NexoColors.bioGreen
                  : selected
                      ? NexoColors.techCyan
                      : NexoColors.borderSubtle,
              width: current ? 2 : 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (done)
                const Icon(Icons.check_circle, size: 16, color: NexoColors.bioGreen)
              else if (current)
                const Icon(Icons.radio_button_checked, size: 16, color: NexoColors.bioGreen)
              else
                Icon(Icons.circle_outlined, size: 16, color: unlocked ? NexoColors.textSecondary : NexoColors.borderSubtle),
              const SizedBox(width: 6),
              Text(
                _stageLabels[stage] ?? stage,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: selected || current ? FontWeight.w600 : FontWeight.normal,
                  color: unlocked ? NexoColors.textPrimary : NexoColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _stageHeader(PestIncident incident, String stage) {
    final acting = _canAct(incident, stage);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          _stageLabels[stage] ?? stage,
          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 6),
        Text(
          _stageHints[stage] ?? "",
          style: const TextStyle(color: NexoColors.textSecondary, fontSize: 14),
        ),
        if (acting) ...[
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: NexoColors.bioGreen.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              "Etapa actual — completa las acciones de abajo",
              style: TextStyle(fontSize: 12, color: NexoColors.bioGreen, fontWeight: FontWeight.w600),
            ),
          ),
        ] else if (_stages.indexOf(stage) < incident.stageIndex) ...[
          const SizedBox(height: 8),
          Text(
            "Etapa completada (solo consulta)",
            style: TextStyle(fontSize: 12, color: NexoColors.textSecondary.withValues(alpha: 0.9)),
          ),
        ],
      ],
    );
  }

  Widget _buildDetectionView(PestIncident incident) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _stageHeader(incident, "detection"),
        const SizedBox(height: 20),
        _infoCard(
          title: "Escaneo de detección",
          children: [
            _infoRow("Plaga", incident.plague),
            _infoRow("Cultivo", incident.crop),
            _infoRow("Severidad", "${incident.severity}"),
            _infoRow("Finca", incident.farmName ?? "—"),
            _infoRow("Municipio", incident.zoneName ?? "—"),
            _infoRow("Escaneo #", "${incident.scanId}"),
            _infoRow("Abierta", _fmtDate(incident.createdAt)),
          ],
        ),
        if (_canAct(incident, "detection")) ...[
          const SizedBox(height: 24),
          PrimaryButton(
            label: "Confirmar diagnóstico y continuar",
            onPressed: _busy ? null : () => _run(() => _incidentRepo.advance(incident.id)),
          ),
        ],
      ],
    );
  }

  Widget _buildDiagnosisView(PestIncident incident) {
    final editable = _canAct(incident, "diagnosis");
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _stageHeader(incident, "diagnosis"),
        const SizedBox(height: 20),
        _infoCard(
          title: "Contexto fitosanitario",
          children: [
            _infoRow("Plaga MAPA", incident.plague),
            _infoRow("Cultivo", incident.crop),
            if (incident.farmSurfaceM2 != null)
              _infoRow("Superficie finca registrada", "${incident.farmSurfaceM2!.toStringAsFixed(0)} m²"),
          ],
        ),
        const SizedBox(height: 16),
        _infoCard(
          title: "Opciones de tratamiento MAPA",
          children: [
            _buildProductOptions(incident, editable: editable),
          ],
        ),
        const SizedBox(height: 16),
        _infoCard(
          title: "Superficie y dosis",
          children: [
            _buildSurfaceSection(incident, editable: editable),
            const SizedBox(height: 16),
            _buildDosePreview(),
          ],
        ),
        if (editable) ...[
          const SizedBox(height: 24),
          PrimaryButton(
            label: "Guardar prescripción MAPA",
            onPressed: _busy || _selectedRegistry == null
                ? null
                : () => _run(() async {
                      final surface = double.tryParse(_surfaceController.text.trim());
                      if (surface == null || surface <= 0) {
                        throw Exception("Indica la superficie a tratar en m²");
                      }
                      await _incidentRepo.prescribe(
                        incident.id,
                        registryNo: _selectedRegistry!,
                        surfaceM2: surface,
                      );
                    }),
          ),
        ] else if (incident.prescriptionProductName != null) ...[
          const SizedBox(height: 16),
          _infoCard(
            title: "Prescripción registrada",
            children: [
              _infoRow("Producto", incident.prescriptionProductName!),
              _infoRow("Registro", incident.prescriptionRegistryNumber ?? "—"),
              if (incident.prescriptionActiveSubstance != null)
                _infoRow("Principio activo", incident.prescriptionActiveSubstance!),
              _infoRow("Superficie tratada", "${incident.prescriptionSurfaceM2?.toStringAsFixed(0) ?? "—"} m²"),
              _infoRow("Dosis", "${incident.prescriptionDoseMl?.toStringAsFixed(1) ?? "—"} ml"),
              _infoRow("Carencia", "${incident.prescriptionSafetyHours ?? "—"} h"),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildPrescriptionView(PestIncident incident) {
    final editable = _canAct(incident, "prescription");
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _stageHeader(incident, "prescription"),
        const SizedBox(height: 20),
        _infoCard(
          title: "Prescripción MAPA seleccionada",
          children: [
            _infoRow("Producto", incident.prescriptionProductName ?? "Pendiente"),
            _infoRow("Registro", incident.prescriptionRegistryNumber ?? "—"),
            if (incident.prescriptionActiveSubstance != null)
              _infoRow("Principio activo", incident.prescriptionActiveSubstance!),
            _infoRow("Superficie a tratar", "${incident.prescriptionSurfaceM2?.toStringAsFixed(0) ?? "—"} m²"),
            _infoRow("Dosis calculada", "${incident.prescriptionDoseMl?.toStringAsFixed(1) ?? "—"} ml"),
            _infoRow("Carencia", "${incident.prescriptionSafetyHours ?? "—"} horas"),
          ],
        ),
        if (editable) ...[
          const SizedBox(height: 16),
          _infoCard(
            title: "¿Cambiar producto o superficie?",
            children: [
              const Text(
                "Puedes elegir otra opción MAPA o ajustar la zona a tratar antes de registrar la aplicación.",
                style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
              ),
              const SizedBox(height: 12),
              _buildProductOptions(incident, editable: true),
              const SizedBox(height: 12),
              _buildSurfaceSection(incident, editable: true),
              const SizedBox(height: 12),
              _buildDosePreview(),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: _busy || _selectedRegistry == null
                    ? null
                    : () => _run(() async {
                          final surface = double.tryParse(_surfaceController.text.trim());
                          if (surface == null || surface <= 0) {
                            throw Exception("Indica la superficie a tratar en m²");
                          }
                          await _incidentRepo.prescribe(
                            incident.id,
                            registryNo: _selectedRegistry!,
                            surfaceM2: surface,
                          );
                        }),
                child: const Text("Actualizar prescripción"),
              ),
            ],
          ),
          const SizedBox(height: 20),
          if (_hasSiexAccess && _farmMissingSigpac) ...[
            const SigpacSiexBanner(compact: true),
            const SizedBox(height: 12),
          ],
          _infoCard(
            title: "Aplicación en campo",
            children: [
              const Text(
                "Al registrar el tratamiento se crea la carencia en tu cuaderno de campo.",
                style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
              ),
              const SizedBox(height: 12),
              CheckboxListTile(
                value: _ackUnverified,
                onChanged: _busy ? null : (v) => setState(() => _ackUnverified = v ?? false),
                controlAffinity: ListTileControlAffinity.leading,
                contentPadding: EdgeInsets.zero,
                title: const Text(
                  "Confirmo la aplicación bajo mi responsabilidad (plaga no verificada por perito).",
                  style: TextStyle(fontSize: 13),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          PrimaryButton(
            label: "Registrar tratamiento y activar carencia",
            onPressed: _busy
                ? null
                : () => _run(() async {
                      final updated = await _incidentRepo.applyTreatment(
                        incident.id,
                        ackUnverified: _ackUnverified,
                      );
                      if (!mounted) return;
                      final msg = updated.siexMessage;
                      if (msg != null && msg.isNotEmpty) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(msg),
                            backgroundColor: updated.siexEntryId != null
                                ? NexoColors.bioGreen
                                : NexoColors.warningAmber,
                            action: _farmMissingSigpac
                                ? SnackBarAction(
                                    label: "Mis fincas",
                                    onPressed: () => Navigator.pushNamed(context, Routes.farms),
                                  )
                                : null,
                          ),
                        );
                      }
                    }),
          ),
        ],
      ],
    );
  }

  Widget _buildTreatmentView(PestIncident incident) {
    final t = incident.treatment;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _stageHeader(incident, "treatment"),
        const SizedBox(height: 20),
        _infoCard(
          title: "Tratamiento activo",
          children: [
            if (t != null) ...[
              _infoRow("Producto", t.productName),
              if (incident.prescriptionActiveSubstance != null)
                _infoRow("Principio activo", incident.prescriptionActiveSubstance!),
              if (incident.prescriptionSurfaceM2 != null)
                _infoRow("Superficie tratada", "${incident.prescriptionSurfaceM2!.toStringAsFixed(0)} m²"),
              if (incident.prescriptionDoseMl != null)
                _infoRow("Dosis aplicada", "${incident.prescriptionDoseMl!.toStringAsFixed(1)} ml"),
              _infoRow("Carencia", "${t.safetyHours} h"),
              _infoRow(
                "Estado",
                t.harvestAllowed
                    ? "Cosecha permitida"
                    : "${t.hoursRemaining?.toStringAsFixed(0) ?? "—"} h restantes",
              ),
            ] else ...[
              _infoRow("Producto", incident.prescriptionProductName ?? "—"),
              const Text("Tratamiento registrado", style: TextStyle(color: NexoColors.textSecondary)),
            ],
          ],
        ),
        if (_canAct(incident, "treatment")) ...[
          const SizedBox(height: 24),
          PrimaryButton(
            label: "Iniciar evaluación de seguimiento",
            onPressed: _busy ? null : () => _run(() => _incidentRepo.startEvaluation(incident.id)),
          ),
          const SizedBox(height: 12),
          OutlinedButton(
            onPressed: _busy ? null : () => _run(() => _incidentRepo.close(incident.id, outcome: "resolved")),
            child: const Text("Cerrar incidencia como resuelta"),
          ),
        ],
      ],
    );
  }

  Widget _buildEvaluationView(PestIncident incident) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _stageHeader(incident, "evaluation"),
        const SizedBox(height: 20),
        if (_loadingScans)
          const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()))
        else ...[
          _infoCard(
            title: "Foto comparativa",
            children: [
              const Text(
                "Toma una foto ahora o elige una de la galería para comparar con el escaneo inicial.",
                style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
              ),
              if (_canAct(incident, "evaluation")) ...[
                const SizedBox(height: 12),
                if (_capturingEvalPhoto)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 12),
                    child: Column(
                      children: [
                        LinearProgressIndicator(),
                        SizedBox(height: 8),
                        Text("Analizando y guardando foto...", style: TextStyle(fontSize: 13)),
                      ],
                    ),
                  )
                else ...[
                  if (!kIsWeb)
                    PrimaryButton(
                      label: "Tomar foto ahora",
                      onPressed: _busy
                          ? null
                          : () => _captureEvaluationPhoto(incident, ImageSource.camera),
                    ),
                  if (!kIsWeb) const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: _busy
                        ? null
                        : () => _captureEvaluationPhoto(incident, ImageSource.gallery),
                    icon: const Icon(Icons.photo_library_outlined),
                    label: Text(kIsWeb ? "Seleccionar imagen" : "Elegir de galería"),
                  ),
                ],
              ],
              if (incident.evaluationScanId != null)
                Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Text(
                    "Adjunto actual: escaneo #${incident.evaluationScanId}",
                    style: const TextStyle(color: NexoColors.bioGreen, fontSize: 13),
                  ),
                ),
              if (_scans.where((s) => s.id != incident.scanId).isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text(
                  "O usa un escaneo anterior",
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<int>(
                  key: ValueKey(_evalScanController.text),
                  initialValue: int.tryParse(_evalScanController.text),
                  decoration: const InputDecoration(labelText: "Escaneo comparativo"),
                  items: _scans
                      .where((s) => s.id != incident.scanId)
                      .map(
                        (s) => DropdownMenuItem(
                          value: s.id,
                          child: Text(
                            "#${s.id} · ${s.plague} · ${s.createdAt?.toLocal().toString().split(".").first ?? "—"}",
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      )
                      .toList(),
                  onChanged: !_canAct(incident, "evaluation") || _busy || _capturingEvalPhoto
                      ? null
                      : (v) {
                          if (v != null) setState(() => _evalScanController.text = "$v");
                        },
                ),
                if (_canAct(incident, "evaluation")) ...[
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: _busy || _capturingEvalPhoto
                        ? null
                        : () => _run(() async {
                              final scanId = int.tryParse(_evalScanController.text.trim());
                              if (scanId == null) throw Exception("Selecciona un escaneo comparativo");
                              await _incidentRepo.attachEvaluationScan(incident.id, scanId);
                            }),
                    icon: const Icon(Icons.attach_file),
                    label: const Text("Adjuntar escaneo seleccionado"),
                  ),
                ],
              ],
            ],
          ),
          if (_canAct(incident, "evaluation")) ...[
            const SizedBox(height: 20),
            _infoCard(
              title: "¿Ha mejorado la plaga?",
              children: [
                PrimaryButton(
                  label: "Sí, hay mejora → cerrar resuelto",
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
                const SizedBox(height: 10),
                OutlinedButton(
                  onPressed: _busy ? null : () => _run(() => _incidentRepo.evaluate(incident.id, improved: false)),
                  child: const Text("No hay mejora → volver a tratamiento"),
                ),
                const SizedBox(height: 10),
                TextButton(
                  onPressed: _busy ? null : () => _run(() => _incidentRepo.close(incident.id, outcome: "crop_lost")),
                  child: const Text("Marcar cosecha perdida", style: TextStyle(color: NexoColors.errorRed)),
                ),
              ],
            ),
          ],
        ],
      ],
    );
  }

  Widget _buildClosedView(PestIncident incident) {
    final resolved = incident.closureOutcome == "resolved";
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _stageHeader(incident, "closed"),
        const SizedBox(height: 20),
        _infoCard(
          title: "Resumen de cierre",
          children: [
            _infoRow(
              "Resultado",
              resolved ? "Resuelto" : incident.closureOutcome == "crop_lost" ? "Cosecha perdida" : "—",
            ),
            if (incident.closedAt != null) _infoRow("Cerrada", _fmtDate(incident.closedAt!)),
            if (incident.prescriptionProductName != null)
              _infoRow("Tratamiento", incident.prescriptionProductName!),
            if (incident.evaluationScanId != null)
              _infoRow("Escaneo eval.", "#${incident.evaluationScanId}"),
          ],
        ),
        const SizedBox(height: 24),
        OutlinedButton(
          onPressed: () => Navigator.pop(context, true),
          child: const Text("Volver al listado"),
        ),
      ],
    );
  }

  Widget _buildStageContent(PestIncident incident) {
    final stage = _viewStage ?? incident.stage;
    switch (stage) {
      case "detection":
        return _buildDetectionView(incident);
      case "diagnosis":
        return _buildDiagnosisView(incident);
      case "prescription":
        return _buildPrescriptionView(incident);
      case "treatment":
        return _buildTreatmentView(incident);
      case "evaluation":
        return _buildEvaluationView(incident);
      case "closed":
        return _buildClosedView(incident);
      default:
        return const SizedBox.shrink();
    }
  }

  String _fmtDate(DateTime dt) {
    final local = dt.toLocal();
    return "${local.day.toString().padLeft(2, "0")}/${local.month.toString().padLeft(2, "0")}/${local.year} "
        "${local.hour.toString().padLeft(2, "0")}:${local.minute.toString().padLeft(2, "0")}";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("CRM incidencia"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _busy ? null : _reload,
            tooltip: "Actualizar",
          ),
        ],
      ),
      body: FutureBuilder<PestIncident>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting && !snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || !snapshot.hasData) {
            return Center(child: Text("Error: ${snapshot.error ?? "Incidencia no encontrada"}"));
          }

          final incident = snapshot.data!;
          final viewStage = _viewStage ?? incident.stage;

          return Stack(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                    child: Text(
                      "${incident.plague} · ${incident.crop}",
                      style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 4, 16, 0),
                    child: Text(
                      "${incident.farmName ?? "Unidad"} · ${incident.zoneName ?? "Municipio"}",
                      style: const TextStyle(color: NexoColors.textSecondary, fontSize: 13),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(height: 8),
                  _stageBar(incident),
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(_error!, style: const TextStyle(color: NexoColors.errorRed)),
                    ),
                  Expanded(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
                      child: _buildStageContent(incident),
                    ),
                  ),
                ],
              ),
              if (_busy)
                Positioned.fill(
                  child: ColoredBox(
                    color: Colors.black26,
                    child: const Center(child: CircularProgressIndicator()),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}