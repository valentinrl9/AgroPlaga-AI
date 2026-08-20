import "dart:async";

import "package:flutter/material.dart";

import "../../../core/nexo_colors.dart";
import "../../../data/repositories/climate_repository.dart";
import "../../../data/repositories/farm_repository.dart";
import "../../../models/farm.dart";
import "../widgets/primary_button.dart";
import "../widgets/nexo_lock_screen.dart";
import "climate/climate_advisor.dart";
import "climate/climate_charts.dart";
import "climate/climate_report_pdf.dart";

class ClimateModuleScreen extends StatefulWidget {
  const ClimateModuleScreen({super.key});

  @override
  State<ClimateModuleScreen> createState() => _ClimateModuleScreenState();
}

class _ClimateModuleScreenState extends State<ClimateModuleScreen> with SingleTickerProviderStateMixin {
  final _repo = ClimateRepository();
  final _farmRepo = FarmRepository();
  late TabController _tabs;
  Timer? _refreshTimer;

  bool _unlocked = false;
  bool _loading = true;
  String? _error;
  String? _lastSync;
  List<Farm> _farms = [];
  List<dynamic> _stations = [];
  int? _selectedFarmId;
  String? _stationLabel;
  String? _autoStationLabel;
  bool _stationManualOverride = false;
  bool _savingStation = false;

  Map<String, dynamic>? _actual;
  Map<String, dynamic>? _recomendaciones;
  Map<String, dynamic>? _recomendaciones30;
  Map<String, dynamic>? _alertas;
  Map<String, dynamic>? _riesgo;
  Map<String, String> _consejos = {};

  static const _refreshInterval = Duration(minutes: 15);

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 5, vsync: this);
    _bootstrap();
    _refreshTimer = Timer.periodic(_refreshInterval, (_) => _bootstrap(silent: true));
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _tabs.dispose();
    super.dispose();
  }

  void _clearClimateData() {
    _actual = null;
    _recomendaciones = null;
    _recomendaciones30 = null;
    _alertas = null;
    _riesgo = null;
    _consejos = {};
    _stationLabel = null;
    _autoStationLabel = null;
    _stationManualOverride = false;
  }

  Future<Map<String, dynamic>> _fetchClimateMap(Future<Map<String, dynamic>> future) async {
    try {
      return await future;
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  Future<void> _bootstrap({bool silent = false, bool notifyError = false}) async {
    if (!silent) {
      setState(() {
        _loading = true;
        _error = null;
        _clearClimateData();
      });
    }
    try {
      final access = await _repo.fetchAccess();
      if (!(access["climate_accessible"] as bool? ?? false)) {
        if (mounted) setState(() => _unlocked = false);
        return;
      }

      if (_farms.isEmpty) {
        final farms = await _farmRepo.fetchFarms();
        if (mounted) {
          setState(() {
            _farms = farms;
            _selectedFarmId ??= farms.where((f) => f.zoneId != null).map((f) => f.id).cast<int?>().firstWhere(
                  (id) => id != null,
                  orElse: () => null,
                );
          });
        }
      }
      if (_stations.isEmpty) {
        final stations = await _repo.fetchStations();
        if (mounted) setState(() => _stations = stations);
      }

      final farmId = _selectedFarmId;
      final actual = await _repo.fetchActual(farmId: farmId);
      final results = await Future.wait([
        _fetchClimateMap(_repo.fetchRecomendaciones(farmId: farmId)),
        _fetchClimateMap(_repo.fetchRecomendaciones(dias: 30, farmId: farmId)),
        _fetchClimateMap(_repo.fetchAlertas(farmId: farmId)),
        _fetchClimateMap(_repo.fetchRiesgo(farmId: farmId)),
        _fetchClimateMap(_repo.fetchEtlStatus()),
      ]);
      if (!mounted) return;
      final recs = results[0];
      final recs30 = results[1];
      final alertas = results[2];
      final riesgo = results[3];
      final etl = results[4];
      final station = actual["station"] as Map<String, dynamic>? ?? recs["station"] as Map<String, dynamic>?;
      final autoStation = actual["auto_station"] as Map<String, dynamic>? ?? recs["auto_station"] as Map<String, dynamic>?;
      setState(() {
        _unlocked = true;
        _actual = actual;
        _recomendaciones = recs;
        _recomendaciones30 = recs30;
        _alertas = alertas;
        _riesgo = riesgo;
        _stationLabel = station?["name"] as String? ?? "Sur de Almería";
        _autoStationLabel = autoStation?["name"] as String? ?? _stationLabel;
        _stationManualOverride = actual["station_manual_override"] as bool? ?? false;
        _consejos = ClimateAdvisor.generate(actual: actual, recomendaciones: recs);
        _lastSync = etl["last_run"]?.toString() ?? DateTime.now().toIso8601String();
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
        if (!silent) _clearClimateData();
      });
      if (notifyError && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("No se pudieron cargar datos de la estación: $e"),
            backgroundColor: NexoColors.errorRed,
          ),
        );
      }
    }
  }

  void _onFarmChanged(int? farmId) {
    setState(() => _selectedFarmId = farmId);
    _bootstrap();
  }

  Farm? get _selectedFarm {
    if (_selectedFarmId == null) return null;
    for (final f in _farms) {
      if (f.id == _selectedFarmId) return f;
    }
    return null;
  }

  Future<void> _onStationChanged(int? stationId) async {
    final farm = _selectedFarm;
    if (farm == null) return;
    setState(() {
      _savingStation = true;
      _loading = true;
      _error = null;
      _clearClimateData();
    });
    try {
      final updated = await _farmRepo.updateFarm(
        farm.id,
        clearClimateStation: stationId == null,
        climateStationId: stationId,
      );
      if (!mounted) return;
      setState(() {
        final idx = _farms.indexWhere((f) => f.id == farm.id);
        if (idx >= 0) _farms[idx] = updated;
      });
      await _bootstrap(notifyError: true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("No se pudo guardar estación: $e"), backgroundColor: NexoColors.errorRed),
        );
      }
    } finally {
      if (mounted) setState(() => _savingStation = false);
    }
  }

  Widget _farmSelector() {
    final withZone = _farms.where((f) => f.zoneId != null).toList();
    if (withZone.isEmpty) {
      return Text(
        _stationLabel ?? "Estación Poniente (fallback)",
        style: const TextStyle(color: NexoColors.textSecondary, fontSize: 13),
      );
    }

    return DropdownButtonFormField<int>(
      value: withZone.any((f) => f.id == _selectedFarmId) ? _selectedFarmId : withZone.first.id,
      decoration: const InputDecoration(labelText: "Finca"),
      items: withZone
          .map(
            (f) => DropdownMenuItem(
              value: f.id,
              child: Text("${f.name} · ${f.crop}", overflow: TextOverflow.ellipsis),
            ),
          )
          .toList(),
      onChanged: _loading || _savingStation ? null : _onFarmChanged,
    );
  }

  Widget _stationSelector() {
    if (_stations.isEmpty) return const SizedBox.shrink();
    final farm = _selectedFarm;
    final currentOverride = farm?.climateStationId;
    final autoLabel = _autoStationLabel ?? "—";

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        DropdownButtonFormField<int?>(
          value: currentOverride,
          decoration: InputDecoration(
            labelText: "Estación meteorológica",
            helperText: _stationManualOverride
                ? "Selección manual activa"
                : "Automática por proximidad al municipio de la finca",
          ),
          items: [
            DropdownMenuItem<int?>(
              value: null,
              child: Text("Automática · $autoLabel", overflow: TextOverflow.ellipsis),
            ),
            ..._stations.map(
              (s) => DropdownMenuItem<int?>(
                value: s["id"] as int,
                child: Text(s["name"] as String, overflow: TextOverflow.ellipsis),
              ),
            ),
          ],
          onChanged: _loading || _savingStation ? null : _onStationChanged,
        ),
        if (_stationLabel != null) ...[
          const SizedBox(height: 6),
          Text(
            _stationManualOverride
                ? "Datos: $_stationLabel (manual)"
                : "Datos: $_stationLabel (automática)",
            style: const TextStyle(color: NexoColors.bioGreen, fontSize: 13, fontWeight: FontWeight.w600),
          ),
          if (_stationManualOverride && _autoStationLabel != null)
            Text(
              "La automática sería: $_autoStationLabel",
              style: const TextStyle(color: NexoColors.textSecondary, fontSize: 12),
            ),
        ],
      ],
    );
  }

  List<Map<String, dynamic>> _chartSeries() {
    final diario = (_recomendaciones?["diario"] as List?)?.cast<Map<String, dynamic>>() ?? [];
    final serie = <Map<String, dynamic>>[];
    if (_actual != null && _actual!["et0_dia"] != null) {
      final parcial = _actual!["et0_parcial"] as bool? ?? false;
      serie.add({
        "fecha": parcial ? "Hoy*" : "Hoy",
        "et0": (_actual!["et0_dia"] as num?)?.toDouble() ?? 0,
        "estres": (_actual!["estres_termico"] as num?)?.toDouble() ?? 0,
        "humedad": (_actual!["humedad_dia"] as num?)?.toDouble() ?? (_actual!["humedad"] as num?)?.toDouble() ?? 0,
      });
    }
    serie.addAll(diario);
    return serie;
  }

  Color _statusColor(String? status) {
    switch (status) {
      case "optimal":
        return NexoColors.successGreen;
      case "warning":
        return NexoColors.warningAmber;
      case "critical":
        return NexoColors.errorRed;
      default:
        return NexoColors.techCyan;
    }
  }

  Color _riskBarColor(int pct) {
    if (pct >= 70) return NexoColors.errorRed;
    if (pct >= 45) return NexoColors.warningAmber;
    return NexoColors.successGreen;
  }

  @override
  Widget build(BuildContext context) {
    if (!_unlocked && !_loading) {
      return const Scaffold(body: NexoLockScreen(moduleName: "NEXO Climate", isB2C: true));
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("NEXO Climate"),
        bottom: TabBar(
          controller: _tabs,
          isScrollable: true,
          tabs: const [
            Tab(text: "Inicio"),
            Tab(text: "Recomendaciones"),
            Tab(text: "Alertas"),
            Tab(text: "Riesgo"),
            Tab(text: "Informe"),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loading ? null : () => _bootstrap()),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: NexoColors.errorRed)))
              : TabBarView(
                  controller: _tabs,
                  children: [
                    _buildInicio(),
                    _buildRecomendaciones(),
                    _buildAlertas(),
                    _buildRiesgo(),
                    _buildInforme(),
                  ],
                ),
    );
  }

  Widget _syncFooter() {
    if (_lastSync == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Text(
        "Sincronización ETL · auto-refresh 15 min · última: ${_lastSync!.substring(0, 16)}",
        style: const TextStyle(fontSize: 11, color: NexoColors.textSecondary),
      ),
    );
  }

  Widget _buildInicio() {
    final serie = _chartSeries();
    final labels = serie.map((e) => e["fecha"].toString()).toList();
    final et0 = serie.map((e) => (e["et0"] as num).toDouble()).toList();
    final estres = serie.map((e) => (e["estres"] as num).toDouble()).toList();
    final humedad = serie.map((e) => (e["humedad"] as num).toDouble()).toList();

    return RefreshIndicator(
      onRefresh: () => _bootstrap(),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            "Clima según tu finca — estación automática o manual",
            style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
          ),
          const SizedBox(height: 8),
          _farmSelector(),
          const SizedBox(height: 12),
          _stationSelector(),
          if (_savingStation)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: LinearProgressIndicator(),
            ),
          const SizedBox(height: 8),
          if (_actual != null) ...[
            ClimateMetricCard(
              emoji: "🌡️",
              title: "Temperatura",
              value: "${(_actual!["temperatura"] as num?)?.toStringAsFixed(1) ?? "-"} °C",
            ),
            const SizedBox(height: 8),
            ClimateMetricCard(
              emoji: "💧",
              title: "Humedad",
              value: "${(_actual!["humedad"] as num?)?.toStringAsFixed(0) ?? "-"} %",
            ),
            const SizedBox(height: 8),
            ClimateMetricCard(
              emoji: "🌿",
              title: "ET0 día",
              value: "${_actual!["et0_dia"] ?? "-"} mm",
              hint: (_actual!["et0_parcial"] as bool? ?? false) ? "Dato parcial del día" : null,
            ),
            const SizedBox(height: 8),
            ClimateMetricCard(
              emoji: "💨",
              title: "DPV",
              value: "${_actual!["dpv_kpa"] ?? "-"} kPa",
              accent: _statusColor(_actual!["dpv_status"] as String?),
            ),
            const SizedBox(height: 8),
            ClimateMetricCard(
              emoji: "🌫️",
              title: "Punto de rocío",
              value: "${_actual!["punto_rocio_c"] ?? "-"} °C",
              hint: "Condensación en cubierta plástica",
              accent: _statusColor(_actual!["punto_rocio_status"] as String?),
            ),
          ],
          const SizedBox(height: 16),
          ClimateLineChart(title: "ET0 (mm/día)", labels: labels, values: et0, color: NexoColors.bioGreen),
          const SizedBox(height: 10),
          ClimateLineChart(title: "Estrés térmico", labels: labels, values: estres, color: NexoColors.warningAmber),
          const SizedBox(height: 10),
          ClimateLineChart(title: "Humedad (%)", labels: labels, values: humedad, color: NexoColors.techCyan),
          const SizedBox(height: 16),
          const Text("Panel IA agronómico", style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          ClimateIaPanel(consejos: _consejos),
          _syncFooter(),
        ],
      ),
    );
  }

  Widget _buildRecomendaciones() {
    final diario = (_recomendaciones?["diario"] as List?) ?? [];
    if (diario.isEmpty) {
      return const Center(child: Text("Sin recomendaciones disponibles"));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: diario.length,
      itemBuilder: (context, i) {
        final d = diario[i] as Map<String, dynamic>;
        final recs = (d["recomendaciones"] as List?)?.cast<String>() ?? [];
        return Card(
          margin: const EdgeInsets.only(bottom: 10),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(d["fecha"]?.toString() ?? "", style: const TextStyle(fontWeight: FontWeight.w700)),
                const SizedBox(height: 6),
                Text("ET0 ${d["et0"]} · Estrés ${d["estres"]} · HR ${d["humedad"]}%"),
                const SizedBox(height: 8),
                ...recs.map((r) => Padding(padding: const EdgeInsets.only(bottom: 4), child: Text("• $r"))),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildAlertas() {
    final prioritarias = (_alertas?["alertas_prioritarias"] as List?)?.cast<String>() ?? [];
    final reales = (_alertas?["alertas_reales"] as List?)?.cast<String>() ?? [];
    final pred = (_alertas?["alertas_prediccion"] as List?)?.cast<String>() ?? [];
    final combinadas = (_alertas?["alertas_combinadas"] as List?)?.cast<String>() ?? [];
    final riesgo = _alertas?["riesgo_acumulado"] as Map<String, dynamic>? ?? {};

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(_alertas?["resumen"]?.toString() ?? "", style: const TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 16),
        _section("Prioritarias", prioritarias),
        _section("Combinadas (riesgo)", combinadas),
        _section("Alertas reales (7 días)", reales),
        _section("Predicción", pred),
        _section("Riesgo acumulado real", (riesgo["real"] as List?)?.cast<String>() ?? []),
        _section("Riesgo acumulado previsto", (riesgo["prediccion"] as List?)?.cast<String>() ?? []),
      ],
    );
  }

  Widget _buildRiesgo() {
    final score = (_riesgo?["score_pct"] as num?)?.toInt() ?? 0;
    final diario = (_riesgo?["diario"] as List?)?.cast<Map<String, dynamic>>() ?? [];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Riesgo acumulado semanal", style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
                const SizedBox(height: 12),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: score / 100,
                    minHeight: 14,
                    color: _riskBarColor(score),
                    backgroundColor: NexoColors.surfaceElevated,
                  ),
                ),
                const SizedBox(height: 8),
                Text("$score% · estrés 60% + humedad 40%", style: const TextStyle(color: NexoColors.textSecondary)),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        ...diario.map((d) {
          final pct = (d["riesgo_pct"] as num?)?.toInt() ?? 0;
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              title: Text(d["fecha"]?.toString() ?? ""),
              subtitle: Text("Estrés ${d["estres"]} · HR ${d["humedad"]}%"),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: _riskBarColor(pct).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text("$pct%", style: TextStyle(fontWeight: FontWeight.bold, color: _riskBarColor(pct))),
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildInforme() {
    final sem = _recomendaciones?["resumen_semanal"] as Map<String, dynamic>? ?? {};
    final mes = _recomendaciones30?["resumen_mensual"] as Map<String, dynamic>? ??
        _recomendaciones?["resumen_mensual"] as Map<String, dynamic>? ??
        {};

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("Informe resumido", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        const Text(
          "Generado desde datos Open-Meteo · NEXO Climate",
          style: TextStyle(color: NexoColors.textSecondary),
        ),
        const SizedBox(height: 20),
        _informeBlock("Resumen semanal", sem),
        const SizedBox(height: 16),
        _informeBlock("Resumen mensual (30 días)", mes),
        const SizedBox(height: 20),
        PrimaryButton(
          label: "Descargar informe PDF",
          onPressed: () => exportClimateMonthlyPdf(resumenMensual: mes, resumenSemanal: sem),
        ),
        _syncFooter(),
      ],
    );
  }

  Widget _section(String title, List<String> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
        const SizedBox(height: 8),
        if (items.isEmpty)
          const Padding(
            padding: EdgeInsets.only(bottom: 16),
            child: Text("Sin alertas en esta categoría.", style: TextStyle(color: NexoColors.textSecondary)),
          )
        else
          ...items.map(
            (a) => Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: Padding(padding: const EdgeInsets.all(12), child: Text(a)),
            ),
          ),
        const SizedBox(height: 8),
      ],
    );
  }

  Widget _informeBlock(String title, Map<String, dynamic> data) {
    final info = (data["informacion"] as List?)?.cast<String>() ?? [];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
            const SizedBox(height: 10),
            ...info.map((line) => Padding(padding: const EdgeInsets.only(bottom: 4), child: Text(line))),
            if (data["nivel_riesgo"] != null) ...[
              const SizedBox(height: 10),
              Text("Riesgo: ${data["nivel_riesgo"]}", style: const TextStyle(fontWeight: FontWeight.w600)),
            ],
            if (data["recomendacion_general"] != null) ...[
              const SizedBox(height: 6),
              Text(data["recomendacion_general"].toString()),
            ],
          ],
        ),
      ),
    );
  }
}
