import "package:flutter/foundation.dart";
import "package:flutter/material.dart";
import "package:image_picker/image_picker.dart";

import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/farm_repository.dart";
import "../../data/repositories/scan_repository.dart";
import "../../models/farm.dart";
import "../../models/scan.dart";
import "../../ml/plaga_classifier.dart";
import "../widgets/primary_button.dart";
import "../widgets/severity_badge.dart";

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final _scanRepository = ScanRepository();
  final _farmRepository = FarmRepository();
  final _picker = ImagePicker();

  String _crop = "Tomate";
  Uint8List? _imageBytes;
  PlagaResult? _diagnosis;
  int _severityLevel = 2;
  int? _selectedFarmId;
  List<Farm> _farms = [];
  bool _farmsLoading = false;
  bool _isAnalyzing = false;
  bool _isSaving = false;
  bool _shareWithTech = false;
  String? _errorMessage;

  static const _crops = ["Tomate", "Pimiento", "Calabacín", "Pepino", "Berenjena", "Lechuga"];
  static const _severityOptions = {1: "Leve", 2: "Moderado", 3: "Alto"};

  bool get _isBusy => _isAnalyzing || _isSaving;

  @override
  void initState() {
    super.initState();
    _loadFarms();
  }

  Future<void> _loadFarms() async {
    setState(() => _farmsLoading = true);
    try {
      final hasSession = await Session.restore();
      if (!hasSession) return;
      final farms = await _farmRepository.fetchFarms();
      if (!mounted) return;
      setState(() {
        _farms = farms;
        if (_selectedFarmId != null && !farms.any((f) => f.id == _selectedFarmId)) {
          _selectedFarmId = null;
        }
      });
    } catch (_) {
      // Sin fincas o sin sesión: el escaneo sigue siendo válido sin vincular finca.
    } finally {
      if (mounted) setState(() => _farmsLoading = false);
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    setState(() {
      _errorMessage = null;
      _diagnosis = null;
    });

    try {
      final file = await _picker.pickImage(source: source, imageQuality: 85, maxWidth: 1024);
      if (file == null) return;

      final bytes = await file.readAsBytes();
      if (!mounted) return;
      setState(() => _imageBytes = bytes);
      await _runAnalysis(bytes);
    } catch (error) {
      if (!mounted) return;
      setState(() => _errorMessage = "No se pudo capturar la imagen: $error");
    }
  }

  Future<void> _runAnalysis(Uint8List bytes) async {
    setState(() {
      _isAnalyzing = true;
      _errorMessage = null;
    });

    try {
      final result = await classifyPlaga(bytes);
      if (!mounted) return;
      setState(() {
        _diagnosis = result;
        _severityLevel = result.suggestedSeverity;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() => _errorMessage = "Error en el análisis IA: $error");
    } finally {
      if (mounted) setState(() => _isAnalyzing = false);
    }
  }

  Future<void> _saveScan() async {
    if (_diagnosis == null) {
      setState(() => _errorMessage = "Primero captura y analiza una hoja.");
      return;
    }

    if (_shareWithTech && _imageBytes == null) {
      setState(() => _errorMessage = "Para compartir con el técnico necesitas una foto.");
      return;
    }

    final hasSession = await Session.restore();
    if (!hasSession) {
      if (!mounted) return;
      final proceed = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text("Inicia sesión"),
          content: const Text("Necesitas una cuenta para guardar el diagnóstico y ver recomendaciones."),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text("Cancelar")),
            TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text("Ir a login")),
          ],
        ),
      );
      if (proceed == true && mounted) {
        Navigator.pushReplacementNamed(context, Routes.login);
      }
      return;
    }

    setState(() {
      _isSaving = true;
      _errorMessage = null;
    });

    try {
      final Scan scan;
      if (_shareWithTech && _imageBytes != null) {
        scan = await _scanRepository.createScanWithImage(
          crop: _crop,
          plague: _diagnosis!.plague,
          severity: _severityOptions[_severityLevel]!,
          confidence: _diagnosis!.confidence,
          farmId: _selectedFarmId,
          imageBytes: _imageBytes!.toList(),
        );
      } else {
        scan = await _scanRepository.createScan(
          crop: _crop,
          plague: _diagnosis!.plague,
          severity: _severityOptions[_severityLevel]!,
          confidence: _diagnosis!.confidence,
          farmId: _selectedFarmId,
        );
      }

      if (!mounted) return;
      Navigator.pushReplacementNamed(context, Routes.result, arguments: scan);
    } catch (error) {
      final msg = error.toString();
      if (msg.contains("401")) {
        if (!mounted) return;
        Navigator.pushReplacementNamed(context, Routes.login);
        return;
      }
      if (mounted) setState(() => _errorMessage = "Error al guardar escaneo: $error");
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("PlagaScan")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Enfoca una hoja afectada, con buena luz y a menos de 20 cm.",
              style: TextStyle(fontSize: 15, color: Color(0xFF424242)),
            ),
            if (kIsWeb)
              const Padding(
                padding: EdgeInsets.only(top: 8),
                child: Text(
                  "Web: análisis heurístico. En Android/iOS se usa el modelo TFLite local.",
                  style: TextStyle(fontSize: 12, color: Color(0xFF757575)),
                ),
              ),
            const SizedBox(height: 16),
            _ImagePreview(
              imageBytes: _imageBytes,
              isAnalyzing: _isAnalyzing,
            ),
            const SizedBox(height: 16),
            if (!kIsWeb)
              PrimaryButton(
                label: "Tomar foto",
                onPressed: _isBusy ? null : () => _pickImage(ImageSource.camera),
              ),
            if (!kIsWeb) const SizedBox(height: 8),
            PrimaryButton(
              label: kIsWeb ? "Seleccionar imagen" : "Elegir de galería",
              onPressed: _isBusy ? null : () => _pickImage(ImageSource.gallery),
            ),
            const SizedBox(height: 20),
            InputDecorator(
              decoration: const InputDecoration(
                labelText: "Cultivo",
                border: OutlineInputBorder(),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  isExpanded: true,
                  value: _crop,
                  items: _crops.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                  onChanged: _isBusy ? null : (v) => setState(() => _crop = v ?? _crop),
                ),
              ),
            ),
            if (_diagnosis != null) ...[
              const SizedBox(height: 20),
              Card(
                color: Colors.white,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Diagnóstico IA",
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        _diagnosis!.plague,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFFC62828),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text("Confianza: ${_diagnosis!.confidencePercent}"),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          const Text("Severidad sugerida: "),
                          SeverityBadge(severity: _severityLevel.toString()),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        "Modelo: ${_diagnosis!.modelVersion}",
                        style: const TextStyle(fontSize: 12, color: Color(0xFF757575)),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              if (_farms.isNotEmpty)
                InputDecorator(
                  decoration: const InputDecoration(
                    labelText: "Finca (opcional)",
                    border: OutlineInputBorder(),
                    helperText: "Vincula el escaneo para ver analítica por finca",
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<int?>(
                      isExpanded: true,
                      value: _selectedFarmId,
                      items: [
                        const DropdownMenuItem<int?>(
                          value: null,
                          child: Text("Sin vincular"),
                        ),
                        ..._farms.map(
                          (f) => DropdownMenuItem<int?>(
                            value: f.id,
                            child: Text("${f.name} (${f.crop})"),
                          ),
                        ),
                      ],
                      onChanged: _isBusy ? null : (v) => setState(() => _selectedFarmId = v),
                    ),
                  ),
                ),
              if (_farms.isNotEmpty) const SizedBox(height: 12),
              if (_farmsLoading)
                const Padding(
                  padding: EdgeInsets.only(bottom: 12),
                  child: LinearProgressIndicator(),
                ),
              InputDecorator(
                decoration: const InputDecoration(
                  labelText: "Ajustar severidad",
                  border: OutlineInputBorder(),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<int>(
                    isExpanded: true,
                    value: _severityLevel,
                    items: _severityOptions.entries
                        .map((e) => DropdownMenuItem(value: e.key, child: Text(e.value)))
                        .toList(),
                    onChanged: _isBusy ? null : (v) => setState(() => _severityLevel = v ?? 2),
                  ),
                ),
              ),
            ],
            if (_diagnosis != null && _imageBytes != null) ...[
              const SizedBox(height: 12),
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                value: _shareWithTech,
                onChanged: _isBusy
                    ? null
                    : (value) => setState(() => _shareWithTech = value ?? false),
                title: const Text("Compartir foto con mi técnico/cooperativa"),
                subtitle: const Text(
                  "Opcional. Solo lo verá tu técnico para validar el diagnóstico. El mapa comunitario sigue siendo anónimo.",
                  style: TextStyle(fontSize: 12),
                ),
                controlAffinity: ListTileControlAffinity.leading,
              ),
            ],
            const SizedBox(height: 20),
            if (_errorMessage != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
              ),
            PrimaryButton(
              label: _isSaving
                  ? "Guardando..."
                  : _isAnalyzing
                      ? "Analizando..."
                      : "Guardar diagnóstico",
              onPressed: _isBusy ? null : _saveScan,
            ),
            const SizedBox(height: 8),
            TextButton(
              onPressed: _isBusy ? null : () => Navigator.pop(context),
              child: const Text("Cancelar"),
            ),
          ],
        ),
      ),
    );
  }
}

class _ImagePreview extends StatelessWidget {
  final Uint8List? imageBytes;
  final bool isAnalyzing;

  const _ImagePreview({required this.imageBytes, required this.isAnalyzing});

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 4 / 3,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFBDBDBD)),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: imageBytes == null
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.eco, size: 48, color: Color(0xFF2E7D32)),
                      SizedBox(height: 8),
                      Text("Sin imagen", style: TextStyle(color: Color(0xFF757575))),
                    ],
                  ),
                )
              : Stack(
                  fit: StackFit.expand,
                  children: [
                    Image.memory(imageBytes!, fit: BoxFit.cover),
                    if (isAnalyzing)
                      Container(
                        color: Colors.black45,
                        child: const Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              CircularProgressIndicator(color: Colors.white),
                              SizedBox(height: 12),
                              Text(
                                "Analizando hoja...",
                                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
        ),
      ),
    );
  }
}
