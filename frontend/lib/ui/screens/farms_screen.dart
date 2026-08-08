import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../data/repositories/crop_repository.dart";
import "../../data/repositories/farm_repository.dart";
import "../../data/repositories/zone_repository.dart";
import "../../models/crop.dart";
import "../../models/farm.dart";
import "../../models/zone.dart";
import "../widgets/primary_button.dart";

class FarmsScreen extends StatefulWidget {
  const FarmsScreen({super.key});

  @override
  State<FarmsScreen> createState() => _FarmsScreenState();
}

class _FarmsScreenState extends State<FarmsScreen> {
  final _repository = FarmRepository();
  final _zoneRepository = ZoneRepository();
  final _cropRepository = CropRepository();
  late Future<List<Farm>> _future;

  final _nameController = TextEditingController();
  final _cropController = TextEditingController();
  final _naveController = TextEditingController();
  final _sectorController = TextEditingController();
  final _variantController = TextEditingController();
  final _sigpacController = TextEditingController();
  final _surfaceController = TextEditingController();

  List<AgriZone> _zones = [];
  List<CropCatalogEntry> _crops = [];
  AgriZone? _selectedZone;
  CropCatalogEntry? _selectedCrop;
  String? _cropStage;
  String _farmType = "greenhouse";

  @override
  void initState() {
    super.initState();
    _future = _repository.fetchFarms();
    _loadCatalogs();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _cropController.dispose();
    _naveController.dispose();
    _sectorController.dispose();
    _variantController.dispose();
    _sigpacController.dispose();
    _surfaceController.dispose();
    super.dispose();
  }

  Future<void> _loadCatalogs() async {
    try {
      final zones = await _zoneRepository.fetchZones();
      final crops = await _cropRepository.search(limit: 50);
      if (!mounted) return;
      setState(() {
        _zones = zones;
        _crops = crops;
      });
    } catch (_) {}
  }

  void _reload() {
    setState(() => _future = _repository.fetchFarms());
  }

  String _zoneLabel(int? zoneId) {
    if (zoneId == null) return "—";
    for (final zone in _zones) {
      if (zone.id == zoneId) return zone.name;
    }
    return "Municipio #$zoneId";
  }

  Future<void> _createFarm() async {
    if (_nameController.text.trim().isEmpty) return;
    final crop = _selectedCrop?.name ?? _cropController.text.trim();
    if (crop.isEmpty) return;

    final surface = double.tryParse(_surfaceController.text.trim());
    await _repository.createFarm(
      name: _nameController.text.trim(),
      crop: crop,
      farmType: _farmType,
      zoneId: _selectedZone?.id,
      nave: _naveController.text.trim(),
      sector: _sectorController.text.trim(),
      cropStage: _cropStage,
      cropVariant: _variantController.text.trim(),
      surfaceM2: surface,
      sigpacCode: _sigpacController.text.trim(),
    );
    _nameController.clear();
    _cropController.clear();
    _naveController.clear();
    _sectorController.clear();
    _variantController.clear();
    _sigpacController.clear();
    _surfaceController.clear();
    setState(() {
      _selectedZone = null;
      _selectedCrop = null;
      _cropStage = null;
    });
    _reload();
  }

  Future<void> _deleteFarm(Farm farm) async {
    await _repository.deleteFarm(farm.id);
    _reload();
  }

  Future<void> _editFarm(Farm farm) async {
    final cropController = TextEditingController(text: farm.crop);
    String? stage = farm.cropStage;
    CropCatalogEntry? cropMatch;
    for (final crop in _crops) {
      if (crop.name == farm.crop) {
        cropMatch = crop;
        break;
      }
    }

    final saved = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text("Editar ${farm.name}"),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: cropController,
                  decoration: const InputDecoration(labelText: "Cultivo"),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  key: ValueKey(stage),
                  initialValue: stage,
                  decoration: const InputDecoration(labelText: "Fase fenológica"),
                  items: (cropMatch?.stages ??
                          const ["plantación", "crecimiento", "floración", "cuajado", "cosecha"])
                      .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                      .toList(),
                  onChanged: (v) => stage = v,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context, false), child: const Text("Cancelar")),
            TextButton(onPressed: () => Navigator.pop(context, true), child: const Text("Guardar")),
          ],
        );
      },
    );

    if (saved != true) return;

    await _repository.updateFarm(
      farm.id,
      crop: cropController.text.trim(),
      cropStage: stage,
    );
    cropController.dispose();
    _reload();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Mis fincas")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Registra fincas, naves y sectores con municipio, cultivo y fase. "
              "SIGPAC recinto es opcional (obligatorio para SIEX cooperativa).",
              style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: "Nombre *", border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              key: ValueKey(_farmType),
              initialValue: _farmType,
              decoration: const InputDecoration(labelText: "Tipo", border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: "greenhouse", child: Text("Invernadero")),
                DropdownMenuItem(value: "farm", child: Text("Finca")),
              ],
              onChanged: (v) => setState(() => _farmType = v ?? "greenhouse"),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _naveController,
              decoration: const InputDecoration(labelText: "Nave", border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _sectorController,
              decoration: const InputDecoration(labelText: "Sector", border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            Autocomplete<AgriZone>(
              optionsBuilder: (query) {
                final q = query.text.trim().toLowerCase();
                if (q.isEmpty) return _zones.take(20);
                return _zones.where((zone) => zone.name.toLowerCase().contains(q)).take(20);
              },
              displayStringForOption: (zone) => zone.name,
              onSelected: (zone) => setState(() => _selectedZone = zone),
              fieldViewBuilder: (context, controller, focusNode, onFieldSubmitted) {
                return TextField(
                  controller: controller,
                  focusNode: focusNode,
                  decoration: const InputDecoration(
                    labelText: "Municipio",
                    hintText: "Busca tu municipio",
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (_) => setState(() => _selectedZone = null),
                );
              },
            ),
            const SizedBox(height: 8),
            Autocomplete<CropCatalogEntry>(
              optionsBuilder: (query) {
                final q = query.text.trim().toLowerCase();
                if (q.isEmpty) return _crops;
                return _crops.where((crop) {
                  final tokens = [crop.name.toLowerCase(), ...crop.aliases.map((a) => a.toLowerCase())];
                  return tokens.any((token) => token.contains(q));
                });
              },
              displayStringForOption: (crop) => crop.name,
              onSelected: (crop) {
                setState(() {
                  _selectedCrop = crop;
                  _cropController.text = crop.name;
                  _cropStage = crop.stages.isNotEmpty ? crop.stages.first : null;
                });
              },
              fieldViewBuilder: (context, controller, focusNode, onFieldSubmitted) {
                return TextField(
                  controller: controller,
                  focusNode: focusNode,
                  decoration: const InputDecoration(labelText: "Cultivo *", border: OutlineInputBorder()),
                  onChanged: (value) {
                    _cropController.text = value;
                    setState(() => _selectedCrop = null);
                  },
                );
              },
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              key: ValueKey("${_selectedCrop?.id ?? 'crop'}-$_cropStage"),
              initialValue: _cropStage,
              decoration: const InputDecoration(labelText: "Fase fenológica", border: OutlineInputBorder()),
              items: (_selectedCrop?.stages ?? const ["plantación", "crecimiento", "floración", "cuajado", "cosecha"])
                  .map((stage) => DropdownMenuItem(value: stage, child: Text(stage)))
                  .toList(),
              onChanged: (v) => setState(() => _cropStage = v),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _variantController,
              decoration: const InputDecoration(labelText: "Variante", border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _sigpacController,
              decoration: const InputDecoration(
                labelText: "SIGPAC recinto (opcional)",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _surfaceController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: "Superficie m²", border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            PrimaryButton(label: "Añadir", onPressed: _createFarm),
            const SizedBox(height: 20),
            Expanded(
              child: FutureBuilder<List<Farm>>(
                future: _future,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    return Center(child: Text("Error: ${snapshot.error}"));
                  }
                  final farms = snapshot.data ?? [];
                  if (farms.isEmpty) {
                    return const Center(child: Text("No tienes fincas registradas."));
                  }
                  return ListView.separated(
                    itemCount: farms.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (context, index) {
                      final farm = farms[index];
                      return Card(
                        child: ListTile(
                          title: Text(farm.name),
                          subtitle: Text(
                            "${farm.typeLabel} · ${farm.crop}\n"
                            "Municipio: ${_zoneLabel(farm.zoneId)}\n"
                            "Nave/sector: ${farm.nave ?? "—"} / ${farm.sector ?? "—"}\n"
                            "Fase: ${farm.cropStage ?? "—"} · Variante: ${farm.cropVariant ?? "—"}\n"
                            "SIGPAC: ${farm.sigpacCode ?? "—"} · Sup.: ${farm.surfaceM2?.toStringAsFixed(0) ?? "—"} m²",
                          ),
                          isThreeLine: false,
                          onTap: () => _editFarm(farm),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete_outline),
                            onPressed: () => _deleteFarm(farm),
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
