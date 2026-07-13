import "dart:typed_data";

import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/plague_catalog.dart";
import "../../data/repositories/tech_repository.dart";
import "../widgets/scan_image_preview.dart";

class TechScanValidationScreen extends StatefulWidget {
  const TechScanValidationScreen({super.key});

  @override
  State<TechScanValidationScreen> createState() => _TechScanValidationScreenState();
}

class _TechScanValidationScreenState extends State<TechScanValidationScreen> {
  final _repo = TechScanRepository();
  List<dynamic> _scans = [];
  final Map<int, Uint8List> _images = {};
  final Map<int, String> _correctPlague = {};
  final Map<int, String> _notes = {};
  bool _loading = true;
  String? _error;
  int? _busyId;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  List<String> _plagueOptionsFor(Map<String, dynamic> scan) {
    final options = List<String>.from(PlagueCatalog.labels);
    final raw = scan["plague"]?.toString().trim().toLowerCase();
    if (raw != null && raw.isNotEmpty && !options.any((o) => o.toLowerCase() == raw)) {
      options.insert(0, raw);
    }
    return options;
  }

  String? _selectedPlague(int id, Map<String, dynamic> scan, List<String> options) {
    final preferred = (_correctPlague[id] ?? scan["plague"]?.toString())?.trim().toLowerCase();
    if (preferred == null || preferred.isEmpty) return null;
    for (final option in options) {
      if (option.toLowerCase() == preferred) return option;
    }
    return null;
  }

  Future<void> _reload() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final scans = await _repo.fetchPending();
      final images = <int, Uint8List>{};
      for (final s in scans) {
        final id = s["id"] as int;
        try {
          images[id] = await _repo.fetchImage(id);
        } catch (_) {
          images[id] = Uint8List(0);
        }
      }
      if (!mounted) return;
      setState(() {
        _scans = scans;
        _images
          ..clear()
          ..addAll(images);
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _act(int scanId, String action) async {
    setState(() => _busyId = scanId);
    try {
      final scan = _scans.cast<Map<String, dynamic>>().firstWhere((s) => s["id"] == scanId);
      final options = _plagueOptionsFor(scan);
      final selected = _selectedPlague(scanId, scan, options);
      await _repo.validate(
        scanId: scanId,
        action: action,
        correctedPlague: action == "correct" ? selected : null,
        techNotes: _notes[scanId],
      );
      await _reload();
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busyId = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Validar escaneos"),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _reload)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: NexoColors.errorRed)))
              : _scans.isEmpty
                  ? const Center(child: Text("No hay escaneos pendientes de validar."))
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _scans.length,
                      itemBuilder: (context, i) {
                        final scan = _scans[i] as Map<String, dynamic>;
                        final id = scan["id"] as int;
                        final bytes = _images[id] ?? Uint8List(0);
                        final busy = _busyId == id;
                        final plagueOptions = _plagueOptionsFor(scan);
                        final selectedPlague = _selectedPlague(id, scan, plagueOptions);
                        return Card(
                          margin: const EdgeInsets.only(bottom: 16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              ScanImagePreview(bytes: bytes, height: 220),
                              Padding(
                                padding: const EdgeInsets.all(14),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      "${scan["plague"]} · ${scan["crop"]}",
                                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                                    ),
                                    Text(
                                      "${scan["farmer_name"]} · ${scan["farm_name"] ?? "Sin finca"}",
                                      style: const TextStyle(color: NexoColors.textSecondary),
                                    ),
                                    Text("Confianza ${((scan["confidence"] as num) * 100).toStringAsFixed(0)}%"),
                                    const SizedBox(height: 10),
                                    DropdownButtonFormField<String>(
                                      value: selectedPlague,
                                      decoration: const InputDecoration(labelText: "Plaga corregida"),
                                      items: plagueOptions
                                          .map((p) => DropdownMenuItem(value: p, child: Text(p)))
                                          .toList(),
                                      onChanged: busy
                                          ? null
                                          : (v) {
                                              if (v == null) return;
                                              setState(() => _correctPlague[id] = v);
                                            },
                                    ),
                                    const SizedBox(height: 8),
                                    TextField(
                                      decoration: const InputDecoration(labelText: "Notas perito"),
                                      maxLines: 2,
                                      onChanged: (v) => _notes[id] = v,
                                    ),
                                    const SizedBox(height: 12),
                                    Row(
                                      children: [
                                        Expanded(
                                          child: ElevatedButton(
                                            onPressed: busy ? null : () => _act(id, "confirm"),
                                            style: ElevatedButton.styleFrom(backgroundColor: NexoColors.bioGreen),
                                            child: const Text("Confirmar"),
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Expanded(
                                          child: OutlinedButton(
                                            onPressed: busy ? null : () => _act(id, "correct"),
                                            child: const Text("Corregir"),
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        IconButton(
                                          onPressed: busy ? null : () => _act(id, "reject"),
                                          icon: const Icon(Icons.cancel, color: NexoColors.errorRed),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
    );
  }
}
