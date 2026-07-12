import "package:flutter/material.dart";
import "package:flutter_map/flutter_map.dart";
import "package:latlong2/latlong.dart";

import "../../core/auth_redirect.dart";
import "../../core/routes.dart";
import "../../data/repositories/map_repository.dart";
import "../../data/repositories/zone_repository.dart";
import "../../models/heatmap_cell.dart";
import "../../models/outbreak_event.dart";
import "../../models/zone.dart";
import "../widgets/map_legend.dart";

enum _MapViewMode { heatmap, markers, both }

class MapScreen extends StatefulWidget {
  final int? initialZoneId;
  final String? initialPlague;

  const MapScreen({super.key, this.initialZoneId, this.initialPlague});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final _mapRepository = MapRepository();
  final _zoneRepository = ZoneRepository();
  final _mapController = MapController();

  static const _ponienteCenter = LatLng(36.77, -2.78);

  int _hours = 168;
  int _minSeverity = 1;
  String? _plagueFilter;
  bool _validatedOnly = false;
  _MapViewMode _viewMode = _MapViewMode.both;
  List<String> _plagueOptions = [];
  bool _isLoading = false;
  _MapData? _data;
  Object? _loadError;
  bool _focusedInitialZone = false;

  @override
  void initState() {
    super.initState();
    if (widget.initialPlague != null) {
      _plagueFilter = widget.initialPlague;
    }
    _reloadData();
  }

  MapFilters get _filters => MapFilters(
        hours: _hours,
        minSeverity: _minSeverity,
        plague: _plagueFilter,
        validatedOnly: _validatedOnly,
      );

  void _reloadData() {
    setState(() {
      _isLoading = true;
      _loadError = null;
      _focusedInitialZone = false;
      _load().then((data) {
        if (mounted) {
          setState(() {
            _isLoading = false;
            _plagueOptions = data.plagueOptions;
            _data = data;
          });
          _focusInitialZoneIfNeeded(data);
        }
        return data;
      }).catchError((Object error) {
        if (mounted) {
          setState(() {
            _isLoading = false;
            _loadError = error;
            _data = null;
          });
          AuthRedirect.redirectIfUnauthorized(context, error);
        }
        throw error;
      });
    });
  }

  Future<_MapData> _load() async {
    final zones = await _zoneRepository.fetchZones();
    final optionsSource = await _mapRepository.fetchOutbreaks(
      filters: MapFilters(hours: _hours, minSeverity: 1),
    );
    final plagueOptions = optionsSource.map((e) => e.plague).toSet().toList()..sort();

    final events = await _mapRepository.fetchOutbreaks(filters: _filters);
    final heatmap = await _mapRepository.fetchHeatmap(filters: _filters);

    return _MapData(
      events: events,
      heatmap: heatmap,
      zoneById: {for (final z in zones) z.id: z},
      plagueOptions: plagueOptions,
    );
  }

  void _focusInitialZoneIfNeeded(_MapData data) {
    if (_focusedInitialZone || widget.initialZoneId == null) return;
    final clusters = _clusters(data.heatmap);
    _ZoneCluster? cluster;
    for (final item in clusters) {
      if (item.zoneId == widget.initialZoneId) {
        cluster = item;
        break;
      }
    }
    if (cluster == null) return;
    _focusedInitialZone = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _mapController.move(LatLng(cluster!.lat, cluster.lon), 12);
      _showClusterDetails(cluster);
    });
  }

  void _setHours(int hours) {
    if (_hours == hours) return;
    _hours = hours;
    _reloadData();
  }

  void _setMinSeverity(int severity) {
    if (_minSeverity == severity) return;
    _minSeverity = severity;
    _reloadData();
  }

  void _setPlague(String? plague) {
    if (_plagueFilter == plague) return;
    _plagueFilter = plague;
    _reloadData();
  }

  void _setValidatedOnly(bool value) {
    if (_validatedOnly == value) return;
    _validatedOnly = value;
    _reloadData();
  }

  List<_ZoneCluster> _clusters(List<HeatmapCell> heatmap) {
    return heatmap
        .map(
          (cell) => _ZoneCluster(
            zoneId: cell.zoneId,
            name: cell.zoneName,
            sigpacCode: cell.sigpacCode,
            lat: cell.lat,
            lon: cell.lon,
            count: cell.count,
            maxSeverity: cell.maxSeverity,
            intensity: cell.intensity,
            validatedCount: cell.validatedCount,
            pendingCount: cell.pendingCount,
          ),
        )
        .toList();
  }

  _ValidationVisual _validationVisual(_ZoneCluster cluster) {
    if (cluster.validatedCount > 0 && cluster.pendingCount == 0) {
      return _ValidationVisual.validated;
    }
    if (cluster.pendingCount > 0 && cluster.validatedCount == 0) {
      return _ValidationVisual.pending;
    }
    return _ValidationVisual.mixed;
  }

  Color _severityColor(int severity) {
    switch (severity) {
      case 3:
        return const Color(0xFFC62828);
      case 2:
        return const Color(0xFFFBC02D);
      default:
        return const Color(0xFF2E7D32);
    }
  }

  void _recenterMap() {
    _mapController.move(_ponienteCenter, 10);
  }

  Color _heatColor(double intensity, _ValidationVisual visual) {
    final base = Color.lerp(
      const Color(0xFFFBC02D),
      const Color(0xFFC62828),
      intensity,
    )!;
    final alpha = visual == _ValidationVisual.pending
        ? 0.18 + intensity * 0.22
        : visual == _ValidationVisual.validated
            ? 0.32 + intensity * 0.45
            : 0.24 + intensity * 0.34;
    if (visual == _ValidationVisual.pending) {
      return Color.lerp(const Color(0xFFFFB200), base, 0.45)!.withValues(alpha: alpha);
    }
    return base.withValues(alpha: alpha);
  }

  Color _markerFillColor(_ZoneCluster cluster) {
    final visual = _validationVisual(cluster);
    if (visual == _ValidationVisual.pending) {
      return const Color(0xFFFFB200);
    }
    return _severityColor(cluster.maxSeverity);
  }

  Color _markerBorderColor(_ZoneCluster cluster) {
    final visual = _validationVisual(cluster);
    if (visual == _ValidationVisual.validated) {
      return const Color(0xFF00A86B);
    }
    if (visual == _ValidationVisual.pending) {
      return const Color(0xFFEF6C00);
    }
    return Colors.white;
  }

  String _markerLabel(_ZoneCluster cluster) {
    final visual = _validationVisual(cluster);
    if (visual == _ValidationVisual.mixed) {
      return "✓${cluster.validatedCount}\n?${cluster.pendingCount}";
    }
    if (visual == _ValidationVisual.pending) {
      return "?${cluster.pendingCount}";
    }
    return "✓${cluster.validatedCount}";
  }

  void _showClusterDetails(_ZoneCluster cluster) {
    final zoneEvents = (_data?.events ?? [])
        .where((event) => event.zoneId == cluster.zoneId)
        .toList();
    final visual = _validationVisual(cluster);

    showModalBottomSheet(
      context: context,
      showDragHandle: true,
      builder: (context) => Padding(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(cluster.name, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            Text("SIGPAC ${cluster.sigpacCode}", style: const TextStyle(color: Color(0xFF757575))),
            const SizedBox(height: 12),
            Text("${cluster.count} reporte(s) · ${_periodLabel()}"),
            const SizedBox(height: 8),
            Text("Validados por perito: ${cluster.validatedCount}"),
            Text("Pendientes IA (sin validar): ${cluster.pendingCount}"),
            if (cluster.validatedCount + cluster.pendingCount < cluster.count)
              Text(
                "Otros estados (p. ej. descartados): ${cluster.count - cluster.validatedCount - cluster.pendingCount}",
                style: const TextStyle(fontSize: 12, color: Color(0xFF757575)),
              ),
            const SizedBox(height: 8),
            Text("Severidad máxima: ${_severityLabel(cluster.maxSeverity)}"),
            const SizedBox(height: 8),
            Text("Intensidad: ${(cluster.intensity * 100).toStringAsFixed(0)}%"),
            const SizedBox(height: 8),
            _ValidationStatusChip(visual: visual),
            if (zoneEvents.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Text("Detalle de avisos", style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              ...zoneEvents.take(5).map(
                (event) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text(
                    "${event.displayPlague} · ${event.severityLabel} · "
                    "${event.isValidated ? "Validado" : "IA sin validar"}"
                    "${event.wasCorrected ? " (corregido por perito)" : ""}",
                    style: const TextStyle(fontSize: 13),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _severityLabel(int level) {
    switch (level) {
      case 3:
        return "Alto";
      case 2:
        return "Moderado";
      default:
        return "Leve";
    }
  }

  String _periodLabel() {
    switch (_hours) {
      case 24:
        return "24 h";
      case 720:
        return "30 días";
      default:
        return "7 días";
    }
  }

  String _footerMessage(List<_ZoneCluster> clusters, _MapData data) {
    if (clusters.isEmpty) {
      return "Sin focos en ${_periodLabel()}. Contribuye tras tu próximo escaneo.";
    }
    return "${data.events.length} reporte(s) · ${clusters.length} zona(s) · ${_periodLabel()} · Toca un foco para detalles";
  }

  Widget _filterChip({
    required String label,
    required bool selected,
    required VoidCallback onSelect,
  }) {
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: ChoiceChip(
        label: Text(label, style: const TextStyle(fontSize: 12)),
        selected: selected,
        visualDensity: VisualDensity.compact,
        onSelected: (value) {
          if (value) onSelect();
        },
      ),
    );
  }

  Widget _buildFilterBar() {
    return SizedBox(
      height: 40,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        children: [
          _filterChip(label: "24 h", selected: _hours == 24, onSelect: () => _setHours(24)),
          _filterChip(label: "7 días", selected: _hours == 168, onSelect: () => _setHours(168)),
          _filterChip(label: "30 días", selected: _hours == 720, onSelect: () => _setHours(720)),
          const _FilterDivider(),
          _filterChip(label: "Todas", selected: _minSeverity == 1, onSelect: () => _setMinSeverity(1)),
          _filterChip(label: "Mod.+", selected: _minSeverity == 2, onSelect: () => _setMinSeverity(2)),
          _filterChip(label: "Alto", selected: _minSeverity == 3, onSelect: () => _setMinSeverity(3)),
          if (_plagueOptions.isNotEmpty) ...[
            const _FilterDivider(),
            _filterChip(label: "Todas plagas", selected: _plagueFilter == null, onSelect: () => _setPlague(null)),
            ..._plagueOptions.map(
              (plague) => _filterChip(
                label: plague,
                selected: _plagueFilter == plague,
                onSelect: () => _setPlague(plague),
              ),
            ),
          ],
          const _FilterDivider(),
          _filterChip(
            label: "Solo validados",
            selected: _validatedOnly,
            onSelect: () => _setValidatedOnly(true),
          ),
          _filterChip(
            label: "Todos",
            selected: !_validatedOnly,
            onSelect: () => _setValidatedOnly(false),
          ),
        ],
      ),
    );
  }

  Widget _buildError(Object error) {
    if (AuthRedirect.isUnauthorized(error)) {
      return const Center(child: Text("Sesión expirada. Redirigiendo al login..."));
    }
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, size: 48, color: Color(0xFF9E9E9E)),
            const SizedBox(height: 12),
            const Text(
              "No se pudo cargar el mapa.\nComprueba la conexión y que el backend esté activo.",
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _reloadData,
              icon: const Icon(Icons.refresh),
              label: const Text("Reintentar"),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyOverlay() {
    return Center(
      child: Card(
        margin: const EdgeInsets.all(24),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.map_outlined, size: 40, color: Color(0xFF2E7D32)),
              const SizedBox(height: 12),
              Text(
                "Sin focos en ${_periodLabel()}",
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                "Escanea una plaga y contribuye al mapa para ayudar a la comarca.",
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: () => Navigator.pushNamed(context, Routes.scan),
                icon: const Icon(Icons.camera_alt_outlined),
                label: const Text("Ir a escanear"),
              ),
            ],
          ),
        ),
      ),
    );
  }

  MarkerLayer _buildTapLayer(List<_ZoneCluster> clusters) {
    return MarkerLayer(
      markers: clusters
          .map(
            (c) => Marker(
              point: LatLng(c.lat, c.lon),
              width: 52,
              height: 52,
              child: GestureDetector(
                behavior: HitTestBehavior.translucent,
                onTap: () => _showClusterDetails(c),
                child: const SizedBox.expand(),
              ),
            ),
          )
          .toList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final clusters = _data == null ? <_ZoneCluster>[] : _clusters(_data!.heatmap);

    return Scaffold(
      appBar: AppBar(
        title: const Text("Mapa de focos"),
        actions: [
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(12),
              child: SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)),
            ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _reloadData, tooltip: "Actualizar"),
        ],
      ),
      floatingActionButton: FloatingActionButton.small(
        onPressed: _recenterMap,
        tooltip: "Centrar Poniente",
        child: const Icon(Icons.my_location),
      ),
      body: Column(
        children: [
          const SizedBox(height: 6),
          _buildFilterBar(),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 6, 12, 4),
            child: SegmentedButton<_MapViewMode>(
              segments: const [
                ButtonSegment(value: _MapViewMode.heatmap, label: Text("Calor"), icon: Icon(Icons.blur_on, size: 18)),
                ButtonSegment(value: _MapViewMode.markers, label: Text("Marcadores"), icon: Icon(Icons.place, size: 18)),
                ButtonSegment(value: _MapViewMode.both, label: Text("Ambos"), icon: Icon(Icons.layers, size: 18)),
              ],
              selected: {_viewMode},
              onSelectionChanged: (value) => setState(() => _viewMode = value.first),
            ),
          ),
          Expanded(
            child: _loadError != null
                ? _buildError(_loadError!)
                : _data == null
                    ? const Center(child: CircularProgressIndicator())
                    : Stack(
                        children: [
                          FlutterMap(
                            mapController: _mapController,
                            options: const MapOptions(
                              initialCenter: _ponienteCenter,
                              initialZoom: 10,
                              interactionOptions: InteractionOptions(flags: InteractiveFlag.all),
                            ),
                            children: [
                              TileLayer(
                                urlTemplate: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                                userAgentPackageName: "com.agroplaga.ai",
                              ),
                              if ((_viewMode == _MapViewMode.heatmap || _viewMode == _MapViewMode.both) && clusters.isNotEmpty)
                                CircleLayer(
                                  circles: clusters
                                      .map(
                                        (c) => CircleMarker(
                                          point: LatLng(c.lat, c.lon),
                                          radius: 28 + c.intensity * 50,
                                          color: _heatColor(c.intensity, _validationVisual(c)),
                                          borderColor: _markerBorderColor(c).withValues(alpha: 0.8),
                                          borderStrokeWidth: _validationVisual(c) == _ValidationVisual.pending ? 2 : 1,
                                          useRadiusInMeter: false,
                                        ),
                                      )
                                      .toList(),
                                ),
                              if ((_viewMode == _MapViewMode.markers || _viewMode == _MapViewMode.both) && clusters.isNotEmpty)
                                MarkerLayer(
                                  markers: clusters
                                      .map(
                                        (c) => Marker(
                                          point: LatLng(c.lat, c.lon),
                                          width: 44,
                                          height: 44,
                                          child: Container(
                                            alignment: Alignment.center,
                                            decoration: BoxDecoration(
                                              color: _markerFillColor(c).withValues(
                                                alpha: _validationVisual(c) == _ValidationVisual.pending ? 0.75 : 1,
                                              ),
                                              shape: BoxShape.circle,
                                              border: Border.all(
                                                color: _markerBorderColor(c),
                                                width: _validationVisual(c) == _ValidationVisual.validated ? 3 : 2,
                                              ),
                                            ),
                                            child: Text(
                                              _markerLabel(c),
                                              textAlign: TextAlign.center,
                                              style: TextStyle(
                                                color: _validationVisual(c) == _ValidationVisual.pending
                                                    ? const Color(0xFF1E293B)
                                                    : Colors.white,
                                                fontWeight: FontWeight.bold,
                                                fontSize: _validationVisual(c) == _ValidationVisual.mixed ? 9 : 12,
                                                height: 1.05,
                                              ),
                                            ),
                                          ),
                                        ),
                                      )
                                      .toList(),
                                ),
                              if (clusters.isNotEmpty) _buildTapLayer(clusters),
                            ],
                          ),
                          if (clusters.isEmpty) _buildEmptyOverlay(),
                          if (_isLoading)
                            const Positioned(
                              top: 8,
                              right: 8,
                              child: Card(
                                child: Padding(
                                  padding: EdgeInsets.all(8),
                                  child: SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  ),
                                ),
                              ),
                            ),
                        ],
                      ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
            child: Column(
              children: [
                const MapLegend(),
                const SizedBox(height: 8),
                Text(
                  _data == null ? "" : _footerMessage(clusters, _data!),
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 13, color: Color(0xFF424242)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterDivider extends StatelessWidget {
  const _FilterDivider();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 1,
      height: 24,
      margin: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
      color: const Color(0xFFBDBDBD),
    );
  }
}

class _MapData {
  final List<OutbreakEvent> events;
  final List<HeatmapCell> heatmap;
  final Map<int, AgriZone> zoneById;
  final List<String> plagueOptions;

  _MapData({
    required this.events,
    required this.heatmap,
    required this.zoneById,
    required this.plagueOptions,
  });
}

class _ZoneCluster {
  final int zoneId;
  final String name;
  final String sigpacCode;
  final double lat;
  final double lon;
  final int count;
  final int maxSeverity;
  final double intensity;
  final int validatedCount;
  final int pendingCount;

  _ZoneCluster({
    required this.zoneId,
    required this.name,
    required this.sigpacCode,
    required this.lat,
    required this.lon,
    required this.count,
    required this.maxSeverity,
    required this.intensity,
    required this.validatedCount,
    required this.pendingCount,
  });
}

enum _ValidationVisual { pending, validated, mixed }

class _ValidationStatusChip extends StatelessWidget {
  final _ValidationVisual visual;

  const _ValidationStatusChip({required this.visual});

  @override
  Widget build(BuildContext context) {
    late final String label;
    late final Color color;
    if (visual == _ValidationVisual.pending) {
      label = "Avisos IA sin validar";
      color = const Color(0xFFFFB200);
    } else if (visual == _ValidationVisual.validated) {
      label = "Validado por perito";
      color = const Color(0xFF00A86B);
    } else {
      label = "Mixto: validados + pendientes";
      color = const Color(0xFF5C6BC0);
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color),
      ),
      child: Text(label, style: TextStyle(color: color, fontWeight: FontWeight.w600, fontSize: 12)),
    );
  }
}
