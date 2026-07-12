import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/auth_repository.dart";
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

  @override
  Widget build(BuildContext context) {
    final greeting = _userName != null && _userName!.isNotEmpty ? "Hola, $_userName" : "Bienvenido";

    return Scaffold(
      appBar: AppBar(
        title: const Text("NEXO Field"),
        actions: [
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
                  const Text(
                    "Diagnostica plagas y contribuye al mapa de tu comarca.",
                    style: TextStyle(fontSize: 14, color: NexoColors.textSecondary, height: 1.4),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
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
                      if (_isTech) ...[
                        const SizedBox(height: 12),
                        PrimaryButton(
                          label: "Validar eventos (técnico)",
                          onPressed: () => Navigator.pushNamed(context, Routes.techValidation),
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
