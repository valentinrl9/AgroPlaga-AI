import "dart:async";

import "package:flutter/material.dart";

import "../../core/home_inbox_prefs.dart";
import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/activity_repository.dart";
import "../../data/repositories/auth_repository.dart";
import "../../data/repositories/scan_repository.dart";
import "../../data/repositories/tech_repository.dart";
import "../../data/repositories/treatment_repository.dart";
import "../../models/activity_summary.dart";
import "../layout/mobile_layout.dart";
import "../widgets/farmer_inbox_sheet.dart";
import "../widgets/app_update_banner.dart";
import "../widgets/nexo_section_card.dart";
import "../widgets/primary_button.dart";

class FieldHomeScreen extends StatefulWidget {
  final bool isActive;
  final VoidCallback? onActivityRefreshed;

  const FieldHomeScreen({super.key, this.isActive = true, this.onActivityRefreshed});

  @override
  State<FieldHomeScreen> createState() => _FieldHomeScreenState();
}

class _FieldHomeScreenState extends State<FieldHomeScreen> {
  bool _isTech = false;
  String? _userName;
  Map<String, dynamic>? _techOverview;
  int _pendingScans = 0;
  int _unreadNotifications = 0;
  Timer? _pollTimer;
  int _lastPendingCount = 0;
  int _lastFarmerUnread = 0;

  ActivitySummary? _activity;
  Map<String, dynamic>? _carenciaActive;
  List<UserNotificationItem> _unreadNotifs = [];
  Set<String> _dismissedInboxIds = {};
  final _activityRepo = ActivityRepository();

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  @override
  void didUpdateWidget(FieldHomeScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive && !oldWidget.isActive) {
      if (_isTech) {
        _loadTechDashboard();
      } else {
        _loadFarmerActivity();
      }
    }
    _syncPolling();
  }

  void _syncPolling() {
    _pollTimer?.cancel();
    if (!widget.isActive) return;
    _pollTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (!widget.isActive) return;
      if (_isTech) {
        _loadTechDashboard(notifyOnNew: true);
      } else {
        _loadFarmerActivity(notifyOnNew: true);
      }
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadProfile() async {
    final isTech = await Session.isTechOrAdmin;
    final name = await Session.name;
    if (mounted) {
      setState(() {
        _isTech = isTech;
        _userName = name;
      });
    }
    if (isTech) {
      await _loadTechDashboard();
    } else {
      await _loadFarmerActivity();
    }
    _syncPolling();
  }

  Future<void> _loadFarmerActivity({bool notifyOnNew = false}) async {
    try {
      final summary = await _activityRepo.fetchSummary();
      final dismissed = await HomeInboxPrefs.dismissedIds();
      List<UserNotificationItem> unreadNotifs = [];
      Map<String, dynamic>? carencia;
      try {
        unreadNotifs = await _activityRepo.fetchNotifications(unreadOnly: true);
      } catch (_) {}
      try {
        final treatments = await TreatmentRepository().fetchActive();
        if (treatments.isNotEmpty) {
          carencia = Map<String, dynamic>.from(treatments.first as Map);
        }
      } catch (_) {}

      if (notifyOnNew && summary.unreadCount > _lastFarmerUnread && _lastFarmerUnread > 0 && mounted) {
        if (unreadNotifs.isNotEmpty) {
          final latest = unreadNotifs.first;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text("${latest.title}: ${latest.body}"),
              action: SnackBarAction(
                label: "Ver",
                onPressed: () => unawaited(_openNotification(context, latest)),
              ),
            ),
          );
        }
      }
      if (!mounted) return;
      setState(() {
        _activity = summary;
        _carenciaActive = carencia;
        _unreadNotifs = unreadNotifs;
        _dismissedInboxIds = dismissed;
        _lastFarmerUnread = summary.unreadCount;
      });
      widget.onActivityRefreshed?.call();
    } catch (_) {}
  }

  List<FarmerInboxItem> _buildInboxItems() {
    final activity = _activity;
    final items = <FarmerInboxItem>[];

    if (_carenciaActive != null) {
      final carencia = carenciaInboxItem(_carenciaActive!);
      if (carencia != null && !_dismissedInboxIds.contains(carencia.id)) {
        items.add(carencia);
      }
    }

    final hasVigilanceNotif = _unreadNotifs.any((n) => n.notificationType == "weekly_vigilance");
    final vigilance = activity?.weeklyVigilance;
    if (vigilance != null && !hasVigilanceNotif) {
      final vItem = vigilanceInboxItem(vigilance, activity?.streakWeeks ?? vigilance.streakWeeks);
      if (!_dismissedInboxIds.contains(vItem.id)) {
        items.add(vItem);
      }
    }

    final sigpacPending = (activity?.siexPendingSigpac ?? 0) + (activity?.farmsMissingSigpac ?? 0);
    if (activity != null && sigpacPending > 0) {
      const sigpacId = "sigpac:pending";
      if (!_dismissedInboxIds.contains(sigpacId)) {
        items.add(
          FarmerInboxItem(
            id: sigpacId,
            title: "SIGPAC pendiente",
            body: activity.siexPendingSigpac > 0
                ? "${activity.siexPendingSigpac} entrada(s) SIEX pendientes de SIGPAC"
                : "${activity.farmsMissingSigpac} finca(s) sin SIGPAC — cuaderno incompleto",
            icon: Icons.map_outlined,
            accentColor: NexoColors.warningAmber,
            onOpen: () async {
              if (!mounted) return;
              Navigator.pushNamed(context, Routes.farms);
            },
          ),
        );
      }
    }

    final incidentsPending = activity?.openIncidentsActionCount ?? 0;
    if (incidentsPending > 0) {
      const incidentsId = "incidents:pending";
      if (!_dismissedInboxIds.contains(incidentsId)) {
        items.add(
          FarmerInboxItem(
            id: incidentsId,
            title: "Incidencias pendientes",
            body: "$incidentsPending incidencia(s) requieren acción (tratar, foto o carencia)",
            icon: Icons.bug_report_outlined,
            accentColor: NexoColors.warningAmber,
            onOpen: () async {
              if (!mounted) return;
              Navigator.pushNamed(context, Routes.incidents);
            },
          ),
        );
      }
    }

    for (final notif in _unreadNotifs) {
      items.add(
        FarmerInboxItem(
          id: "notification:${notif.id}",
          title: notif.title,
          body: notif.body,
          icon: Icons.mark_email_unread_outlined,
          accentColor: NexoColors.techCyan,
          onOpen: () => _openNotification(context, notif),
        ),
      );
    }

    return items;
  }

  int get _inboxBadgeCount => _buildInboxItems().length;

  Future<void> _navigateAndRefresh(String route, {Object? arguments}) async {
    await Navigator.pushNamed(context, route, arguments: arguments);
    if (mounted) await _loadFarmerActivity();
  }

  Future<void> _openInboxSheet() async {
    final items = _buildInboxItems();
    await showFarmerInboxSheet(
      context: context,
      items: items,
      onDismiss: (item) async {
        if (item.id.startsWith("notification:")) {
          final notifId = int.tryParse(item.id.split(":").last);
          if (notifId != null) {
            try {
              await _activityRepo.markNotificationRead(notifId);
            } catch (_) {}
          }
        } else {
          await HomeInboxPrefs.dismiss(item.id);
        }
        if (mounted) await _loadFarmerActivity();
      },
    );
  }

  Future<void> _openNotification(BuildContext context, UserNotificationItem item) async {
    try {
      await _activityRepo.markNotificationRead(item.id);
    } catch (_) {}

    if (!context.mounted) return;

    if (item.referenceType == "scan" && item.referenceId != null) {
      try {
        final scan = await ScanRepository().fetchScan(item.referenceId!);
        if (!context.mounted) return;
        Navigator.pushNamed(context, Routes.result, arguments: scan);
        _loadFarmerActivity();
        return;
      } catch (_) {
        if (!context.mounted) return;
        Navigator.pushNamed(context, Routes.history);
        return;
      }
    }
    if (item.referenceType == "incident" && item.referenceId != null) {
      Navigator.pushNamed(context, Routes.incidentDetail, arguments: item.referenceId);
      _loadFarmerActivity();
      return;
    }
    if (item.section == "history") {
      Navigator.pushNamed(context, Routes.history);
      _loadFarmerActivity();
      return;
    }
    if (item.section == "incidents") {
      Navigator.pushNamed(context, Routes.incidents);
      _loadFarmerActivity();
      return;
    }
    if (item.section == "community") {
      Navigator.pushNamed(context, Routes.community);
      _loadFarmerActivity();
      return;
    }
    Navigator.pushNamed(context, Routes.alerts);
    _loadFarmerActivity();
  }

  Future<void> _loadTechDashboard({bool notifyOnNew = false}) async {
    try {
      final repo = TechDashboardRepository();
      final dash = await repo.fetchDashboard();
      final summary = await repo.fetchNotificationSummary();
      final pending = summary["pending_scans"] as int? ?? 0;
      if (notifyOnNew && pending > _lastPendingCount && _lastPendingCount > 0 && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Nueva validación pendiente ($pending en cola)"),
            action: SnackBarAction(
              label: "Ver",
              onPressed: () => Navigator.pushNamed(context, Routes.techScanValidation),
            ),
          ),
        );
      }
      if (!mounted) return;
      setState(() {
        _techOverview = dash["overview"] as Map<String, dynamic>?;
        _pendingScans = pending;
        _unreadNotifications = summary["unread_count"] as int? ?? 0;
        _lastPendingCount = pending;
      });
    } catch (_) {}
  }

  Future<void> _logout(BuildContext context) async {
    await AuthRepository().logout();
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, Routes.login, (_) => false);
  }

  Widget _actionRow(List<Widget> tiles) {
    return Row(
      children: [
        for (var i = 0; i < tiles.length; i++) ...[
          if (i > 0) const SizedBox(width: 10),
          Expanded(child: tiles[i]),
        ],
      ],
    );
  }

  Widget _kpiTile(String label, String value) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: NexoColors.surfaceElevated,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: NexoColors.borderSubtle),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 11, color: NexoColors.textSecondary)),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
          ],
        ),
      ),
    );
  }

  Widget _buildTechHome(String greeting) {
    final o = _techOverview;
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          NexoSectionCard(
            title: "CENTRO DE MANDO",
            children: [
              Row(
                children: [
                  _kpiTile("Eventos 7d", "${o?["events_recent"] ?? "-"}"),
                  const SizedBox(width: 8),
                  _kpiTile("Validados", "${o?["validated_recent"] ?? "-"}"),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  _kpiTile("Alertas", "${o?["active_alerts"] ?? "-"}"),
                  const SizedBox(width: 8),
                  _kpiTile("Zonas", "${o?["active_zones"] ?? "-"}"),
                ],
              ),
              const SizedBox(height: 14),
              if (_pendingScans > 0)
                Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: NexoColors.warningAmber.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: NexoColors.warningAmber.withValues(alpha: 0.5)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.notifications_active, color: NexoColors.warningAmber),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          "$_pendingScans validación(es) pendiente(s)"
                          "${_unreadNotifications > 0 ? " · $_unreadNotifications sin leer" : ""}",
                          style: const TextStyle(fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
              PrimaryButton(
                label: "Validar escaneos ($_pendingScans)",
                onPressed: () => Navigator.pushNamed(context, Routes.techScanValidation),
              ),
              const SizedBox(height: 10),
              _actionRow([
                NexoActionTile(
                  icon: Icons.map_outlined,
                  label: "Mapa técnico",
                  onTap: () => Navigator.pushNamed(context, Routes.map),
                ),
                NexoActionTile(
                  icon: Icons.fact_check_outlined,
                  label: "Eventos mapa",
                  onTap: () => Navigator.pushNamed(context, Routes.techValidation),
                ),
              ]),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFarmerHome() {
    final activity = _activity;
    final incidentsPending = activity?.openIncidentsActionCount ?? 0;

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          NexoSectionCard(
            title: "ESCANEAR",
            children: [
              PrimaryButton(
                label: "Nuevo escaneo",
                compact: true,
                onPressed: () => Navigator.pushNamed(context, Routes.scan),
              ),
              const SizedBox(height: 8),
              _actionRow([
                NexoActionTile(
                  icon: Icons.history_rounded,
                  label: "Historial",
                  showBadge: (activity?.sectionCount("history") ?? 0) > 0,
                  onTap: () => _navigateAndRefresh(Routes.history),
                ),
                NexoActionTile(
                  icon: Icons.insights_rounded,
                  label: "Mi analítica",
                  onTap: () => Navigator.pushNamed(context, Routes.analytics),
                ),
              ]),
            ],
          ),
          NexoSectionCard(
            title: "COLABORACIÓN",
            children: [
              PrimaryButton(
                label: "Mapa de focos",
                compact: true,
                onPressed: () => Navigator.pushNamed(context, Routes.map),
              ),
              const SizedBox(height: 8),
              _actionRow([
                NexoActionTile(
                  icon: Icons.notifications_active_outlined,
                  label: "Alertas",
                  showBadge: (activity?.sectionCount("alerts") ?? 0) > 0,
                  onTap: () => _navigateAndRefresh(Routes.alerts),
                ),
                NexoActionTile(
                  icon: Icons.groups_outlined,
                  label: "Comunidad",
                  showBadge: (activity?.sectionCount("community") ?? 0) > 0,
                  onTap: () => _navigateAndRefresh(Routes.community),
                ),
              ]),
            ],
          ),
          NexoSectionCard(
            title: "GESTIÓN",
            children: [
              _actionRow([
                NexoActionTile(
                  icon: Icons.settings_outlined,
                  label: "Ajustes",
                  onTap: () => Navigator.pushNamed(context, Routes.settings),
                ),
                NexoActionTile(
                  icon: Icons.agriculture_outlined,
                  label: "Mis fincas",
                  showBadge: (activity?.farmsMissingSigpac ?? 0) > 0,
                  onTap: () => _navigateAndRefresh(Routes.farms),
                ),
                NexoActionTile(
                  icon: Icons.bug_report_outlined,
                  label: "Incidencias",
                  showBadge: (activity?.sectionCount("incidents") ?? 0) > 0 || incidentsPending > 0,
                  onTap: () => _navigateAndRefresh(Routes.incidents),
                ),
              ]),
            ],
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final greeting = _userName != null && _userName!.isNotEmpty ? "Hola, $_userName" : "Bienvenido";

    return Scaffold(
      appBar: AppBar(
        title: Text(_isTech ? "AgroPlaga · Perito" : "AgroPlaga"),
        actions: [
          if (!_isTech)
            IconButton(
              tooltip: "Avisos",
              onPressed: _openInboxSheet,
              icon: Badge(
                isLabelVisible: _inboxBadgeCount > 0,
                label: Text("$_inboxBadgeCount"),
                child: const Icon(Icons.notifications_outlined),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isTech ? _loadTechDashboard : _loadFarmerActivity,
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _logout(context),
            tooltip: "Cerrar sesión",
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: MobileLayout.scrollPadding(context),
        keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const AppUpdateBanner(),
            Container(
              width: double.infinity,
              padding: EdgeInsets.fromLTRB(16, _isTech ? 16 : 8, 16, _isTech ? 16 : 10),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [NexoColors.deepBlue, NexoColors.surfaceElevated],
                ),
                border: Border(
                  bottom: BorderSide(color: NexoColors.techCyan.withValues(alpha: 0.25)),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    greeting,
                    style: TextStyle(
                      fontSize: _isTech ? 24 : 20,
                      fontWeight: FontWeight.w800,
                      color: NexoColors.textPrimary,
                      letterSpacing: -0.5,
                    ),
                  ),
                  if (_isTech) ...[
                    const SizedBox(height: 4),
                    const Text(
                      "Centro de mando móvil para validación y supervisión de campo.",
                      style: TextStyle(fontSize: 13, color: NexoColors.textSecondary, height: 1.35),
                    ),
                  ],
                ],
              ),
            ),
            _isTech ? _buildTechHome(greeting) : _buildFarmerHome(),
          ],
        ),
      ),
    );
  }
}

