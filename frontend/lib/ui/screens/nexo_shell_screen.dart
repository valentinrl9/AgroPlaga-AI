import "dart:async";

import "package:flutter/material.dart";

import "../../data/repositories/activity_repository.dart";
import "climate_module_screen.dart";
import "field_home_screen.dart";
import "siex_module_screen.dart";

class NexoShellScreen extends StatefulWidget {
  const NexoShellScreen({super.key});

  @override
  State<NexoShellScreen> createState() => _NexoShellScreenState();
}

class _NexoShellScreenState extends State<NexoShellScreen> {
  int _index = 0;
  int _siexBadge = 0;
  Timer? _badgeTimer;
  final _activityRepo = ActivityRepository();

  @override
  void initState() {
    super.initState();
    _loadSiexBadge();
    _badgeTimer = Timer.periodic(const Duration(seconds: 30), (_) => _loadSiexBadge());
  }

  @override
  void dispose() {
    _badgeTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadSiexBadge() async {
    try {
      final summary = await _activityRepo.fetchSummary();
      if (!mounted) return;
      setState(() {
        _siexBadge = summary.siexPendingSigpac + summary.farmsMissingSigpac;
      });
    } catch (_) {}
  }

  Widget _badgedIcon(IconData icon, {bool show = false}) {
    if (!show) return Icon(icon);
    return Badge(
      isLabelVisible: _siexBadge > 0,
      label: Text("$_siexBadge"),
      child: Icon(icon),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _index,
        children: [
          FieldHomeScreen(isActive: _index == 0),
          ClimateModuleScreen(isActive: _index == 1),
          SiexModuleScreen(isActive: _index == 2),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (value) {
          setState(() => _index = value);
          if (value == 2) _loadSiexBadge();
        },
        destinations: [
          const NavigationDestination(
            icon: Icon(Icons.eco_outlined),
            selectedIcon: Icon(Icons.eco),
            label: "Inicio",
          ),
          const NavigationDestination(
            icon: Icon(Icons.cloud_outlined),
            selectedIcon: Icon(Icons.cloud),
            label: "Clima",
          ),
          NavigationDestination(
            icon: _badgedIcon(Icons.description_outlined, show: _siexBadge > 0),
            selectedIcon: _badgedIcon(Icons.description, show: _siexBadge > 0),
            label: "SIEX",
          ),
        ],
      ),
    );
  }
}
