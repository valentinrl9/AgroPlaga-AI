import "dart:async";

import "package:flutter/material.dart";

import "../../../core/nexo_colors.dart";
import "../../../data/repositories/climate_repository.dart";
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
  late TabController _tabs;
  Timer? _refreshTimer;

  bool _unlocked = false;
  bool _loading = true;
  String? _error;
  String? _lastSync;

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

  Future<void> _bootstrap({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _loading = true;
        _error = null;
      });
    }
    try {
      final access = await _repo.fetchAccess();
      if (!(access["climate_accessible"] as bool? ?? false)) {
        if (mounted) setState(() => _unlocked = false);
        return;
      }
      final results = await Future.wait([
        _repo.fetchActual(),
        _repo.fetchRecomendaciones(),
        _repo.fetchRecomendaciones(dias: 30),
        _repo.fetchAlertas(),
        _repo.fetchRiesgo(),
        _repo.fetchEtlStatus(),
      ]);
      if (!mounted) return;
      final actual = results[0] as Map<String, dynamic>;
      final recs = results[1] as Map<String, dynamic>;
      final recs30 = results[2] as Map<String, dynamic>;
      final alertas = results[3] as Map<String, dynamic>;
      final riesgo = results[4] as Map<String, dynamic>;
      final etl = results[5] as Map<String, dynamic>;
      setState(() {
        _unlocked = true;
        _actual = actual;
        _recomendaciones = recs;
        _recomendaciones30 = recs30;
        _alertas = alertas;
        _riesgo = riesgo;
        _consejos = ClimateAdvisor.generate(actual: actual, recomendaciones: recs);
        _lastSync = etl["last_run"]?.toString() ?? DateTime.now().toIso8601String();
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
            "El Ejido, Almería · Clima en tiempo real",
            style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
          ),
          const SizedBox(height: 12),
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
