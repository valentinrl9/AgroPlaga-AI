import "package:flutter/material.dart";

import "../../core/auth_redirect.dart";
import "../../core/nexo_colors.dart";
import "../../core/navigation.dart";
import "../../core/routes.dart";
import "../../core/session.dart";
import "../../core/severity.dart";
import "../../data/repositories/outbreak_event_repository.dart";
import "../../data/repositories/zone_repository.dart";
import "../../models/scan.dart";
import "../../models/zone.dart";
import "../widgets/card_scan.dart";
import "../widgets/primary_button.dart";

class ContributeScreen extends StatefulWidget {
  final Scan scan;

  const ContributeScreen({super.key, required this.scan});

  @override
  State<ContributeScreen> createState() => _ContributeScreenState();
}

class _ContributeScreenState extends State<ContributeScreen> {
  final _zoneRepository = ZoneRepository();
  final _eventRepository = OutbreakEventRepository();

  List<AgriZone> _zones = [];
  AgriZone? _selectedZone;
  bool _loadingZones = true;
  bool _submitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadZones();
  }

  Future<void> _loadZones() async {
    try {
      final zones = await _zoneRepository.fetchZones();
      if (!mounted) return;
      setState(() {
        _zones = zones;
        _loadingZones = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _error = "No se pudieron cargar las zonas SIGPAC: $error";
        _loadingZones = false;
      });
    }
  }

  Future<void> _submit() async {
    if (_selectedZone == null) {
      setState(() => _error = "Selecciona tu municipio SIGPAC.");
      return;
    }

    final severityLevel = Severity.parseToLevel(widget.scan.severity);
    if (severityLevel == null || severityLevel < 1 || severityLevel > 3) {
      setState(() => _error = "Severidad no válida para contribuir.");
      return;
    }

    setState(() {
      _submitting = true;
      _error = null;
    });

    try {
      await _eventRepository.contribute(
        plague: widget.scan.plague,
        severity: severityLevel,
        zoneId: _selectedZone!.id,
        modelVersion: "v1.0",
        sourceScanId: widget.scan.id,
      );
      await Session.markContributed(widget.scan.id);

      if (!mounted) return;
      goHome(context);
      final rootContext = AuthRedirect.navigatorKey.currentContext;
      if (rootContext == null) return;
      ScaffoldMessenger.of(rootContext).showSnackBar(
        SnackBar(
          content: const Text("¡Gracias! Tu aporte ayuda al mapa de plagas de la comarca."),
          backgroundColor: NexoColors.bioGreen,
          action: SnackBarAction(
            label: "Ver mapa",
            textColor: Colors.white,
            onPressed: () => AuthRedirect.navigatorKey.currentState?.pushNamed(Routes.map),
          ),
        ),
      );
    } catch (error) {
      if (!mounted) return;
      final msg = error.toString();
      if (msg.contains("401")) {
        Navigator.pushReplacementNamed(context, Routes.login);
        return;
      }
      setState(() {
        _error = msg.contains("Failed to fetch")
            ? "No se pudo conectar con el servidor. Comprueba que Docker está activo."
            : "Error al contribuir: $error";
        _submitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Contribuir al mapa")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Comparte de forma anónima",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            const Text(
              "Solo se envía la plaga, severidad y municipio SIGPAC. "
              "Nunca se comparte tu parcela ni coordenadas exactas.",
              style: TextStyle(fontSize: 14, color: NexoColors.textPrimary),
            ),
            const SizedBox(height: 20),
            CardScan.fromScan(
              widget.scan,
              title: "Resumen del escaneo",
            ),
            const SizedBox(height: 20),
            if (_loadingZones)
              const Expanded(child: Center(child: CircularProgressIndicator()))
            else ...[
              InputDecorator(
                decoration: const InputDecoration(
                  labelText: "Municipio SIGPAC",
                  hintText: "Selecciona tu zona",
                  border: OutlineInputBorder(),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<AgriZone>(
                    isExpanded: true,
                    value: _selectedZone,
                    hint: const Text("Selecciona tu zona"),
                    items: _zones
                        .map(
                          (zone) => DropdownMenuItem(
                            value: zone,
                            child: Text("${zone.name} (${zone.sigpacCode})"),
                          ),
                        )
                        .toList(),
                    onChanged: _submitting ? null : (value) => setState(() => _selectedZone = value),
                  ),
                ),
              ),
              const Spacer(),
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Text(_error!, style: const TextStyle(color: NexoColors.errorRed)),
                ),
              PrimaryButton(
                label: _submitting ? "Enviando..." : "Sí, contribuir",
                onPressed: _submitting ? null : _submit,
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: _submitting ? null : () => Navigator.pop(context),
                child: const Text("Cancelar"),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
