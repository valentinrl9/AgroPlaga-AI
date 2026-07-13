import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/auth_repository.dart";
import "../../data/repositories/tech_repository.dart";
import "../widgets/carencia_banner.dart";
import "../widgets/nexo_section_card.dart";
import "../widgets/primary_button.dart";

class FieldHomeScreen extends StatefulWidget {
  const FieldHomeScreen({super.key});

  @override
  State<FieldHomeScreen> createState() => _FieldHomeScreenState();
}

class _FieldHomeScreenState extends State<FieldHomeScreen> {
  bool _isTech = false;
  String? _userName;
  Map<String, dynamic>? _techOverview;
  int _pendingScans = 0;

  @override
  void initState() {
    super.initState();
    _loadProfile();
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
    if (isTech) await _loadTechDashboard();
  }

  Future<void> _loadTechDashboard() async {
    try {
      final repo = TechDashboardRepository();
      final dash = await repo.fetchDashboard();
      final scans = await repo.fetchPendingScans();
      if (!mounted) return;
      setState(() {
        _techOverview = dash["overview"] as Map<String, dynamic>?;
        _pendingScans = scans.length;
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
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const CarenciaBanner(),
          NexoSectionCard(
            title: "ESCANEAR",
            children: [
              PrimaryButton(
                label: "Nuevo escaneo",
                onPressed: () => Navigator.pushNamed(context, Routes.scan),
              ),
              const SizedBox(height: 10),
              _actionRow([
                NexoActionTile(
                  icon: Icons.history_rounded,
                  label: "Historial",
                  onTap: () => Navigator.pushNamed(context, Routes.history),
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
                onPressed: () => Navigator.pushNamed(context, Routes.map),
              ),
              const SizedBox(height: 10),
              _actionRow([
                NexoActionTile(
                  icon: Icons.notifications_active_outlined,
                  label: "Alertas",
                  onTap: () => Navigator.pushNamed(context, Routes.alerts),
                ),
                NexoActionTile(
                  icon: Icons.groups_outlined,
                  label: "Comunidad",
                  onTap: () => Navigator.pushNamed(context, Routes.community),
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
                  label: "Ajustes API",
                  onTap: () => Navigator.pushNamed(context, Routes.settings),
                ),
                NexoActionTile(
                  icon: Icons.agriculture_outlined,
                  label: "Mis fincas",
                  onTap: () => Navigator.pushNamed(context, Routes.farms),
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
        title: Text(_isTech ? "NEXO Field · Perito" : "NEXO Field"),
        actions: [
          if (_isTech)
            IconButton(icon: const Icon(Icons.refresh), onPressed: _loadTechDashboard),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _logout(context),
            tooltip: "Cerrar sesión",
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 24),
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
                    style: const TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.w800,
                      color: NexoColors.textPrimary,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    _isTech
                        ? "Centro de mando móvil para validación y supervisión de campo."
                        : "Diagnostica plagas y contribuye al mapa de tu comarca.",
                    style: const TextStyle(fontSize: 14, color: NexoColors.textSecondary, height: 1.4),
                  ),
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
