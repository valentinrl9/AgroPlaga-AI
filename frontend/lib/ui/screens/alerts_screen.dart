import "package:flutter/material.dart";

import "../../core/auth_redirect.dart";
import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../data/repositories/alert_repository.dart";
import "../../models/alert.dart";
import "map_screen_args.dart";
import "../widgets/primary_button.dart";

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  final _repository = AlertRepository();
  late Future<List<PlagaAlert>> _alertsFuture;

  @override
  void initState() {
    super.initState();
    _alertsFuture = _repository.fetchAlerts();
  }

  Future<void> _reload() async {
    final newFuture = _repository.fetchAlerts();
    setState(() {
      _alertsFuture = newFuture;
    });
    await newFuture;
  }

  IconData _iconFor(String type) {
    switch (type) {
      case "spike":
        return Icons.trending_up;
      case "new_plague":
        return Icons.fiber_new;
      case "severity_surge":
        return Icons.priority_high;
      default:
        return Icons.warning_amber_rounded;
    }
  }

  String _typeLabel(String type) {
    switch (type) {
      case "spike":
        return "Pico";
      case "new_plague":
        return "Nueva plaga";
      case "severity_surge":
        return "Severidad alta";
      default:
        return type;
    }
  }

  Color _priorityColor(double? score) {
    if (score == null) return NexoColors.textSecondary;
    if (score >= 0.7) return NexoColors.errorRed;
    if (score >= 0.4) return NexoColors.warningAmber;
    return NexoColors.bioGreen;
  }

  String _timeAgo(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inMinutes < 60) return "hace ${diff.inMinutes} min";
    if (diff.inHours < 24) return "hace ${diff.inHours} h";
    return "hace ${diff.inDays} d";
  }

  Future<void> _openPreferences() async {
    final saved = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => const _AlertPreferencesSheet()),
    );
    if (saved == true) _reload();
  }

  Future<void> _dismiss(PlagaAlert alert) async {
    try {
      await _repository.dismissAlert(alert.id);
      if (!mounted) return;
      _reload();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Alerta descartada")),
      );
    } catch (error) {
      if (!mounted) return;
      AuthRedirect.redirectIfUnauthorized(context, error);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("No se pudo descartar: $error")),
      );
    }
  }

  void _openOnMap(PlagaAlert alert) {
    Navigator.pushNamed(
      context,
      Routes.map,
      arguments: MapScreenArgs(zoneId: alert.zoneId, plague: alert.plague),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Alertas de zona"),
        actions: [
          IconButton(
            icon: const Icon(Icons.tune),
            tooltip: "Preferencias",
            onPressed: _openPreferences,
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _reload),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Alertas tempranas",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              "Avisos automáticos cuando aumentan diagnósticos, aparece una plaga nueva o sube la severidad.",
              style: TextStyle(color: NexoColors.textPrimary),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: FutureBuilder<List<PlagaAlert>>(
                future: _alertsFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    if (AuthRedirect.isUnauthorized(snapshot.error!)) {
                      AuthRedirect.redirectIfUnauthorized(context, snapshot.error!);
                      return const Center(child: Text("Sesión expirada. Redirigiendo al login..."));
                    }
                    return Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.cloud_off, size: 48, color: Color(0xFF9E9E9E)),
                          const SizedBox(height: 12),
                          Text("Error: ${snapshot.error}", textAlign: TextAlign.center),
                          const SizedBox(height: 12),
                          OutlinedButton(onPressed: _reload, child: const Text("Reintentar")),
                        ],
                      ),
                    );
                  }

                  final alerts = snapshot.data ?? [];
                  if (alerts.isEmpty) {
                    return Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.notifications_none, size: 48, color: Color(0xFF9E9E9E)),
                          const SizedBox(height: 12),
                          const Text(
                            "No hay alertas activas.\nEl motor revisa la red cada 30 min.",
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          OutlinedButton.icon(
                            onPressed: _openPreferences,
                            icon: const Icon(Icons.tune),
                            label: const Text("Configurar plagas"),
                          ),
                        ],
                      ),
                    );
                  }

                  return RefreshIndicator(
                    onRefresh: () async => _reload(),
                    child: ListView.separated(
                      physics: const AlwaysScrollableScrollPhysics(),
                      itemCount: alerts.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final alert = alerts[index];
                        final priority = alert.priorityScore;
                        return Dismissible(
                          key: ValueKey(alert.id),
                          direction: DismissDirection.endToStart,
                          background: Container(
                            alignment: Alignment.centerRight,
                            padding: const EdgeInsets.only(right: 20),
                            decoration: BoxDecoration(
                              color: NexoColors.errorRed.withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(Icons.delete_outline, color: NexoColors.errorRed),
                          ),
                          onDismissed: (_) => _dismiss(alert),
                          child: Card(
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: _priorityColor(priority).withValues(alpha: 0.15),
                                child: Icon(_iconFor(alert.alertType), color: _priorityColor(priority)),
                              ),
                              title: Text(
                                "${alert.plague} · ${alert.zoneName ?? "Zona ${alert.zoneId}"}",
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 4),
                                  Text(alert.description),
                                  const SizedBox(height: 6),
                                  Wrap(
                                    spacing: 6,
                                    runSpacing: 4,
                                    children: [
                                      Chip(
                                        label: Text(_typeLabel(alert.alertType), style: const TextStyle(fontSize: 11)),
                                        visualDensity: VisualDensity.compact,
                                        padding: EdgeInsets.zero,
                                      ),
                                      if (priority != null)
                                        Chip(
                                          label: Text(
                                            "Prioridad ${(priority * 100).toStringAsFixed(0)}%",
                                            style: const TextStyle(fontSize: 11),
                                          ),
                                          visualDensity: VisualDensity.compact,
                                          padding: EdgeInsets.zero,
                                        ),
                                      Chip(
                                        label: Text(_timeAgo(alert.createdAt), style: const TextStyle(fontSize: 11)),
                                        visualDensity: VisualDensity.compact,
                                        padding: EdgeInsets.zero,
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Align(
                                    alignment: Alignment.centerLeft,
                                    child: TextButton.icon(
                                      onPressed: () => _openOnMap(alert),
                                      icon: const Icon(Icons.map_outlined, size: 18),
                                      label: const Text("Ver en mapa"),
                                    ),
                                  ),
                                ],
                              ),
                              isThreeLine: true,
                              trailing: IconButton(
                                icon: const Icon(Icons.close),
                                tooltip: "Descartar",
                                onPressed: () => _dismiss(alert),
                              ),
                            ),
                          ),
                        );
                      },
                    ),
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

class _AlertPreferencesSheet extends StatefulWidget {
  const _AlertPreferencesSheet();

  @override
  State<_AlertPreferencesSheet> createState() => _AlertPreferencesSheetState();
}

class _AlertPreferencesSheetState extends State<_AlertPreferencesSheet> {
  final _repository = AlertRepository();
  late Future<AlertPreferencesData> _prefsFuture;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _prefsFuture = _repository.fetchPreferences();
  }

  Future<void> _save(List<AlertPreference> prefs) async {
    setState(() => _saving = true);
    try {
      await _repository.savePreferences(prefs);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Preferencias de alertas")),
      body: FutureBuilder<AlertPreferencesData>(
        future: _prefsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text("Error: ${snapshot.error}"));
          }

          final data = snapshot.data!;
          if (data.availablePlagues.isEmpty) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Text(
                  "Aún no hay plagas en la red. Contribuye tras un escaneo para configurar avisos.",
                  textAlign: TextAlign.center,
                ),
              ),
            );
          }

          final prefs = List<AlertPreference>.from(data.preferences);

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text(
                "Elige qué plagas quieres ver en tus alertas. Si desactivas una, no aparecerá en la lista.",
                style: TextStyle(color: NexoColors.textPrimary),
              ),
              const SizedBox(height: 16),
              ...List.generate(prefs.length, (index) {
                final pref = prefs[index];
                return SwitchListTile(
                  title: Text(pref.plague),
                  value: pref.enabled,
                  onChanged: _saving
                      ? null
                      : (value) {
                          setState(() {
                            prefs[index] = AlertPreference(plague: pref.plague, enabled: value);
                          });
                        },
                );
              }),
              const SizedBox(height: 16),
              PrimaryButton(
                label: _saving ? "Guardando..." : "Guardar preferencias",
                onPressed: _saving ? null : () => _save(prefs),
              ),
            ],
          );
        },
      ),
    );
  }
}
