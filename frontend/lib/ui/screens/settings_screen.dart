import "package:flutter/material.dart";
import "package:http/http.dart" as http;

import "../../core/api_config.dart";
import "../../core/nexo_colors.dart";
import "../../core/session.dart";
import "../../data/repositories/activity_repository.dart";
import "../../models/notification_preferences.dart";
import "../layout/mobile_layout.dart";
import "../widgets/primary_button.dart";

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late final TextEditingController _urlController;
  final _activityRepo = ActivityRepository();
  bool _testing = false;
  bool _saving = false;
  bool _loadingPrefs = true;
  bool _savingPrefs = false;
  String? _status;
  NotificationPreferences? _prefs;
  bool _isTech = false;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: ApiConfig.baseUrl);
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    _isTech = await Session.isTechOrAdmin;
    await _loadNotificationPreferences();
  }

  Future<void> _loadNotificationPreferences() async {
    setState(() => _loadingPrefs = true);
    try {
      final prefs = await _activityRepo.fetchNotificationPreferences();
      if (!mounted) return;
      setState(() => _prefs = prefs);
    } catch (_) {
      if (!mounted) return;
      setState(() => _status = "No se pudieron cargar las preferencias de notificación.");
    } finally {
      if (mounted) setState(() => _loadingPrefs = false);
    }
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<bool> _pingServer(String baseUrl) async {
    final uri = Uri.parse("${ApiConfig.normalize(baseUrl)}/api/v1/climate/health");
    final response = await http.get(uri).timeout(const Duration(seconds: 8));
    return response.statusCode == 200;
  }

  Future<void> _testConnection() async {
    FocusManager.instance.primaryFocus?.unfocus();
    setState(() {
      _testing = true;
      _status = null;
    });
    try {
      final ok = await _pingServer(_urlController.text);
      if (!mounted) return;
      setState(() {
        _status = ok ? "Conexión correcta con el servidor." : "El servidor respondió con error.";
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _status = "No se pudo conectar. Comprueba la IP, Wi‑Fi y que Docker esté activo.";
      });
    } finally {
      if (mounted) setState(() => _testing = false);
    }
  }

  Future<void> _save() async {
    FocusManager.instance.primaryFocus?.unfocus();
    setState(() {
      _saving = true;
      _status = null;
    });
    try {
      final normalized = ApiConfig.normalize(_urlController.text);
      await ApiConfig.save(normalized);
      if (!mounted) return;
      setState(() {
        _urlController.text = normalized;
        _status = "URL guardada. No hace falta reinstalar la app.";
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _status = e.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _reset() async {
    await ApiConfig.reset();
    if (!mounted) return;
    setState(() {
      _urlController.text = ApiConfig.baseUrl;
      _status = "Restaurada la URL por defecto.";
    });
  }

  Future<void> _saveNotificationPreferences() async {
    final prefs = _prefs;
    if (prefs == null) return;
    setState(() {
      _savingPrefs = true;
      _status = null;
    });
    try {
      final saved = await _activityRepo.updateNotificationPreferences(prefs);
      if (!mounted) return;
      setState(() {
        _prefs = saved;
        _status = "Preferencias de notificación guardadas.";
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _status = e.toString());
    } finally {
      if (mounted) setState(() => _savingPrefs = false);
    }
  }

  void _patchPrefs(NotificationPreferences Function(NotificationPreferences p) patch) {
    final current = _prefs;
    if (current == null) return;
    setState(() => _prefs = patch(current));
  }

  bool _isSuccessStatus(String? msg) {
    if (msg == null) return false;
    return msg.contains("correcta") ||
        msg.contains("guardad") ||
        msg.contains("Restaurada") ||
        msg.contains("Preferencias");
  }

  Widget _prefSwitch({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return SwitchListTile(
      title: Text(title),
      subtitle: Text(subtitle, style: const TextStyle(fontSize: 12, color: NexoColors.textSecondary)),
      value: value,
      onChanged: onChanged,
    );
  }

  Widget _notificationPreferencesSection() {
    if (_loadingPrefs) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 24),
        child: Center(child: CircularProgressIndicator()),
      );
    }
    final prefs = _prefs;
    if (prefs == null) {
      return const Text("Preferencias no disponibles.", style: TextStyle(color: NexoColors.textSecondary));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text("Notificaciones push", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        const Text(
          "Controla qué avisos llegan al móvil. Los badges in-app siguen activos.",
          style: TextStyle(color: NexoColors.textSecondary),
        ),
        const SizedBox(height: 8),
        if (_isTech)
          _prefSwitch(
            title: "Validaciones pendientes (perito)",
            subtitle: "Cuando un agricultor comparte un escaneo.",
            value: prefs.pushTechPending,
            onChanged: (v) => _patchPrefs((p) => p.copyWith(pushTechPending: v)),
          )
        else ...[
          _prefSwitch(
            title: "Validación del técnico",
            subtitle: "Confirmación, corrección o rechazo de escaneos.",
            value: prefs.pushScanValidation,
            onChanged: (v) => _patchPrefs((p) => p.copyWith(pushScanValidation: v)),
          ),
          _prefSwitch(
            title: "Incidencias CRM",
            subtitle: "Recordatorios de tratamiento, foto o evaluación.",
            value: prefs.pushIncidents,
            onChanged: (v) => _patchPrefs((p) => p.copyWith(pushIncidents: v)),
          ),
          _prefSwitch(
            title: "Carencia cumplida",
            subtitle: "Aviso cuando finaliza el plazo de seguridad.",
            value: prefs.pushCarencia,
            onChanged: (v) => _patchPrefs((p) => p.copyWith(pushCarencia: v)),
          ),
          _prefSwitch(
            title: "Alertas comarcales",
            subtitle: "Solo si tienes finca en la zona y la plaga está activada.",
            value: prefs.pushAlertsComarcal,
            onChanged: (v) => _patchPrefs((p) => p.copyWith(pushAlertsComarcal: v)),
          ),
          _prefSwitch(
            title: "Insignias y reto semanal",
            subtitle: "Gamificación y objetivo de vigilancia.",
            value: prefs.pushBadges && prefs.pushWeekly,
            onChanged: (v) => _patchPrefs((p) => p.copyWith(pushBadges: v, pushWeekly: v)),
          ),
        ],
        const Divider(height: 24),
        _prefSwitch(
          title: "Horario quieto (22:00–07:00)",
          subtitle: "Silencia push no críticos por la noche.",
          value: prefs.quietHoursEnabled,
          onChanged: (v) => _patchPrefs((p) => p.copyWith(quietHoursEnabled: v)),
        ),
        const SizedBox(height: 12),
        PrimaryButton(
          label: _savingPrefs ? "Guardando..." : "Guardar preferencias",
          onPressed: _savingPrefs ? null : _saveNotificationPreferences,
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Ajustes")),
      body: SafeArea(
        child: MobileLayout.dismissKeyboardOnTap(
          context: context,
          child: SingleChildScrollView(
            padding: MobileLayout.scrollPadding(context),
            keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _notificationPreferencesSection(),
                const SizedBox(height: 28),
                if (_status != null && !ApiConfig.allowCustomServerUrl)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(
                      _status!,
                      style: TextStyle(
                        color: _isSuccessStatus(_status) ? NexoColors.bioGreen : NexoColors.errorRed,
                      ),
                    ),
                  ),
                if (ApiConfig.allowCustomServerUrl) ...[
                  const Text("Servidor API (solo desarrollo)", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _urlController,
                    decoration: const InputDecoration(
                      labelText: "URL del backend",
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.url,
                    autocorrect: false,
                  ),
                  if (_status != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      _status!,
                      style: TextStyle(
                        color: _isSuccessStatus(_status) ? NexoColors.bioGreen : NexoColors.errorRed,
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  PrimaryButton(
                    label: _testing ? "Comprobando..." : "Probar conexión",
                    onPressed: _testing ? null : _testConnection,
                  ),
                  const SizedBox(height: 10),
                  PrimaryButton(
                    label: _saving ? "Guardando..." : "Guardar URL",
                    onPressed: _saving ? null : _save,
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton(onPressed: _reset, child: const Text("Restaurar por defecto")),
                ] else ...[
                  const Text("Servidor API", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  Text(ApiConfig.baseUrl, style: const TextStyle(color: NexoColors.textPrimary)),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
