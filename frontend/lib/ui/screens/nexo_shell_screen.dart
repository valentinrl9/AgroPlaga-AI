import "package:flutter/material.dart";

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

  static const _tabs = [
    FieldHomeScreen(),
    ClimateModuleScreen(),
    SiexModuleScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _index,
        children: _tabs,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (value) => setState(() => _index = value),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.eco_outlined),
            selectedIcon: Icon(Icons.eco),
            label: "Field",
          ),
          NavigationDestination(
            icon: Icon(Icons.cloud_outlined),
            selectedIcon: Icon(Icons.cloud),
            label: "Climate",
          ),
          NavigationDestination(
            icon: Icon(Icons.description_outlined),
            selectedIcon: Icon(Icons.description),
            label: "SIEX",
          ),
        ],
      ),
    );
  }
}
