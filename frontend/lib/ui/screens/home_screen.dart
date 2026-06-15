import "package:flutter/material.dart";

import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/auth_repository.dart";
import "../widgets/primary_button.dart";

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
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

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(top: 4, bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: Color(0xFF757575),
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final greeting = _userName != null && _userName!.isNotEmpty ? "Hola, $_userName" : "Bienvenido";

    return Scaffold(
      appBar: AppBar(
        title: const Text("AgroPlaga AI"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _logout(context),
            tooltip: "Cerrar sesión",
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              greeting,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF424242)),
            ),
            const SizedBox(height: 4),
            const Text(
              "Diagnostica plagas y contribuye al mapa de tu comarca.",
              style: TextStyle(fontSize: 14, color: Color(0xFF757575)),
            ),
            const SizedBox(height: 20),
            _sectionTitle("ESCANEAR"),
            PrimaryButton(
              label: "Nuevo escaneo",
              onPressed: () => Navigator.pushNamed(context, Routes.scan),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pushNamed(context, Routes.history),
                    child: const Text("Historial"),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pushNamed(context, Routes.analytics),
                    child: const Text("Mi analítica"),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _sectionTitle("COLABORACIÓN"),
            PrimaryButton(
              label: "Mapa de focos",
              onPressed: () => Navigator.pushNamed(context, Routes.map),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pushNamed(context, Routes.alerts),
                    child: const Text("Alertas"),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pushNamed(context, Routes.community),
                    child: const Text("Comunidad"),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _sectionTitle("GESTIÓN"),
            OutlinedButton(
              onPressed: () => Navigator.pushNamed(context, Routes.settings),
              child: const Text("Servidor API / Ajustes"),
            ),
            const SizedBox(height: 10),
            OutlinedButton(
              onPressed: () => Navigator.pushNamed(context, Routes.farms),
              child: const Text("Mis fincas"),
            ),
            if (_isTech) ...[
              const SizedBox(height: 10),
              PrimaryButton(
                label: "Validar eventos (técnico)",
                onPressed: () => Navigator.pushNamed(context, Routes.techValidation),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
