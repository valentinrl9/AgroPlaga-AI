import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/session.dart";
import "../../data/repositories/farm_repository.dart";
import "../../data/repositories/scan_repository.dart";
import "../../data/repositories/treatment_repository.dart";
import "../../models/farm.dart";
import "../../models/scan.dart";
import "../widgets/primary_button.dart";
import "../widgets/scan_validation_banner.dart";

class RegisterTreatmentScreen extends StatefulWidget {
  final Scan? scan;

  const RegisterTreatmentScreen({super.key, this.scan});

  @override
  State<RegisterTreatmentScreen> createState() => _RegisterTreatmentScreenState();
}

class _RegisterTreatmentScreenState extends State<RegisterTreatmentScreen> {
  final _repo = TreatmentRepository();
  final _farmRepo = FarmRepository();
  final _scanRepo = ScanRepository();
  List<Farm> _farms = [];
  int? _selectedFarmId;
  Scan? _scan;
  final _productController = TextEditingController();
  final _hoursController = TextEditingController(text: "48");
  final _surfaceController = TextEditingController(text: "5000");
  final _notesController = TextEditingController();

  List<dynamic> _biocides = [];
  String? _selectedRegistry;
  bool _loading = true;
  bool _saving = false;
  bool _ackUnverified = false;
  bool _isEnterprise = false;
  String? _error;
  Map<String, dynamic>? _dosePreview;

  @override
  void initState() {
    super.initState();
    _selectedFarmId = widget.scan?.farmId;
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      _isEnterprise = await Session.hasSiexEnterprise;
      if (widget.scan != null) {
        _scan = await _scanRepo.fetchScan(widget.scan!.id);
      }
      if (_scan?.isRejectedByTech == true) {
        if (mounted) {
          setState(() {
            _loading = false;
            _error = "Este escaneo fue rechazado por el perito. No se puede registrar un tratamiento.";
          });
        }
        return;
      }
      final farms = await _farmRepo.fetchFarms();
      if (!mounted) return;
      setState(() => _farms = farms);
      if (_selectedFarmId == null && farms.isNotEmpty) {
        final withSigpac = farms.where((f) => f.hasSigpac).toList();
        _selectedFarmId = withSigpac.isNotEmpty ? withSigpac.first.id : farms.first.id;
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
    await _loadBiocides();
  }

  @override
  void dispose() {
    _productController.dispose();
    _hoursController.dispose();
    _surfaceController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  String get _plagueKey => _scan?.effectivePlague ?? "tuta absoluta";

  String get _cropKey => _scan?.crop ?? "tomate";

  Future<void> _loadBiocides() async {
    try {
      final list = await _repo.fetchBiocides(plague: _plagueKey, crop: _cropKey);
      if (!mounted) return;
      setState(() {
        _biocides = list;
        _loading = false;
        if (list.isNotEmpty) {
          _selectedRegistry = list.first["registry_no"] as String?;
          _productController.text = list.first["name"] as String? ?? "";
          _hoursController.text = "${list.first["safety_hours"] ?? 48}";
        }
      });
      await _previewDose();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _previewDose() async {
    final registry = _selectedRegistry;
    final surface = double.tryParse(_surfaceController.text.trim());
    if (registry == null || surface == null || surface <= 0) return;
    try {
      final dose = await _repo.calculateDose(
        surfaceM2: surface,
        registryNo: registry,
        plague: _plagueKey,
        crop: _cropKey,
      );
      if (mounted) setState(() => _dosePreview = dose);
    } catch (_) {}
  }

  Future<bool> _confirmUnverified() async {
    if (_scan == null || _scan!.isVerifiedByTech) return true;
    if (_ackUnverified) return true;

    final accepted = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Plaga no verificada"),
        content: Text(
          _isEnterprise
              ? "El diagnóstico «${_scan!.plague}» no ha sido validado por el perito. "
                  "Puedes registrar la carencia local, pero el cuaderno SIEX de cooperativa "
                  "no se generará hasta validación."
              : "El producto MAPA se selecciona para «${_scan!.effectivePlague}» según la IA, "
                  "sin confirmación del perito. Al continuar, asumes la responsabilidad "
                  "de la elección fitosanitaria.",
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text("Cancelar")),
          TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text("Continuar")),
        ],
      ),
    );
    if (accepted == true && mounted) {
      setState(() => _ackUnverified = true);
      return true;
    }
    return false;
  }

  Future<void> _save() async {
    if (_scan?.isRejectedByTech == true) return;
    if (_scan != null && _scan!.isUnverified && !_ackUnverified) {
      final ok = await _confirmUnverified();
      if (!ok) return;
    }

    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      final hours = int.tryParse(_hoursController.text.trim()) ?? 48;
      await _repo.createTreatment({
        "scan_id": _scan?.id,
        "farm_id": _selectedFarmId,
        "product_name": _productController.text.trim(),
        "registry_number": _selectedRegistry,
        "safety_hours": hours,
        "dose_ml": _dosePreview?["dose_ml"],
        "notes": _notesController.text.trim().isEmpty ? null : _notesController.text.trim(),
        if (_scan != null && _scan!.isUnverified) "ack_unverified": true,
      });
      if (!mounted) return;
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scan = _scan;
    final blocked = scan?.isRejectedByTech == true;

    return Scaffold(
      appBar: AppBar(title: const Text("Registrar tratamiento")),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (scan != null) ...[
                    ScanValidationBanner(scan: scan),
                    const SizedBox(height: 12),
                    Text(
                      "Plaga para MAPA: ${scan.effectivePlague} · ${scan.crop}",
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 8),
                  ],
                  Text(
                    "Vademécum MAPA (Registro Fitosanitarios). Orientación técnica — consulte ficha oficial.",
                    style: TextStyle(fontSize: 12, color: NexoColors.textSecondary),
                  ),
                  if (scan != null && scan.isUnverified) ...[
                    const SizedBox(height: 12),
                    CheckboxListTile(
                      value: _ackUnverified,
                      onChanged: blocked
                          ? null
                          : (v) => setState(() => _ackUnverified = v ?? false),
                      controlAffinity: ListTileControlAffinity.leading,
                      contentPadding: EdgeInsets.zero,
                      title: const Text(
                        "Confirmo que aplico el tratamiento bajo mi responsabilidad "
                        "sin validación previa del perito.",
                        style: TextStyle(fontSize: 13),
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  if (_farms.isNotEmpty)
                    DropdownButtonFormField<int>(
                      value: _farms.any((f) => f.id == _selectedFarmId) ? _selectedFarmId : null,
                      decoration: const InputDecoration(labelText: "Finca / invernadero (SIGPAC)"),
                      items: _farms
                          .map(
                            (f) => DropdownMenuItem(
                              value: f.id,
                              child: Text(
                                "${f.name} · SIGPAC ${f.sigpacCode ?? "pendiente"}",
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          )
                          .toList(),
                      onChanged: blocked ? null : (v) => setState(() => _selectedFarmId = v),
                    ),
                  if (_farms.isEmpty)
                    const Text(
                      "Añade una finca con SIGPAC en «Mis fincas» para generar entrada SIEX.",
                      style: TextStyle(color: NexoColors.warningAmber, fontSize: 12),
                    ),
                  const SizedBox(height: 12),
                  if (_biocides.isNotEmpty)
                    DropdownButtonFormField<String>(
                      value: _selectedRegistry,
                      decoration: const InputDecoration(labelText: "Producto MAPA autorizado"),
                      items: _biocides
                          .map(
                            (b) => DropdownMenuItem(
                              value: b["registry_no"] as String,
                              child: Text(b["name"] as String),
                            ),
                          )
                          .toList(),
                      onChanged: blocked
                          ? null
                          : (v) async {
                              setState(() {
                                _selectedRegistry = v;
                                final match =
                                    _biocides.cast<Map<String, dynamic>>().firstWhere((b) => b["registry_no"] == v);
                                _productController.text = match["name"] as String? ?? "";
                                _hoursController.text = "${match["safety_hours"] ?? 48}";
                              });
                              await _previewDose();
                            },
                    ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _productController,
                    enabled: !blocked,
                    decoration: const InputDecoration(labelText: "Nombre producto"),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _surfaceController,
                    enabled: !blocked,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: "Superficie invernadero (m²)"),
                    onSubmitted: (_) => _previewDose(),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _hoursController,
                    enabled: !blocked,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: "Plazo de seguridad (horas)"),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _notesController,
                    enabled: !blocked,
                    decoration: const InputDecoration(labelText: "Notas"),
                    maxLines: 2,
                  ),
                  if (_dosePreview != null) ...[
                    const SizedBox(height: 16),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Text(
                          "Dosis estimada: ${_dosePreview!["dose_ml"]} ml · "
                          "${_dosePreview!["dose_l_ha"]} L/ha",
                        ),
                      ),
                    ),
                  ],
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(_error!, style: const TextStyle(color: NexoColors.errorRed)),
                  ],
                  const SizedBox(height: 20),
                  PrimaryButton(
                    label: _saving ? "Guardando..." : "Registrar y activar carencia",
                    onPressed: blocked || _saving ? null : _save,
                  ),
                ],
              ),
            ),
    );
  }
}
