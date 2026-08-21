import "dart:async";

import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../data/repositories/crop_repository.dart";
import "../../data/repositories/farm_repository.dart";
import "../../data/repositories/zone_repository.dart";
import "../../models/crop.dart";
import "../../models/zone.dart";
import "../layout/mobile_layout.dart";
import "../widgets/primary_button.dart";

class OnboardingWizardScreen extends StatefulWidget {
  const OnboardingWizardScreen({super.key});

  @override
  State<OnboardingWizardScreen> createState() => _OnboardingWizardScreenState();
}

class _OnboardingWizardScreenState extends State<OnboardingWizardScreen> {
  final _farmRepository = FarmRepository();
  final _zoneRepository = ZoneRepository();
  final _cropRepository = CropRepository();
  Timer? _cropSearchDebounce;

  final _nameController = TextEditingController();
  final _naveController = TextEditingController();
  final _sectorController = TextEditingController();
  final _cropController = TextEditingController();
  final _variantController = TextEditingController();
  final _sigpacController = TextEditingController();
  final _surfaceController = TextEditingController();
  final _municipalityController = TextEditingController();

  List<AgriZone> _zones = [];
  List<CropCatalogEntry> _crops = [];
  AgriZone? _selectedZone;
  CropCatalogEntry? _selectedCrop;
  String? _cropStage;
  String _farmType = "greenhouse";
  bool _loading = true;
  bool _submitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadCatalogs();
  }

  @override
  void dispose() {
    _cropSearchDebounce?.cancel();
    _nameController.dispose();
    _naveController.dispose();
    _sectorController.dispose();
    _cropController.dispose();
    _variantController.dispose();
    _sigpacController.dispose();
    _surfaceController.dispose();
    _municipalityController.dispose();
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
        _loading = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _error = "No se pudieron cargar municipios o cultivos: $error";
        _loading = false;
      });
    }
  }

  void _scheduleCropSearch(String query) {
    _cropSearchDebounce?.cancel();
    if (query.trim().length < 2) return;
    _cropSearchDebounce = Timer(const Duration(milliseconds: 350), () {
      _searchCrops(query);
    });
  }

  Future<void> _searchCrops(String query) async {
    if (query.trim().length < 2) return;
    try {
      final crops = await _cropRepository.search(query: query);
      if (!mounted) return;
      setState(() => _crops = crops);
    } catch (_) {}
  }

  Future<void> _submit() async {
    final name = _nameController.text.trim();
    final crop = _selectedCrop?.name ?? _cropController.text.trim();

    if (name.isEmpty) {
      setState(() => _error = "Indica un nombre para la finca o invernadero.");
      return;
    }
    if (_selectedZone == null) {
      setState(() => _error = "Selecciona el municipio.");
      return;
    }
    if (crop.isEmpty) {
      setState(() => _error = "Selecciona o escribe el cultivo.");
      return;
    }
    if (_cropStage == null || _cropStage!.isEmpty) {
      setState(() => _error = "Indica la fase fenológica.");
      return;
    }

    final surface = double.tryParse(_surfaceController.text.trim());

    setState(() {
      _submitting = true;
      _error = null;
    });

    try {
      await _farmRepository.createFarm(
        name: name,
        crop: crop,
        farmType: _farmType,
        zoneId: _selectedZone!.id,
        nave: _naveController.text.trim(),
        sector: _sectorController.text.trim(),
        cropStage: _cropStage,
        cropVariant: _variantController.text.trim(),
        surfaceM2: surface,
        sigpacCode: _sigpacController.text.trim(),
      );

      if (!mounted) return;
      Navigator.pushReplacementNamed(context, Routes.home);
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.toString();
        _submitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Configura tu explotación")),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : MobileLayout.dismissKeyboardOnTap(
              context: context,
              child: SingleChildScrollView(
                padding: MobileLayout.scrollPadding(context),
                keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
                child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    "Paso 3 · Tu unidad productiva",
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    "Registra al menos una finca, nave o sector. "
                    "Podrás editar cultivo y fase más adelante desde Mis fincas.",
                    style: TextStyle(color: NexoColors.textSecondary),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    controller: _nameController,
                    decoration: const InputDecoration(
                      labelText: "Nombre de la unidad *",
                      hintText: "Ej. Invernadero Norte",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    key: ValueKey(_farmType),
                    initialValue: _farmType,
                    decoration: const InputDecoration(labelText: "Tipo", border: OutlineInputBorder()),
                    items: const [
                      DropdownMenuItem(value: "greenhouse", child: Text("Invernadero")),
                      DropdownMenuItem(value: "farm", child: Text("Finca / campo")),
                    ],
                    onChanged: _submitting ? null : (v) => setState(() => _farmType = v ?? "greenhouse"),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _naveController,
                    decoration: const InputDecoration(
                      labelText: "Nave (opcional)",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _sectorController,
                    decoration: const InputDecoration(
                      labelText: "Sector (opcional)",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Autocomplete<AgriZone>(
                    optionsBuilder: (query) {
                      final q = query.text.trim().toLowerCase();
                      if (q.isEmpty) return _zones.take(20);
                      return _zones.where((zone) => zone.name.toLowerCase().contains(q)).take(20);
                    },
                    displayStringForOption: (zone) => zone.name,
                    onSelected: (zone) {
                      setState(() {
                        _selectedZone = zone;
                        _municipalityController.text = zone.name;
                      });
                    },
                    fieldViewBuilder: (context, controller, focusNode, onFieldSubmitted) {
                      if (_municipalityController.text.isNotEmpty && controller.text.isEmpty) {
                        controller.text = _municipalityController.text;
                      }
                      return TextField(
                        controller: controller,
                        focusNode: focusNode,
                        decoration: const InputDecoration(
                          labelText: "Municipio *",
                          hintText: "Busca tu municipio",
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (_) => setState(() => _selectedZone = null),
                      );
                    },
                  ),
                  const SizedBox(height: 12),
                  Autocomplete<CropCatalogEntry>(
                    optionsBuilder: (query) {
                      final q = query.text.trim().toLowerCase();
                      if (q.isEmpty) return _crops;
                      return _crops.where((crop) {
                        final haystack = [crop.name.toLowerCase(), ...crop.aliases.map((a) => a.toLowerCase())];
                        return haystack.any((token) => token.contains(q));
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
                        decoration: const InputDecoration(
                          labelText: "Cultivo *",
                          hintText: "Tomate, pimiento…",
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (value) {
                          setState(() {
                            _selectedCrop = null;
                            _cropController.text = value;
                          });
                          _scheduleCropSearch(value);
                        },
                      );
                    },
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    key: ValueKey("${_selectedCrop?.id ?? 'crop'}-$_cropStage"),
                    initialValue: _cropStage,
                    decoration: const InputDecoration(
                      labelText: "Fase fenológica *",
                      border: OutlineInputBorder(),
                    ),
                    items: (_selectedCrop?.stages ?? const ["plantación", "crecimiento", "floración", "cuajado", "cosecha"])
                        .map((stage) => DropdownMenuItem(value: stage, child: Text(stage)))
                        .toList(),
                    onChanged: _submitting ? null : (v) => setState(() => _cropStage = v),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _variantController,
                    decoration: const InputDecoration(
                      labelText: "Variante (opcional)",
                      hintText: "Ej. pera, cherry",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _surfaceController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: "Superficie m² (opcional)",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _sigpacController,
                    decoration: const InputDecoration(
                      labelText: "SIGPAC recinto (opcional)",
                      hintText: "Obligatorio solo para SIEX cooperativa",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 20),
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Text(_error!, style: const TextStyle(color: NexoColors.errorRed)),
                    ),
                  PrimaryButton(
                    label: _submitting ? "Guardando..." : "Finalizar y entrar",
                    onPressed: _submitting ? null : _submit,
                  ),
                ],
              ),
            ),
            ),
    );
  }
}
