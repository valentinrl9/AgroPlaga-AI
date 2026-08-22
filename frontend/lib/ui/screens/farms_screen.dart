import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../data/repositories/crop_repository.dart";
import "../../data/repositories/farm_repository.dart";
import "../../data/repositories/zone_repository.dart";
import "../../models/crop.dart";
import "../../models/farm.dart";
import "../../models/zone.dart";
import "../layout/mobile_layout.dart";
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
  bool _showAddForm = false;

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
    setState(() {
      _future = _repository.fetchFarms();
    });
  }

  String _zoneLabel(int? zoneId) {
    if (zoneId == null) return "—";
    for (final zone in _zones) {
      if (zone.id == zoneId) return zone.name;
    }
    return "Municipio #$zoneId";
  }

  void _resetForm() {
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
      _farmType = "greenhouse";
      _showAddForm = false;
    });
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
    _resetForm();
    _reload();
  }

  Future<void> _deleteFarm(Farm farm) async {
    await _repository.deleteFarm(farm.id);
    _reload();
  }

  Future<void> _editFarm(Farm farm) async {
    final cropController = TextEditingController(text: farm.crop);
    final sigpacController = TextEditingController(text: farm.sigpacCode ?? "");
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
                const SizedBox(height: 12),
                TextField(
                  controller: sigpacController,
                  decoration: const InputDecoration(
                    labelText: "SIGPAC recinto",
                    hintText: "Ej. 04079A00100001",
                    helperText: "Obligatorio para cuaderno SIEX · visor SIGPAC (MAPA)",
                  ),
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

    if (saved != true) {
      cropController.dispose();
      sigpacController.dispose();
      return;
    }

    try {
      await _repository.updateFarm(
        farm.id,
        crop: cropController.text.trim(),
        cropStage: stage,
        sigpacCode: sigpacController.text.trim(),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("No se pudo guardar: $e")),
        );
      }
    } finally {
      cropController.dispose();
      sigpacController.dispose();
    }
    _reload();
  }

  Widget _buildForm() {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text(
                    "Nueva finca",
                    style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16),
                  ),
                ),
                IconButton(
                  tooltip: "Cerrar",
                  onPressed: _resetForm,
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
            const Text(
              "El SIGPAC del recinto solo hace falta si usas el cuaderno SIEX.",
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
                labelText: "SIGPAC recinto (solo SIEX)",
                hintText: "Ej. 04079A00100001",
                helperText: "Opcional ahora · visor SIGPAC del MAPA",
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
            PrimaryButton(label: "Guardar finca", onPressed: _createFarm),
          ],
        ),
      ),
    );
  }

  Widget _buildFarmCard(Farm farm) {
    return Card(
      child: ListTile(
        title: Text(farm.name),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "${farm.typeLabel} · ${farm.crop}\n"
              "Municipio: ${_zoneLabel(farm.zoneId)}\n"
              "Nave/sector: ${farm.nave ?? "—"} / ${farm.sector ?? "—"}\n"
              "Fase: ${farm.cropStage ?? "—"} · Variante: ${farm.cropVariant ?? "—"}\n"
              "SIGPAC: ${farm.sigpacCode ?? "—"} · Sup.: ${farm.surfaceM2?.toStringAsFixed(0) ?? "—"} m²",
            ),
            if (!farm.hasSigpac)
              const Padding(
                padding: EdgeInsets.only(top: 6),
                child: Text(
                  "Sin SIGPAC — cuaderno SIEX incompleto",
                  style: TextStyle(color: NexoColors.warningAmber, fontSize: 12),
                ),
              ),
          ],
        ),
        isThreeLine: false,
        onTap: () => _editFarm(farm),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline),
          onPressed: () => _deleteFarm(farm),
        ),
      ),
    );
  }

  Widget _buildAddButton() {
    return OutlinedButton.icon(
      onPressed: () => setState(() => _showAddForm = true),
      icon: const Icon(Icons.add),
      label: const Text("Añadir finca"),
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 14),
        side: const BorderSide(color: NexoColors.bioGreen),
        foregroundColor: NexoColors.bioGreen,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Mis fincas"),
        actions: [
          if (!_showAddForm)
            IconButton(
              tooltip: "Añadir finca",
              onPressed: () => setState(() => _showAddForm = true),
              icon: const Icon(Icons.add),
            ),
        ],
      ),
      body: MobileLayout.dismissKeyboardOnTap(
        context: context,
        child: FutureBuilder<List<Farm>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting && !snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return MobileLayout.errorState(error: snapshot.error!, onRetry: _reload);
            }

            final farms = snapshot.data ?? [];
            return CustomScrollView(
              keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
              slivers: [
                SliverPadding(
                  padding: MobileLayout.scrollPadding(context).copyWith(bottom: 8),
                  sliver: SliverList(
                    delegate: SliverChildListDelegate([
                      if (farms.isEmpty && !_showAddForm) ...[
                        const SizedBox(height: 24),
                        const Icon(Icons.agriculture_outlined, size: 48, color: NexoColors.textSecondary),
                        const SizedBox(height: 12),
                        const Text(
                          "No tienes fincas registradas.",
                          textAlign: TextAlign.center,
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          "Pulsa «Añadir finca» para registrar tu invernadero o parcela.",
                          textAlign: TextAlign.center,
                          style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
                        ),
                        const SizedBox(height: 20),
                        _buildAddButton(),
                      ] else ...[
                        if (farms.isNotEmpty) ...[
                          Text(
                            "${farms.length} finca${farms.length == 1 ? "" : "s"} · Toca una para editar cultivo o SIGPAC",
                            style: const TextStyle(color: NexoColors.textSecondary, fontSize: 13),
                          ),
                          const SizedBox(height: 12),
                          ...farms.map(_buildFarmCard).expand((card) => [card, const SizedBox(height: 8)]),
                          if (!_showAddForm) ...[
                            const SizedBox(height: 4),
                            _buildAddButton(),
                          ],
                        ],
                      ],
                      if (_showAddForm) ...[
                        if (farms.isNotEmpty) const SizedBox(height: 8),
                        _buildForm(),
                      ],
                      const SizedBox(height: 16),
                    ]),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
