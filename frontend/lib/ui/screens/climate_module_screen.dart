import "package:flutter/material.dart";

import "../../../core/nexo_colors.dart";
import "../../../data/repositories/climate_repository.dart";
import "../widgets/nexo_lock_screen.dart";
import "climate/climate_advisor.dart";
import "climate/climate_charts.dart";

class ClimateModuleScreen extends StatefulWidget {
  const ClimateModuleScreen({super.key});

  @override
  State<ClimateModuleScreen> createState() => _ClimateModuleScreenState();
}

class _ClimateModuleScreenState extends State<ClimateModuleScreen> with SingleTickerProviderStateMixin {
  final _repo = ClimateRepository();
  late TabController _tabs;

  bool _unlocked = false;
  bool _loading = true;
  String? _error;

  Map<String, dynamic>? _actual;
  Map<String, dynamic>? _recomendaciones;
  Map<String, dynamic>? _alertas;
  List<dynamic> _prediccion = [];
  Map<String, String> _consejos = {};

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 4, vsync: this);
    _bootstrap();
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _bootstrap() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final access = await _repo.fetchAccess();
      if (!(access["climate_accessible"] as bool? ?? false)) {
        if (mounted) setState(() => _unlocked = false);
        return;
      }
      final results = await Future.wait([
        _repo.fetchActual(),
        _repo.fetchRecomendaciones(),
        _repo.fetchAlertas(),
        _repo.fetchPrediccion(),
      ]);
      if (!mounted) return;
      final actual = results[0] as Map<String, dynamic>;
      final recs = results[1] as Map<String, dynamic>;
      final alertas = results[2] as Map<String, dynamic>;
      final pred = results[3] as List<dynamic>;
      setState(() {
        _unlocked = true;
        _actual = actual;
        _recomendaciones = recs;
        _alertas = alertas;
        _prediccion = pred;
        _consejos = ClimateAdvisor.generate(actual: actual, recomendaciones: recs);
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

  Color _dpvColor(String? status) {
    switch (status) {
      case "optimal":
        return const Color(0xFF10B981);
      case "warning":
        return NexoColors.warningAmber;
      case "critical":
        return const Color(0xFFEF4444);
      default:
        return NexoColors.techCyan;
    }
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
            Tab(text: "Informe"),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loading ? null : _bootstrap),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
              : TabBarView(
                  controller: _tabs,
                  children: [
                    _buildInicio(),
                    _buildRecomendaciones(),
                    _buildAlertas(),
                    _buildInforme(),
                  ],
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
      onRefresh: _bootstrap,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            "El Ejido, Almería · Clima en tiempo real",
            style: TextStyle(color: NexoColors.lightText, fontSize: 13),
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
              accent: _dpvColor(_actual!["dpv_status"] as String?),
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
    final riesgo = _alertas?["riesgo_acumulado"] as Map<String, dynamic>? ?? {};

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(_alertas?["resumen"]?.toString() ?? "", style: const TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 16),
        _section("Prioritarias", prioritarias),
        _section("Alertas reales (7 días)", reales),
        _section("Predicción", pred),
        _section("Riesgo acumulado real", (riesgo["real"] as List?)?.cast<String>() ?? []),
        _section("Riesgo acumulado previsto", (riesgo["prediccion"] as List?)?.cast<String>() ?? []),
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
            child: Text("Sin alertas en esta categoría.", style: TextStyle(color: Colors.grey)),
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

  Widget _buildInforme() {
    final sem = _recomendaciones?["resumen_semanal"] as Map<String, dynamic>? ?? {};
    final mes = _recomendaciones?["resumen_mensual"] as Map<String, dynamic>? ?? {};

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("Informe resumido", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Text("Generado desde datos Open-Meteo · NEXO Climate", style: TextStyle(color: NexoColors.lightText)),
        const SizedBox(height: 20),
        _informeBlock("Resumen semanal", sem),
        const SizedBox(height: 16),
        _informeBlock("Resumen mensual", mes),
        const SizedBox(height: 20),
        const Text(
          "La exportación PDF estará disponible en una próxima iteración.",
          style: TextStyle(fontSize: 12, color: Colors.grey),
        ),
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
